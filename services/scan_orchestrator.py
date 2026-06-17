import json
import re
import subprocess
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from ai.providers import AnthropicProvider, LLMProvider, OllamaProvider, OpenAIProvider
from models.finding import Finding
from models.project import Project
from models.scan import Scan
from models.target import Target
from services.command_runner import CommandExecutionError, CommandResult, run_command
from services.tool_registry import ToolRegistryError, build_command, list_tools


VALID_PLANNED_STATUSES = {"pending_approval"}
VALID_APPROVED_STATUSES = {"approved"}


class ScanOrchestrationError(ValueError):
    pass


def get_provider(name: str = "ollama") -> LLMProvider:
    providers = {
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    provider_cls = providers.get(name)
    if not provider_cls:
        raise ScanOrchestrationError(f"Unsupported AI provider: {name}")
    return provider_cls()


def _extract_json_object(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ScanOrchestrationError("AI response did not contain JSON")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ScanOrchestrationError("AI response JSON was malformed") from exc


def _normalize_plan(raw_plan: dict[str, Any]) -> dict[str, Any]:
    if "steps" in raw_plan:
        steps = raw_plan.get("steps") or []
        if not steps:
            raise ScanOrchestrationError("AI plan did not include any steps")
        first_step = steps[0]
    else:
        first_step = raw_plan

    tool = first_step.get("tool")
    if not isinstance(tool, str):
        raise ScanOrchestrationError("AI plan must include a tool name")

    options = first_step.get("options") or []
    if not isinstance(options, list) or not all(isinstance(option, str) for option in options):
        raise ScanOrchestrationError("AI plan options must be a list of strings")

    return {
        "tool": tool,
        "options": options,
        "reason": str(first_step.get("reason", raw_plan.get("reason", ""))),
    }


def _planner_prompt(goal: str, project: Project, target: Target) -> str:
    tools = json.dumps(list_tools(), indent=2)
    return f"""
You are planning an authorized cybersecurity scan inside GlitchRecon.
Return only valid JSON. Do not include shell commands.

Project:
- id: {project.id}
- name: {project.name}
- scope: {project.scope}

Target:
- id: {target.id}
- type: {target.type}
- value: {target.value}

User goal:
{goal}

Allowed tools:
{tools}

Return this JSON shape:
{{"tool":"one allowed tool name","options":["zero or more allowed option names"],"reason":"short reason"}}
""".strip()


def _get_project_target(db: Session, project_id: int, target_id: int) -> tuple[Project, Target]:
    project = db.query(Project).filter(Project.id == project_id).first()
    target = db.query(Target).filter(Target.id == target_id, Target.project_id == project_id).first()
    if not project or not target:
        raise ScanOrchestrationError("Invalid project_id or target_id")
    return project, target


def create_scan_plan(
    db: Session,
    project_id: int,
    target_id: int,
    goal: str,
    provider_name: str = "ollama",
    provider: LLMProvider | None = None,
) -> Scan:
    project, target = _get_project_target(db, project_id, target_id)
    provider = provider or get_provider(provider_name)
    raw_response = provider.generate(_planner_prompt(goal, project, target))
    plan = _normalize_plan(_extract_json_object(raw_response))
    command_spec = build_command(plan["tool"], target.type, target.value, plan["options"])

    proposed_plan = {
        "goal": goal,
        "provider": provider_name,
        "tool": plan["tool"],
        "options": plan["options"],
        "reason": plan["reason"],
        "command": command_spec.argv,
        "stdin": command_spec.stdin,
        "risk_level": command_spec.risk_level,
        "timeout_seconds": command_spec.timeout_seconds,
    }

    scan = Scan(
        project_id=project_id,
        target_id=target_id,
        scanner=plan["tool"],
        status="pending_approval",
        proposed_plan=json.dumps(proposed_plan),
        executed_command=json.dumps(command_spec.argv),
        started_at=None,
        finished_at=None,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def approve_scan(db: Session, scan_id: int) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise ScanOrchestrationError("Scan not found")
    if scan.status not in VALID_PLANNED_STATUSES:
        raise ScanOrchestrationError("Only pending approval scans can be approved")

    scan.status = "approved"
    scan.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(scan)
    return scan


def _load_scan_command(db: Session, scan: Scan):
    target = db.query(Target).filter(Target.id == scan.target_id, Target.project_id == scan.project_id).first()
    if not target:
        raise ScanOrchestrationError("Scan target is outside project scope")

    plan = json.loads(scan.proposed_plan or "{}")
    return build_command(plan.get("tool", scan.scanner), target.type, target.value, plan.get("options", []))


def _persist_result(db: Session, scan: Scan, result: CommandResult):
    scan.stdout = result.stdout
    scan.stderr = result.stderr
    scan.return_code = result.return_code
    scan.executed_command = json.dumps(result.argv)
    scan.started_at = result.started_at
    scan.finished_at = result.finished_at
    scan.status = "completed" if result.return_code == 0 else "failed"
    if result.return_code != 0:
        scan.error_message = result.stderr or f"Command exited with code {result.return_code}"

    _create_findings_from_output(db, scan, result)
    db.commit()
    db.refresh(scan)


def _create_findings_from_output(db: Session, scan: Scan, result: CommandResult):
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    for line in lines[:25]:
        db.add(
            Finding(
                scan_id=scan.id,
                title=f"{scan.scanner} result",
                severity="info",
                description=line[:500],
                evidence=line[:1000],
                remediation="Review the tool output and validate the finding manually.",
                cve=None,
                cvss=None,
            )
        )


def run_approved_scan(db: Session, scan_id: int) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise ScanOrchestrationError("Scan not found")
    if scan.status not in VALID_APPROVED_STATUSES:
        raise ScanOrchestrationError("Scan must be approved before execution")

    command_spec = _load_scan_command(db, scan)
    scan.status = "running"
    scan.started_at = datetime.now(timezone.utc)
    db.commit()

    try:
        result = run_command(command_spec)
    except (CommandExecutionError, ToolRegistryError, subprocess.TimeoutExpired) as exc:
        scan.status = "failed"
        scan.error_message = str(exc)
        scan.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)
        return scan

    _persist_result(db, scan, result)
    return scan


def get_scan_logs(db: Session, scan_id: int) -> dict[str, Any]:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise ScanOrchestrationError("Scan not found")
    return {
        "scan_id": scan.id,
        "status": scan.status,
        "command": json.loads(scan.executed_command or "[]"),
        "stdout": scan.stdout,
        "stderr": scan.stderr,
        "return_code": scan.return_code,
        "error_message": scan.error_message,
    }

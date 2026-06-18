import json
import os
import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from ai.providers import AnthropicProvider, LLMProvider, OllamaProvider, OpenAIProvider
from models.finding import Finding
from models.project import Project
from models.scan import Scan
from models.target import Target
from services.scan_job_runner import (
    ScanJobError,
    cancel_scan,
    read_scan_logs,
    refresh_scan_status,
    start_scan_job,
)
from services.tool_registry import ToolRegistryError, build_command, derive_hostname, list_tools


VALID_PLANNED_STATUSES = {"pending_approval"}
VALID_APPROVED_STATUSES = {"approved"}
SCAN_PLAN_TIMEOUT_SECONDS = float(os.getenv("SCAN_PLAN_TIMEOUT_SECONDS", "20"))
MULTI_RECON_MARKERS = (
    "all reconnaissance",
    "all recon",
    "comprehensive reconnaissance",
    "use all recon",
    "attack surface",
)


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


def _fallback_plan(target: Target, goal: str, reason: str) -> dict[str, Any]:
    target_type = (target.type or "").lower()
    goal_text = (goal or "").lower()

    if target_type == "url":
        if any(word in goal_text for word in ("crawl", "spider", "links", "recon")):
            return {
                "tool": "katana",
                "options": ["depth_3"],
                "reason": f"{reason}; used safe default web crawler plan",
                "planner": "fallback",
            }
        return {
            "tool": "nuclei",
            "options": ["fast"],
            "reason": f"{reason}; used safe default vulnerability scan plan",
            "planner": "fallback",
        }

    if target_type in {"domain", "hostname"}:
        return {
            "tool": "amass",
            "options": ["passive"],
            "reason": f"{reason}; used safe default passive enumeration plan",
            "planner": "fallback",
        }

    if target_type in {"repo", "path"}:
        tool = "trufflehog" if "trufflehog" in goal_text else "gitleaks"
        return {
            "tool": tool,
            "options": [],
            "reason": f"{reason}; used safe default secret scanning plan",
            "planner": "fallback",
        }

    raise ScanOrchestrationError(f"No safe fallback plan for target type: {target.type}")


def _wants_multi_recon(goal: str) -> bool:
    goal_text = (goal or "").lower()
    return any(marker in goal_text for marker in MULTI_RECON_MARKERS)


def _recon_steps_for_target(target: Target) -> list[dict[str, Any]]:
    target_type = (target.type or "").lower()
    target_value = target.value

    if target_type == "url":
        hostname = derive_hostname(target_value)
        return [
            {"tool": "katana", "options": ["depth_3"], "target_type": "url", "target_value": target_value},
            {"tool": "hakrawler", "options": ["depth_3"], "target_type": "url", "target_value": target_value},
            {"tool": "gau", "options": [], "target_type": "domain", "target_value": hostname},
            {"tool": "waybackurls", "options": [], "target_type": "domain", "target_value": hostname},
            {"tool": "whatweb", "options": [], "target_type": "url", "target_value": target_value},
            {"tool": "wappalyzer", "options": [], "target_type": "url", "target_value": target_value},
            {"tool": "nuclei", "options": ["fast"], "target_type": "url", "target_value": target_value},
        ]

    if target_type in {"domain", "hostname"}:
        return [
            {"tool": "amass", "options": ["passive"], "target_type": target_type, "target_value": target_value},
            {"tool": "assetfinder", "options": ["subs_only"], "target_type": target_type, "target_value": target_value},
            {"tool": "findomain", "options": [], "target_type": target_type, "target_value": target_value},
            {"tool": "dnsx", "options": [], "target_type": target_type, "target_value": target_value},
            {"tool": "gau", "options": [], "target_type": target_type, "target_value": target_value},
            {"tool": "waybackurls", "options": [], "target_type": target_type, "target_value": target_value},
        ]

    return []


def _build_recon_suite_plan(target: Target, goal: str, provider_name: str, reason: str) -> dict[str, Any]:
    steps = []
    for step in _recon_steps_for_target(target):
        command_spec = build_command(step["tool"], step["target_type"], step["target_value"], step["options"])
        steps.append(
            {
                **step,
                "command": command_spec.argv,
                "stdin": command_spec.stdin,
                "risk_level": command_spec.risk_level,
                "timeout_seconds": command_spec.timeout_seconds,
                "status": "pending",
            }
        )

    if not steps:
        raise ScanOrchestrationError(f"No recon suite available for target type: {target.type}")

    return {
        "goal": goal,
        "provider": provider_name,
        "planner": "fallback",
        "mode": "multi_step",
        "tool": "recon_suite",
        "options": [],
        "reason": reason,
        "steps": steps,
        "plan_timeout_seconds": SCAN_PLAN_TIMEOUT_SECONDS,
    }


def _provider_generate_plan(provider: LLMProvider, prompt: str) -> str:
    generate_json = getattr(provider, "generate_json", None)
    if callable(generate_json):
        return generate_json(prompt)
    return provider.generate(prompt)


def _planner_error_reason(exc: BaseException) -> str:
    message = str(exc).strip()
    if message:
        return f"{type(exc).__name__}: {message}"
    return type(exc).__name__


def _plan_with_fallback(provider: LLMProvider, prompt: str, target: Target, goal: str) -> dict[str, Any]:
    try:
        raw_response = _provider_generate_plan(provider, prompt)
        plan = _normalize_plan(_extract_json_object(raw_response))
        plan["planner"] = "ai"
        return plan
    except Exception as exc:
        return _fallback_plan(target, goal, f"AI planner failed: {_planner_error_reason(exc)}")


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
    if _wants_multi_recon(goal):
        proposed_plan = _build_recon_suite_plan(
            target,
            goal,
            provider_name,
            "Comprehensive reconnaissance requested; created safe multi-tool recon suite",
        )
        scan = Scan(
            project_id=project_id,
            target_id=target_id,
            scanner="recon_suite",
            status="pending_approval",
            proposed_plan=json.dumps(proposed_plan),
            executed_command=json.dumps([step["command"] for step in proposed_plan["steps"]]),
            started_at=None,
            finished_at=None,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        _create_child_scans(db, scan, proposed_plan)
        db.refresh(scan)
        return scan

    provider_error = None
    if provider is None:
        try:
            provider = get_provider(provider_name)
        except ScanOrchestrationError:
            raise
        except Exception as exc:
            provider_error = exc

    if provider_error:
        plan = _fallback_plan(target, goal, f"AI provider failed: {_planner_error_reason(provider_error)}")
    else:
        plan = _plan_with_fallback(provider, _planner_prompt(goal, project, target), target, goal)
    try:
        command_spec = build_command(plan["tool"], target.type, target.value, plan["options"])
    except ToolRegistryError as exc:
        if plan.get("planner") == "fallback":
            raise ScanOrchestrationError(str(exc)) from exc
        plan = _fallback_plan(target, goal, f"AI planner selected an unsupported tool or option: {exc}")
        command_spec = build_command(plan["tool"], target.type, target.value, plan["options"])

    proposed_plan = {
        "goal": goal,
        "provider": provider_name,
        "planner": plan.get("planner", "ai"),
        "tool": plan["tool"],
        "options": plan["options"],
        "reason": plan["reason"],
        "command": command_spec.argv,
        "stdin": command_spec.stdin,
        "risk_level": command_spec.risk_level,
        "timeout_seconds": command_spec.timeout_seconds,
        "plan_timeout_seconds": SCAN_PLAN_TIMEOUT_SECONDS,
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


def _create_child_scans(db: Session, parent: Scan, proposed_plan: dict[str, Any]):
    for step in proposed_plan.get("steps", []):
        child_plan = {
            "goal": proposed_plan.get("goal"),
            "provider": proposed_plan.get("provider"),
            "planner": proposed_plan.get("planner"),
            "mode": "child_step",
            "parent_scan_id": parent.id,
            "tool": step["tool"],
            "options": step.get("options", []),
            "reason": proposed_plan.get("reason"),
            "command": step["command"],
            "stdin": step.get("stdin"),
            "risk_level": step.get("risk_level"),
            "timeout_seconds": step.get("timeout_seconds"),
            "target_type": step.get("target_type"),
            "target_value": step.get("target_value"),
        }
        db.add(
            Scan(
                parent_scan_id=parent.id,
                project_id=parent.project_id,
                target_id=parent.target_id,
                scanner=step["tool"],
                status="pending",
                proposed_plan=json.dumps(child_plan),
                executed_command=json.dumps(step["command"]),
            )
        )
    db.commit()


def approve_scan(db: Session, scan_id: int) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise ScanOrchestrationError("Scan not found")
    if scan.status not in VALID_PLANNED_STATUSES:
        raise ScanOrchestrationError("Only pending approval scans can be approved")

    scan.status = "approved"
    scan.approved_at = datetime.now(timezone.utc)
    for child in _child_scans(db, scan.id):
        if child.status == "pending":
            child.status = "approved"
            child.approved_at = scan.approved_at
    db.commit()
    db.refresh(scan)
    return scan


def _load_scan_command(db: Session, scan: Scan):
    target = db.query(Target).filter(Target.id == scan.target_id, Target.project_id == scan.project_id).first()
    if not target:
        raise ScanOrchestrationError("Scan target is outside project scope")

    plan = json.loads(scan.proposed_plan or "{}")
    return build_command(
        plan.get("tool", scan.scanner),
        plan.get("target_type", target.type),
        plan.get("target_value", target.value),
        plan.get("options", []),
    )


def _child_scans(db: Session, parent_scan_id: int):
    return db.query(Scan).filter(Scan.parent_scan_id == parent_scan_id).order_by(Scan.id).all()


def _is_parent_scan(scan: Scan) -> bool:
    try:
        plan = json.loads(scan.proposed_plan or "{}")
    except json.JSONDecodeError:
        return False
    return plan.get("mode") == "multi_step"


def _refresh_parent_status(db: Session, parent: Scan) -> Scan:
    children = _child_scans(db, parent.id)
    for child in children:
        previous_status = child.status
        refresh_scan_status(child)
        if previous_status == "running" and child.status in {"completed", "failed"}:
            logs = read_scan_logs(child)
            _create_findings_from_output(db, child, logs.get("output") or "")

    if any(child.status == "running" for child in children):
        parent.status = "running"
    elif children and all(child.status == "completed" for child in children):
        parent.status = "completed"
        parent.return_code = 0
        parent.finished_at = datetime.now(timezone.utc)
    elif any(child.status == "failed" for child in children):
        parent.status = "failed"
        parent.return_code = 1
        parent.finished_at = datetime.now(timezone.utc)
        parent.error_message = "One or more child scans failed"
    elif any(child.status == "cancelled" for child in children):
        parent.status = "cancelled"
        parent.return_code = -1
        parent.finished_at = datetime.now(timezone.utc)
    return parent


def _start_next_child(db: Session, parent: Scan) -> Scan | None:
    _refresh_parent_status(db, parent)
    running = next((child for child in _child_scans(db, parent.id) if child.status == "running"), None)
    if running:
        return running

    next_child = next((child for child in _child_scans(db, parent.id) if child.status in {"approved", "pending"}), None)
    if not next_child:
        return None

    if next_child.status == "pending":
        next_child.status = "approved"
        next_child.approved_at = parent.approved_at

    command_spec = _load_scan_command(db, next_child)
    start_scan_job(next_child, command_spec)
    parent.status = "running"
    parent.started_at = parent.started_at or datetime.now(timezone.utc)
    return next_child


def _create_findings_from_output(db: Session, scan: Scan, output: str):
    if db.query(Finding).filter(Finding.scan_id == scan.id).first():
        return

    lines = [line.strip() for line in output.splitlines() if line.strip()]
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

    if _is_parent_scan(scan):
        try:
            _start_next_child(db, scan)
        except (ScanJobError, ToolRegistryError, RuntimeError) as exc:
            scan.status = "failed"
            scan.error_message = str(exc)
            scan.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)
        return scan

    command_spec = _load_scan_command(db, scan)
    try:
        start_scan_job(scan, command_spec)
    except (ScanJobError, ToolRegistryError, RuntimeError) as exc:
        scan.status = "failed"
        scan.error_message = str(exc)
        scan.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)
        return scan

    db.commit()
    db.refresh(scan)
    return scan


def get_scan_status(db: Session, scan_id: int) -> dict[str, Any]:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise ScanOrchestrationError("Scan not found")

    if _is_parent_scan(scan):
        _refresh_parent_status(db, scan)
        if scan.status == "running":
            _start_next_child(db, scan)
    else:
        previous_status = scan.status
        refresh_scan_status(scan)
        if previous_status == "running" and scan.status in {"completed", "failed"}:
            logs = read_scan_logs(scan)
            _create_findings_from_output(db, scan, logs.get("output") or "")

    db.commit()
    db.refresh(scan)
    children = _child_scans(db, scan.id) if _is_parent_scan(scan) else []
    return {
        "scan_id": scan.id,
        "status": scan.status,
        "pid": scan.pid,
        "started_at": scan.started_at,
        "finished_at": scan.finished_at,
        "return_code": scan.return_code,
        "timed_out": bool(scan.timed_out),
        "error_message": scan.error_message,
        "status_url": f"/scan/{scan.id}/status",
        "logs_url": f"/scan/{scan.id}/logs",
        "children": [
            {
                "scan_id": child.id,
                "scanner": child.scanner,
                "status": child.status,
                "return_code": child.return_code,
                "logs_url": f"/scan/{child.id}/logs",
            }
            for child in children
        ],
    }


def get_scan_logs(db: Session, scan_id: int) -> dict[str, Any]:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise ScanOrchestrationError("Scan not found")
    if _is_parent_scan(scan):
        _refresh_parent_status(db, scan)
        children = _child_scans(db, scan.id)
        db.commit()
        return {
            "scan_id": scan.id,
            "status": scan.status,
            "scanner": scan.scanner,
            "children": [
                {
                    "scan_id": child.id,
                    "scanner": child.scanner,
                    "status": child.status,
                    "return_code": child.return_code,
                    "log_path": child.log_path,
                }
                for child in children
            ],
        }

    refresh_scan_status(scan)
    db.commit()
    db.refresh(scan)
    return read_scan_logs(scan)


def cancel_running_scan(db: Session, scan_id: int) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise ScanOrchestrationError("Scan not found")
    try:
        if _is_parent_scan(scan):
            for child in _child_scans(db, scan.id):
                if child.status == "running":
                    cancel_scan(child)
                elif child.status in {"pending", "approved"}:
                    child.status = "cancelled"
                    child.cancelled_at = datetime.now(timezone.utc)
            scan.status = "cancelled"
            scan.cancelled_at = datetime.now(timezone.utc)
            scan.finished_at = scan.cancelled_at
            scan.return_code = -1
        else:
            cancel_scan(scan)
    except ScanJobError as exc:
        raise ScanOrchestrationError(str(exc)) from exc
    db.commit()
    db.refresh(scan)
    return scan


def list_child_scans(db: Session, scan_id: int) -> list[Scan]:
    parent = db.query(Scan).filter(Scan.id == scan_id).first()
    if not parent:
        raise ScanOrchestrationError("Scan not found")
    return _child_scans(db, scan_id)

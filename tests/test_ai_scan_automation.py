import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import services.scan_orchestrator as scan_orchestrator
import services.scan_job_runner as scan_job_runner
from core.database import Base
from models.finding import Finding
from models.project import Project
from models.scan import Scan
from models.target import Target
from models.users import Users
from services.command_runner import CommandExecutionError, run_command
from services.scan_job_runner import cancel_scan, read_scan_logs, refresh_scan_status
from services.scan_orchestrator import (
    ScanOrchestrationError,
    approve_scan,
    create_scan_plan,
    get_scan_status,
    list_child_scans,
    run_approved_scan,
)
from services.tool_registry import ToolRegistryError, build_command


class FakeProvider:
    def __init__(self, response):
        self.response = response

    def generate(self, prompt: str, model: str | None = None) -> str:
        return self.response


class TimeoutProvider:
    def generate(self, prompt: str, model: str | None = None) -> str:
        raise TimeoutError("planner took too long")


class HttpxTimeoutProvider:
    def generate(self, prompt: str, model: str | None = None) -> str:
        raise httpx.ReadTimeout("ollama read timed out")


class BrokenProvider:
    def generate(self, prompt: str, model: str | None = None) -> str:
        raise Exception("ollama client exploded")


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    db.add(Project(id=1, owner_id=1, name="Demo", description="Demo", scope="example.com", status="active"))
    db.add(Target(id=1, project_id=1, type="url", value="https://example.com", notes="web"))
    db.commit()
    try:
        yield db
    finally:
        db.close()


def test_tool_registry_rejects_unknown_tools_and_options():
    with pytest.raises(ToolRegistryError):
        build_command("rm", "url", "https://example.com")

    with pytest.raises(ToolRegistryError):
        build_command("nuclei", "url", "https://example.com", ["delete_everything"])


def test_command_runner_blocks_shell_metacharacters():
    spec = build_command("nuclei", "url", "https://example.com;rm", ["fast"])

    with pytest.raises(CommandExecutionError):
        run_command(spec)


def test_ai_planner_malformed_json_falls_back_to_safe_plan(db_session):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="scan the target",
        provider=FakeProvider("not json"),
    )

    assert scan.status == "pending_approval"
    assert scan.scanner == "nuclei"
    assert '"planner": "fallback"' in scan.proposed_plan
    assert '"fast"' in scan.proposed_plan


def test_ai_planner_timeout_falls_back_to_nuclei_fast(db_session):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="Run a quick vulnerability scan against this web target",
        provider=TimeoutProvider(),
    )

    assert scan.status == "pending_approval"
    assert scan.scanner == "nuclei"
    assert '"planner": "fallback"' in scan.proposed_plan
    assert '"fast"' in scan.proposed_plan


def test_ai_planner_httpx_read_timeout_falls_back_to_nuclei_fast(db_session):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="Run a quick vulnerability scan against this web target",
        provider=HttpxTimeoutProvider(),
    )

    assert scan.status == "pending_approval"
    assert scan.scanner == "nuclei"
    assert '"planner": "fallback"' in scan.proposed_plan
    assert "ReadTimeout" in scan.proposed_plan


def test_ai_planner_generic_provider_error_falls_back(db_session):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="Run a quick vulnerability scan against this web target",
        provider=BrokenProvider(),
    )

    assert scan.status == "pending_approval"
    assert scan.scanner == "nuclei"
    assert '"planner": "fallback"' in scan.proposed_plan
    assert "ollama client exploded" in scan.proposed_plan


def test_unsupported_provider_returns_clean_error(db_session):
    with pytest.raises(ScanOrchestrationError, match="Unsupported AI provider"):
        create_scan_plan(
            db_session,
            project_id=1,
            target_id=1,
            goal="scan the target",
            provider_name="not-a-provider",
        )


def test_ai_unsupported_tool_falls_back(db_session):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="scan the target",
        provider=FakeProvider('{"tool":"rm","options":["rf"],"reason":"bad"}'),
    )

    assert scan.status == "pending_approval"
    assert scan.scanner == "nuclei"
    assert '"planner": "fallback"' in scan.proposed_plan


def test_comprehensive_recon_url_creates_multi_step_parent_and_children(db_session):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="Perform comprehensive reconnaissance and map the attack surface",
        provider=FakeProvider('{"tool":"amass","options":["passive"],"reason":"bad for url"}'),
    )

    plan = json.loads(scan.proposed_plan)
    children = list_child_scans(db_session, scan.id)
    child_tools = [child.scanner for child in children]

    assert scan.scanner == "recon_suite"
    assert plan["mode"] == "multi_step"
    assert {"katana", "hakrawler", "gau", "waybackurls", "whatweb", "wappalyzer", "nuclei"}.issubset(child_tools)
    assert "amass" not in child_tools
    assert all(child.parent_scan_id == scan.id for child in children)


def test_comprehensive_recon_domain_creates_domain_tools(db_session):
    db_session.add(Target(id=2, project_id=1, type="domain", value="example.com", notes="domain"))
    db_session.commit()

    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=2,
        goal="Use all recon tools for attack surface mapping",
        provider=FakeProvider('{"tool":"amass","options":["passive"],"reason":"ok"}'),
    )

    child_tools = [child.scanner for child in list_child_scans(db_session, scan.id)]

    assert scan.scanner == "recon_suite"
    assert {"amass", "assetfinder", "findomain", "dnsx", "gau", "waybackurls"}.issubset(child_tools)


def test_parent_scan_launches_children_sequentially(monkeypatch, db_session):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="Perform comprehensive reconnaissance and map the attack surface",
        provider=FakeProvider('{"tool":"katana","options":["depth_3"],"reason":"ok"}'),
    )
    approve_scan(db_session, scan.id)

    launched = []

    def fake_start_scan_job(child, command_spec):
        launched.append(child.scanner)
        child.status = "running"
        child.pid = 12345
        child.log_path = f"storage/scan_jobs/{child.id}.log"
        child.exit_path = f"storage/scan_jobs/{child.id}.exit"
        child.executed_command = json.dumps(command_spec.argv)
        child.started_at = datetime.now(timezone.utc)
        return child

    monkeypatch.setattr(scan_orchestrator, "start_scan_job", fake_start_scan_job)
    running_parent = run_approved_scan(db_session, scan.id)
    children = list_child_scans(db_session, scan.id)

    assert running_parent.status == "running"
    assert launched == [children[0].scanner]
    assert sum(child.status == "running" for child in children) == 1


def test_scan_lifecycle_requires_approval_and_starts_background_job(monkeypatch, db_session):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="quick nuclei scan",
        provider=FakeProvider('{"tool":"nuclei","options":["fast"],"reason":"quick coverage"}'),
    )

    assert scan.status == "pending_approval"
    with pytest.raises(ScanOrchestrationError):
        run_approved_scan(db_session, scan.id)

    approved = approve_scan(db_session, scan.id)
    assert approved.status == "approved"

    def fake_start_scan_job(scan, command_spec):
        scan.status = "running"
        scan.pid = 12345
        scan.log_path = "storage/scan_jobs/test.log"
        scan.exit_path = "storage/scan_jobs/test.exit"
        scan.executed_command = '["nuclei"]'
        scan.started_at = datetime.now(timezone.utc)
        return scan

    monkeypatch.setattr(scan_orchestrator, "start_scan_job", fake_start_scan_job)
    running = run_approved_scan(db_session, scan.id)

    assert running.status == "running"
    assert running.pid == 12345
    assert "nuclei" in running.executed_command


def test_status_poll_marks_completed_and_creates_findings(monkeypatch, db_session, tmp_path):
    scan = create_scan_plan(
        db_session,
        project_id=1,
        target_id=1,
        goal="quick nuclei scan",
        provider=FakeProvider('{"tool":"nuclei","options":["fast"],"reason":"quick coverage"}'),
    )
    approve_scan(db_session, scan.id)

    log_path = tmp_path / "scan.log"
    exit_path = tmp_path / "scan.exit"
    log_path.write_text("https://example.com [info] test finding\n", encoding="utf-8")
    exit_path.write_text("0", encoding="utf-8")

    def fake_start_scan_job(scan, command_spec):
        scan.status = "running"
        scan.pid = 12345
        scan.log_path = str(log_path)
        scan.exit_path = str(exit_path)
        scan.executed_command = '["nuclei"]'
        scan.started_at = datetime.now(timezone.utc)
        return scan

    monkeypatch.setattr(scan_orchestrator, "start_scan_job", fake_start_scan_job)
    running = run_approved_scan(db_session, scan.id)
    status = get_scan_status(db_session, running.id)

    assert status["status"] == "completed"
    assert status["return_code"] == 0
    assert db_session.query(Finding).filter(Finding.scan_id == running.id).count() == 1


def test_scan_logs_are_read_from_file_with_truncation(tmp_path):
    log_path = tmp_path / "scan.log"
    log_path.write_text("A" * 100 + "B" * 100, encoding="utf-8")
    scan = Scan(id=1, status="running", log_path=str(log_path), executed_command='["nuclei"]')

    logs = read_scan_logs(scan, max_chars=80)

    assert logs["output"].startswith("A")
    assert "...[truncated]..." in logs["output"]
    assert logs["output"].endswith("B" * 40)


def test_refresh_status_marks_timeout(monkeypatch):
    killed = {}

    def fake_kill(pid):
        killed["pid"] = pid

    monkeypatch.setattr(scan_job_runner, "_kill_process_group", fake_kill)
    scan = Scan(
        id=1,
        status="running",
        pid=999,
        started_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        proposed_plan='{"timeout_seconds": 1}',
    )

    refresh_scan_status(scan)

    assert scan.status == "failed"
    assert scan.timed_out is True
    assert killed["pid"] == 999


def test_refresh_status_handles_sqlite_naive_started_at(monkeypatch):
    monkeypatch.setattr(scan_job_runner, "_pid_alive", lambda pid: True)
    scan = Scan(
        id=1,
        status="running",
        pid=999,
        started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        proposed_plan='{"timeout_seconds": 180}',
    )

    refresh_scan_status(scan)

    assert scan.status == "running"


def test_cancel_running_scan_marks_cancelled(monkeypatch):
    killed = {}

    def fake_kill(pid):
        killed["pid"] = pid

    monkeypatch.setattr(scan_job_runner, "_kill_process_group", fake_kill)
    scan = Scan(id=1, status="running", pid=777)

    cancel_scan(scan)

    assert scan.status == "cancelled"
    assert scan.return_code == -1
    assert killed["pid"] == 777

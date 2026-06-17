import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
    run_approved_scan,
)
from services.tool_registry import ToolRegistryError, build_command


class FakeProvider:
    def __init__(self, response):
        self.response = response

    def generate(self, prompt: str, model: str | None = None) -> str:
        return self.response


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


def test_ai_planner_rejects_malformed_json(db_session):
    with pytest.raises(ScanOrchestrationError):
        create_scan_plan(
            db_session,
            project_id=1,
            target_id=1,
            goal="scan the target",
            provider=FakeProvider("not json"),
        )


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

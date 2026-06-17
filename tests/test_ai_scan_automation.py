import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import services.scan_orchestrator as scan_orchestrator
from core.database import Base
from models.finding import Finding
from models.project import Project
from models.scan import Scan
from models.target import Target
from models.users import Users
from services.command_runner import CommandExecutionError, CommandResult, run_command
from services.scan_orchestrator import (
    ScanOrchestrationError,
    approve_scan,
    create_scan_plan,
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


def test_scan_lifecycle_requires_approval_and_runs(monkeypatch, db_session):
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

    def fake_run_command(command_spec):
        return CommandResult(
            argv=command_spec.argv,
            stdout="https://example.com [info] test finding\n",
            stderr="",
            return_code=0,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(scan_orchestrator, "run_command", fake_run_command)
    completed = run_approved_scan(db_session, scan.id)

    assert completed.status == "completed"
    assert completed.return_code == 0
    assert "nuclei" in completed.executed_command

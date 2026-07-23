"""Tests for durable timestamped scan JSON artifacts."""

from __future__ import annotations

import asyncio
import json
import stat
from datetime import timezone

import pytest

from app.models.schemas import Report
from app.pipeline.context import PipelineContext
from repositories.finding_repository import FindingRepository
from repositories.json_scan_artifact_repository import JsonScanArtifactRepository
from repositories.report_repository import ReportRepository
from repositories.scan_repository import ScanRepository
from services.finding_service import FindingService
from services.scan_service import ScanExecutionError, ScanService


class SuccessfulPipeline:
    """Pipeline fixture that returns one scanner finding."""

    async def run(self, target: str) -> PipelineContext:
        """Return deterministic successful scanner evidence."""

        context = PipelineContext(target=target, status="completed")
        context.add_finding(
            title="Missing Header",
            severity="low",
            description="The header was not observed.",
            evidence={"header_checked": "X-Frame-Options", "header_present": False},
            scanner_id="misconfiguration.headers",
            scanner_name="Header Scanner",
            confidence=0.95,
        )
        return context


class FailingPipeline:
    """Pipeline fixture that fails before report generation."""

    async def run(self, target: str) -> PipelineContext:
        """Return a failed pipeline context."""

        context = PipelineContext(target=target, status="failed")
        context.add_error("Target validation failed")
        return context


class DeterministicAIService:
    """AI service fixture that returns a timestamped deterministic report."""

    async def generate_report(
        self,
        findings: list,
        target: str,
        technologies: list[str],
    ) -> Report:
        """Return a report containing the scanner findings unchanged."""

        return Report(
            executive_summary="One finding was observed.",
            risk_score=23.8,
            findings=findings,
            recommendations=["Set the missing header."],
            ai_summary="Evidence-only report.",
        )


def build_service(tmp_path, pipeline) -> ScanService:
    """Build a scan service using repositories isolated to one test."""

    return ScanService(
        pipeline=pipeline,
        scan_repository=ScanRepository(),
        finding_repository=FindingRepository(),
        report_repository=ReportRepository(),
        artifact_repository=JsonScanArtifactRepository(tmp_path / "reports"),
        finding_service=FindingService(),
        ai_service=DeterministicAIService(),
    )


def test_completed_scan_writes_timestamped_json_artifact(tmp_path) -> None:
    """Completed scans persist all report evidence into one JSON artifact."""

    service = build_service(tmp_path, SuccessfulPipeline())
    report = asyncio.run(service.start_scan("https://example.test"))
    files = list((tmp_path / "reports").glob("*.json"))

    assert len(files) == 1
    artifact_path = files[0]
    assert artifact_path.name.endswith(".json")
    assert "T" in artifact_path.name
    assert stat.S_IMODE(artifact_path.stat().st_mode) == 0o600

    stored = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert stored["schema_version"] == "1.0"
    assert stored["scan"]["status"] == "completed"
    assert stored["report"]["generated_at"] == report.generated_at.isoformat().replace("+00:00", "Z")
    assert stored["scan"]["findings"][0]["evidence"]["header_checked"] == "X-Frame-Options"
    assert report.generated_at.tzinfo == timezone.utc


def test_failed_scan_does_not_write_json_artifact(tmp_path) -> None:
    """Failed scans do not create completed-report artifacts."""

    service = build_service(tmp_path, FailingPipeline())

    with pytest.raises(ScanExecutionError):
        asyncio.run(service.start_scan("https://example.test"))

    assert not (tmp_path / "reports").exists()

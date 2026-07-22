"""Orchestrates scan execution, AI analysis, and persistence."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Protocol

from app.models.schemas import Report, Scan, ScanStatus
from app.pipeline.context import PipelineContext
from repositories.finding_repository import FindingRepository
from repositories.report_repository import ReportRepository
from repositories.scan_repository import ScanRepository
from services.ai_service import AIService
from services.finding_service import FindingService

logger = logging.getLogger(__name__)


class ScanPipeline(Protocol):
    """Protocol that allows any compatible pipeline to be injected."""

    async def run(self, target: str) -> PipelineContext:
        """Execute a scan pipeline for a target."""


class ScanExecutionError(RuntimeError):
    """Raised when the pipeline cannot complete a scan."""


class ScanService:
    """Coordinates the application workflow without owning persistence details."""

    def __init__(
        self,
        pipeline: ScanPipeline,
        scan_repository: ScanRepository,
        finding_repository: FindingRepository,
        report_repository: ReportRepository,
        finding_service: FindingService,
        ai_service: AIService,
    ) -> None:
        self._pipeline = pipeline
        self._scan_repository = scan_repository
        self._finding_repository = finding_repository
        self._report_repository = report_repository
        self._finding_service = finding_service
        self._ai_service = ai_service

    async def start_scan(self, target: str) -> Report:
        """Run a scan and return its persisted, completed report."""

        scan = Scan(target=target, status=ScanStatus.RUNNING)
        await self._scan_repository.create(scan)
        try:
            context = await self._pipeline.run(str(scan.target))
            if context.status == "failed" or context.errors:
                raise ScanExecutionError("; ".join(context.errors) or "Pipeline failed")

            findings = await self._finding_service.prepare_findings(context.findings)
            enriched_findings, ai_summary = await self._ai_service.analyze_findings(findings)
            for finding in enriched_findings:
                await self._finding_repository.create(finding)

            report = await self._ai_service.generate_report(
                findings=enriched_findings,
                target=str(scan.target),
                technologies=list(dict.fromkeys(context.technologies)),
                ai_analysis_summary=ai_summary,
            )
            await self._report_repository.create(scan.id, report)
            completed_scan = scan.model_copy(
                update={
                    "status": ScanStatus.COMPLETED,
                    "completed_at": datetime.now(timezone.utc),
                    "findings": enriched_findings,
                    "technologies": list(dict.fromkeys(context.technologies)),
                    "metadata": {**context.metadata, "ai_summary": ai_summary},
                }
            )
            await self._scan_repository.update(scan.id, completed_scan)
            logger.info("Scan %s completed with %s findings", scan.id, len(enriched_findings))
            return report
        except Exception:
            failed_scan = scan.model_copy(
                update={"status": ScanStatus.FAILED, "completed_at": datetime.now(timezone.utc)}
            )
            await self._scan_repository.update(scan.id, failed_scan)
            logger.exception("Scan %s failed", scan.id)
            raise

    async def get_scan(self, scan_id: str) -> Scan | None:
        """Retrieve a stored scan."""

        return await self._scan_repository.find_by_id(scan_id)

    async def get_report(self, scan_id: str) -> Report | None:
        """Retrieve the report belonging to a scan."""

        return await self._report_repository.find_by_id(scan_id)

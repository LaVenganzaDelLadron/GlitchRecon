"""FastAPI dependency providers for application services."""

from __future__ import annotations

from functools import lru_cache

from app.config import get_llm_provider
from app.pipeline.pipeline import Pipeline
from app.pipeline.stages import ScannerExecutionStage, ValidationStage
from repositories.finding_repository import FindingRepository
from repositories.json_scan_artifact_repository import JsonScanArtifactRepository
from repositories.report_repository import ReportRepository
from repositories.scan_repository import ScanRepository
from scanners.manager import ScannerManager
from scanners.registry import ScannerRegistry
from services.ai_service import AIService
from services.finding_service import FindingService
from services.scan_service import ScanService


@lru_cache
def get_scan_repository() -> ScanRepository:
    """Return the process-scoped scan repository adapter."""

    return ScanRepository()


@lru_cache
def get_finding_repository() -> FindingRepository:
    """Return the process-scoped finding repository adapter."""

    return FindingRepository()


@lru_cache
def get_report_repository() -> ReportRepository:
    """Return the process-scoped report repository adapter."""

    return ReportRepository()


@lru_cache
def get_artifact_repository() -> JsonScanArtifactRepository:
    """Return the local JSON artifact persistence adapter."""

    return JsonScanArtifactRepository()


@lru_cache
def get_scanner_registry() -> ScannerRegistry:
    """Discover scanner plugins once for the process lifetime."""

    registry = ScannerRegistry()
    registry.discover()
    return registry


@lru_cache
def get_scanner_manager() -> ScannerManager:
    """Return the scanner execution coordinator."""

    return ScannerManager(get_scanner_registry())


def get_pipeline() -> Pipeline:
    """Build the default scanner pipeline for one request."""

    pipeline = Pipeline()
    pipeline.add_stage(ValidationStage())
    pipeline.add_stage(ScannerExecutionStage(get_scanner_manager()))
    return pipeline


def get_scan_service() -> ScanService:
    """Build a scan service with explicit infrastructure dependencies."""

    return ScanService(
        pipeline=get_pipeline(),
        scan_repository=get_scan_repository(),
        finding_repository=get_finding_repository(),
        report_repository=get_report_repository(),
        artifact_repository=get_artifact_repository(),
        finding_service=FindingService(),
        ai_service=AIService(get_llm_provider()),
    )

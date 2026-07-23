"""Concurrent execution orchestration for scanner plugins."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Iterable

import httpx

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.exceptions import ScannerExecutionError, ScannerTimeout
from scanners.registry import ScannerRegistry
from scanners.utils import DEFAULT_TIMEOUT_SECONDS, USER_AGENT

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ScannerFailure:
    """Structured information describing one scanner execution failure."""

    scanner_id: str
    error_type: str
    message: str


@dataclass(slots=True)
class ScannerRunResult:
    """Aggregated scanner findings and non-fatal execution failures."""

    findings: list[Finding]
    failures: list[ScannerFailure]


class ScannerManager:
    """Selects and runs scanner plugins concurrently without stopping on failure."""

    def __init__(self, registry: ScannerRegistry, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        self._registry = registry
        self._timeout_seconds = timeout_seconds

    async def execute(
        self,
        context: PipelineContext,
        *,
        categories: set[str] | None = None,
        tags: set[str] | None = None,
        severities: set[Severity] | None = None,
    ) -> ScannerRunResult:
        """Run selected enabled scanners and return all evidence and failures."""

        scanners = self._select(categories, tags, severities)
        timeout = httpx.Timeout(self._timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": USER_AGENT}) as client:
            context.http_client = client
            try:
                outcomes = await asyncio.gather(*(self._execute_one(scanner, context) for scanner in scanners))
            finally:
                context.http_client = None
        findings: list[Finding] = []
        failures: list[ScannerFailure] = []
        for scanner_findings, failure in outcomes:
            findings.extend(scanner_findings)
            if failure:
                failures.append(failure)
        if failures:
            context.metadata["scanner_failures"] = [
                {"scanner_id": failure.scanner_id, "error_type": failure.error_type, "message": failure.message}
                for failure in failures
            ]
        context.findings.extend(findings)
        return ScannerRunResult(findings=findings, failures=failures)

    def _select(self, categories: set[str] | None, tags: set[str] | None, severities: set[Severity] | None) -> list[Scanner]:
        """Filter enabled scanner plugins by optional AND-combined criteria."""

        selected = self._registry.get_enabled()
        if categories:
            selected = [scanner for scanner in selected if scanner.category in categories]
        if tags:
            selected = [scanner for scanner in selected if scanner.tags.intersection(tags)]
        if severities:
            selected = [scanner for scanner in selected if scanner.severity in severities]
        return selected

    async def _execute_one(self, scanner: Scanner, context: PipelineContext) -> tuple[list[Finding], ScannerFailure | None]:
        """Execute one scanner with a deadline and convert exceptions to failures."""

        try:
            findings = await asyncio.wait_for(scanner.scan(context), timeout=self._timeout_seconds)
            if not isinstance(findings, list) or not all(isinstance(finding, Finding) for finding in findings):
                raise ScannerExecutionError("scan() must return list[Finding]")
            return findings, None
        except TimeoutError:
            failure = ScannerFailure(scanner.id, ScannerTimeout.__name__, f"Timed out after {self._timeout_seconds:.1f}s")
        except Exception as exc:
            logger.exception(
                "Scanner execution failed",
                extra={"scanner_id": scanner.id, "scanner_category": scanner.category},
            )
            failure = ScannerFailure(scanner.id, type(exc).__name__, str(exc))
        return [], failure

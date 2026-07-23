"""Pipeline stage that runs discovered scanner plugins."""

from __future__ import annotations

from app.pipeline.base import PipelineStage
from app.pipeline.context import PipelineContext
from scanners.manager import ScannerManager, ScannerRunResult


class ScannerExecutionStage(PipelineStage):
    """Execute all selected scanner plugins through the scanner manager."""

    def __init__(self, manager: ScannerManager, categories: set[str] | None = None) -> None:
        self._manager = manager
        self._categories = categories

    async def run(self, context: PipelineContext) -> None:
        """Run scanner plugins and retain their non-fatal failures as metadata."""

        result: ScannerRunResult = await self._manager.execute(context, categories=self._categories)
        context.metadata["scanners_executed"] = len(result.findings)

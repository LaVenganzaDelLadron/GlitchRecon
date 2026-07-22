"""Pipeline stage for technology fingerprint collection."""

from __future__ import annotations

from app.pipeline.base import PipelineStage
from app.pipeline.context import PipelineContext
from scanners.fingerprinting.fingerprinting import FingerprintScanner


class FingerprintingStage(PipelineStage):
    """Collect observed technologies without asking the AI to infer them."""

    def __init__(self, scanner: FingerprintScanner | None = None) -> None:
        self._scanner = scanner or FingerprintScanner()

    async def run(self, context: PipelineContext) -> None:
        """Run the fingerprint scanner."""

        await self._scanner.scan(context)

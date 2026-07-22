"""Pipeline stage that invokes injected vulnerability scanners."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from app.pipeline.base import PipelineStage
from app.pipeline.context import PipelineContext
from scanners.base import Scanner

logger = logging.getLogger(__name__)


class ReconStage(PipelineStage):
    """Execute scanner implementations against the validated pipeline context."""

    def __init__(self, scanners: Sequence[Scanner]) -> None:
        self._scanners = tuple(scanners)

    async def run(self, context: PipelineContext) -> None:
        """Run each scanner sequentially so evidence remains deterministic."""

        for scanner in self._scanners:
            logger.info("Running scanner %s", scanner.name)
            try:
                await scanner.scan(context)
            except Exception as exc:
                logger.exception("Scanner %s failed", scanner.name)
                context.add_error(f"{scanner.name} failed: {exc}")
                return

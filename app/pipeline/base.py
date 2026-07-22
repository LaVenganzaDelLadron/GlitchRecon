#app/pipeline/base.py
from abc import ABC, abstractmethod
from app.pipeline.context import PipelineContext


class PipelineStage(ABC):
    """Base class for every pipeline stage."""

    @abstractmethod
    async def run(self, context: PipelineContext) -> None:
        """Execute the stage."""
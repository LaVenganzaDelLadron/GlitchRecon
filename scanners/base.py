#scanners/base.py
from abc import ABC, abstractmethod

from app.pipeline.context import PipelineContext


class Scanner(ABC):
    """Base class for all scanners."""

    name: str = "Scanner"

    @abstractmethod
    async def scan(self, context: PipelineContext) -> None:
        """Run the scanner."""
#app/core/base.py

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Common interface for supported text-generation providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        """Generate text for *prompt* with an optional output-token limit."""

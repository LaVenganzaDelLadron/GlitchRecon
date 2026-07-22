from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Common interface for supported text-generation providers."""

    @abstractmethod
    def generate(self, prompt: str, model: str | None = None) -> str:
        """Generate text for *prompt*."""
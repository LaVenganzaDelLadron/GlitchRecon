"""Configuration and provider selection."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from glitchrecon.providers import GroqProvider, LLMProvider, OllamaProvider

load_dotenv()


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    """Create the provider selected by ``LLM_PROVIDER`` (Groq by default)."""

    selected_provider = (provider_name or os.getenv("LLM_PROVIDER", "groq")).strip().lower()

    if selected_provider == "groq":
        return GroqProvider()
    if selected_provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {selected_provider!r}. Use 'groq' or 'ollama'."
    )

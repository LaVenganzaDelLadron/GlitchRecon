"""LLM provider implementations used by the command-line client."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Common interface for supported text-generation providers."""

    @abstractmethod
    def generate(self, prompt: str, model: str | None = None) -> str:
        """Generate text for *prompt*."""


class GroqProvider(LLMProvider):
    """LLM provider backed by Groq's OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        api_key = api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY must be set to use the Groq provider")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "Install the OpenAI Python package to use the Groq provider: pip install openai"
            ) from exc

        configured_base_url = base_url or os.getenv("GROQ_BASE_URL")
        timeout = timeout_seconds or float(os.getenv("GROQ_TIMEOUT", "60"))
        self.client = OpenAI(
            api_key=api_key,
            base_url=configured_base_url or None,
            timeout=timeout,
        )
        self.default_model = default_model or os.getenv(
            "GROQ_MODEL", "openai/gpt-oss-20b"
        )

    def generate(self, prompt: str, model: str | None = None) -> str:
        response = self.client.responses.create(
            input=prompt,
            model=model or self.default_model,
        )
        return response.output_text.strip()


class OllamaProvider(LLMProvider):
    """LLM provider backed by a local or remote Ollama server."""

    def __init__(
        self,
        host: str | None = None,
        default_model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        try:
            from ollama import Client
        except ImportError as exc:
            raise RuntimeError("Install the ollama package to use OllamaProvider") from exc

        timeout = timeout_seconds or float(os.getenv("OLLAMA_TIMEOUT", "60"))
        configured_host = host or os.getenv("OLLAMA_HOST")
        self.client = Client(host=configured_host or None, timeout=timeout)
        self.default_model = default_model or os.getenv("OLLAMA_MODEL")

    def generate(self, prompt: str, model: str | None = None) -> str:
        selected_model = model or self.default_model
        if not selected_model:
            raise ValueError("OLLAMA_MODEL must be set to use the Ollama provider")

        response = self.client.generate(model=selected_model, prompt=prompt)

        if isinstance(response, str):
            return response.strip()
        if isinstance(response, dict):
            if isinstance(response.get("response"), str):
                return response["response"].strip()
            message = response.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"].strip()

        value = getattr(response, "response", None) or getattr(response, "content", None)
        if isinstance(value, str):
            return value.strip()

        message = getattr(response, "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content.strip()

        return str(response).strip()

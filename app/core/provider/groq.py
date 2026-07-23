#app/core/provider/groq.py
import os
import asyncio
from app.core.base import LLMProvider


class GroqProvider(LLMProvider):
    """LLM provider backed by Groq's OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str | None = None,
        timeout_seconds: float | None = None,
        reasoning_effort: str | None = None,
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
        self.reasoning_effort = reasoning_effort or os.getenv(
            "GROQ_REASONING_EFFORT", "low"
        )

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        """Generate a response without blocking the application's event loop."""

        selected_model = model or self.default_model
        request: dict[str, object] = {"input": prompt, "model": selected_model}
        if max_output_tokens is not None:
            request["max_output_tokens"] = max_output_tokens
        if selected_model.startswith("openai/gpt-oss-"):
            request["reasoning"] = {"effort": self.reasoning_effort}
        response = await asyncio.to_thread(
            self.client.responses.create,
            **request,
        )
        return response.output_text.strip()

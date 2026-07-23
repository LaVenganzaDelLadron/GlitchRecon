import os
import asyncio
from app.core.base import LLMProvider


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

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        """Generate a response without blocking the application's event loop."""

        selected_model = model or self.default_model
        if not selected_model:
            raise ValueError("OLLAMA_MODEL must be set to use the Ollama provider")

        request: dict[str, object] = {"model": selected_model, "prompt": prompt}
        if max_output_tokens is not None:
            request["options"] = {"num_predict": max_output_tokens}
        response = await asyncio.to_thread(
            self.client.generate, **request
        )

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

import os

from ai.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        host: str = "http://localhost:11434",
        default_model: str = "deepseek-r1:8b",
        timeout_seconds: float | None = None,
    ):
        try:
            from ollama import Client
        except ImportError as exc:
            raise RuntimeError("Install the ollama package to use OllamaProvider") from exc

        timeout = timeout_seconds or float(os.getenv("SCAN_PLAN_TIMEOUT_SECONDS", "20"))
        self.client = Client(host=host, timeout=timeout)
        self.default_model = default_model

    def generate(self, prompt: str, model: str | None = None) -> str:
        response = self.client.chat(
            model=model or self.default_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]

    def generate_json(self, prompt: str, model: str | None = None) -> str:
        response = self.client.chat(
            model=model or self.default_model,
            messages=[{"role": "user", "content": prompt}],
            format="json",
            think=False,
            options={
                "temperature": 0,
                "num_predict": 160,
                "top_p": 0.1,
            },
        )
        return response["message"]["content"]

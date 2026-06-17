from ai.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, host: str = "http://localhost:11434", default_model: str = "deepseek-r1:8b"):
        try:
            from ollama import Client
        except ImportError as exc:
            raise RuntimeError("Install the ollama package to use OllamaProvider") from exc

        self.client = Client(host=host)
        self.default_model = default_model

    def generate(self, prompt: str, model: str | None = None) -> str:
        response = self.client.chat(
            model=model or self.default_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]

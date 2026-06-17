import os

from ai.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, default_model: str = "gpt-4.1-mini"):
        self.default_model = default_model

    def generate(self, prompt: str, model: str | None = None) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the openai package to use OpenAIProvider") from exc

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model=model or self.default_model,
            input=prompt,
        )
        return response.output_text


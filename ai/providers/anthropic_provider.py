import os

from ai.providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, default_model: str = "claude-3-5-sonnet-latest"):
        self.default_model = default_model

    def generate(self, prompt: str, model: str | None = None) -> str:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("Install the anthropic package to use AnthropicProvider") from exc

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model=model or self.default_model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if getattr(block, "type", None) == "text")


from ai.providers.ollama_provider import OllamaProvider

client = OllamaProvider()


def generate(
    prompt: str,
    model: str = "qwen3:8b"
):
    return client.generate(prompt, model=model)

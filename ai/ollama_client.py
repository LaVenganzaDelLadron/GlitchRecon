from ai.providers.ollama_provider import OllamaProvider

client = OllamaProvider()


def generate(
    prompt: str,
    model: str = "deepseek-r1:8b"
):
    return client.generate(prompt, model=model)

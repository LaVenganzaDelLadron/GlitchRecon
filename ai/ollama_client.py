from ai.providers.ollama_provider import OllamaProvider

client = OllamaProvider()


def generate(
    prompt: str,
    model: str = "gemma2:2b"
):
    return client.generate(prompt, model=model)

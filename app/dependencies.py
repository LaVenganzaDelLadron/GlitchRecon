import os
from dotenv import load_dotenv

from app.ai_pipeline.providers.groq import GroqProvider
from app.ai_pipeline.providers.ollama import OllamaProvider
from app.ai_pipeline.providers.base import LLMProvider

load_dotenv()


def get_llm_provider() -> LLMProvider:
    return GroqProvider()

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider_name}. "
        "Use 'groq' or 'ollama'."
    )
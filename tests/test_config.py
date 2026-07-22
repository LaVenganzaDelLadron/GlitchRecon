import pytest

from app import config
from app.providers import GroqProvider


def test_selects_groq_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeGroq:
        pass

    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setattr(config, "GroqProvider", FakeGroq)

    assert isinstance(config.get_llm_provider(), FakeGroq)


def test_selects_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeOllama:
        pass

    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setattr(config, "OllamaProvider", FakeOllama)

    assert isinstance(config.get_llm_provider(), FakeOllama)


def test_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="Use 'groq' or 'ollama'"):
        config.get_llm_provider("unknown")


def test_groq_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        GroqProvider()

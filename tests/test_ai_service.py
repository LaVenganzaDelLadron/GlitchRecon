"""Regression tests for token-bounded AI reporting."""

from __future__ import annotations

import asyncio

from app.models.schemas import Finding, Severity
from services.ai_service import AIService


class RecordingProvider:
    """Test provider that records bounded generation requests."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        """Record the request and return the configured response."""

        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "max_output_tokens": max_output_tokens,
            }
        )
        return self.response


class FailingProvider:
    """Test provider that simulates a provider-side request failure."""

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        """Raise a representative provider error."""

        raise RuntimeError("request too large")


def make_finding(index: int, evidence: dict[str, object] | None = None) -> Finding:
    """Create a representative scanner finding for report tests."""

    return Finding(
        scanner_id="misconfiguration.headers",
        scanner_name="Header Scanner",
        title=f"Finding {index}",
        description="A" * 2_000,
        severity=Severity.HIGH if index == 0 else Severity.LOW,
        confidence=0.95,
        evidence=evidence or {"response_url": "https://example.test/", "body": "B" * 2_000},
    )


def test_large_prompt_is_compacted_and_provider_called_once() -> None:
    """Large scans fit the configured prompt cap and invoke one model request."""

    provider = RecordingProvider(
        '{"executive_summary":"Summary","risk_score":70,"recommendations":["Fix it"],"ai_summary":"AI summary"}'
    )
    service = AIService(provider, max_prompt_chars=12_000, max_output_tokens=800)
    findings = [make_finding(index) for index in range(30)]

    report = asyncio.run(service.generate_report(findings, "https://example.test", []))

    assert len(provider.calls) == 1
    assert len(str(provider.calls[0]["prompt"])) <= 12_000
    assert provider.calls[0]["max_output_tokens"] == 800
    assert report.findings == findings


def test_secret_like_evidence_is_redacted_before_prompt() -> None:
    """Prompt compaction never forwards token-like values or secret-key values."""

    provider = RecordingProvider(
        '{"executive_summary":"Summary","risk_score":0,"recommendations":[],"ai_summary":"AI summary"}'
    )
    service = AIService(provider)
    evidence = {"api_key": "AKIA1234567890123456", "safe": "visible"}

    asyncio.run(service.generate_report([make_finding(1, evidence)], "https://example.test", []))

    prompt = str(provider.calls[0]["prompt"])
    assert "AKIA1234567890123456" not in prompt
    assert "[REDACTED]" in prompt
    assert "visible" in prompt


def test_provider_error_returns_all_findings_in_fallback_report() -> None:
    """Provider failures produce a successful deterministic evidence-only report."""

    findings = [make_finding(1), make_finding(2)]
    service = AIService(FailingProvider())

    report = asyncio.run(service.generate_report(findings, "https://example.test", []))

    assert report.findings == findings
    assert "AI analysis unavailable" in report.ai_summary


def test_malformed_json_returns_fallback_report() -> None:
    """Malformed provider output cannot fail a completed scanner report."""

    findings = [make_finding(1)]
    service = AIService(RecordingProvider("not-json"))

    report = asyncio.run(service.generate_report(findings, "https://example.test", []))

    assert report.findings == findings
    assert "AI analysis unavailable" in report.ai_summary

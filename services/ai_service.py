"""Token-bounded AI reporting grounded exclusively in scanner evidence."""

from __future__ import annotations

import json
import logging
import os
import re
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.core.base import LLMProvider
from app.models.schemas import Finding, Report, Severity

logger = logging.getLogger(__name__)

_SENSITIVE_KEY_PATTERN = re.compile(
    r"(?:api[_-]?key|authorization|credential|cookie|password|secret|session|token)",
    re.IGNORECASE,
)
_SENSITIVE_VALUE_PATTERN = re.compile(
    r"(?:\bAKIA[A-Z0-9]{12,}\b|\beyJ[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{8,}\b)"
)


class AIReportResponse(BaseModel):
    """Structured output accepted from the compact report-generation prompt."""

    executive_summary: str
    risk_score: float = Field(ge=0.0, le=100.0)
    recommendations: list[str] = Field(default_factory=list)
    ai_summary: str


class AIService:
    """Produces one bounded AI report request and never discovers vulnerabilities."""

    _SEVERITY_WEIGHT = {
        Severity.CRITICAL: 5,
        Severity.HIGH: 4,
        Severity.MEDIUM: 3,
        Severity.LOW: 2,
        Severity.INFO: 1,
    }

    def __init__(
        self,
        provider: LLMProvider,
        model: str | None = None,
        max_prompt_chars: int | None = None,
        max_output_tokens: int | None = None,
    ) -> None:
        self._provider = provider
        self._model = model
        self._max_prompt_chars = max_prompt_chars or self._read_positive_int(
            "AI_MAX_PROMPT_CHARS", 12_000
        )
        self._max_output_tokens = max_output_tokens or self._read_positive_int(
            "AI_MAX_OUTPUT_TOKENS", 800
        )

    async def generate_report(
        self,
        findings: list[Finding],
        target: str,
        technologies: list[str],
    ) -> Report:
        """Generate one compact report, falling back safely if the provider fails."""

        if not findings:
            return self._fallback_report(findings, "No scanner findings were identified.")

        prompt = self._build_report_prompt(target, technologies, findings)
        try:
            response = await self._provider.generate(
                prompt,
                model=self._model,
                max_output_tokens=self._max_output_tokens,
            )
            parsed = AIReportResponse.model_validate(self._parse_json(response))
            return Report(
                executive_summary=parsed.executive_summary,
                risk_score=parsed.risk_score,
                findings=findings,
                recommendations=parsed.recommendations,
                ai_summary=parsed.ai_summary,
            )
        except Exception as exc:
            logger.warning(
                "AI report generation failed; returning deterministic report",
                exc_info=True,
                extra={"error_type": type(exc).__name__, "finding_count": len(findings)},
            )
            return self._fallback_report(
                findings,
                "AI analysis unavailable; this report is derived solely from scanner evidence.",
            )

    def _build_report_prompt(
        self,
        target: str,
        technologies: list[str],
        findings: list[Finding],
    ) -> str:
        """Build a prompt within the configured character budget.

        Character budgeting is deliberately conservative for the configured TPM
        tier. Findings are ranked before truncation; the full evidence remains
        in the persisted report regardless of what is sent to the LLM.
        """

        ranked = sorted(
            findings,
            key=lambda item: (self._SEVERITY_WEIGHT[item.severity], item.confidence),
            reverse=True,
        )
        compact: list[dict[str, Any]] = []
        for finding in ranked:
            candidate = self._compact_finding(finding)
            prospective = [*compact, candidate]
            prompt = self._render_prompt(target, technologies, prospective, len(findings))
            if len(prompt) > self._max_prompt_chars:
                break
            compact.append(candidate)

        prompt = self._render_prompt(target, technologies, compact, len(findings))
        if len(prompt) > self._max_prompt_chars:
            raise ValueError("Configured AI prompt limit is too small for report instructions")
        return prompt

    def _render_prompt(
        self,
        target: str,
        technologies: list[str],
        findings: list[dict[str, Any]],
        total_findings: int,
    ) -> str:
        """Render the fixed instructions and compact evidence payload."""

        payload = {
            "target": self._truncate_text(target, 500),
            "technologies": [self._truncate_text(value, 80) for value in technologies[:25]],
            "total_finding_count": total_findings,
            "included_finding_count": len(findings),
            "evidence_truncated": len(findings) < total_findings,
            "findings": findings,
        }
        return (
            "You are a cybersecurity reporting assistant. Use only the scanner evidence below. "
            "Do not crawl, test, infer unobserved vulnerabilities, or change finding existence. "
            "The evidence may be compacted; report only what it supports. Return JSON only with "
            "executive_summary, risk_score (0-100), recommendations, and ai_summary. Keep all "
            "text concise.\nEvidence:\n"
            f"{json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}"
        )

    def _compact_finding(self, finding: Finding) -> dict[str, Any]:
        """Create a redacted, bounded LLM representation of one finding."""

        return {
            "id": finding.id,
            "scanner_id": finding.scanner_id,
            "title": self._truncate_text(finding.title, 180),
            "severity": finding.severity.value,
            "confidence": finding.confidence,
            "description": self._sanitize_value(finding.description, depth=0),
            "evidence": self._sanitize_value(finding.evidence, depth=0),
        }

    def _sanitize_value(self, value: Any, depth: int) -> Any:
        """Redact secret-like values and bound nested evidence before prompt use."""

        if depth >= 3:
            return "[TRUNCATED]"
        if isinstance(value, str):
            redacted = _SENSITIVE_VALUE_PATTERN.sub("[REDACTED]", value)
            return self._truncate_text(redacted, 240)
        if isinstance(value, Mapping):
            sanitized: dict[str, Any] = {}
            for index, (key, nested_value) in enumerate(value.items()):
                if index >= 8:
                    sanitized["additional_fields"] = "[TRUNCATED]"
                    break
                key_text = self._truncate_text(str(key), 80)
                sanitized[key_text] = (
                    "[REDACTED]"
                    if _SENSITIVE_KEY_PATTERN.search(key_text)
                    else self._sanitize_value(nested_value, depth + 1)
                )
            return sanitized
        if isinstance(value, (list, tuple, set)):
            values = list(value)
            sanitized_values = [self._sanitize_value(item, depth + 1) for item in values[:10]]
            if len(values) > 10:
                sanitized_values.append("[TRUNCATED]")
            return sanitized_values
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        return self._truncate_text(str(value), 240)

    @staticmethod
    def _truncate_text(value: str, limit: int) -> str:
        """Return a visibly truncated string no longer than ``limit`` characters."""

        return value if len(value) <= limit else f"{value[: limit - 1]}…"

    @staticmethod
    def _read_positive_int(name: str, default: int) -> int:
        """Read a positive integer environment setting with a safe default."""

        try:
            value = int(os.getenv(name, str(default)))
        except ValueError:
            return default
        return value if value > 0 else default

    @staticmethod
    def _parse_json(response: str) -> dict[str, Any]:
        """Parse a JSON object, accepting a fenced JSON response from an LLM."""

        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else ""
            if text.endswith("```"):
                text = text[:-3]
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end < start:
            raise ValueError("No JSON object found in LLM response")
        parsed = json.loads(text[start : end + 1])
        if not isinstance(parsed, dict):
            raise ValueError("LLM response must be a JSON object")
        return parsed

    def _fallback_report(self, findings: list[Finding], ai_summary: str) -> Report:
        """Produce a deterministic evidence-only report when AI is unavailable."""

        weights = {
            Severity.CRITICAL: 100.0,
            Severity.HIGH: 75.0,
            Severity.MEDIUM: 50.0,
            Severity.LOW: 25.0,
            Severity.INFO: 5.0,
        }
        risk_score = max((weights[item.severity] * item.confidence for item in findings), default=0.0)
        recommendations = list(
            dict.fromkeys(
                item.remediation
                for item in findings
                if item.remediation and item.remediation.strip()
            )
        )
        return Report(
            executive_summary=f"The scan produced {len(findings)} normalized finding(s).",
            risk_score=round(risk_score, 1),
            findings=findings,
            recommendations=recommendations,
            ai_summary=ai_summary,
        )

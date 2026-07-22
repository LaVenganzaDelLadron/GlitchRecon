"""AI analysis service constrained to evidence already collected by scanners."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.core.base import LLMProvider
from app.models.schemas import Finding, Report, Severity

logger = logging.getLogger(__name__)


class AIFindingAnalysis(BaseModel):
    """Allowed AI enrichment for an existing scanner finding."""

    finding_id: str
    description: str | None = None
    remediation: str | None = None
    priority: Severity | None = None


class AIAnalysisResponse(BaseModel):
    """Structured response expected from the finding-analysis prompt."""

    ai_summary: str = "AI analysis was unavailable."
    findings: list[AIFindingAnalysis] = Field(default_factory=list)


class AIReportResponse(BaseModel):
    """Structured response expected from the report-generation prompt."""

    executive_summary: str
    risk_score: float = Field(ge=0.0, le=100.0)
    recommendations: list[str] = Field(default_factory=list)
    ai_summary: str


class AIService:
    """Uses an LLM only to reason about scanner evidence; never to scan targets."""

    def __init__(self, provider: LLMProvider, model: str | None = None) -> None:
        self._provider = provider
        self._model = model

    async def analyze_findings(self, findings: list[Finding]) -> tuple[list[Finding], str]:
        """Enrich findings with AI explanation and remediation suggestions."""

        if not findings:
            return findings, "No scanner findings were identified."
        payload = [finding.model_dump(mode="json") for finding in findings]
        response = await self._provider.generate(
            self._build_analysis_prompt(payload), model=self._model
        )
        try:
            parsed = AIAnalysisResponse.model_validate(self._parse_json(response))
        except (ValueError, ValidationError) as exc:
            logger.warning("LLM finding analysis was not valid JSON: %s", exc)
            return findings, "AI analysis could not be parsed; scanner evidence is unchanged."

        analyses = {analysis.finding_id: analysis for analysis in parsed.findings}
        enriched: list[Finding] = []
        for finding in findings:
            analysis = analyses.get(finding.id)
            if analysis is None:
                enriched.append(finding)
                continue
            enriched.append(
                finding.model_copy(
                    update={
                        "description": analysis.description or finding.description,
                        "remediation": analysis.remediation or finding.remediation,
                        "severity": analysis.priority or finding.severity,
                    }
                )
            )
        return enriched, parsed.ai_summary

    async def generate_report(
        self,
        findings: list[Finding],
        target: str,
        technologies: list[str],
        ai_analysis_summary: str,
    ) -> Report:
        """Generate a structured report grounded exclusively in supplied findings."""

        payload = [finding.model_dump(mode="json") for finding in findings]
        response = await self._provider.generate(
            self._build_report_prompt(target, technologies, payload), model=self._model
        )
        try:
            parsed = AIReportResponse.model_validate(self._parse_json(response))
            return Report(
                executive_summary=parsed.executive_summary,
                risk_score=parsed.risk_score,
                findings=findings,
                recommendations=parsed.recommendations,
                ai_summary=parsed.ai_summary,
            )
        except (ValueError, ValidationError) as exc:
            logger.warning("LLM report response was not valid JSON: %s", exc)
            return self._fallback_report(findings, ai_analysis_summary)

    def _build_analysis_prompt(self, findings: list[dict[str, Any]]) -> str:
        """Build a strict JSON prompt for evidence interpretation."""

        return (
            "You are a cybersecurity reporting assistant. Analyze only the supplied "
            "scanner evidence. Do not crawl targets, propose tests, or invent findings. "
            "Return JSON only with keys ai_summary and findings. Each findings item must "
            "contain finding_id and may contain description, remediation, priority "
            "(critical, high, medium, low, or info).\nScanner findings:\n"
            f"{json.dumps(findings, ensure_ascii=False)}"
        )

    def _build_report_prompt(
        self,
        target: str,
        technologies: list[str],
        findings: list[dict[str, Any]],
    ) -> str:
        """Build a strict JSON prompt for a risk report."""

        return (
            "You are a cybersecurity reporting assistant. Use only the supplied "
            "scanner findings. Do not assert unobserved vulnerabilities. Return JSON only "
            "with executive_summary, risk_score (0-100), recommendations, and ai_summary.\n"
            f"Target: {target}\nTechnologies: {json.dumps(technologies)}\n"
            f"Findings: {json.dumps(findings, ensure_ascii=False)}"
        )

    def _parse_json(self, response: str) -> dict[str, Any]:
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
        """Produce a deterministic evidence-only report when AI output is invalid."""

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

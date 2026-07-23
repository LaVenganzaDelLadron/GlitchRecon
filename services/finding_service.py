"""Business logic for preparing scanner findings."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from app.models.schemas import Finding, Severity


class FindingService:
    """Normalizes, deduplicates, and scores scanner-produced evidence."""

    _SEVERITY_ALIASES: dict[str, Severity] = {
        "critical": Severity.CRITICAL,
        "crit": Severity.CRITICAL,
        "high": Severity.HIGH,
        "medium": Severity.MEDIUM,
        "moderate": Severity.MEDIUM,
        "low": Severity.LOW,
        "info": Severity.INFO,
        "informational": Severity.INFO,
        "none": Severity.INFO,
    }
    _BASE_CONFIDENCE: dict[Severity, float] = {
        Severity.CRITICAL: 0.85,
        Severity.HIGH: 0.80,
        Severity.MEDIUM: 0.70,
        Severity.LOW: 0.60,
        Severity.INFO: 0.50,
    }

    async def prepare_findings(
        self, raw_findings: list[Finding | Mapping[str, Any]]
    ) -> list[Finding]:
        """Convert scanner output into storage-ready, unique findings."""

        normalized = [await self.normalize_finding(finding) for finding in raw_findings]
        return await self.merge_duplicates(normalized)

    async def normalize_finding(self, raw_finding: Finding | Mapping[str, Any]) -> Finding:
        """Validate a finding and normalize its severity and confidence."""

        data = (
            raw_finding.model_dump(mode="python")
            if isinstance(raw_finding, Finding)
            else dict(raw_finding)
        )
        severity = await self.normalize_severity(data.get("severity"))
        evidence = data.get("evidence")
        if not isinstance(evidence, dict):
            evidence = {"raw_evidence": evidence}

        supplied_confidence = data.get("confidence")
        confidence = await self.calculate_confidence(
            severity=severity,
            evidence=evidence,
            supplied_confidence=supplied_confidence,
        )
        finding_data: dict[str, Any] = {
            "scanner_id": str(data.get("scanner_id") or data.get("scanner_name") or "unknown-scanner").strip(),
            "title": str(data.get("title") or "Untitled finding").strip(),
            "severity": severity,
            "confidence": confidence,
            "description": str(data.get("description") or "No description provided.").strip(),
            "evidence": evidence,
            "remediation": data.get("remediation"),
            "scanner_name": str(data.get("scanner_name") or "unknown-scanner").strip(),
            "references": [str(reference) for reference in data.get("references", [])],
        }
        if data.get("id"):
            finding_data["id"] = data["id"]
        if data.get("timestamp"):
            finding_data["timestamp"] = data["timestamp"]
        return Finding(**finding_data)

    async def normalize_severity(self, value: Any) -> Severity:
        """Map scanner-specific labels to the supported severity vocabulary."""

        if isinstance(value, Severity):
            return value
        normalized = str(value or "info").strip().lower()
        return self._SEVERITY_ALIASES.get(normalized, Severity.INFO)

    async def calculate_confidence(
        self,
        severity: Severity,
        evidence: Mapping[str, Any],
        supplied_confidence: Any = None,
    ) -> float:
        """Calculate an evidence-based confidence score in the range 0..1."""

        if isinstance(supplied_confidence, (int, float)) and not isinstance(
            supplied_confidence, bool
        ):
            return max(0.0, min(1.0, float(supplied_confidence)))

        base = self._BASE_CONFIDENCE[severity]
        populated_values = sum(
            1 for value in evidence.values() if value not in (None, "", [], {})
        )
        return round(min(0.95, base + min(populated_values, 3) * 0.05), 2)

    async def merge_duplicates(self, findings: list[Finding]) -> list[Finding]:
        """Merge findings with matching scanner, title, and evidence.

        The earliest finding ID/timestamp is retained while confidence uses the
        strongest score observed across duplicate evidence.
        """

        merged: dict[str, Finding] = {}
        for finding in findings:
            key = self._duplicate_key(finding)
            existing = merged.get(key)
            if existing is None:
                merged[key] = finding
                continue
            merged[key] = existing.model_copy(
                update={
                    "confidence": max(existing.confidence, finding.confidence),
                    "severity": self._higher_severity(existing.severity, finding.severity),
                    "remediation": existing.remediation or finding.remediation,
                }
            )
        return list(merged.values())

    def _duplicate_key(self, finding: Finding) -> str:
        """Create a stable deduplication key from scanner evidence."""

        evidence = json.dumps(finding.evidence, sort_keys=True, default=str)
        return f"{finding.scanner_id.casefold()}|{finding.title.casefold()}|{evidence}"

    def _higher_severity(self, first: Severity, second: Severity) -> Severity:
        """Return the higher-priority severity."""

        order = list(Severity)
        return first if order.index(first) <= order.index(second) else second

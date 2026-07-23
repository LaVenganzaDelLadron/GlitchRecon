"""HTTP response hardening header scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class HeaderScanner(Scanner):
    """Check baseline hardening headers not covered by specialized plugins."""

    id = "misconfiguration.headers"
    name = "HTTP Hardening Header Scanner"
    category = "misconfiguration"
    description = "Checks baseline HTTP hardening headers in the observed response."
    severity = Severity.LOW
    tags = frozenset({"headers", "http", "misconfiguration", "passive"})
    enabled = True

    SECURITY_HEADERS = [
        "Content-Security-Policy",
        "Strict-Transport-Security",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Permissions-Policy",
    ]

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Return a finding for each missing baseline hardening header."""

        response = await get(context, context.target)
        context.headers = dict(response.headers)
        findings: list[Finding] = []
        for header in self.SECURITY_HEADERS:
            if header.lower() not in response.headers:
                findings.append(Finding(scanner_id=self.id, scanner_name=self.name, title=f"Missing HTTP hardening header: {header}", severity=self.severity, confidence=0.95, description=f"The observed response does not include {header}.", evidence={**response_evidence(response), "observation": "header_absent", "header_checked": header, "header_present": False}, references=["https://owasp.org/www-project-secure-headers/"]))
        return findings

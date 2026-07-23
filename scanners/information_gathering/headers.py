"""Passive HTTP response-header observation scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class HeaderScanner(Scanner):
    """Observe configured security response headers without modifying the target."""

    id = "information.headers"
    name = "HTTP Security Header Scanner"
    category = "information_gathering"
    description = "Observes the presence of commonly deployed HTTP security headers."
    severity = Severity.LOW
    tags = frozenset({"http", "headers", "misconfiguration", "passive"})
    enabled = True
    SECURITY_HEADERS = (
        "Content-Security-Policy", "Strict-Transport-Security", "X-Frame-Options",
        "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy",
    )

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Fetch the target once and report observed missing security headers."""

        response = await get(context, context.target)
        context.headers = dict(response.headers)
        base_evidence = response_evidence(response)
        findings: list[Finding] = []
        for header in self.SECURITY_HEADERS:
            if header.lower() not in response.headers:
                findings.append(Finding(
                    scanner_id=self.id, scanner_name=self.name,
                    title=f"Missing HTTP security header: {header}", severity=self.severity,
                    confidence=0.95, description=f"The observed response does not include the {header} header.",
                    evidence={**base_evidence, "observation": "header_absent", "header_checked": header, "header_present": False},
                    references=["https://owasp.org/www-project-secure-headers/"],
                ))
        return findings

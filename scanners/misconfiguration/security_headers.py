"""Cross-header consistency scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class SecurityHeadersScanner(Scanner):
    """Detect unsafe values in legacy framing and MIME-sniffing protections."""

    id = "misconfiguration.security_headers"
    name = "Security Header Consistency Scanner"
    category = "misconfiguration"
    description = "Checks observed X-Frame-Options and X-Content-Type-Options values."
    severity = Severity.MEDIUM
    tags = frozenset({"headers", "clickjacking", "mime", "misconfiguration", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Report unsafe observed values rather than inferring missing controls."""

        response = await get(context, context.target)
        xfo = response.headers.get("x-frame-options", "").upper()
        xcto = response.headers.get("x-content-type-options", "").lower()
        evidence = {**response_evidence(response), "x_frame_options": xfo or None, "x_content_type_options": xcto or None}
        findings: list[Finding] = []
        if xfo and xfo not in {"DENY", "SAMEORIGIN"}:
            findings.append(Finding(scanner_id=self.id, scanner_name=self.name, title="Unrecognized X-Frame-Options value", severity=self.severity, confidence=0.9, description="The observed X-Frame-Options value is not a recognized protective directive.", evidence={**evidence, "observation": "x_frame_options_unsafe"}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options"]))
        if xcto and xcto != "nosniff":
            findings.append(Finding(scanner_id=self.id, scanner_name=self.name, title="X-Content-Type-Options does not use nosniff", severity=Severity.LOW, confidence=0.95, description="The observed MIME-sniffing protection header does not have the nosniff value.", evidence={**evidence, "observation": "x_content_type_options_unsafe"}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options"]))
        return findings

"""Server fingerprint disclosure scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class FingerprintScanner(Scanner):
    """Report explicit product version disclosures in public response headers."""

    id = "misconfiguration.fingerprinting"
    name = "Server Fingerprint Disclosure Scanner"
    category = "misconfiguration"
    description = "Identifies server or framework headers that expose product version information."
    severity = Severity.LOW
    tags = frozenset({"fingerprinting", "headers", "information-disclosure", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Observe server-identifying headers and report version-bearing values."""

        response = await get(context, context.target)
        disclosed = {header: response.headers[header] for header in ("server", "x-powered-by", "x-aspnet-version", "x-runtime") if response.headers.get(header) and any(char.isdigit() for char in response.headers[header])}
        context.technologies.extend(value for value in disclosed.values() if value not in context.technologies)
        if not disclosed:
            return []
        return [Finding(scanner_id=self.id, scanner_name=self.name, title="Version-bearing server headers disclosed", severity=self.severity, confidence=0.9, description="The response exposes product header values containing version-like information.", evidence={**response_evidence(response), "observation": "version_disclosure", "headers": disclosed}, references=[])]

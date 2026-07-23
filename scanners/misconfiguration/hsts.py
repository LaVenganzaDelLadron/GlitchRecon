"""HTTP Strict Transport Security scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class HSTSScanner(Scanner):
    """Check the observed HSTS policy on HTTPS targets."""

    id = "misconfiguration.hsts"
    name = "HSTS Policy Scanner"
    category = "misconfiguration"
    description = "Checks whether HTTPS responses declare an adequate HSTS max-age."
    severity = Severity.MEDIUM
    tags = frozenset({"hsts", "tls", "headers", "misconfiguration", "passive"})
    enabled = True
    MINIMUM_MAX_AGE = 15_552_000

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Report missing or short HSTS only when the target itself uses HTTPS."""

        if not context.target.lower().startswith("https://"):
            return []
        response = await get(context, context.target)
        policy = response.headers.get("strict-transport-security")
        evidence = {**response_evidence(response), "strict_transport_security": policy}
        if not policy:
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="HSTS header missing on HTTPS response", severity=self.severity, confidence=0.95, description="The observed HTTPS response does not declare Strict-Transport-Security.", evidence={**evidence, "observation": "hsts_missing"}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security"])]
        max_age = next((part.split("=", 1)[1] for part in policy.lower().split(";") if part.strip().startswith("max-age=") and part.split("=", 1)[1].isdigit()), None)
        if max_age is not None and int(max_age) < self.MINIMUM_MAX_AGE:
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="HSTS max-age is shorter than six months", severity=Severity.LOW, confidence=0.95, description="The observed HSTS policy has a short max-age value.", evidence={**evidence, "observation": "hsts_short_max_age", "max_age_seconds": int(max_age)}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security"])]
        return []

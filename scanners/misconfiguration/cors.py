"""CORS response policy scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import request, response_evidence


class CorsScanner(Scanner):
    """Observe permissive CORS headers using a non-sensitive synthetic origin."""

    id = "misconfiguration.cors"
    name = "CORS Policy Scanner"
    category = "misconfiguration"
    description = "Checks observed cross-origin response headers for dangerous combinations."
    severity = Severity.HIGH
    tags = frozenset({"cors", "http", "misconfiguration", "passive"})
    enabled = True
    TEST_ORIGIN = "https://glitchrecon.invalid"

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Make one preflight-like OPTIONS observation without accessing protected data."""

        response = await request(context, "OPTIONS", context.target, headers={"Origin": self.TEST_ORIGIN, "Access-Control-Request-Method": "GET"})
        allowed_origin = response.headers.get("access-control-allow-origin")
        credentials = response.headers.get("access-control-allow-credentials", "").lower() == "true"
        evidence = {**response_evidence(response), "request_origin": self.TEST_ORIGIN, "access_control_allow_origin": allowed_origin, "access_control_allow_credentials": credentials}
        if allowed_origin == "*" and credentials:
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="CORS wildcard origin combined with credentials", severity=self.severity, confidence=0.95, description="The observed CORS response allows any origin and credentials, an unsafe policy combination.", evidence={**evidence, "observation": "cors_wildcard_with_credentials"}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS"])]
        if allowed_origin == self.TEST_ORIGIN and credentials:
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="CORS reflects an arbitrary origin with credentials", severity=self.severity, confidence=0.9, description="The synthetic origin was reflected while credentials were allowed; manual validation is recommended.", evidence={**evidence, "observation": "cors_origin_reflection_with_credentials"}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS"])]
        return []

"""Content Security Policy scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class CSPScanner(Scanner):
    """Evaluate only observable high-risk CSP policy omissions and directives."""

    id = "misconfiguration.csp"
    name = "Content Security Policy Scanner"
    category = "misconfiguration"
    description = "Checks for absent or obviously unsafe Content-Security-Policy directives."
    severity = Severity.MEDIUM
    tags = frozenset({"csp", "headers", "client-side", "misconfiguration", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Inspect the target response CSP header without executing page scripts."""

        response = await get(context, context.target)
        policy = response.headers.get("content-security-policy")
        evidence = {**response_evidence(response), "content_security_policy": policy}
        if not policy:
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="Content-Security-Policy header missing", severity=self.severity, confidence=0.95, description="The observed response does not set a Content-Security-Policy header.", evidence={**evidence, "observation": "csp_missing"}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP"])]
        unsafe = [token for token in ("'unsafe-inline'", "'unsafe-eval'") if token in policy.lower()]
        if unsafe:
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="CSP permits unsafe script behavior", severity=self.severity, confidence=0.9, description="The observed CSP contains directives that weaken browser script protections.", evidence={**evidence, "observation": "csp_unsafe_directive", "unsafe_tokens": unsafe}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP"])]
        return []

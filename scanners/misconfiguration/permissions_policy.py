"""Permissions-Policy scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class PermissionsPolicyScanner(Scanner):
    """Observe absent or wildcard Permissions-Policy directives."""

    id = "misconfiguration.permissions_policy"
    name = "Permissions Policy Scanner"
    category = "misconfiguration"
    description = "Checks the response Permissions-Policy header for absent or wildcard controls."
    severity = Severity.LOW
    tags = frozenset({"permissions-policy", "headers", "browser", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Report an absent policy or directives that explicitly allow all origins."""

        response = await get(context, context.target)
        policy = response.headers.get("permissions-policy")
        evidence = {**response_evidence(response), "permissions_policy": policy}
        if not policy:
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="Permissions-Policy header missing", severity=self.severity, confidence=0.95, description="The observed response does not limit browser feature delegation with Permissions-Policy.", evidence={**evidence, "observation": "permissions_policy_missing"}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy"])]
        wildcard_directives = [directive.strip() for directive in policy.split(",") if "=*" in directive.replace(" ", "")]
        if wildcard_directives:
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="Permissions-Policy contains wildcard directive", severity=self.severity, confidence=0.9, description="The observed policy explicitly delegates one or more browser features to all origins.", evidence={**evidence, "observation": "permissions_policy_wildcard", "wildcard_directives": wildcard_directives}, references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy"])]
        return []

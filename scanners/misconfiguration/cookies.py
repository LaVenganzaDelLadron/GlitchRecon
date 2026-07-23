"""Cookie misconfiguration scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class CookieScanner(Scanner):
    """Identify insecure attributes on response cookies without retaining values."""

    id = "misconfiguration.cookies"
    name = "Cookie Misconfiguration Scanner"
    category = "misconfiguration"
    description = "Checks observed cookies for Secure, HttpOnly, and SameSite attributes."
    severity = Severity.MEDIUM
    tags = frozenset({"cookies", "session", "misconfiguration", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Return evidence-backed findings for cookie flag misconfigurations."""

        response = await get(context, context.target)
        findings: list[Finding] = []

        for cookie in response.cookies.jar:
            raw = str(cookie)
            observed = {**response_evidence(response), "cookie_name": cookie.name, "cookie_domain": cookie.domain, "cookie_path": cookie.path, "secure_observed": bool(cookie.secure), "httponly_observed": "HttpOnly" in raw, "samesite_observed": cookie._rest.get("SameSite") if hasattr(cookie, "_rest") else None}
            checks = ((not cookie.secure, "Secure", "cookie_secure_flag_absent"), ("HttpOnly" not in raw, "HttpOnly", "cookie_httponly_flag_absent"), (not observed["samesite_observed"], "SameSite", "cookie_samesite_attribute_absent"))
            for missing, attribute, observation in checks:
                if missing:
                    findings.append(Finding(scanner_id=self.id, scanner_name=self.name, title=f"Cookie missing {attribute}: {cookie.name}", severity=self.severity, confidence=0.9, description=f"The observed response cookie does not declare the {attribute} attribute.", evidence={**observed, "observation": observation, "missing_attribute": attribute}, references=["https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html"]))
        return findings

"""Passive cookie attribute observation scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence


class CookieScanner(Scanner):
    """Observe cookie security attributes without collecting cookie values."""

    id = "information.cookies"
    name = "Cookie Attribute Scanner"
    category = "information_gathering"
    description = "Observes Secure and HttpOnly attributes on response cookies."
    severity = Severity.MEDIUM
    tags = frozenset({"http", "cookies", "session", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Report security flags absent from observed response cookies."""

        response = await get(context, context.target)
        findings: list[Finding] = []
        for cookie in response.cookies.jar:
            attributes = {
                **response_evidence(response), "cookie_name": cookie.name,
                "cookie_domain": cookie.domain, "cookie_path": cookie.path,
                "secure_observed": bool(cookie.secure),
                "httponly_observed": "HttpOnly" in str(cookie),
            }
            if not cookie.secure:
                findings.append(Finding(
                    scanner_id=self.id, scanner_name=self.name, title=f"Cookie missing Secure flag: {cookie.name}",
                    severity=self.severity, confidence=0.95,
                    description="A response cookie was observed without the Secure attribute.",
                    evidence={**attributes, "observation": "cookie_secure_flag_absent"},
                    references=["https://owasp.org/www-community/controls/SecureCookieAttribute"],
                ))
            if not attributes["httponly_observed"]:
                findings.append(Finding(
                    scanner_id=self.id, scanner_name=self.name, title=f"Cookie missing HttpOnly flag: {cookie.name}",
                    severity=self.severity, confidence=0.9,
                    description="A response cookie was observed without the HttpOnly attribute.",
                    evidence={**attributes, "observation": "cookie_httponly_flag_absent"},
                    references=["https://owasp.org/www-community/HttpOnly"],
                ))
        return findings

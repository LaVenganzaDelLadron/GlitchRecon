"""Clickjacking protection scanner."""
from __future__ import annotations
from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence
class ClickjackingScanner(Scanner):
    """Reports only observed absence of framing protections."""
    id="client_side.clickjacking"; name="Clickjacking Protection Scanner"; category="client_side"; description="Checks observed CSP frame-ancestors and X-Frame-Options protections."; severity=Severity.MEDIUM; tags=frozenset({"client-side","clickjacking","headers","passive"}); enabled=True
    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Inspect response framing headers without rendering the page in a browser."""
        response=await get(context,context.target); csp=response.headers.get("content-security-policy",""); xfo=response.headers.get("x-frame-options")
        if xfo or "frame-ancestors" in csp.lower(): return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="Framing protection not observed",severity=self.severity,confidence=.9,description="The response lacks X-Frame-Options and CSP frame-ancestors protections.",evidence={**response_evidence(response),"observation":"framing_protection_absent","x_frame_options":xfo,"content_security_policy":csp or None},references=["https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html"])]

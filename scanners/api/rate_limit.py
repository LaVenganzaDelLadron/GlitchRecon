"""API rate-limit header scanner."""
from __future__ import annotations
from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence
class RateLimitScanner(Scanner):
    """Observes advertised rate-limit headers without generating traffic bursts."""
    id="api.rate_limit"; name="API Rate Limit Evidence Scanner"; category="api"; description="Records API rate-limit response headers from a single request."; severity=Severity.INFO; tags=frozenset({"api","rate-limit","passive"}); enabled=True
    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Return a finding only when rate-limit headers are observed."""
        response=await get(context,context.target)
        headers={key:value for key,value in response.headers.items() if "ratelimit" in key.lower() or key.lower()=="retry-after"}
        if not headers: return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="API rate-limit headers observed",severity=self.severity,confidence=1.0,description="Rate-limit metadata was observed in one response; enforcement strength was not tested.",evidence={**response_evidence(response),"observation":"api_rate_limit_headers_observed","headers":headers},references=["https://datatracker.ietf.org/doc/html/rfc9333"])]

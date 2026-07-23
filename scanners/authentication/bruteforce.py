"""Login throttling evidence scanner."""
from __future__ import annotations
from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get, response_evidence

class BruteForceScanner(Scanner):
    """Observes advertised rate-limit controls without attempting any login."""
    id="authentication.bruteforce"; name="Login Throttling Evidence Scanner"; category="authentication"; description="Records rate-limit headers exposed by the initial response."; severity=Severity.INFO; tags=frozenset({"authentication","rate-limit","passive"}); enabled=True
    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Report exposed rate-limit header evidence; no credentials or retries are used."""
        response=await get(context, context.target)
        values={key:value for key,value in response.headers.items() if key.lower() in {"ratelimit-limit","x-ratelimit-limit","retry-after"}}
        if not values: return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="Rate-limit response headers observed",severity=self.severity,confidence=1.0,description="Rate-limit controls are advertised in the observed response; login throttling was not tested.",evidence={**response_evidence(response),"observation":"rate_limit_headers_observed","headers":values},references=["https://datatracker.ietf.org/doc/html/rfc9333"])]

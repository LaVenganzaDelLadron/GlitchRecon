"""HTTP cache-control scanner."""
from __future__ import annotations
from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get,response_evidence
class CacheScanner(Scanner):
    """Observes cache directives without accessing authenticated content."""
    id="http.cache"; name="HTTP Cache Policy Scanner"; category="http"; description="Records public cache-control directives for manual review."; severity=Severity.INFO; tags=frozenset({"http","cache","passive"}); enabled=True
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Return a finding when a Cache-Control header is present."""
        response=await get(context,context.target); value=response.headers.get("cache-control")
        if not value:return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="HTTP cache policy observed",severity=self.severity,confidence=1,description="A public Cache-Control directive was observed; content sensitivity was not inferred.",evidence={**response_evidence(response),"observation":"cache_control_observed","cache_control":value},references=[])]

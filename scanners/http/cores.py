"""Cross-origin isolation header scanner."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get,response_evidence
class CORESScanner(Scanner):
    """Observes COOP, COEP, and CORP isolation headers."""
    id="http.cores";name="Cross-Origin Isolation Header Scanner";category="http";description="Records cross-origin isolation response headers.";severity=Severity.INFO;tags=frozenset({"http","cross-origin","passive"});enabled=True
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Return evidence when any isolation header is declared."""
        response=await get(context,context.target);headers={k:v for k,v in response.headers.items() if k.lower() in {"cross-origin-opener-policy","cross-origin-embedder-policy","cross-origin-resource-policy"}}
        if not headers:return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="Cross-origin isolation headers observed",severity=self.severity,confidence=1,description="Cross-origin isolation configuration was observed for researcher review.",evidence={**response_evidence(response),"observation":"cross_origin_headers_observed","headers":headers},references=[])]

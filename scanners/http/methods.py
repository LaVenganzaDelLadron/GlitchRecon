"""HTTP method advertisement scanner."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import request,response_evidence
class HTTPMethodsScanner(Scanner):
    """Uses one OPTIONS request to observe advertised methods only."""
    id="http.methods";name="HTTP Method Advertisement Scanner";category="http";description="Observes methods advertised by an OPTIONS response.";severity=Severity.INFO;tags=frozenset({"http","methods","passive"});enabled=True
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Record the Allow header without invoking unsafe methods."""
        response=await request(context,"OPTIONS",context.target);allow=response.headers.get("allow")
        if not allow:return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="HTTP methods advertised",severity=self.severity,confidence=1,description="The server advertised HTTP methods in response to OPTIONS; no state-changing method was invoked.",evidence={**response_evidence(response),"observation":"allow_header_observed","allow":allow},references=[])]

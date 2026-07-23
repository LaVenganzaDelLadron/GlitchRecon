"""HTTP redirect observation scanner."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get,response_evidence
class RedirectScanner(Scanner):
    """Observes redirect behavior without manipulating redirect parameters."""
    id="http.redirects";name="HTTP Redirect Scanner";category="http";description="Records whether the target redirects an initial public request.";severity=Severity.INFO;tags=frozenset({"http","redirect","passive"});enabled=True
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Capture one non-followed redirect response when present."""
        response=await get(context,context.target,follow_redirects=False)
        location=response.headers.get("location")
        if not location:return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="HTTP redirect observed",severity=self.severity,confidence=1,description="The initial public request returned a redirect location; no alternate destinations were supplied.",evidence={**response_evidence(response),"observation":"redirect_observed","location":location},references=[])]

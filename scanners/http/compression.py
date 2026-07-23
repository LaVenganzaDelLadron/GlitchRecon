"""HTTP compression policy scanner."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import get,response_evidence
class CompressionScanner(Scanner):
    """Observes response compression headers without compression attacks."""
    id="http.compression";name="HTTP Compression Scanner";category="http";description="Records content-encoding and compression-related response metadata.";severity=Severity.INFO;tags=frozenset({"http","compression","passive"});enabled=True
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Report the observed compression encoding when present."""
        response=await get(context,context.target);encoding=response.headers.get("content-encoding")
        if not encoding:return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="HTTP response compression observed",severity=self.severity,confidence=1,description="Response compression was observed; no compression side-channel attack was attempted.",evidence={**response_evidence(response),"observation":"content_encoding_observed","content_encoding":encoding},references=[])]

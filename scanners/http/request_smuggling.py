"""Request-smuggling safety control."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
class RequestSmugglingScanner(Scanner):
    """Is intentionally disabled because safe detection needs malformed requests."""
    id="http.request_smuggling";name="Request Smuggling Safety Scanner";category="http";description="Documents that malformed transfer requests are not sent by passive scans.";severity=Severity.INFO;tags=frozenset({"http","request-smuggling","safety"});enabled=False
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Return no result because malformed request probing is intentionally omitted."""
        return []

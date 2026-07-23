"""Directory index response scanner."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text,get,response_evidence
class DirectoryListingScanner(Scanner):
    """Identifies an index-style response only at the supplied target URL."""
    id="files.directory_listing";name="Directory Listing Scanner";category="files";description="Observes directory index signatures at the target URL without path enumeration.";severity=Severity.MEDIUM;tags=frozenset({"files","directory-listing","passive"});enabled=True
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Report an index signature when publicly returned by the target URL."""
        response=await get(context,context.target);body=bounded_text(response,10000).lower();markers=("index of /","directory listing for")
        if not any(marker in body for marker in markers):return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="Directory index signature observed",severity=self.severity,confidence=.9,description="The target response resembles a directory index. No child paths were enumerated.",evidence={**response_evidence(response),"observation":"directory_index_marker_observed","markers":[m for m in markers if m in body]},references=[])]

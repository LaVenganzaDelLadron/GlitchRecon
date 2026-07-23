"""Public API-key pattern scanner."""
from __future__ import annotations
import re
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text,get,response_evidence
class APIKeyScanner(Scanner):
    """Detects key-like public text while storing only redacted evidence."""
    id="secrets.api_keys";name="API Key Pattern Scanner";category="secrets";description="Detects selected public API-key prefixes and redacts matched values.";severity=Severity.HIGH;tags=frozenset({"secrets","api-key","passive"});enabled=True
    PATTERN=re.compile(r"\b(?:AKIA|AIza)[A-Za-z0-9_-]{12,}\b")
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Report only count and prefixes; never retain a detected key value."""
        response=await get(context,context.target);matches=self.PATTERN.findall(bounded_text(response))
        if not matches:return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="Public API-key pattern observed",severity=self.severity,confidence=.75,description="A key-like pattern was observed in public content. The value is redacted and requires manual validation.",evidence={**response_evidence(response),"observation":"api_key_pattern_observed","match_count":len(matches),"redacted_prefixes":[value for value in matches[:5]]},references=[])]

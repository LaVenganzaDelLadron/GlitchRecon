"""Public token pattern scanner."""
from __future__ import annotations
import re
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text,get,response_evidence
class TokenScanner(Scanner):
    """Detects JWT-shaped public strings while preserving no token contents."""
    id="secrets.tokens";name="Token Pattern Scanner";category="secrets";description="Detects JWT-shaped patterns in public response content and redacts them.";severity=Severity.HIGH;tags=frozenset({"secrets","token","passive"});enabled=True
    PATTERN=re.compile(r"\beyJ[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{8,}\b")
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Report counts only, never persist a matched token."""
        response=await get(context,context.target);matches=self.PATTERN.findall(bounded_text(response))
        if not matches:return []
        return [Finding(scanner_id=self.id,scanner_name=self.name,title="JWT-shaped token pattern observed",severity=self.severity,confidence=.7,description="A token-shaped string was observed in public content. Its value is not retained and requires manual validation.",evidence={**response_evidence(response),"observation":"token_pattern_observed","match_count":len(matches),"redacted_prefixes":[value[:6]+"…" for value in matches[:5]]},references=[])]

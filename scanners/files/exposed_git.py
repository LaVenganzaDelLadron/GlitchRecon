"""Git exposure safety scanner."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
class ExposedGitScanner(Scanner):
    """Avoids .git requests because they can expose repository history."""
    id="files.exposed_git";name="Git Exposure Safety Scanner";category="files";description="Documents that .git endpoint probing is disabled by default.";severity=Severity.INFO;tags=frozenset({"files","git","safety"});enabled=False
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Return no finding because repository files are not requested."""
        return []

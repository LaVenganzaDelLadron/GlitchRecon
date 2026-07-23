"""Environment-file exposure safety scanner."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
class ExposedEnvironmentScanner(Scanner):
    """Avoids .env path requests because they may retrieve credentials."""
    id="files.exposed_env";name="Environment File Safety Scanner";category="files";description="Documents that .env endpoint probing is disabled by default.";severity=Severity.INFO;tags=frozenset({"files","environment","safety"});enabled=False
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Return no finding because credential-bearing files are never requested."""
        return []

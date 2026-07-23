"""Environment-file safety control."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
class EnvironmentFileScanner(Scanner):
    """Is disabled because requesting environment files risks collecting secrets."""
    id="secrets.env_files";name="Environment File Secret Safety Scanner";category="secrets";description="Documents that secret-bearing environment file requests are disabled.";severity=Severity.INFO;tags=frozenset({"secrets","environment","safety"});enabled=False
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Return no finding because environment files are never requested."""
        return []

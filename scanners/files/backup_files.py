"""Backup exposure safety scanner."""
from __future__ import annotations
from app.models.schemas import Finding,Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
class BackupFilesScanner(Scanner):
    """Avoids backup filename probing because it can expose sensitive content."""
    id="files.backup_files";name="Backup File Safety Scanner";category="files";description="Documents that backup filename enumeration is disabled by default.";severity=Severity.INFO;tags=frozenset({"files","backup","safety"});enabled=False
    async def scan(self,context:PipelineContext)->list[Finding]:
        """Return no finding because sensitive backup paths are not probed."""
        return []

"""Cloud metadata exposure safeguard."""
from __future__ import annotations
from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
class CloudMetadataScanner(Scanner):
    """Records that cloud metadata endpoints are intentionally never requested."""
    id="cloud.metadata"; name="Cloud Metadata Safety Scanner"; category="cloud"; description="Provides an explicit non-probing control for cloud instance metadata endpoints."; severity=Severity.INFO; tags=frozenset({"cloud","metadata","safety"}); enabled=False
    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Return no finding because metadata endpoint probing is intentionally disabled."""
        return []

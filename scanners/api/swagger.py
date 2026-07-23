"""Swagger UI discovery scanner."""
from __future__ import annotations
from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text, get, response_evidence, target_url
class SwaggerScanner(Scanner):
    """Discovers public Swagger UI resources without submitting API requests."""
    id="api.swagger"; name="Swagger UI Discovery Scanner"; category="api"; description="Discovers public Swagger UI pages."; severity=Severity.INFO; tags=frozenset({"api","swagger","documentation","passive"}); enabled=True
    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Check standard Swagger UI locations and report only confirmed pages."""
        for path in ("/swagger","/swagger/","/docs"):
            response=await get(context,target_url(context,path))
            if response.status_code==200 and "swagger" in bounded_text(response,5000).lower():
                return [Finding(scanner_id=self.id,scanner_name=self.name,title="Public Swagger UI discovered",severity=self.severity,confidence=0.9,description="A public Swagger UI page was found; no API operation was invoked.",evidence={**response_evidence(response),"observation":"swagger_ui_available","location":path},references=["https://swagger.io/specification/"])]
        return []

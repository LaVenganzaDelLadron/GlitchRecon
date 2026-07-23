"""OpenAPI document discovery scanner."""
from __future__ import annotations
from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text, get, response_evidence, target_url
class OpenAPIScanner(Scanner):
    """Retrieves known public OpenAPI document locations without calling documented operations."""
    id="api.openapi"; name="OpenAPI Discovery Scanner"; category="api"; description="Discovers publicly exposed OpenAPI documents."; severity=Severity.INFO; tags=frozenset({"api","openapi","documentation","passive"}); enabled=True
    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Check standard OpenAPI JSON locations and record bounded metadata."""
        for path in ("/openapi.json","/api/openapi.json"):
            response=await get(context,target_url(context,path))
            if response.status_code==200 and "openapi" in bounded_text(response,5000).lower():
                return [Finding(scanner_id=self.id,scanner_name=self.name,title="Public OpenAPI document discovered",severity=self.severity,confidence=0.95,description="A public OpenAPI document was found; documented endpoints were not invoked.",evidence={**response_evidence(response),"observation":"openapi_document_available","location":path},references=["https://spec.openapis.org/oas/latest.html"])]
        return []

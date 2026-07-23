"""Source-map reference scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class SourceMapScanner(PassiveMarkerScanner):
    """Observes public source-map references without fetching maps."""
    id="client_side.source_maps"; name="Source Map Reference Scanner"; category="client_side"; description="Detects source-map URL comments and references in public markup."; severity=Severity.LOW; tags=frozenset({"client-side","source-map","passive"}); enabled=True
    markers=("sourceMappingURL=", ".map\""); observation="source_map_reference_observed"; finding_title="Source-map reference observed"; finding_description="A source-map reference was observed. The source map itself was not requested."; references=()

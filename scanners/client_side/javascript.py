"""JavaScript asset marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class JavaScriptScanner(PassiveMarkerScanner):
    """Observes linked JavaScript assets without downloading arbitrary assets."""
    id="client_side.javascript"; name="JavaScript Asset Marker Scanner"; category="client_side"; description="Records public JavaScript asset references."; severity=Severity.INFO; tags=frozenset({"client-side","javascript","passive"}); enabled=True
    markers=("<script src=",".js\""); observation="javascript_asset_marker_observed"; finding_title="JavaScript asset marker observed"; finding_description="Public JavaScript asset references were observed; linked scripts were not fetched or executed."; references=()

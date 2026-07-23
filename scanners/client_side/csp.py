"""Client-side CSP marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class ClientCSPScanner(PassiveMarkerScanner):
    """Observes inline script markers; it does not execute JavaScript."""
    id="client_side.csp"; name="Inline Script Marker Scanner"; category="client_side"; description="Observes inline script markup for CSP review."; severity=Severity.INFO; tags=frozenset({"client-side","csp","passive"}); enabled=True
    markers=("<script>","onclick=","onload="); observation="inline_script_marker_observed"; finding_title="Inline script marker observed"; finding_description="Inline script markup was observed. CSP enforcement is assessed separately from this marker."; references=()

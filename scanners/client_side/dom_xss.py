"""DOM input sink marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class DOMXSSScanner(PassiveMarkerScanner):
    """Observes public DOM sink names without running browser payloads."""
    id="client_side.dom_xss"; name="DOM Sink Marker Scanner"; category="client_side"; description="Detects public DOM sink terms for manual code review."; severity=Severity.INFO; tags=frozenset({"client-side","dom-xss","passive"}); enabled=True
    markers=("innerhtml","document.write","location.hash"); observation="dom_sink_marker_observed"; finding_title="DOM sink marker observed"; finding_description="A DOM sink marker was observed in public markup. No JavaScript payload was executed."; references=("https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html",)

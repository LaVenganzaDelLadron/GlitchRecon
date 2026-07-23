"""Access-control UI marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner

class AccessControlScanner(PassiveMarkerScanner):
    """Observes public role or permission UI markers without switching identities."""
    id="authorization.access_control"; name="Access Control Marker Scanner"; category="authorization"; description="Discovers public role and permission terminology for scope review."; severity=Severity.INFO; tags=frozenset({"authorization","access-control","passive"}); enabled=True
    markers=("admin", "role=", "permission"); observation="access_control_marker_observed"; finding_title="Access-control marker observed"; finding_description="A public role or permission marker was observed. Enforcement was not tested."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html",)

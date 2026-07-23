"""Session management UI marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner

class SessionScanner(PassiveMarkerScanner):
    """Observes public session-management controls without modifying a session."""
    id="authentication.session"; name="Session Marker Scanner"; category="authentication"; description="Discovers public logout or session management UI markers."; severity=Severity.INFO; tags=frozenset({"authentication","session","passive"}); enabled=True
    markers=("logout", "sign out", "session expired"); observation="session_marker_observed"; finding_title="Session-management marker observed"; finding_description="A public session-management marker was observed; session lifecycle controls were not exercised."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html",)

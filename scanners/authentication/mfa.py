"""MFA UI marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner

class MFAScanner(PassiveMarkerScanner):
    """Observes MFA-related public UI markers without authentication attempts."""
    id="authentication.mfa"; name="MFA Marker Scanner"; category="authentication"; description="Discovers public multi-factor authentication UI markers."; severity=Severity.INFO; tags=frozenset({"authentication","mfa","passive"}); enabled=True
    markers=("one-time password", "two-factor", "multifactor", "authenticator app"); observation="mfa_marker_observed"; finding_title="MFA interface marker observed"; finding_description="A public MFA-related marker was observed; this does not verify MFA enforcement."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html",)

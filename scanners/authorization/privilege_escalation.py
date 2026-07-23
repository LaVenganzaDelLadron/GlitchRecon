"""Privilege-management UI marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner

class PrivilegeEscalationScanner(PassiveMarkerScanner):
    """Observes public administrative terminology without privilege modification."""
    id="authorization.privilege_escalation"; name="Privilege Management Marker Scanner"; category="authorization"; description="Discovers public administrative privilege-management markers."; severity=Severity.INFO; tags=frozenset({"authorization","privileges","passive"}); enabled=True
    markers=("manage users", "administrator", "elevated privileges"); observation="privilege_management_marker_observed"; finding_title="Privilege-management marker observed"; finding_description="A public administrative marker was observed. No role changes or privileged actions were attempted."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html",)

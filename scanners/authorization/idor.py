"""Object-reference surface scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner

class IDORScanner(PassiveMarkerScanner):
    """Observes public object-reference naming without altering identifiers."""
    id="authorization.idor"; name="Object Reference Surface Scanner"; category="authorization"; description="Identifies public object-reference parameter markers for manual authorized review."; severity=Severity.INFO; tags=frozenset({"authorization","idor","object-reference","passive"}); enabled=True
    markers=("user_id", "account_id", "order_id", "resource_id"); observation="object_reference_marker_observed"; finding_title="Object-reference marker observed"; finding_description="A public object-reference marker was observed. No alternate identifiers were requested."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html",)

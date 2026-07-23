"""Password policy UI scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner

class PasswordPolicyScanner(PassiveMarkerScanner):
    """Observes client-side password policy attributes without creating accounts."""
    id="authentication.password_policy"; name="Password Policy UI Scanner"; category="authentication"; description="Records public password field constraints for manual review."; severity=Severity.INFO; tags=frozenset({"authentication","password","passive"}); enabled=True
    markers=("minlength=", "password requirements", "password must"); observation="password_policy_marker_observed"; finding_title="Password policy UI marker observed"; finding_description="A public password policy marker was observed; server-side enforcement is not inferred."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",)

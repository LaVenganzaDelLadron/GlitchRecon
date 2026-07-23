"""Login form discovery scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner

class LoginScanner(PassiveMarkerScanner):
    """Observes publicly rendered login forms without submitting credentials."""
    id="authentication.login"; name="Login Surface Scanner"; category="authentication"; description="Discovers public password login form markers."; severity=Severity.INFO; tags=frozenset({"authentication","login","passive"}); enabled=True
    markers=("type=\"password\"", "type='password'"); observation="login_form_observed"; finding_title="Password login form observed"; finding_description="A public password field was observed. No credentials were submitted."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",)

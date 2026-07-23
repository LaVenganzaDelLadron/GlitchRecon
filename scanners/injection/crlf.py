"""Header-input surface scanner; it never sends CRLF sequences."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class CRLFScanner(PassiveMarkerScanner):
    """Reports redirect or header-related public input markers only."""
    id="injection.crlf"; name="Header Input Surface Scanner"; category="injection"; description="Observes public redirect parameter markers without malformed header requests."; severity=Severity.INFO; tags=frozenset({"injection","crlf","passive"}); enabled=True
    markers=("redirect_uri", "return_url", "next="); observation="redirect_input_marker_observed"; finding_title="Redirect input marker observed"; finding_description="A public redirect marker was observed. No encoded control characters were sent."; references=("https://owasp.org/www-community/vulnerabilities/CRLF_Injection",)

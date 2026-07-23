"""Directory-query surface scanner; it never sends LDAP filters."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class LDAPScanner(PassiveMarkerScanner):
    """Reports public directory-search markers without directory queries."""
    id="injection.ldap"; name="Directory Query Surface Scanner"; category="injection"; description="Observes public directory lookup terminology without LDAP filter submission."; severity=Severity.INFO; tags=frozenset({"injection","ldap","passive"}); enabled=True
    markers=("directory search", "ldap", "employee lookup"); observation="directory_query_marker_observed"; finding_title="Directory-query marker observed"; finding_description="A public directory marker was observed. No LDAP filter was submitted."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html",)

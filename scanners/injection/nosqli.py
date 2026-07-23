"""Document-query surface scanner; it never sends NoSQL operators."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class NoSQLiScanner(PassiveMarkerScanner):
    """Reports public JSON filter markers without submitting query operators."""
    id="injection.nosqli"; name="Document Query Surface Scanner"; category="injection"; description="Observes public JSON filter terminology without NoSQL operator submission."; severity=Severity.INFO; tags=frozenset({"injection","nosqli","passive"}); enabled=True
    markers=("json filter", "mongodb", "document query"); observation="document_query_marker_observed"; finding_title="Document-query marker observed"; finding_description="A public document-query marker was observed. No NoSQL operator was sent."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html",)

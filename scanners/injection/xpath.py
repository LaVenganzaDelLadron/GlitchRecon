"""XML query surface scanner; it never sends XPath expressions."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class XPathScanner(PassiveMarkerScanner):
    """Reports public XML-search markers for manual review only."""
    id="injection.xpath"; name="XML Query Surface Scanner"; category="injection"; description="Observes public XML query terminology without XPath expression submission."; severity=Severity.INFO; tags=frozenset({"injection","xpath","passive"}); enabled=True
    markers=("xpath", "xml search", "xml query"); observation="xml_query_marker_observed"; finding_title="XML-query marker observed"; finding_description="A public XML query marker was observed. No XPath expression was submitted."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html",)

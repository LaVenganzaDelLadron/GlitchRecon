"""XML upload surface scanner; it never submits XML entities."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class XXEScanner(PassiveMarkerScanner):
    """Reports public XML upload indicators without uploading any documents."""
    id="injection.xxe"; name="XML Upload Surface Scanner"; category="injection"; description="Observes public XML upload or import markers without XML submission."; severity=Severity.INFO; tags=frozenset({"injection","xxe","passive"}); enabled=True
    markers=("accept=\".xml", "xml import", "xml upload"); observation="xml_upload_marker_observed"; finding_title="XML upload marker observed"; finding_description="A public XML import marker was observed. No XML document or external entity was submitted."; references=("https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html",)

"""Mixed-content reference scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class MixedContentScanner(PassiveMarkerScanner):
    """Reports HTTP resource references only on HTTPS targets."""
    id="client_side.mixed_content"; name="Mixed Content Reference Scanner"; category="client_side"; description="Observes insecure HTTP resource references in HTTPS response markup."; severity=Severity.MEDIUM; tags=frozenset({"client-side","mixed-content","passive"}); enabled=True
    markers=("src=\"http://","href=\"http://"); observation="http_resource_reference_observed"; finding_title="Insecure HTTP resource reference observed"; finding_description="An HTTP resource reference was observed in markup. Browser loading behavior was not tested."; references=["https://developer.mozilla.org/en-US/docs/Web/Security/Mixed_content"]

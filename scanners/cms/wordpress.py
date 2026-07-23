"""WordPress marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class WordPressScanner(PassiveMarkerScanner):
    """Observes public WordPress markers without enumerating plugins or users."""
    id="cms.wordpress"; name="WordPress Marker Scanner"; category="cms"; description="Detects public WordPress resource markers."; severity=Severity.INFO; tags=frozenset({"cms","wordpress","passive"}); enabled=True
    markers=("wp-content/","wp-includes/"); observation="wordpress_marker_observed"; finding_title="WordPress marker observed"; finding_description="Public WordPress resource markers were observed; no users, plugins, or endpoints were enumerated."; references=()

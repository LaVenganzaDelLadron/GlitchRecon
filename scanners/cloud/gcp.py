"""Google Cloud marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class GCPScanner(PassiveMarkerScanner):
    """Observes public Google Cloud service markers without requesting metadata."""
    id="cloud.gcp"; name="Google Cloud Marker Scanner"; category="cloud"; description="Detects public Google Cloud hosting or asset markers."; severity=Severity.INFO; tags=frozenset({"cloud","gcp","passive"}); enabled=True
    markers=("appspot.com","cloudfunctions.net","storage.googleapis.com"); observation="gcp_marker_observed"; finding_title="Google Cloud service marker observed"; finding_description="A public Google Cloud marker was observed. No metadata service or storage enumeration was attempted."; references=()

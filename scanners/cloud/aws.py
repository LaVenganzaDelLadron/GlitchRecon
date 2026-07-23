"""AWS marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class AWSScanner(PassiveMarkerScanner):
    """Observes public AWS service markers without requesting cloud metadata."""
    id="cloud.aws"; name="AWS Marker Scanner"; category="cloud"; description="Detects public AWS hosting or asset markers."; severity=Severity.INFO; tags=frozenset({"cloud","aws","passive"}); enabled=True
    markers=("amazonaws.com","cloudfront.net","s3.amazonaws.com"); observation="aws_marker_observed"; finding_title="AWS service marker observed"; finding_description="A public AWS service marker was observed. No metadata service or bucket enumeration was attempted."; references=()

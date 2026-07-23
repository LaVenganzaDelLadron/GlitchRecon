"""Public credential-assignment pattern scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class CredentialScanner(PassiveMarkerScanner):
    """Observes assignment labels but never records potential secret values."""
    id="secrets.credentials";name="Credential Assignment Marker Scanner";category="secrets";description="Detects public credential-assignment labels for manual review.";severity=Severity.MEDIUM;tags=frozenset({"secrets","credentials","passive"});enabled=True
    markers=("password =","secret =","client_secret");observation="credential_assignment_marker_observed";finding_title="Credential assignment marker observed";finding_description="A public credential-assignment marker was observed. Potential values are not collected.";references=()

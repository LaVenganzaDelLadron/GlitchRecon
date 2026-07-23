"""Azure marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class AzureScanner(PassiveMarkerScanner):
    """Observes public Azure service markers without requesting cloud metadata."""
    id="cloud.azure"; name="Azure Marker Scanner"; category="cloud"; description="Detects public Azure hosting or asset markers."; severity=Severity.INFO; tags=frozenset({"cloud","azure","passive"}); enabled=True
    markers=("azurewebsites.net","blob.core.windows.net","azureedge.net"); observation="azure_marker_observed"; finding_title="Azure service marker observed"; finding_description="A public Azure service marker was observed. No metadata service or storage enumeration was attempted."; references=()

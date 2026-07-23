"""File-upload UI marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class UploadScanner(PassiveMarkerScanner):
    """Observes public upload controls without submitting files."""
    id="files.uploads";name="File Upload Surface Scanner";category="files";description="Detects public file input controls.";severity=Severity.INFO;tags=frozenset({"files","upload","passive"});enabled=True
    markers=("type=\"file\"","type='file'");observation="file_input_observed";finding_title="File upload control observed";finding_description="A public file input was observed. No file was uploaded.";references=()

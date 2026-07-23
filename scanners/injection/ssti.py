"""Template input surface scanner; it never sends template expressions."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class SSTIScanner(PassiveMarkerScanner):
    """Reports public template-customization markers for manual review only."""
    id="injection.ssti"; name="Template Input Surface Scanner"; category="injection"; description="Observes public template-related markers without expression submission."; severity=Severity.INFO; tags=frozenset({"injection","ssti","passive"}); enabled=True
    markers=("template", "custom message", "email preview"); observation="template_input_marker_observed"; finding_title="Template input marker observed"; finding_description="A public template marker was observed. No template expression was submitted."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html",)

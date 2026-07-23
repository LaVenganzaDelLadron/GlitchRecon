"""Reflected-input surface scanner; it never sends scripts."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class XSSScanner(PassiveMarkerScanner):
    """Reports public text input surfaces for authorized manual review only."""
    id="injection.xss"; name="Client Input Surface Scanner"; category="injection"; description="Observes public text inputs without submitting markup or scripts."; severity=Severity.INFO; tags=frozenset({"injection","xss","passive"}); enabled=True
    markers=("<textarea", "type=\"text\"", "contenteditable"); observation="text_input_surface_observed"; finding_title="Text input surface observed"; finding_description="A public text input surface was observed. No markup or script payload was submitted."; references=("https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",)

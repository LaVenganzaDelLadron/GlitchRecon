"""Command-oriented input surface scanner; it never sends commands."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class CommandInjectionScanner(PassiveMarkerScanner):
    """Reports public diagnostic input terminology for manual scope review only."""
    id="injection.command_injection"; name="Command Input Surface Scanner"; category="injection"; description="Observes public diagnostic or host input markers without command submission."; severity=Severity.INFO; tags=frozenset({"injection","command","passive"}); enabled=True
    markers=("ping", "hostname", "diagnostic"); observation="command_input_marker_observed"; finding_title="Command-oriented input marker observed"; finding_description="A public diagnostic marker was observed. No shell syntax or command was submitted."; references=("https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html",)

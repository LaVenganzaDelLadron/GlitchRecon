"""SQL input-surface scanner; it never sends SQL payloads."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class SQLiScanner(PassiveMarkerScanner):
    """Reports public database-oriented input markers for manual review only."""
    id="injection.sqli"; name="SQL Input Surface Scanner"; category="injection"; description="Observes public query and search input markers without payload submission."; severity=Severity.INFO; tags=frozenset({"injection","sqli","passive"}); enabled=True
    markers=("name=\"search\"", "name=\"query\"", "name=\"filter\""); observation="sql_input_surface_observed"; finding_title="Database-oriented input surface observed"; finding_description="A public input marker was observed. No SQL syntax or payload was sent."; references=("https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",)

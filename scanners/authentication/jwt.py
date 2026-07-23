"""JWT implementation marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner

class JWTScanner(PassiveMarkerScanner):
    """Observes public JWT implementation references without crafting tokens."""
    id="authentication.jwt"; name="JWT Marker Scanner"; category="authentication"; description="Discovers public JWT markers for manual configuration review."; severity=Severity.INFO; tags=frozenset({"authentication","jwt","passive"}); enabled=True
    markers=("jsonwebtoken", "bearer token", "jwt"); observation="jwt_marker_observed"; finding_title="JWT implementation marker observed"; finding_description="A public JWT-related marker was observed. Token validation was not tested."; references=("https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html",)

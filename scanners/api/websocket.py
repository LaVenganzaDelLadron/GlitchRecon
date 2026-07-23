"""WebSocket endpoint marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class WebSocketScanner(PassiveMarkerScanner):
    """Observes public WebSocket URL markers without opening a socket."""
    id="api.websocket"; name="WebSocket Surface Scanner"; category="api"; description="Discovers public WebSocket endpoint markers without creating a connection."; severity=Severity.INFO; tags=frozenset({"api","websocket","passive"}); enabled=True
    markers=("ws://", "wss://", "websocket"); observation="websocket_marker_observed"; finding_title="WebSocket marker observed"; finding_description="A public WebSocket marker was observed. No WebSocket connection was opened."; references=("https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html",)

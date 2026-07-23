"""TLS transport configuration scanner."""

from __future__ import annotations

import asyncio
import ssl
from urllib.parse import urlparse

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import target_host


class TLSScanner(Scanner):
    """Observe the negotiated TLS version and cipher without weakening negotiation."""

    id = "misconfiguration.tls"
    name = "TLS Configuration Scanner"
    category = "misconfiguration"
    description = "Flags weak cryptographic details only when negotiated by a standard TLS client."
    severity = Severity.HIGH
    tags = frozenset({"tls", "transport", "cipher", "misconfiguration", "passive"})
    enabled = True
    WEAK_CIPHER_MARKERS = ("RC4", "3DES", "DES-", "NULL", "MD5")

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Observe one normal TLS handshake and report only weak negotiated details."""

        if not context.target.lower().startswith("https://"):
            return []
        host = target_host(context)
        port = urlparse(context.target).port or 443
        _reader, writer = await asyncio.open_connection(host, port, ssl=ssl.create_default_context(), server_hostname=host)
        try:
            connection = writer.get_extra_info("ssl_object")
            if connection is None:
                return []
            version = connection.version() or "unknown"
            cipher = connection.cipher()[0] if connection.cipher() else "unknown"
            evidence = {"observation": "tls_negotiation", "hostname": host, "port": port, "tls_version": version, "cipher": cipher}
            weak = version in {"TLSv1", "TLSv1.1"} or any(marker in cipher.upper() for marker in self.WEAK_CIPHER_MARKERS)
            if not weak:
                return []
            return [Finding(scanner_id=self.id, scanner_name=self.name, title="Weak TLS protocol or cipher negotiated", severity=self.severity, confidence=0.95, description="A standard TLS handshake negotiated an obsolete protocol version or weak cipher suite.", evidence={**evidence, "observation": "weak_tls_negotiation"}, references=["https://owasp.org/www-project-cheat-sheets/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html"])]
        finally:
            writer.close()
            await writer.wait_closed()

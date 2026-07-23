"""Passive TLS certificate observation scanner."""

from __future__ import annotations

import asyncio
import ssl
from datetime import UTC, datetime
from urllib.parse import urlparse

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import target_host


class TLSScanner(Scanner):
    """Observe certificate and negotiated TLS details for HTTPS targets."""

    id = "information.tls"
    name = "TLS Certificate Scanner"
    category = "information_gathering"
    description = "Collects negotiated TLS version and validated peer certificate metadata."
    severity = Severity.INFO
    tags = frozenset({"tls", "certificate", "transport", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Establish one standard TLS connection and record public certificate metadata."""

        if not context.target.lower().startswith("https://"):
            return []
        host = target_host(context)
        tls_context = ssl.create_default_context()
        port = urlparse(context.target).port or 443
        _reader, writer = await asyncio.open_connection(host, port, ssl=tls_context, server_hostname=host)
        try:
            ssl_object = writer.get_extra_info("ssl_object")
            if ssl_object is None:
                return []
            certificate = ssl_object.getpeercert()
            not_after = certificate.get("notAfter")
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC).isoformat() if not_after else None
            subject = {key: value for entries in certificate.get("subject", ()) for key, value in entries}
            return [Finding(
                scanner_id=self.id, scanner_name=self.name, title="TLS certificate observed",
                severity=self.severity, confidence=1.0,
                description="A standard TLS connection succeeded; the displayed certificate metadata is provided for review.",
                evidence={"observation": "tls_connection", "hostname": host, "port": port, "tls_version": ssl_object.version(), "cipher": ssl_object.cipher()[0] if ssl_object.cipher() else None, "certificate_subject": subject, "certificate_expires_at": expiry},
                references=[],
            )]
        finally:
            writer.close()
            await writer.wait_closed()

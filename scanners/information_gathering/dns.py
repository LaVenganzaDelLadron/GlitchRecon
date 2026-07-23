"""Passive DNS resolution scanner."""

from __future__ import annotations

import asyncio
import socket

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import target_host


class DNSScanner(Scanner):
    """Resolve the target hostname using the operating system resolver only."""

    id = "information.dns"
    name = "DNS Resolution Scanner"
    category = "information_gathering"
    description = "Records A or AAAA addresses returned by the local resolver."
    severity = Severity.INFO
    tags = frozenset({"dns", "reconnaissance", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Resolve the target hostname without zone transfers or active probing."""

        host = target_host(context)
        loop = asyncio.get_running_loop()
        records = await loop.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        addresses = sorted({record[4][0] for record in records})
        if not addresses:
            return []
        return [Finding(
            scanner_id=self.id, scanner_name=self.name, title="DNS addresses resolved",
            severity=self.severity, confidence=0.9,
            description="The local resolver returned the listed network addresses for the target hostname.",
            evidence={"observation": "dns_resolution", "hostname": host, "addresses": addresses},
            references=[],
        )]

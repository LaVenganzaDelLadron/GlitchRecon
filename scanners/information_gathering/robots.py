"""Passive robots.txt discovery scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text, get, response_evidence, target_url


class RobotsScanner(Scanner):
    """Observe public robots.txt directives and referenced sitemap locations."""

    id = "information.robots"
    name = "Robots.txt Scanner"
    category = "information_gathering"
    description = "Collects publicly exposed robots.txt directives for researcher review."
    severity = Severity.INFO
    tags = frozenset({"robots", "content-discovery", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Retrieve robots.txt and report its public directives as evidence."""

        url = target_url(context, "/robots.txt")
        response = await get(context, url)
        if response.status_code != 200:
            return []
        directives = [line.strip() for line in bounded_text(response).splitlines() if line.strip()][:100]
        if not directives:
            return []
        return [Finding(
            scanner_id=self.id, scanner_name=self.name, title="Public robots.txt discovered",
            severity=self.severity, confidence=1.0,
            description="A robots.txt file is publicly available. Directives are included for manual scope review.",
            evidence={**response_evidence(response), "observation": "robots_txt_available", "directives": directives},
            references=["https://www.rfc-editor.org/rfc/rfc9309"],
        )]

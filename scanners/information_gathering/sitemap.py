"""Passive sitemap discovery scanner."""

from __future__ import annotations

from xml.etree import ElementTree

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text, get, response_evidence, target_url


class SitemapScanner(Scanner):
    """Observe public sitemap URLs without crawling the listed pages."""

    id = "information.sitemap"
    name = "Sitemap Scanner"
    category = "information_gathering"
    description = "Retrieves a public sitemap index or URL set and records listed locations."
    severity = Severity.INFO
    tags = frozenset({"sitemap", "content-discovery", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Retrieve sitemap.xml and record a bounded list of declared URLs."""

        response = await get(context, target_url(context, "/sitemap.xml"))
        if response.status_code != 200:
            return []
        try:
            root = ElementTree.fromstring(bounded_text(response))
        except ElementTree.ParseError:
            return []
        locations = [element.text for element in root.iter() if element.tag.endswith("loc") and element.text][:100]
        if not locations:
            return []
        context.endpoints.extend(url for url in locations if url not in context.endpoints)
        return [Finding(
            scanner_id=self.id, scanner_name=self.name, title="Public sitemap discovered",
            severity=self.severity, confidence=1.0,
            description="A public sitemap contains URLs that may help define the authorized assessment scope.",
            evidence={**response_evidence(response), "observation": "sitemap_available", "url_count_observed": len(locations), "locations": locations},
            references=["https://www.sitemaps.org/protocol.html"],
        )]

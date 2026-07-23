"""Passive technology fingerprinting scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text, get, response_evidence


class TechnologyScanner(Scanner):
    """Identify technologies only from explicitly observed headers and markup markers."""

    id = "information.technologies"
    name = "Technology Fingerprint Scanner"
    category = "information_gathering"
    description = "Records technologies indicated by response headers and public HTML markers."
    severity = Severity.INFO
    tags = frozenset({"fingerprinting", "technologies", "passive"})
    enabled = True
    MARKERS = {
        "wp-content": "WordPress", "__next": "Next.js", "react": "React",
        "vue": "Vue.js", "laravel": "Laravel",
    }

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Collect observed technology indicators from one target response."""

        response = await get(context, context.target)
        observed: list[dict[str, str]] = []
        for header in ("server", "x-powered-by"):
            if value := response.headers.get(header):
                observed.append({"technology": value, "source": f"header:{header}"})
        body = bounded_text(response).lower()
        for marker, technology in self.MARKERS.items():
            if marker in body:
                observed.append({"technology": technology, "source": f"html-marker:{marker}"})
        technologies = list(dict.fromkeys(item["technology"] for item in observed))
        context.technologies.extend(item for item in technologies if item not in context.technologies)
        if not observed:
            return []
        return [Finding(
            scanner_id=self.id, scanner_name=self.name, title="Technology indicators observed",
            severity=self.severity, confidence=0.75,
            description="Public response headers or markup contain the listed technology indicators; they are not version confirmation.",
            evidence={**response_evidence(response), "observation": "technology_indicators", "indicators": observed},
            references=[],
        )]

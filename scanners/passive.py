"""Reusable passive scanner primitives for non-exploitative categories."""

from __future__ import annotations

from abc import ABC

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text, get, response_evidence, target_url


class PassiveMarkerScanner(Scanner, ABC):
    """Base scanner that reports explicitly observed public response markers."""

    markers: tuple[str, ...] = ()
    observation: str = "public_marker_observed"
    finding_title: str = "Public security-relevant marker observed"
    finding_description: str = "The response contains public markers that warrant authorized manual review."
    references: tuple[str, ...] = ()

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Fetch one response and report only configured literal marker matches."""

        response = await get(context, context.target)
        body = bounded_text(response).lower()
        matched = [marker for marker in self.markers if marker.lower() in body]
        if not matched:
            return []
        return [Finding(
            scanner_id=self.id, scanner_name=self.name, title=self.finding_title,
            severity=self.severity, confidence=0.75, description=self.finding_description,
            evidence={**response_evidence(response), "observation": self.observation, "matched_markers": matched},
            references=list(self.references),
        )]


class PublicDocumentScanner(Scanner, ABC):
    """Base scanner for bounded checks of public documentation resources."""

    paths: tuple[str, ...] = ()
    required_markers: tuple[str, ...] = ()
    observation: str = "public_document_observed"
    finding_title: str = "Public document observed"
    finding_description: str = "A public document was observed without invoking its linked operations."
    references: tuple[str, ...] = ()

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Fetch known public document paths and report only confirmed marker matches."""

        for path in self.paths:
            response = await get(context, target_url(context, path))
            if response.status_code != 200:
                continue
            body = bounded_text(response, 20_000).lower()
            if self.required_markers and not any(marker.lower() in body for marker in self.required_markers):
                continue
            return [Finding(
                scanner_id=self.id, scanner_name=self.name, title=self.finding_title,
                severity=self.severity, confidence=0.9, description=self.finding_description,
                evidence={**response_evidence(response), "observation": self.observation, "location": path},
                references=list(self.references),
            )]
        return []

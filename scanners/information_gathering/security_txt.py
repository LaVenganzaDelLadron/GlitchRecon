"""Passive security.txt discovery scanner."""

from __future__ import annotations

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text, get, response_evidence, target_url


class SecurityTxtScanner(Scanner):
    """Observe the RFC 9116 security contact policy when it is published."""

    id = "information.security_txt"
    name = "security.txt Scanner"
    category = "information_gathering"
    description = "Discovers a published security.txt policy or reports its absence."
    severity = Severity.INFO
    tags = frozenset({"security-txt", "disclosure", "passive"})
    enabled = True

    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Check standard security.txt locations without probing other paths."""

        attempts: list[dict[str, int | str]] = []
        for path in ("/.well-known/security.txt", "/security.txt"):
            response = await get(context, target_url(context, path))
            attempts.append({"location": path, "status_code": response.status_code})
            if response.status_code != 200:
                continue
            lines = [line.strip() for line in bounded_text(response).splitlines() if line.strip()][:100]
            return [Finding(
                scanner_id=self.id, scanner_name=self.name, title="Published security.txt discovered",
                severity=self.severity, confidence=1.0,
                description="The target publishes a security disclosure policy for researcher review.",
                evidence={**response_evidence(response), "observation": "security_txt_available", "policy_lines": lines},
                references=["https://www.rfc-editor.org/rfc/rfc9116"],
            )]
        all_not_found = all(attempt["status_code"] == 404 for attempt in attempts)
        return [Finding(
            scanner_id=self.id, scanner_name=self.name,
            title="security.txt not found" if all_not_found else "security.txt availability could not be confirmed",
            severity=Severity.LOW if all_not_found else Severity.INFO,
            confidence=0.9 if all_not_found else 0.5,
            description="Both standard security.txt locations returned HTTP 404." if all_not_found else "At least one standard security.txt location returned a response other than 200 or 404; manual review is required.",
            evidence={"observation": "security_txt_not_found" if all_not_found else "security_txt_inconclusive", "locations_checked": attempts},
            references=["https://www.rfc-editor.org/rfc/rfc9116"],
        )]

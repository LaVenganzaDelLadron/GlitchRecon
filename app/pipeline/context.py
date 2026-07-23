#app/pipeline/context
from dataclasses import dataclass, field
from typing import Any

from app.models.schemas import Finding

@dataclass
class PipelineContext:
    """Shared state across the scanning pipeline."""
    target: str
    valid: bool = False
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    technologies: list[str] = field(default_factory=list)
    endpoints: list[str] = field(default_factory=list)
    findings: list[Finding | dict[str, Any]] = field(default_factory=list)
    ai_summary: str | None = None
    errors: list[str] = field(default_factory=list)
    http_client: Any | None = field(default=None, repr=False)

    def add_finding(
        self,
        title: str,
        severity: str,
        description: str,
        evidence: dict[str, Any] | None = None,
        scanner_name: str = "unknown-scanner",
        scanner_id: str = "unknown-scanner",
        confidence: float = 0.5,
        references: list[str] | None = None,
    ) -> None:
        """Add scanner-produced evidence to the shared pipeline state."""

        self.findings.append(
            {
                "title": title,
                "scanner_id": scanner_id,
                "severity": severity,
                "description": description,
                "evidence": evidence or {},
                "scanner_name": scanner_name,
                "confidence": confidence,
                "references": references or [],
            }
        )

    def add_error(self, error: str) -> None:
        self.errors.append(error)

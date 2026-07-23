"""Abstract contract for evidence-producing scanner plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.exceptions import ScannerConfigurationError


SCANNER_CATEGORIES = frozenset(
    {
        "information_gathering", "authentication", "authorization", "injection",
        "api", "http", "client_side", "files", "server", "cloud", "cms",
        "misconfiguration", "secrets",
    }
)


class Scanner(ABC):
    """Base class for a passive, evidence-producing vulnerability scanner plugin."""

    id: str = ""
    name: str = ""
    category: str = ""
    description: str = ""
    severity: Severity = Severity.INFO
    tags: frozenset[str] = frozenset()
    enabled: bool = True

    def validate_configuration(self) -> None:
        """Validate plugin metadata before the scanner is registered or executed."""

        if not all(isinstance(value, str) and value.strip() for value in (self.id, self.name, self.category, self.description)):
            raise ScannerConfigurationError(f"{type(self).__name__} has incomplete scanner metadata")
        if self.category not in SCANNER_CATEGORIES:
            raise ScannerConfigurationError(f"{self.id} has unsupported category {self.category!r}")
        if not isinstance(self.severity, Severity):
            raise ScannerConfigurationError(f"{self.id} must use a Severity value")
        if not isinstance(self.tags, Collection) or any(not isinstance(tag, str) or not tag for tag in self.tags):
            raise ScannerConfigurationError(f"{self.id} has invalid tags")

    @abstractmethod
    async def scan(self, context: PipelineContext) -> list[Finding]:
        """Observe the target and return evidence-backed findings only."""

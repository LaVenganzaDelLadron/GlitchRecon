"""Discovery and registration of scanner plugins."""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from collections.abc import Iterable

from scanners.base import Scanner
from scanners.exceptions import ScannerConfigurationError

logger = logging.getLogger(__name__)


class ScannerRegistry:
    """Thread-safe-at-startup registry of configured scanner plugin instances."""

    def __init__(self) -> None:
        self._scanners: dict[str, Scanner] = {}

    def register(self, scanner: Scanner) -> None:
        """Register one uniquely identified, valid scanner instance."""

        scanner.validate_configuration()
        if scanner.id in self._scanners:
            raise ScannerConfigurationError(f"Scanner ID {scanner.id!r} is already registered")
        self._scanners[scanner.id] = scanner
        logger.debug("Registered scanner %s", scanner.id)

    def unregister(self, scanner_id: str) -> Scanner | None:
        """Remove and return a scanner by identifier."""

        return self._scanners.pop(scanner_id, None)

    def get_by_id(self, scanner_id: str) -> Scanner | None:
        """Return the registered scanner with the supplied identifier."""

        return self._scanners.get(scanner_id)

    def get_by_category(self, category: str) -> list[Scanner]:
        """Return scanners belonging to one category."""

        return [scanner for scanner in self._scanners.values() if scanner.category == category]

    def get_enabled(self) -> list[Scanner]:
        """Return all currently enabled scanners."""

        return [scanner for scanner in self._scanners.values() if scanner.enabled]

    def list(self) -> list[Scanner]:
        """Return every registered scanner in registration order."""

        return list(self._scanners.values())

    def discover(self, package_name: str = "scanners") -> list[str]:
        """Import scanner modules and register explicitly configured subclasses.

        A new plugin needs only to inherit :class:`Scanner` and declare the
        required class metadata. No central import list needs updating.
        """

        package = importlib.import_module(package_name)
        discovered: list[str] = []
        for module_info in pkgutil.walk_packages(package.__path__, f"{package.__name__}."):
            module = importlib.import_module(module_info.name)
            for _, scanner_type in inspect.getmembers(module, inspect.isclass):
                if scanner_type is Scanner or not issubclass(scanner_type, Scanner):
                    continue
                if scanner_type.__module__ != module.__name__ or "id" not in scanner_type.__dict__:
                    continue
                try:
                    scanner = scanner_type()
                    if self.get_by_id(scanner.id) is None:
                        self.register(scanner)
                        discovered.append(scanner.id)
                except ScannerConfigurationError as exc:
                    logger.warning("Skipped misconfigured scanner %s: %s", scanner_type.__name__, exc)
        logger.info("Discovered %d scanner plugin(s)", len(discovered))
        return discovered

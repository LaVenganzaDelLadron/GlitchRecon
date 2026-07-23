"""Scanner framework exception hierarchy."""

from __future__ import annotations


class ScannerError(Exception):
    """Base exception for all scanner framework errors."""


class ScannerTimeout(ScannerError):
    """Raised when a scanner exceeds its configured execution deadline."""


class ScannerConfigurationError(ScannerError):
    """Raised when scanner metadata or configuration is invalid."""


class ScannerExecutionError(ScannerError):
    """Raised when a scanner cannot complete its observation safely."""

"""Validated domain schemas for scan results and reports."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class Severity(str, Enum):
    """Supported normalized vulnerability severities."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanStatus(str, Enum):
    """Lifecycle states for a scan."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Finding(BaseModel):
    """Evidence produced by a scanner and optionally enriched by the AI."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    scanner_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=300)
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    description: str = Field(min_length=1)
    evidence: dict[str, Any] = Field(default_factory=dict)
    references: list[str] = Field(default_factory=list)
    remediation: str | None = None
    scanner_name: str = Field(min_length=1, max_length=120)
    timestamp: datetime = Field(default_factory=utc_now)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_aware(cls, value: datetime) -> datetime:
        """Normalize timestamps to UTC and reject naive values."""

        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone information")
        return value.astimezone(timezone.utc)


class Scan(BaseModel):
    """A complete scanner execution and its captured evidence."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    target: HttpUrl
    status: ScanStatus = ScanStatus.PENDING
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    findings: list[Finding] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Report(BaseModel):
    """AI-assisted but scanner-evidence-grounded report for a scan."""

    executive_summary: str = Field(min_length=1)
    risk_score: float = Field(ge=0.0, le=100.0)
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    ai_summary: str = Field(min_length=1)

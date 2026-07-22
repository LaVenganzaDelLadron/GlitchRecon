"""Persistence adapter for reports associated with scans."""

from __future__ import annotations

import asyncio

from app.models.schemas import Report


class ReportRepository:
    """Concurrency-safe in-memory report repository keyed by scan ID."""

    def __init__(self) -> None:
        self._items: dict[str, Report] = {}
        self._lock = asyncio.Lock()

    async def create(self, scan_id: str, entity: Report) -> Report:
        """Create the report for a scan."""

        async with self._lock:
            if scan_id in self._items:
                raise ValueError(f"Report for scan {scan_id} already exists")
            self._items[scan_id] = entity.model_copy(deep=True)
            return entity.model_copy(deep=True)

    async def update(self, scan_id: str, entity: Report) -> Report | None:
        """Replace the report for a scan."""

        async with self._lock:
            if scan_id not in self._items:
                return None
            self._items[scan_id] = entity.model_copy(deep=True)
            return entity.model_copy(deep=True)

    async def delete(self, scan_id: str) -> bool:
        """Delete a scan report."""

        async with self._lock:
            return self._items.pop(scan_id, None) is not None

    async def find_by_id(self, scan_id: str) -> Report | None:
        """Retrieve the report for a scan."""

        async with self._lock:
            item = self._items.get(scan_id)
            return item.model_copy(deep=True) if item else None

    async def list(self) -> list[Report]:
        """List reports."""

        async with self._lock:
            return [item.model_copy(deep=True) for item in self._items.values()]

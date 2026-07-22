"""Persistence adapter for scan records."""

from __future__ import annotations

import asyncio

from app.models.schemas import Scan
from repositories.base import Repository


class ScanRepository(Repository[Scan]):
    """Concurrency-safe in-memory scan repository.

    Replace this adapter with a database implementation without changing the
    services that consume the repository contract.
    """

    def __init__(self) -> None:
        self._items: dict[str, Scan] = {}
        self._lock = asyncio.Lock()

    async def create(self, entity: Scan) -> Scan:
        """Create a scan record."""

        async with self._lock:
            if entity.id in self._items:
                raise ValueError(f"Scan {entity.id} already exists")
            self._items[entity.id] = entity.model_copy(deep=True)
            return entity.model_copy(deep=True)

    async def update(self, entity_id: str, entity: Scan) -> Scan | None:
        """Update one scan record."""

        async with self._lock:
            if entity_id not in self._items:
                return None
            stored = entity.model_copy(update={"id": entity_id}, deep=True)
            self._items[entity_id] = stored
            return stored.model_copy(deep=True)

    async def delete(self, entity_id: str) -> bool:
        """Delete a scan record."""

        async with self._lock:
            return self._items.pop(entity_id, None) is not None

    async def find_by_id(self, entity_id: str) -> Scan | None:
        """Retrieve a scan record."""

        async with self._lock:
            item = self._items.get(entity_id)
            return item.model_copy(deep=True) if item else None

    async def list(self) -> list[Scan]:
        """List all scan records."""

        async with self._lock:
            return [item.model_copy(deep=True) for item in self._items.values()]

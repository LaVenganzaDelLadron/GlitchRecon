"""Persistence adapter for findings."""

from __future__ import annotations

import asyncio

from app.models.schemas import Finding
from repositories.base import Repository


class FindingRepository(Repository[Finding]):
    """Concurrency-safe in-memory repository for normalized findings."""

    def __init__(self) -> None:
        self._items: dict[str, Finding] = {}
        self._lock = asyncio.Lock()

    async def create(self, entity: Finding) -> Finding:
        """Create a finding."""

        async with self._lock:
            if entity.id in self._items:
                raise ValueError(f"Finding {entity.id} already exists")
            self._items[entity.id] = entity.model_copy(deep=True)
            return entity.model_copy(deep=True)

    async def update(self, entity_id: str, entity: Finding) -> Finding | None:
        """Update a finding."""

        async with self._lock:
            if entity_id not in self._items:
                return None
            stored = entity.model_copy(update={"id": entity_id}, deep=True)
            self._items[entity_id] = stored
            return stored.model_copy(deep=True)

    async def delete(self, entity_id: str) -> bool:
        """Delete a finding."""

        async with self._lock:
            return self._items.pop(entity_id, None) is not None

    async def find_by_id(self, entity_id: str) -> Finding | None:
        """Retrieve a finding."""

        async with self._lock:
            item = self._items.get(entity_id)
            return item.model_copy(deep=True) if item else None

    async def list(self) -> list[Finding]:
        """List findings."""

        async with self._lock:
            return [item.model_copy(deep=True) for item in self._items.values()]

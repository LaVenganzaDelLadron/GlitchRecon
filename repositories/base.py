"""Repository interfaces for persistence adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


ModelT = TypeVar("ModelT")


class Repository(ABC, Generic[ModelT]):
    """Minimal asynchronous CRUD contract implemented by repositories."""

    @abstractmethod
    async def create(self, entity: ModelT) -> ModelT:
        """Persist and return an entity."""

    @abstractmethod
    async def update(self, entity_id: str, entity: ModelT) -> ModelT | None:
        """Replace an existing entity, returning ``None`` when absent."""

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity and report whether it existed."""

    @abstractmethod
    async def find_by_id(self, entity_id: str) -> ModelT | None:
        """Retrieve an entity by identifier."""

    @abstractmethod
    async def list(self) -> list[ModelT]:
        """Return all entities."""

"""Atomic local JSON persistence for completed scan artifacts."""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

from app.models.schemas import ScanArtifact
from repositories.base import Repository

class JsonScanArtifactRepository(Repository[ScanArtifact]):
    """Store completed scan exports as timestamped JSON files with owner-only access."""

    def __init__(self, directory: Path | str = "reports") -> None:
        self._directory = Path(directory)
        self._lock = asyncio.Lock()

    async def create(self, entity: ScanArtifact) -> ScanArtifact:
        """Atomically write a new artifact for the entity's scan ID."""

        async with self._lock:
            if self._find_path_sync(entity.scan.id):
                raise ValueError(f"Artifact for scan {entity.scan.id} already exists")
            self._write_sync(entity)
            return entity.model_copy(deep=True)

    async def update(self, entity_id: str, entity: ScanArtifact) -> ScanArtifact | None:
        """Replace the existing artifact for a scan, retaining CRUD semantics."""

        async with self._lock:
            existing = self._find_path_sync(entity_id)
            if existing is None:
                return None
            existing.unlink()
            updated = entity.model_copy(update={"scan": entity.scan.model_copy(update={"id": entity_id})}, deep=True)
            self._write_sync(updated)
            return updated.model_copy(deep=True)

    async def delete(self, entity_id: str) -> bool:
        """Delete the artifact belonging to a scan ID."""

        async with self._lock:
            existing = self._find_path_sync(entity_id)
            if existing is None:
                return False
            existing.unlink()
            return True

    async def find_by_id(self, entity_id: str) -> ScanArtifact | None:
        """Load the artifact belonging to a scan ID."""

        async with self._lock:
            path = self._find_path_sync(entity_id)
            if path is None:
                return None
            return self._read_sync(path)

    async def list(self) -> list[ScanArtifact]:
        """Load all stored artifacts ordered by their timestamped filenames."""

        async with self._lock:
            paths = self._list_paths_sync()
            return [self._read_sync(path) for path in paths]

    def _write_sync(self, artifact: ScanArtifact) -> None:
        """Write one JSON artifact atomically with restrictive permissions."""

        self._directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        timestamp = artifact.stored_at.strftime("%Y%m%dT%H%M%S%fZ")
        destination = self._directory / f"{timestamp}_{artifact.scan.id}.json"
        descriptor, temporary_name = tempfile.mkstemp(prefix=".artifact-", suffix=".tmp", dir=self._directory)
        temporary_path = Path(temporary_name)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(artifact.model_dump_json(indent=2))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, destination)
            os.chmod(destination, 0o600)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

    def _find_path_sync(self, scan_id: str) -> Path | None:
        """Find the timestamped filename that belongs to one scan."""

        matches = sorted(self._directory.glob(f"*_{scan_id}.json")) if self._directory.exists() else []
        return matches[-1] if matches else None

    def _list_paths_sync(self) -> list[Path]:
        """Return timestamped artifact paths in chronological filename order."""

        if not self._directory.exists():
            return []
        return sorted(self._directory.glob("*.json"))

    @staticmethod
    def _read_sync(path: Path) -> ScanArtifact:
        """Parse one JSON artifact from disk."""

        return ScanArtifact.model_validate_json(path.read_text(encoding="utf-8"))

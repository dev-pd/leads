"""Storage backend interface over resume-file persistence."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class StoredObject:
    """What a backend returns when streaming a stored file back out."""

    data: bytes
    content_type: str
    filename: str


class StorageBackend(ABC):
    @abstractmethod
    def put(
        self, key: str, data: bytes, content_type: str, filename: str
    ) -> str:
        """Persist ``data`` under ``key``; return the canonical storage key."""

    @abstractmethod
    def get(self, key: str) -> StoredObject:
        """Fetch a previously stored object. Raises if the key is missing."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove an object. Idempotent — missing keys are a no-op."""

    @staticmethod
    def build_key(lead_id: str, filename: str) -> str:
        """Tenant-style, collision-free key layout: ``leads/{id}/resume.pdf``."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        return f"leads/{lead_id}/resume.{ext}"

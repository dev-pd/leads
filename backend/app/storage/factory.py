"""Resolve and cache the configured storage backend (singleton)."""
from functools import lru_cache

from app.config import settings
from app.storage.base import StorageBackend


@lru_cache
def get_storage() -> StorageBackend:
    if settings.storage_backend == "s3":
        from app.storage.s3 import S3Backend

        return S3Backend()
    from app.storage.local import LocalDiskBackend

    return LocalDiskBackend(settings.local_storage_dir)

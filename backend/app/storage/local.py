"""Local-disk storage backend (zero-infra default for dev/demo).

Content-type and original filename are persisted in a sidecar JSON so ``get``
can faithfully reconstruct the response.
"""
import json
from pathlib import Path

from app.core.errors import not_found
from app.core.logging_config import get_logger
from app.storage.base import StorageBackend, StoredObject

_log = get_logger("app.storage.local")


class LocalDiskBackend(StorageBackend):
    def __init__(self, root: str):
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self._root / key

    def put(self, key: str, data: bytes, content_type: str, filename: str) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.with_suffix(path.suffix + ".meta.json").write_text(
            json.dumps({"content_type": content_type, "filename": filename})
        )
        _log.info("stored_object", extra={"key": key, "bytes": len(data)})
        return key

    def get(self, key: str) -> StoredObject:
        path = self._path(key)
        if not path.exists():
            raise not_found("RESUME_NOT_FOUND", "Resume file not found")
        meta_path = path.with_suffix(path.suffix + ".meta.json")
        meta = (
            json.loads(meta_path.read_text())
            if meta_path.exists()
            else {"content_type": "application/octet-stream", "filename": path.name}
        )
        return StoredObject(
            data=path.read_bytes(),
            content_type=meta["content_type"],
            filename=meta["filename"],
        )

    def delete(self, key: str) -> None:
        path = self._path(key)
        path.unlink(missing_ok=True)
        path.with_suffix(path.suffix + ".meta.json").unlink(missing_ok=True)

"""Unit tests for the local storage backend and key layout."""
from app.storage.base import StorageBackend
from app.storage.local import LocalDiskBackend


def test_put_and_get_roundtrip(storage_dir):
    backend = LocalDiskBackend(str(storage_dir))
    key = StorageBackend.build_key("lead-123", "cv.pdf")
    backend.put(key, b"hello", "application/pdf", "cv.pdf")

    obj = backend.get(key)
    assert obj.data == b"hello"
    assert obj.content_type == "application/pdf"
    assert obj.filename == "cv.pdf"


def test_build_key_layout():
    key = StorageBackend.build_key("abc", "My Resume.PDF")
    assert key == "leads/abc/resume.pdf"


def test_get_missing_raises(storage_dir):
    backend = LocalDiskBackend(str(storage_dir))
    try:
        backend.get("leads/none/resume.pdf")
        raise AssertionError("expected not_found")
    except Exception as exc:  # AppError
        assert getattr(exc, "code", None) == "RESUME_NOT_FOUND"


def test_delete_is_idempotent(storage_dir):
    backend = LocalDiskBackend(str(storage_dir))
    key = StorageBackend.build_key("x", "r.pdf")
    backend.put(key, b"x", "application/pdf", "r.pdf")
    backend.delete(key)
    backend.delete(key)  # no error on second delete

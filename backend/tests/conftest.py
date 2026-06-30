"""Pytest fixtures: isolated SQLite DB, temp storage, stubbed email, auth token.

Tests never touch Postgres, MinIO, or Resend — the corresponding dependencies
are overridden so the suite is fast, hermetic, and safe to run offline.
"""
import os

# Required settings have no defaults in production code; provide test values
# before importing the app (which instantiates Settings at import time).
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("ATTORNEY_EMAIL", "attorney@example.com")
os.environ.setdefault("ATTORNEY_PASSWORD", "secret123")
os.environ.setdefault("ATTORNEY_NAME", "Test Attorney")

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import routes
from app.core.security import create_access_token, hash_password
from app.db import Base, get_db
from app.main import app
from app.models.user import User
from app.storage import get_storage
from app.storage.local import LocalDiskBackend


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def storage_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture()
def attorney(db_session):
    user = User(
        email="attorney@example.com",
        name="Test Attorney",
        password_hash=hash_password("secret123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(attorney):
    token = create_access_token(subject=attorney.id, extra={"email": attorney.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sent_emails(monkeypatch):
    """Capture email payloads instead of sending them."""
    calls: list[dict] = []

    def _record(**kwargs):
        calls.append(kwargs)

    # The route imports the function into its own namespace.
    monkeypatch.setattr(routes.leads, "send_lead_emails", _record)
    return calls


@pytest.fixture()
def client(db_session, storage_dir, sent_emails):
    storage = LocalDiskBackend(str(storage_dir))
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def pdf_bytes() -> bytes:
    return b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF"

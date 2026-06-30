"""Shared FastAPI dependencies: DB session, storage, and the auth guard."""
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import unauthorized
from app.core.security import decode_access_token
from app.db import get_db
from app.models.user import User
from app.schemas.auth import CurrentUser
from app.storage import StorageBackend, get_storage

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]
Storage = Annotated[StorageBackend, Depends(get_storage)]


def require_attorney(
    db: DbSession,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> CurrentUser:
    if creds is None or not creds.credentials:
        raise unauthorized("MISSING_TOKEN", "Authorization token required")
    payload = decode_access_token(creds.credentials)
    user_id = payload.get("sub")
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise unauthorized("INVALID_TOKEN", "User no longer exists")
    return CurrentUser(id=user.id, email=user.email, name=user.name)


CurrentAttorney = Annotated[CurrentUser, Depends(require_attorney)]

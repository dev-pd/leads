"""Shared FastAPI dependencies: DB session, storage, repositories, auth guard."""
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import unauthorized
from app.core.security import decode_access_token
from app.db import get_db
from app.repositories.leads import LeadRepository
from app.repositories.users import UserRepository
from app.schemas.auth import CurrentUser
from app.storage import StorageBackend, get_storage

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]
Storage = Annotated[StorageBackend, Depends(get_storage)]


def get_lead_repository(db: DbSession) -> LeadRepository:
    return LeadRepository(db)


def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepository(db)


LeadRepo = Annotated[LeadRepository, Depends(get_lead_repository)]
UserRepo = Annotated[UserRepository, Depends(get_user_repository)]


def require_attorney(
    users: UserRepo,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> CurrentUser:
    if creds is None or not creds.credentials:
        raise unauthorized("MISSING_TOKEN", "Authorization token required")
    payload = decode_access_token(creds.credentials)
    user_id = payload.get("sub")
    user = users.get(user_id) if user_id else None
    if user is None:
        raise unauthorized("INVALID_TOKEN", "User no longer exists")
    return CurrentUser(id=user.id, email=user.email, name=user.name)


CurrentAttorney = Annotated[CurrentUser, Depends(require_attorney)]

"""Auth routes: attorney login + current-user lookup."""
from fastapi import APIRouter

from app.api.deps import CurrentAttorney, DbSession
from app.core.errors import unauthorized
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import CurrentUser, LoginRequest, TokenResponse
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: DbSession) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == body.email))
    # Constant-ish response: same error whether email or password is wrong.
    if user is None or not verify_password(body.password, user.password_hash):
        raise unauthorized("INVALID_CREDENTIALS", "Invalid email or password")
    token = create_access_token(subject=user.id, extra={"email": user.email})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUser)
def me(current: CurrentAttorney) -> CurrentUser:
    return current

"""Auth routes: attorney login + current-user lookup."""
from fastapi import APIRouter

from app.api.deps import CurrentAttorney, UserRepo
from app.core.errors import unauthorized
from app.core.security import create_access_token, verify_password
from app.schemas.auth import CurrentUser, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, users: UserRepo) -> TokenResponse:
    user = users.get_by_email(body.email)
    # Product choice: distinct messages for unknown-email vs wrong-password so the
    # attorney gets clear feedback. This permits email enumeration, which is an
    # acceptable tradeoff for a single-account internal tool.
    if user is None:
        raise unauthorized("USER_NOT_FOUND", "No account found for this email")
    if not verify_password(body.password, user.password_hash):
        raise unauthorized("INVALID_PASSWORD", "Incorrect password")
    token = create_access_token(subject=user.id, extra={"email": user.email})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUser)
def me(current: CurrentAttorney) -> CurrentUser:
    return current

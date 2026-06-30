"""Seed the single internal attorney account from environment settings.

Idempotent: re-running updates the existing account rather than duplicating it.
"""
from sqlalchemy import select

from app.config import settings
from app.core.logging_config import configure_logging, get_logger
from app.core.security import hash_password
from app.db import SessionLocal
from app.models.user import User

_log = get_logger("app.seed")


def seed_attorney() -> None:
    configure_logging()
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == settings.attorney_email))
        if user is None:
            user = User(
                email=settings.attorney_email,
                name=settings.attorney_name,
                password_hash=hash_password(settings.attorney_password),
            )
            db.add(user)
            _log.info("attorney_created", extra={"email": settings.attorney_email})
        else:
            user.name = settings.attorney_name
            user.password_hash = hash_password(settings.attorney_password)
            _log.info("attorney_updated", extra={"email": settings.attorney_email})
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_attorney()

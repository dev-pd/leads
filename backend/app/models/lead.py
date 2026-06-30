"""Lead model — a prospect intake submission with a workflow state."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class LeadState(str, enum.Enum):
    """Lead lifecycle. Starts PENDING, attorney moves it to REACHED_OUT."""

    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"


def _uuid() -> str:
    return str(uuid.uuid4())


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(320), nullable=False, unique=True, index=True
    )

    # Storage key (not the bytes). Resolved by the active storage backend.
    resume_key: Mapped[str] = mapped_column(String(512), nullable=False)
    resume_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_content_type: Mapped[str] = mapped_column(String(127), nullable=False)

    state: Mapped[LeadState] = mapped_column(
        Enum(LeadState, name="lead_state"),
        nullable=False,
        default=LeadState.PENDING,
        server_default=LeadState.PENDING.value,
        index=True,
    )

    # Set when the lead transitions to REACHED_OUT — powers the activity trail.
    reached_out_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Parsed resume text (pypdf) + AI analysis, filled async on submit.
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_score: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True
    )
    profile_rating: Mapped[str | None] = mapped_column(
        String(16), nullable=True, index=True
    )
    profile_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

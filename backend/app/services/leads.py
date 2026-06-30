"""Lead business logic: creation (store + persist), listing, state transitions.

Routes stay thin — all domain rules (valid state transitions, file storage
orchestration) live here.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import bad_request, conflict, not_found
from app.core.logging_config import get_logger
from app.models.lead import Lead, LeadState
from app.storage import StorageBackend, StoredObject

_log = get_logger("app.leads")

# Allowed state transitions. Single source of truth for the workflow.
_TRANSITIONS: dict[LeadState, set[LeadState]] = {
    LeadState.PENDING: {LeadState.REACHED_OUT},
    LeadState.REACHED_OUT: set(),
}


def create_lead(
    db: Session,
    storage: StorageBackend,
    *,
    first_name: str,
    last_name: str,
    email: str,
    resume_bytes: bytes,
    resume_filename: str,
    resume_content_type: str,
) -> Lead:
    """Persist a lead and its resume atomically (DB row first, then file).

    Prospect email is unique — a second submission with the same email is
    rejected rather than creating a duplicate lead.
    """
    existing = db.scalar(select(Lead).where(Lead.email == email))
    if existing is not None:
        raise conflict(
            "DUPLICATE_LEAD",
            "A lead with this email already exists",
        )

    lead = Lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_filename=resume_filename,
        resume_content_type=resume_content_type,
        resume_key="",  # set after we know the id
    )
    db.add(lead)
    db.flush()  # assigns lead.id without committing

    key = StorageBackend.build_key(lead.id, resume_filename)
    storage.put(key, resume_bytes, resume_content_type, resume_filename)
    lead.resume_key = key

    db.commit()
    db.refresh(lead)
    _log.info("lead_created", extra={"lead_id": lead.id, "email": email})
    return lead


def list_leads(db: Session) -> tuple[list[Lead], int]:
    items = list(db.scalars(select(Lead).order_by(Lead.created_at.desc())))
    total = db.scalar(select(func.count()).select_from(Lead)) or 0
    return items, total


def get_lead(db: Session, lead_id: str) -> Lead:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise not_found("LEAD_NOT_FOUND", "Lead not found")
    return lead


def update_lead_state(db: Session, lead_id: str, new_state: LeadState) -> Lead:
    lead = get_lead(db, lead_id)
    if new_state == lead.state:
        return lead  # idempotent no-op
    if new_state not in _TRANSITIONS[lead.state]:
        raise bad_request(
            "INVALID_STATE_TRANSITION",
            f"Cannot move lead from {lead.state.value} to {new_state.value}",
        )
    lead.state = new_state
    db.commit()
    db.refresh(lead)
    _log.info(
        "lead_state_changed",
        extra={"lead_id": lead.id, "state": new_state.value},
    )
    return lead


def get_resume(db: Session, storage: StorageBackend, lead_id: str) -> StoredObject:
    lead = get_lead(db, lead_id)
    return storage.get(lead.resume_key)

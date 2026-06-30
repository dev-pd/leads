"""Lead business logic: creation, listing, and state transitions.

Holds the domain rules (uniqueness, valid state transitions, storage
orchestration) and delegates all persistence to the LeadRepository.
"""
from datetime import UTC, datetime

from app.core.errors import bad_request, conflict, not_found
from app.core.logging_config import get_logger
from app.models.lead import Lead, LeadState
from app.repositories.leads import LeadRepository
from app.storage import StorageBackend, StoredObject

_log = get_logger("app.leads")

# Single source of truth for the PENDING -> REACHED_OUT workflow.
_TRANSITIONS: dict[LeadState, set[LeadState]] = {
    LeadState.PENDING: {LeadState.REACHED_OUT},
    LeadState.REACHED_OUT: set(),
}


def create_lead(
    leads: LeadRepository,
    storage: StorageBackend,
    *,
    first_name: str,
    last_name: str,
    email: str,
    resume_bytes: bytes,
    resume_filename: str,
    resume_content_type: str,
) -> Lead:
    """Persist a lead and its resume (DB row first to get an id, then the file).

    Prospect email is unique — a duplicate submission is rejected.
    """
    if leads.get_by_email(email) is not None:
        raise conflict("DUPLICATE_LEAD", "A lead with this email already exists")

    lead = Lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_filename=resume_filename,
        resume_content_type=resume_content_type,
        resume_key="",  # set after the flush assigns an id
    )
    leads.add(lead)

    key = StorageBackend.build_key(lead.id, resume_filename)
    storage.put(key, resume_bytes, resume_content_type, resume_filename)
    lead.resume_key = key

    leads.commit(lead)
    _log.info("lead_created", extra={"lead_id": lead.id, "email": email})
    return lead


def list_leads(
    leads: LeadRepository,
    *,
    limit: int | None = None,
    offset: int = 0,
    rating: str | None = None,
    sort: str = "recent",
) -> tuple[list[Lead], int]:
    items = leads.list(limit=limit, offset=offset, rating=rating, sort=sort)
    return items, leads.count(rating=rating)


def get_stats(leads: LeadRepository) -> dict[str, int]:
    counts = leads.state_counts()
    pending = counts.get(LeadState.PENDING.value, 0)
    reached_out = counts.get(LeadState.REACHED_OUT.value, 0)
    return {
        "total": pending + reached_out,
        "pending": pending,
        "reached_out": reached_out,
    }


def get_lead(leads: LeadRepository, lead_id: str) -> Lead:
    lead = leads.get(lead_id)
    if lead is None:
        raise not_found("LEAD_NOT_FOUND", "Lead not found")
    return lead


def update_lead_state(
    leads: LeadRepository, lead_id: str, new_state: LeadState
) -> Lead:
    lead = get_lead(leads, lead_id)
    if new_state == lead.state:
        return lead  # idempotent no-op
    if new_state not in _TRANSITIONS[lead.state]:
        raise bad_request(
            "INVALID_STATE_TRANSITION",
            f"Cannot move lead from {lead.state.value} to {new_state.value}",
        )
    lead.state = new_state
    if new_state == LeadState.REACHED_OUT:
        lead.reached_out_at = datetime.now(UTC)
    leads.commit(lead)
    _log.info("lead_state_changed", extra={"lead_id": lead.id, "state": new_state.value})
    return lead


def get_resume(
    leads: LeadRepository, storage: StorageBackend, lead_id: str
) -> StoredObject:
    lead = get_lead(leads, lead_id)
    return storage.get(lead.resume_key)

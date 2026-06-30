"""Lead routes.

Public:
  POST   /api/leads                 submit intake form + resume (multipart)

Attorney-only (Bearer JWT):
  GET    /api/leads                 list all leads
  GET    /api/leads/{id}            lead detail
  PATCH  /api/leads/{id}            transition state (PENDING -> REACHED_OUT)
  GET    /api/leads/{id}/resume     stream the stored resume
"""
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, File, Form, Query, Response, UploadFile
from pydantic import EmailStr
from starlette.concurrency import run_in_threadpool

from app.api.deps import CurrentAttorney, LeadRepo, Storage
from app.config import settings
from app.core.errors import bad_request
from app.schemas.lead import LeadList, LeadOut, LeadStateUpdate, LeadStats
from app.services import leads as lead_service
from app.services.email import send_lead_emails
from app.services.resume_ai import generate_and_store_summary

router = APIRouter(prefix="/leads", tags=["leads"])


def _validate_resume(file: UploadFile, data: bytes) -> None:
    if not data:
        raise bad_request("EMPTY_FILE", "Resume file is empty")
    if len(data) > settings.max_upload_bytes:
        raise bad_request(
            "FILE_TOO_LARGE",
            f"Resume exceeds {settings.max_upload_mb}MB limit",
        )
    if file.content_type not in settings.allowed_resume_types_list:
        raise bad_request(
            "UNSUPPORTED_FILE_TYPE",
            f"Resume must be one of: {', '.join(settings.allowed_resume_types_list)}",
        )


@router.post("", response_model=LeadOut, status_code=201)
async def create_lead(
    leads: LeadRepo,
    storage: Storage,
    background: BackgroundTasks,
    first_name: str = Form(..., min_length=1, max_length=120),
    last_name: str = Form(..., min_length=1, max_length=120),
    email: EmailStr = Form(...),
    resume: UploadFile = File(...),
) -> LeadOut:
    """Public endpoint — no auth. Stores the lead, then emails async."""
    data = await resume.read()
    _validate_resume(resume, data)

    # Offload the synchronous DB + storage work to a threadpool so it never
    # blocks the event loop.
    lead = await run_in_threadpool(
        lead_service.create_lead,
        leads,
        storage,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email.strip().lower(),
        resume_bytes=data,
        resume_filename=resume.filename or "resume.pdf",
        resume_content_type=resume.content_type or "application/pdf",
    )

    # Fire-and-forget: never block the response or fail the submission on email.
    background.add_task(
        send_lead_emails,
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
    )
    # Generate the AI resume profile out of band (Anthropic API call).
    background.add_task(
        generate_and_store_summary,
        lead.id,
        data,
        resume.content_type or "application/pdf",
    )
    return LeadOut.model_validate(lead)


@router.get("", response_model=LeadList)
def list_leads(
    leads: LeadRepo,
    _: CurrentAttorney,
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    rating: Literal["strong", "moderate", "weak"] | None = Query(default=None),
    sort: Literal["recent", "score"] = Query(default="recent"),
) -> LeadList:
    items, total = lead_service.list_leads(
        leads, limit=limit, offset=offset, rating=rating, sort=sort
    )
    return LeadList(items=[LeadOut.model_validate(i) for i in items], total=total)


@router.get("/stats", response_model=LeadStats)
def lead_stats(leads: LeadRepo, _: CurrentAttorney) -> LeadStats:
    return LeadStats(**lead_service.get_stats(leads))


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str, leads: LeadRepo, _: CurrentAttorney) -> LeadOut:
    return LeadOut.model_validate(lead_service.get_lead(leads, lead_id))


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: str, body: LeadStateUpdate, leads: LeadRepo, _: CurrentAttorney
) -> LeadOut:
    lead = lead_service.update_lead_state(leads, lead_id, body.state)
    return LeadOut.model_validate(lead)


@router.get("/{lead_id}/resume")
def download_resume(
    lead_id: str, leads: LeadRepo, storage: Storage, _: CurrentAttorney
) -> Response:
    obj = lead_service.get_resume(leads, storage, lead_id)
    return Response(
        content=obj.data,
        media_type=obj.content_type,
        headers={
            "Content-Disposition": f'inline; filename="{obj.filename}"',
        },
    )

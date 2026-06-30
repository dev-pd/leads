"""Lead routes.

Public:
  POST   /api/leads                 submit intake form + resume (multipart)

Attorney-only (Bearer JWT):
  GET    /api/leads                 list all leads
  GET    /api/leads/{id}            lead detail
  PATCH  /api/leads/{id}            transition state (PENDING -> REACHED_OUT)
  GET    /api/leads/{id}/resume     stream the stored resume
"""
from fastapi import APIRouter, BackgroundTasks, File, Form, Response, UploadFile
from pydantic import EmailStr

from app.api.deps import CurrentAttorney, DbSession, Storage
from app.config import settings
from app.core.errors import bad_request
from app.schemas.lead import LeadList, LeadOut, LeadStateUpdate
from app.services import leads as lead_service
from app.services.email import send_lead_emails

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
    db: DbSession,
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

    lead = lead_service.create_lead(
        db,
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
    return LeadOut.model_validate(lead)


@router.get("", response_model=LeadList)
def list_leads(db: DbSession, _: CurrentAttorney) -> LeadList:
    items, total = lead_service.list_leads(db)
    return LeadList(items=[LeadOut.model_validate(i) for i in items], total=total)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str, db: DbSession, _: CurrentAttorney) -> LeadOut:
    return LeadOut.model_validate(lead_service.get_lead(db, lead_id))


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: str, body: LeadStateUpdate, db: DbSession, _: CurrentAttorney
) -> LeadOut:
    lead = lead_service.update_lead_state(db, lead_id, body.state)
    return LeadOut.model_validate(lead)


@router.get("/{lead_id}/resume")
def download_resume(lead_id: str, db: DbSession, storage: Storage, _: CurrentAttorney):
    obj = lead_service.get_resume(db, storage, lead_id)
    return Response(
        content=obj.data,
        media_type=obj.content_type,
        headers={
            "Content-Disposition": f'inline; filename="{obj.filename}"',
        },
    )

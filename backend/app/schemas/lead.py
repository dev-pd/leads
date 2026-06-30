"""Pydantic request/response schemas for leads."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.lead import LeadState


class LeadCreate(BaseModel):
    """Public intake fields. The resume arrives as a multipart file, not here."""

    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    resume_filename: str
    resume_content_type: str
    state: LeadState
    created_at: datetime
    updated_at: datetime


class LeadStateUpdate(BaseModel):
    state: LeadState


class LeadList(BaseModel):
    items: list[LeadOut]
    total: int

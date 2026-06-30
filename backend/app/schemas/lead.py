"""Pydantic request/response schemas for leads."""
import json
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.lead import LeadState


class LeadCreate(BaseModel):
    """Public intake fields. The resume arrives as a multipart file, not here."""

    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class ProfileAssessment(BaseModel):
    rationale: str = ""
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    most_recent_role: str = ""
    years_experience: int | None = None
    education: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    resume_filename: str
    resume_content_type: str
    state: LeadState
    reached_out_at: datetime | None
    resume_summary: str | None
    profile_score: int | None
    profile_rating: str | None
    profile_assessment: ProfileAssessment | None
    created_at: datetime
    updated_at: datetime

    @field_validator("profile_assessment", mode="before")
    @classmethod
    def _parse_assessment(cls, v):
        # Stored as a JSON string on the ORM row; parse to the nested model.
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class LeadStateUpdate(BaseModel):
    state: LeadState


class LeadList(BaseModel):
    items: list[LeadOut]
    total: int


class LeadStats(BaseModel):
    total: int
    pending: int
    reached_out: int

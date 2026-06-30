"""Resume analysis via the Anthropic API.

Pipeline: pypdf extracts the resume text (cheap, deterministic) -> we store it
-> the text is sent to the Messages API, where Claude does the understanding:
it returns a JSON assessment (profile, fit score, rating, strengths/concerns,
and structured details) so the attorney can quickly triage prospects.

If text extraction yields almost nothing (e.g. a scanned image with no text
layer) we fall back to sending the PDF itself as a base64 ``document`` block,
which Claude reads via vision.

Backward compatibility: the request uses only ``model`` / ``max_tokens`` /
``messages`` (no model-specific params like thinking or sampling), so it works
across every Claude model. The response is parsed defensively, so prompt or
model changes never break the flow.
"""
import base64
import io
import json
import re
from dataclasses import dataclass

import anthropic
from pypdf import PdfReader

from app.config import settings
from app.core.logging_config import get_logger
from app.db import SessionLocal
from app.prompts import RESUME_ASSESSMENT_PROMPT
from app.repositories.leads import LeadRepository

_log = get_logger("app.resume_ai")

_RATINGS = {"strong", "moderate", "weak"}
# Below this many characters we treat extraction as failed (likely a scan).
_MIN_TEXT_CHARS = 40


def extract_text(pdf_bytes: bytes) -> str:
    """Extract plain text from a PDF with pypdf. Returns '' on failure."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception:  # noqa: BLE001 — fall back to sending the PDF itself
        _log.exception("resume_text_extraction_failed")
        return ""


@dataclass(frozen=True)
class ResumeAssessment:
    summary: str
    score: int
    rating: str
    rationale: str
    strengths: list[str]
    concerns: list[str]
    most_recent_role: str
    years_experience: int | None
    education: list[str]
    skills: list[str]


def _str_list(value: object, cap: int = 4) -> list[str]:
    return [str(x) for x in value][:cap] if isinstance(value, list) else []


def _opt_int(value: object) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _coerce(raw: dict) -> ResumeAssessment:
    """Normalize the model's JSON into a validated assessment."""
    score = max(0, min(100, int(raw.get("score", 0))))
    rating = str(raw.get("rating", "")).lower().strip()
    if rating not in _RATINGS:
        rating = "strong" if score >= 70 else "moderate" if score >= 40 else "weak"
    return ResumeAssessment(
        summary=str(raw.get("summary", "")).strip(),
        score=score,
        rating=rating,
        rationale=str(raw.get("rationale", "")).strip(),
        strengths=_str_list(raw.get("strengths")),
        concerns=_str_list(raw.get("concerns"), cap=3),
        most_recent_role=str(raw.get("most_recent_role", "")).strip(),
        years_experience=_opt_int(raw.get("years_experience")),
        education=_str_list(raw.get("education"), cap=6),
        skills=_str_list(raw.get("skills"), cap=8),
    )


def _resume_content_block(
    resume_text: str, pdf_bytes: bytes, content_type: str
) -> dict:
    """Prefer the extracted text; fall back to the PDF for scanned resumes."""
    if len(resume_text) >= _MIN_TEXT_CHARS:
        return {"type": "text", "text": f"Resume text:\n\n{resume_text}"}
    encoded = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    return {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": content_type or "application/pdf",
            "data": encoded,
        },
    }


def assess_resume(
    resume_text: str, pdf_bytes: bytes, content_type: str
) -> ResumeAssessment | None:
    """Call Claude and return a parsed assessment, or None if disabled/failed."""
    if not settings.anthropic_api_key:
        _log.warning("resume_assessment_skipped_no_api_key")
        return None
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            # Disable thinking: this is a structured-extraction task, not
            # reasoning. On models that default thinking on (e.g. Sonnet 5) it
            # otherwise adds latency and can consume max_tokens before the JSON.
            thinking={"type": "disabled"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        _resume_content_block(resume_text, pdf_bytes, content_type),
                        {"type": "text", "text": RESUME_ASSESSMENT_PROMPT},
                    ],
                }
            ],
        )
        text = "".join(b.text for b in message.content if b.type == "text")
        # Defensive: pull the first {...} block in case the model adds prose.
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            _log.warning("resume_assessment_no_json")
            return None
        assessment = _coerce(json.loads(match.group(0)))
        _log.info(
            "resume_assessment_generated",
            extra={"score": assessment.score, "rating": assessment.rating},
        )
        return assessment
    except Exception:  # noqa: BLE001 — analysis is optional, never fail the flow
        _log.exception("resume_assessment_failed")
        return None


def generate_and_store_summary(
    lead_id: str, pdf_bytes: bytes, content_type: str
) -> None:
    """Background task: parse the resume, assess it, and persist on the lead."""
    resume_text = extract_text(pdf_bytes)
    assessment = assess_resume(resume_text, pdf_bytes, content_type)
    if assessment is None and not resume_text:
        return
    db = SessionLocal()
    try:
        leads = LeadRepository(db)
        lead = leads.get(lead_id)
        if lead is None:
            return
        if resume_text:
            lead.resume_text = resume_text
        if assessment is not None:
            lead.resume_summary = assessment.summary
            lead.profile_score = assessment.score
            lead.profile_rating = assessment.rating
            lead.profile_assessment = json.dumps(
                {
                    "rationale": assessment.rationale,
                    "strengths": assessment.strengths,
                    "concerns": assessment.concerns,
                    "most_recent_role": assessment.most_recent_role,
                    "years_experience": assessment.years_experience,
                    "education": assessment.education,
                    "skills": assessment.skills,
                }
            )
        leads.commit(lead)
    finally:
        db.close()

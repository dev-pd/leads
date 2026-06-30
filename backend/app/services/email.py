"""Email delivery via Resend.

Two transactional emails fire when a lead is submitted:
  1. prospect confirmation  ("we received your application")
  2. attorney notification   ("a new lead came in")

Design notes:
  * Sends are best-effort and never block or fail the lead submission — they run
    in a FastAPI BackgroundTask and swallow/log their own errors.
  * If ``RESEND_API_KEY`` is unset the payload is logged instead of sent, so the
    app is fully runnable without credentials. With the key set, mail is real.
  * Templates are small inline HTML with explicit escaping of user input.
"""
from html import escape

import resend

from app.config import settings
from app.core.logging_config import get_logger

_log = get_logger("app.email")


def _send(to: str, subject: str, html: str) -> None:
    """Low-level send. Logs on every path; raises nothing to callers' detriment."""
    if not settings.resend_api_key:
        _log.warning(
            "email_skipped_no_api_key",
            extra={"to": to, "subject": subject},
        )
        return
    try:
        resend.api_key = settings.resend_api_key
        result = resend.Emails.send(
            {
                "from": settings.email_from,
                "to": [to],
                "subject": subject,
                "html": html,
            }
        )
        _log.info(
            "email_sent",
            extra={"to": to, "subject": subject, "id": result.get("id")},
        )
    except Exception:  # noqa: BLE001 — email must never break the request flow
        _log.exception("email_failed", extra={"to": to, "subject": subject})


def send_prospect_confirmation(
    *, to: str, first_name: str
) -> None:
    name = escape(first_name)
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:auto">
      <h2>Application received</h2>
      <p>Hi {name},</p>
      <p>Thanks for submitting your information. Our team has received your
         application and resume. An attorney will review it and reach out to
         you shortly.</p>
      <p>— The Legal Team</p>
    </div>
    """
    _send(to=to, subject="We received your application", html=html)


def send_attorney_notification(
    *, first_name: str, last_name: str, prospect_email: str
) -> None:
    name = escape(f"{first_name} {last_name}")
    prospect = escape(prospect_email)
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:auto">
      <h2>New lead submitted</h2>
      <p>A new prospect has submitted the intake form.</p>
      <ul>
        <li><strong>Name:</strong> {name}</li>
        <li><strong>Email:</strong> {prospect}</li>
      </ul>
      <p>Open the internal dashboard to review the resume and mark the lead as
         reached out.</p>
    </div>
    """
    _send(
        to=settings.notify_attorney_email,
        subject=f"New lead: {name}",
        html=html,
    )


def send_lead_emails(
    *, first_name: str, last_name: str, email: str
) -> None:
    """Fire both transactional emails. Intended to run as a BackgroundTask."""
    send_prospect_confirmation(to=email, first_name=first_name)
    send_attorney_notification(
        first_name=first_name,
        last_name=last_name,
        prospect_email=email,
    )

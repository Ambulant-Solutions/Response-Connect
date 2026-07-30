from __future__ import annotations

from typing import Any

from app.blueprints.email.services import send_email
from app.blueprints.jobs.models import Job, JobType
from app.blueprints.jobs.registry import register_handler


@register_handler(JobType.EMAIL_SEND)
def handle_send_email(job: Job) -> dict[str, Any]:
    """Send an email described by an EMAIL_SEND job payload."""

    payload = job.payload or {}

    required_fields = (
        "to",
        "subject",
        "text_body",
    )

    missing_fields = [
        field
        for field in required_fields
        if not payload.get(field)
    ]

    if missing_fields:
        raise ValueError(
            "Email job payload is missing required fields: "
            + ", ".join(missing_fields)
        )

    return send_email(
        to=payload["to"],
        subject=payload["subject"],
        text_body=payload["text_body"],
        html_body=payload.get("html_body"),
        cc=payload.get("cc"),
        bcc=payload.get("bcc"),
        reply_to=payload.get("reply_to"),
        sender=payload.get("sender"),
    )
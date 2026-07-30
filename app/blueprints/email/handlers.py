from __future__ import annotations

from typing import Any

from app.blueprints.email.services import send_email
from app.blueprints.email.templates import render_email_template
from app.blueprints.jobs.models import Job, JobType
from app.blueprints.jobs.registry import register_handler


@register_handler(JobType.EMAIL_SEND)
def handle_send_email(job: Job) -> dict[str, Any]:
    """Send an email described by an EMAIL_SEND job payload."""

    payload = job.payload or {}

    if not payload.get("to"):
        raise ValueError(
            "Email job payload is missing required field: to"
        )

    template_name = payload.get("template_name")

    if template_name:
        rendered = render_email_template(
            template_name=template_name,
            context=payload.get("context") or {},
        )

        subject = rendered.subject
        text_body = rendered.text_body
        html_body = rendered.html_body
    else:
        missing_fields = [
            field
            for field in ("subject", "text_body")
            if not payload.get(field)
        ]

        if missing_fields:
            raise ValueError(
                "Email job payload is missing required fields: "
                + ", ".join(missing_fields)
            )

        subject = payload["subject"]
        text_body = payload["text_body"]
        html_body = payload.get("html_body")

    return send_email(
        to=payload["to"],
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        cc=payload.get("cc"),
        bcc=payload.get("bcc"),
        reply_to=payload.get("reply_to"),
        sender=payload.get("sender"),
    )
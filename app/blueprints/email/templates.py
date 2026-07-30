from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from flask import current_app, render_template
from jinja2 import TemplateNotFound


_TEMPLATE_NAME_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9_/-]*$"
)


class EmailTemplateError(RuntimeError):
    """Raised when an email template cannot be rendered."""


@dataclass(frozen=True)
class RenderedEmail:
    """The rendered components of an outgoing email."""

    subject: str
    text_body: str
    html_body: str


def render_email_template(
    template_name: str,
    context: dict[str, Any] | None = None,
) -> RenderedEmail:
    """
    Render the subject, plain-text body, and HTML body for an email.

    Example template name:
        auth/password_reset

    Corresponding files:
        email/auth/password_reset/subject.txt
        email/auth/password_reset/body.txt
        email/auth/password_reset/body.html
    """

    template_name = template_name.strip()

    if not _TEMPLATE_NAME_PATTERN.fullmatch(template_name):
        raise EmailTemplateError(
            f"Invalid email template name: {template_name!r}"
        )

    template_context = {
        **_get_global_template_context(),
        **(context or {}),
    }

    template_root = f"email/{template_name}"

    try:
        subject = render_template(
            f"{template_root}/subject.txt",
            **template_context,
        )
        text_body = render_template(
            f"{template_root}/body.txt",
            **template_context,
        )
        html_body = render_template(
            f"{template_root}/body.html",
            **template_context,
        )
    except TemplateNotFound as exc:
        raise EmailTemplateError(
            f"Email template file was not found: {exc.name}"
        ) from exc
    except Exception as exc:
        raise EmailTemplateError(
            f"Could not render email template "
            f"{template_name!r}: {exc}"
        ) from exc

    subject = _normalise_subject(subject)
    text_body = text_body.strip()
    html_body = html_body.strip()

    if not subject:
        raise EmailTemplateError(
            f"Email template {template_name!r} produced an empty subject."
        )

    if not text_body:
        raise EmailTemplateError(
            f"Email template {template_name!r} produced an empty text body."
        )

    if not html_body:
        raise EmailTemplateError(
            f"Email template {template_name!r} produced an empty HTML body."
        )

    return RenderedEmail(
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


def _get_global_template_context() -> dict[str, Any]:
    """Return values available to every email template."""

    return {
        "email_brand_name": current_app.config.get(
            "MAIL_BRAND_NAME",
            "Response Connect",
        ),
        "email_support_email": current_app.config.get(
            "MAIL_SUPPORT_EMAIL",
            "",
        ),
        "email_public_url": current_app.config.get(
            "MAIL_PUBLIC_URL",
            "",
        ).rstrip("/"),
    }


def _normalise_subject(subject: str) -> str:
    """Collapse a rendered subject into one line."""

    return " ".join(subject.split())
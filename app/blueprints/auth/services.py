from __future__ import annotations

from flask import current_app, url_for

from app.blueprints.auth.models import UserAccount
from app.blueprints.auth.password_reset import (
    generate_password_reset_token,
)
from app.blueprints.email.services import queue_templated_email
from app.blueprints.jobs.models import Job


def queue_password_reset_email(
    user: UserAccount,
) -> Job:
    """Queue a password-reset email for a user."""

    token = generate_password_reset_token(user)
    reset_url = _build_password_reset_url(token)

    return queue_templated_email(
        template_name="auth/password_reset",
        to=user.email,
        context={
            "recipient_name": user.display_name,
            "reset_url": reset_url,
            "expires_in_minutes": _get_expiry_minutes(),
        },
        priority=3,
    )


def _build_password_reset_url(token: str) -> str:
    """
    Build an absolute password-reset URL.

    MAIL_PUBLIC_URL is preferred because Celery and reverse-proxy
    deployments may not know the installation's external hostname.
    """

    path = url_for(
        "auth.reset_password",
        token=token,
    )

    public_url = current_app.config.get(
        "MAIL_PUBLIC_URL",
        "",
    ).rstrip("/")

    if public_url:
        return f"{public_url}{path}"

    return url_for(
        "auth.reset_password",
        token=token,
        _external=True,
    )


def _get_expiry_minutes() -> int:
    max_age_seconds = int(
        current_app.config.get(
            "PASSWORD_RESET_TOKEN_MAX_AGE",
            3600,
        )
    )

    return max(1, max_age_seconds // 60)
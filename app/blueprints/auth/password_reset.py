from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from flask import current_app
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)

from app.blueprints.auth.models import UserAccount
from app.extensions import db
from app.exceptions import (
    ConfigurationError,
    ValidationError,
)


class PasswordResetTokenError(ValidationError):
    """Raised when a password-reset token is invalid or expired."""


@dataclass(frozen=True)
class PasswordResetTokenResult:
    """The validated result of a password-reset token."""

    user: UserAccount


def generate_password_reset_token(user: UserAccount) -> str:
    """Generate a signed password-reset token for a user."""

    serializer = _get_serializer()

    payload = {
        "user_id": str(user.id),
        "password_fingerprint": _password_fingerprint(
            user.password_hash
        ),
    }

    return serializer.dumps(
        payload,
        salt=_get_salt(),
    )


def validate_password_reset_token(
    token: str,
) -> PasswordResetTokenResult:
    """
    Validate a password-reset token and return its user.

    The token becomes invalid when:
    - it expires;
    - its signature is invalid;
    - the user no longer exists;
    - the account is inactive;
    - the user's password has changed.
    """

    if not token:
        raise PasswordResetTokenError(
            "The password-reset link is invalid."
        )

    serializer = _get_serializer()

    try:
        payload = serializer.loads(
            token,
            salt=_get_salt(),
            max_age=_get_max_age(),
        )
    except SignatureExpired as exc:
        raise PasswordResetTokenError(
            "This password-reset link has expired."
        ) from exc
    except BadSignature as exc:
        raise PasswordResetTokenError(
            "This password-reset link is invalid."
        ) from exc

    try:
        user_id = uuid.UUID(str(payload["user_id"]))
        supplied_fingerprint = str(
            payload["password_fingerprint"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise PasswordResetTokenError(
            "This password-reset link is invalid."
        ) from exc

    user = db.session.get(UserAccount, user_id)

    if user is None or not user.is_active:
        raise PasswordResetTokenError(
            "This password-reset link is invalid."
        )

    expected_fingerprint = _password_fingerprint(
        user.password_hash
    )

    if supplied_fingerprint != expected_fingerprint:
        raise PasswordResetTokenError(
            "This password-reset link has already been used "
            "or is no longer valid."
        )

    return PasswordResetTokenResult(user=user)


def _get_serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config.get(
        "SECRET_KEY"
    )

    if not secret_key:
        raise ConfigurationError(
            "SECRET_KEY must be configured before "
            "password-reset tokens can be generated."
        )

    return URLSafeTimedSerializer(
        secret_key
    )


def _get_salt() -> str:
    return current_app.config.get(
        "PASSWORD_RESET_SALT",
        "response-connect-password-reset",
    )


def _get_max_age() -> int:
    configured_value = current_app.config.get(
        "PASSWORD_RESET_TOKEN_MAX_AGE",
        3600,
    )

    try:
        max_age = int(configured_value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(
            "PASSWORD_RESET_TOKEN_MAX_AGE must "
            "be a valid integer."
        ) from exc

    if max_age <= 0:
        raise ConfigurationError(
            "PASSWORD_RESET_TOKEN_MAX_AGE must "
            "be greater than zero."
        )

    return max_age


def _password_fingerprint(password_hash: str) -> str:
    """
    Create a compact fingerprint of the current password hash.

    The password hash itself is not placed in the token.
    """

    return hashlib.sha256(
        password_hash.encode("utf-8")
    ).hexdigest()
"""Validation helpers for Desk data."""

from __future__ import annotations

import re

from app.desks.exceptions import InvalidDeskError


DESK_CODE_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)


def normalise_desk_code(
    value: str,
) -> str:
    """Return a normalised stable Desk code."""

    return value.strip().lower()


def validate_desk_code(
    value: str,
) -> str:
    """Validate and return a stable Desk code."""

    code = normalise_desk_code(value)

    if not code:
        raise InvalidDeskError(
            "A Desk code is required."
        )

    if not DESK_CODE_PATTERN.fullmatch(code):
        raise InvalidDeskError(
            "Desk codes must use lowercase "
            "snake_case."
        )

    return code


def validate_desk_name(
    value: str,
) -> str:
    """Validate and return a Desk display name."""

    name = value.strip()

    if not name:
        raise InvalidDeskError(
            "A Desk name is required."
        )

    if len(name) > 200:
        raise InvalidDeskError(
            "Desk names must not exceed "
            "200 characters."
        )

    return name


def validate_desk_description(
    value: str | None,
) -> str | None:
    """Validate and normalise an optional description."""

    if value is None:
        return None

    description = value.strip()

    if not description:
        return None

    if len(description) > 2000:
        raise InvalidDeskError(
            "Desk descriptions must not exceed "
            "2000 characters."
        )

    return description
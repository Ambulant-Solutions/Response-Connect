"""Validation helpers for Journal Entries."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
import json
from collections.abc import Mapping
from typing import Any
from app.journal.constants import (
    EVENT_CODE_MAX_LENGTH,
    JOURNAL_DETAILS_MAX_LENGTH,
    JOURNAL_EVENT_CODE_PATTERN,
    JOURNAL_EVENT_METADATA_MAX_BYTES,
    JOURNAL_REFERENCE_DISPLAY_NAME_MAX_LENGTH,
    JOURNAL_REFERENCE_STABLE_KEY_MAX_LENGTH,
    JOURNAL_REFERENCE_STABLE_KEY_PATTERN,
    JOURNAL_REFERENCE_TYPE_MAX_LENGTH,
    JOURNAL_REFERENCE_TYPE_PATTERN,
    JOURNAL_SUMMARY_MAX_LENGTH,
)
from app.journal.exceptions import (
    InvalidJournalEntryError,
    InvalidJournalReferenceError,
)

_EVENT_CODE_PATTERN = re.compile(
    JOURNAL_EVENT_CODE_PATTERN
)

_REFERENCE_TYPE_PATTERN = re.compile(
    JOURNAL_REFERENCE_TYPE_PATTERN
)

_REFERENCE_STABLE_KEY_PATTERN = re.compile(
    JOURNAL_REFERENCE_STABLE_KEY_PATTERN
)


def validate_event_code(
    value: str,
) -> str:
    """Validate and return a stable event code."""

    event_code = value.strip()

    if not event_code:
        raise InvalidJournalEntryError(
            "A Journal event code is required."
        )

    if len(event_code) > EVENT_CODE_MAX_LENGTH:
        raise InvalidJournalEntryError(
            "Journal event codes must not exceed "
            f"{EVENT_CODE_MAX_LENGTH} characters."
        )

    if not _EVENT_CODE_PATTERN.fullmatch(
        event_code
    ):
        raise InvalidJournalEntryError(
            "Journal event codes must use the "
            "'domain.action' lowercase format."
        )

    return event_code


def validate_summary(
    value: str,
) -> str:
    """Validate and return a Journal summary."""

    summary = value.strip()

    if not summary:
        raise InvalidJournalEntryError(
            "A Journal Entry summary is required."
        )

    if len(summary) > JOURNAL_SUMMARY_MAX_LENGTH:
        raise InvalidJournalEntryError(
            "Journal Entry summaries must not exceed "
            f"{JOURNAL_SUMMARY_MAX_LENGTH} characters."
        )

    return summary


def validate_details(
    value: str | None,
) -> str | None:
    """Validate and normalise optional Journal details."""

    if value is None:
        return None

    details = value.strip()

    if not details:
        return None

    if len(details) > JOURNAL_DETAILS_MAX_LENGTH:
        raise InvalidJournalEntryError(
            "Journal Entry details must not exceed "
            f"{JOURNAL_DETAILS_MAX_LENGTH} characters."
        )

    return details

def validate_occurred_at(
    value: datetime,
) -> datetime:
    """Validate and return a timezone-aware occurrence time."""

    if value.tzinfo is None:
        raise InvalidJournalEntryError(
            "Journal occurrence times must include "
            "timezone information."
        )

    if value.utcoffset() is None:
        raise InvalidJournalEntryError(
            "Journal occurrence times must include "
            "timezone information."
        )

    return value

def validate_reference_type(
    value: str,
) -> str:
    reference_type = value.strip()

    if not reference_type:
        raise InvalidJournalReferenceError(
            "A Journal Reference type is required."
        )

    if (
        len(reference_type)
        > JOURNAL_REFERENCE_TYPE_MAX_LENGTH
    ):
        raise InvalidJournalReferenceError(
            "Journal Reference types must not exceed "
            f"{JOURNAL_REFERENCE_TYPE_MAX_LENGTH} characters."
        )

    if not _REFERENCE_TYPE_PATTERN.fullmatch(
        reference_type
    ):
        raise InvalidJournalReferenceError(
            "Journal Reference types must use "
            "lowercase snake_case."
        )

    return reference_type


def validate_reference_display_name(
    value: str,
) -> str:
    display_name = value.strip()

    if not display_name:
        raise InvalidJournalReferenceError(
            "A Journal Reference display name is required."
        )

    if (
        len(display_name)
        > JOURNAL_REFERENCE_DISPLAY_NAME_MAX_LENGTH
    ):
        raise InvalidJournalReferenceError(
            "Journal Reference display names must not exceed "
            f"{JOURNAL_REFERENCE_DISPLAY_NAME_MAX_LENGTH} characters."
        )

    return display_name


def validate_reference_stable_key(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    stable_key = value.strip()

    if not stable_key:
        return None

    if (
        len(stable_key)
        > JOURNAL_REFERENCE_STABLE_KEY_MAX_LENGTH
    ):
        raise InvalidJournalReferenceError(
            "Journal Reference stable keys must not exceed "
            f"{JOURNAL_REFERENCE_STABLE_KEY_MAX_LENGTH} characters."
        )

    if not _REFERENCE_STABLE_KEY_PATTERN.fullmatch(
        stable_key
    ):
        raise InvalidJournalReferenceError(
            "Journal Reference stable keys must use "
            "lowercase letters, numbers, colons, hyphens, "
            "or underscores."
        )

    return stable_key


def validate_reference_identity(
    *,
    source_id: uuid.UUID | None,
    stable_key: str | None,
) -> None:
    if source_id is None and stable_key is None:
        raise InvalidJournalReferenceError(
            "A Journal Reference requires a source ID "
            "or stable key."
        )

def validate_event_metadata(
    value: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Validate and copy optional structured Journal metadata.

    Metadata must be a JSON-serialisable object at its top level.
    """

    if value is None:
        return None

    if not isinstance(value, Mapping):
        raise InvalidJournalEntryError(
            "Journal event metadata must be an object."
        )

    try:
        encoded = json.dumps(
            dict(value),
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise InvalidJournalEntryError(
            "Journal event metadata must contain only "
            "JSON-serialisable values."
        ) from exc

    if len(encoded) > JOURNAL_EVENT_METADATA_MAX_BYTES:
        raise InvalidJournalEntryError(
            "Journal event metadata must not exceed "
            f"{JOURNAL_EVENT_METADATA_MAX_BYTES} bytes."
        )

    # Decode the validated JSON so the stored structure is detached from
    # mutable objects supplied by the caller.
    return json.loads(
        encoded.decode("utf-8")
    )
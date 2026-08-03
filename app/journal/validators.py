"""Validation helpers for Journal Entries."""

from __future__ import annotations

import re

from app.journal.constants import (
    EVENT_CODE_MAX_LENGTH,
    JOURNAL_DETAILS_MAX_LENGTH,
    JOURNAL_EVENT_CODE_PATTERN,
    JOURNAL_SUMMARY_MAX_LENGTH,
)
from app.journal.exceptions import (
    InvalidJournalEntryError,
)


_EVENT_CODE_PATTERN = re.compile(
    JOURNAL_EVENT_CODE_PATTERN
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
"""Tests for Event Journal recording services."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.journal.commands import (
    RecordJournalEntryCommand,
)
from app.journal.exceptions import (
    InvalidJournalEntryError,
    JournalPersistenceError,
)
from app.journal.models import JournalEntry
from app.journal.services import (
    JournalEntryService,
)


@pytest.fixture
def journal_service(
    app,
) -> JournalEntryService:
    return JournalEntryService(
        session=db.session,
    )


def test_record_returns_created_journal_entry(
    app,
    journal_service: JournalEntryService,
) -> None:
    occurred_at = datetime.now(
        timezone.utc
    )

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_recorded",
            occurred_at=occurred_at,
            summary="A test occurrence was recorded.",
            details="Additional test context.",
        )
    )

    assert isinstance(entry, JournalEntry)
    assert entry.id is not None
    assert entry.event_code == (
        "system.test_recorded"
    )
    assert entry.occurred_at == occurred_at
    assert entry.summary == (
        "A test occurrence was recorded."
    )
    assert entry.details == (
        "Additional test context."
    )
    assert entry.recorded_at is not None
    assert entry.created_at is not None


def test_record_normalises_summary_and_details(
    app,
    journal_service: JournalEntryService,
) -> None:
    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_normalised",
            occurred_at=datetime.now(
                timezone.utc
            ),
            summary=(
                "  A test occurrence was recorded.  "
            ),
            details="  Additional context.  ",
        )
    )

    assert entry.summary == (
        "A test occurrence was recorded."
    )
    assert entry.details == (
        "Additional context."
    )


def test_record_normalises_blank_details_to_none(
    app,
    journal_service: JournalEntryService,
) -> None:
    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_blank_details",
            occurred_at=datetime.now(
                timezone.utc
            ),
            summary="A test occurrence was recorded.",
            details="   ",
        )
    )

    assert entry.details is None


@pytest.mark.parametrize(
    "event_code",
    [
        "",
        "System.test_recorded",
        "system",
        "system.test.recorded",
    ],
)
def test_record_rejects_invalid_event_code(
    app,
    journal_service: JournalEntryService,
    event_code: str,
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code=event_code,
                occurred_at=datetime.now(
                    timezone.utc
                ),
                summary=(
                    "A test occurrence was recorded."
                ),
            )
        )


def test_record_rejects_blank_summary(
    app,
    journal_service: JournalEntryService,
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
        match="summary",
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code="system.test_recorded",
                occurred_at=datetime.now(
                    timezone.utc
                ),
                summary="   ",
            )
        )


def test_record_rejects_naive_occurred_at(
    app,
    journal_service: JournalEntryService,
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
        match="timezone",
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code="system.test_recorded",
                occurred_at=datetime.now(),
                summary=(
                    "A test occurrence was recorded."
                ),
            )
        )


def test_record_accepts_non_utc_timezone(
    app,
    journal_service: JournalEntryService,
) -> None:
    occurred_at = datetime.now().astimezone()

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_timezone",
            occurred_at=occurred_at,
            summary="A timezone-aware occurrence.",
        )
    )

    assert entry.occurred_at == occurred_at


def test_record_rolls_back_and_translates_persistence_failure(
    app,
) -> None:
    session = Mock()

    session.commit.side_effect = (
        SQLAlchemyError(
            "Database failure"
        )
    )

    service = JournalEntryService(
        session=session,
    )

    with pytest.raises(
        JournalPersistenceError,
        match="could not be recorded",
    ):
        service.record(
            RecordJournalEntryCommand(
                event_code="system.test_failure",
                occurred_at=datetime.now(
                    timezone.utc
                ),
                summary=(
                    "A failing Journal Entry."
                ),
            )
        )

    session.add.assert_called_once()
    session.rollback.assert_called_once()


def test_record_does_not_persist_invalid_command(
    app,
) -> None:
    session = Mock()

    service = JournalEntryService(
        session=session,
    )

    with pytest.raises(
        InvalidJournalEntryError,
    ):
        service.record(
            RecordJournalEntryCommand(
                event_code="INVALID",
                occurred_at=datetime.now(
                    timezone.utc
                ),
                summary="Invalid occurrence.",
            )
        )

    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()
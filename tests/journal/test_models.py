"""Tests for persistent Event Journal models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.journal.models import JournalEntry


def create_entry(
    *,
    event_code: str = "system.test_recorded",
    summary: str = "A test occurrence was recorded.",
    details: str | None = None,
) -> JournalEntry:
    entry = JournalEntry(
        event_code=event_code,
        occurred_at=datetime.now(
            timezone.utc
        ),
        summary=summary,
        details=details,
    )

    db.session.add(entry)
    db.session.flush()

    return entry


def test_journal_entry_uses_uuid_identity(
    app,
) -> None:
    with app.app_context():
        entry = create_entry()

        assert isinstance(
            entry.id,
            uuid.UUID,
        )


def test_journal_entry_records_required_values(
    app,
) -> None:
    with app.app_context():
        occurred_at = datetime.now(
            timezone.utc
        )

        entry = JournalEntry(
            event_code="desk.created",
            occurred_at=occurred_at,
            summary="A Desk was created.",
            details="Created during a test.",
        )

        db.session.add(entry)
        db.session.flush()

        assert entry.event_code == "desk.created"
        assert entry.occurred_at == occurred_at
        assert entry.summary == (
            "A Desk was created."
        )
        assert entry.details == (
            "Created during a test."
        )


def test_journal_entry_sets_recorded_and_created_times(
    app,
) -> None:
    with app.app_context():
        entry = create_entry()

        db.session.refresh(entry)

        assert entry.recorded_at is not None
        assert entry.created_at is not None


def test_journal_entry_details_are_optional(
    app,
) -> None:
    with app.app_context():
        entry = create_entry(
            details=None,
        )

        assert entry.details is None


def test_journal_entry_requires_event_code(
    app,
) -> None:
    with app.app_context():
        entry = JournalEntry(
            event_code=None,
            occurred_at=datetime.now(
                timezone.utc
            ),
            summary="Missing event code.",
        )

        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_entry_requires_summary(
    app,
) -> None:
    with app.app_context():
        entry = JournalEntry(
            event_code="system.test_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            summary=None,
        )

        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_entry_repr_contains_identity_and_code(
    app,
) -> None:
    with app.app_context():
        entry = create_entry(
            event_code="desk.created",
        )

        representation = repr(entry)

        assert str(entry.id) in representation
        assert "desk.created" in representation
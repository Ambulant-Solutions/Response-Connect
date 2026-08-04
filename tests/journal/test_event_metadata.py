"""Tests for structured Journal event metadata."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.extensions import db
from app.journal import (
    JournalReferenceSpec,
    JournalService,
)
from app.journal.exceptions import (
    InvalidJournalEntryError,
)
from app.journal.models import JournalEntry
from app.journal.validators import (
    validate_event_metadata,
)


@pytest.fixture
def journal(
    app,
) -> JournalService:
    return JournalService(
        session=db.session,
    )


def actor_spec() -> JournalReferenceSpec:
    return JournalReferenceSpec.from_stable_key(
        reference_type="system",
        stable_key=(
            f"test_system:metadata:{uuid.uuid4()}"
        ),
        display_name="Metadata Test",
    )


def test_validate_event_metadata_accepts_object() -> None:
    metadata = {
        "changed_fields": [
            "name",
            "description",
        ],
        "previous": {
            "name": "Operations",
        },
        "current": {
            "name": "Operations Control",
        },
    }

    assert validate_event_metadata(
        metadata
    ) == metadata


def test_validate_event_metadata_allows_none() -> None:
    assert validate_event_metadata(
        None
    ) is None


@pytest.mark.parametrize(
    "value",
    [
        [],
        "metadata",
        123,
        True,
    ],
)
def test_validate_event_metadata_requires_object(
    value,
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
        match="object",
    ):
        validate_event_metadata(value)


def test_validate_event_metadata_rejects_non_json_value(
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
        match="JSON",
    ):
        validate_event_metadata(
            {
                "record_id": uuid.uuid4(),
            }
        )


def test_validate_event_metadata_returns_detached_copy(
) -> None:
    original = {
        "changed_fields": [
            "name",
        ],
    }

    validated = validate_event_metadata(
        original
    )

    assert validated == original
    assert validated is not original
    assert (
        validated["changed_fields"]
        is not original["changed_fields"]
    )


def test_public_service_stores_event_metadata(
    app,
    journal: JournalService,
) -> None:
    metadata = {
        "changed_fields": [
            "name",
            "description",
        ],
        "previous": {
            "name": "Operations",
            "description": "Operational services.",
        },
        "current": {
            "name": "Operations Control",
            "description": "Command and control.",
        },
    }

    entry = journal.record(
        event_code="system.test_metadata",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(),
        summary="Structured metadata was recorded.",
        event_metadata=metadata,
    )

    assert entry.event_metadata == metadata

    db.session.expire_all()

    persisted = db.session.get(
        JournalEntry,
        entry.id,
    )

    assert persisted is not None
    assert persisted.event_metadata == metadata


def test_public_service_stores_null_metadata(
    app,
    journal: JournalService,
) -> None:
    entry = journal.record(
        event_code="system.test_no_metadata",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(),
        summary="No metadata was supplied.",
    )

    assert entry.event_metadata is None


def test_nested_metadata_survives_database_round_trip(
    app,
    journal: JournalService,
) -> None:
    metadata = {
        "values": {
            "boolean": True,
            "integer": 42,
            "decimal_as_string": "12.50",
            "null": None,
            "items": [
                "one",
                "two",
            ],
        },
    }

    entry = journal.record(
        event_code="system.test_nested_metadata",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(),
        summary="Nested metadata was recorded.",
        event_metadata=metadata,
    )

    entry_id = entry.id

    db.session.expire_all()

    persisted = db.session.get(
        JournalEntry,
        entry_id,
    )

    assert persisted is not None
    assert persisted.event_metadata == metadata


def test_metadata_is_removed_by_caller_rollback(
    app,
    journal: JournalService,
) -> None:
    entry = journal.record(
        event_code="system.test_metadata_rollback",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(),
        summary="Metadata will be rolled back.",
        event_metadata={
            "rolled_back": True,
        },
        commit=False,
    )

    entry_id = entry.id

    db.session.rollback()

    assert db.session.get(
        JournalEntry,
        entry_id,
    ) is None


def test_invalid_metadata_creates_no_journal_entry(
    app,
    journal: JournalService,
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
    ):
        journal.record(
            event_code="system.test_invalid_metadata",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor=actor_spec(),
            summary="Invalid metadata.",
            event_metadata={
                "invalid_uuid": uuid.uuid4(),
            },
            commit=False,
        )

    assert (
        db.session.query(JournalEntry)
        .filter(
            JournalEntry.event_code
            == "system.test_invalid_metadata"
        )
        .count()
        == 0
    )
"""Tests for caller-owned Journal transactions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.journal import (
    JournalReferenceSpec,
    JournalService,
)
from app.journal.commands import (
    RecordJournalEntryCommand,
    RegisterJournalReferenceCommand,
)
from app.journal.exceptions import (
    InvalidJournalEntryError,
    JournalPersistenceError,
)
from app.journal.models import (
    JournalEntry,
    JournalReference,
)
from app.journal.services import (
    JournalEntryService,
    JournalReferenceService,
)


@pytest.fixture
def journal(
    app,
) -> JournalService:
    return JournalService(
        session=db.session,
    )


def test_public_record_commits_by_default(
    app,
    journal: JournalService,
) -> None:
    entry = journal.record(
        event_code="system.test_default_commit",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=JournalReferenceSpec(
            reference_type="system",
            stable_key=(
                f"test_system:{uuid.uuid4()}"
            ),
            display_name="Response Connect",
        ),
        summary="A committed Journal Entry.",
    )

    db.session.expire_all()

    persisted = db.session.get(
        JournalEntry,
        entry.id,
    )

    assert persisted is not None


def test_entry_service_commit_false_flushes_without_commit(
    app,
) -> None:
    actor = JournalReference(
        reference_type="system",
        stable_key=(
            f"test_system:{uuid.uuid4()}"
        ),
        display_name="Response Connect",
    )

    db.session.add(actor)
    db.session.flush()

    service = JournalEntryService(
        session=db.session,
    )

    entry = service.record(
        RecordJournalEntryCommand(
            event_code="system.test_flush_only",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            summary="A flushed Journal Entry.",
        ),
        commit=False,
    )

    assert entry.id is not None
    assert entry in db.session


def test_reference_service_commit_false_flushes_without_commit(
    app,
) -> None:
    service = JournalReferenceService(
        session=db.session,
    )

    reference = service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="system",
            stable_key=(
                f"test_system:{uuid.uuid4()}"
            ),
            display_name="Response Connect",
        ),
        commit=False,
    )

    assert reference.id is not None
    assert reference in db.session


def test_public_record_commit_false_creates_reference_and_entry(
    app,
    journal: JournalService,
) -> None:
    stable_key = (
        f"test_system:{uuid.uuid4()}"
    )

    entry = journal.record(
        event_code="system.test_public_flush",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=JournalReferenceSpec(
            reference_type="system",
            stable_key=stable_key,
            display_name="Response Connect",
        ),
        summary="A caller-owned Journal Entry.",
        commit=False,
    )

    assert entry.id is not None
    assert entry.actor_reference_id is not None

    reference = db.session.scalar(
        select(JournalReference).where(
            JournalReference.reference_type
            == "system",
            JournalReference.stable_key
            == stable_key,
        )
    )

    assert reference is not None
    assert reference.id == (
        entry.actor_reference_id
    )


def test_caller_rollback_removes_reference_and_entry(
    app,
    journal: JournalService,
) -> None:
    stable_key = (
        f"test_system:{uuid.uuid4()}"
    )

    entry = journal.record(
        event_code="system.test_rollback",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=JournalReferenceSpec(
            reference_type="system",
            stable_key=stable_key,
            display_name="Response Connect",
        ),
        summary="A rolled-back Journal Entry.",
        commit=False,
    )

    entry_id = entry.id

    db.session.rollback()

    assert db.session.get(
        JournalEntry,
        entry_id,
    ) is None

    reference = db.session.scalar(
        select(JournalReference).where(
            JournalReference.reference_type
            == "system",
            JournalReference.stable_key
            == stable_key,
        )
    )

    assert reference is None


def test_caller_commit_preserves_reference_and_entry(
    app,
    journal: JournalService,
) -> None:
    stable_key = (
        f"test_system:{uuid.uuid4()}"
    )

    entry = journal.record(
        event_code="system.test_caller_commit",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=JournalReferenceSpec(
            reference_type="system",
            stable_key=stable_key,
            display_name="Response Connect",
        ),
        summary="A caller-committed Journal Entry.",
        commit=False,
    )

    entry_id = entry.id

    db.session.commit()
    db.session.expire_all()

    assert db.session.get(
        JournalEntry,
        entry_id,
    ) is not None

    reference = db.session.scalar(
        select(JournalReference).where(
            JournalReference.reference_type
            == "system",
            JournalReference.stable_key
            == stable_key,
        )
    )

    assert reference is not None


def test_validation_failure_creates_no_records(
    app,
    journal: JournalService,
) -> None:
    stable_key = (
        f"test_system:{uuid.uuid4()}"
    )

    with pytest.raises(
        InvalidJournalEntryError,
    ):
        journal.record(
            event_code="INVALID",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor=JournalReferenceSpec(
                reference_type="system",
                stable_key=stable_key,
                display_name="Response Connect",
            ),
            summary="Invalid occurrence.",
            commit=False,
        )

    assert db.session.scalar(
        select(JournalReference).where(
            JournalReference.reference_type
            == "system",
            JournalReference.stable_key
            == stable_key,
        )
    ) is None

    assert db.session.scalar(
        select(JournalEntry).where(
            JournalEntry.event_code
            == "INVALID",
        )
    ) is None


def test_entry_persistence_failure_is_translated(
    app,
) -> None:
    actor_id = uuid.uuid4()

    actor = Mock(
        spec=JournalReference
    )
    actor.id = actor_id

    session = Mock()
    session.get.side_effect = (
        lambda model, identifier: (
            actor
            if (
                model is JournalReference
                and identifier == actor_id
            )
            else None
        )
    )
    session.flush.side_effect = SQLAlchemyError(
        "Database failure"
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
                actor_reference_id=actor_id,
                summary="A failing Journal Entry.",
            ),
            commit=False,
        )

    session.add.assert_called_once()
    session.commit.assert_not_called()
    session.rollback.assert_called_once()
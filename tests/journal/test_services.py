"""Tests for Event Journal recording services."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.desks import Desk, DeskNotFoundError
from app.extensions import db
from app.journal.commands import RecordJournalEntryCommand
from app.journal.exceptions import (
    InvalidJournalEntryError,
    JournalPersistenceError,
    JournalReferenceNotFoundError,
)
from app.journal.models import (
    JournalEntry,
    JournalReference,
)
from app.journal.services import JournalEntryService


@pytest.fixture
def journal_service(
    app,
) -> JournalEntryService:
    return JournalEntryService(
        session=db.session,
    )


def create_reference(
    *,
    reference_type: str = "system",
    display_name: str = "Response Connect",
) -> JournalReference:
    reference = JournalReference(
        reference_type=reference_type,
        source_id=uuid.uuid4(),
        stable_key=None,
        display_name=display_name,
    )

    db.session.add(reference)
    db.session.flush()

    return reference


def create_root_desk() -> Desk:
    root = Desk(
        code="test_journal_service_root",
        name="Journal Service Organisation",
        is_root=True,
        parent_id=None,
    )

    db.session.add(root)
    db.session.flush()

    return root


def create_desk(
    *,
    parent: Desk,
) -> Desk:
    desk = Desk(
        code="test_journal_service_desk",
        name="Journal Service Desk",
        parent=parent,
        is_root=False,
    )

    db.session.add(desk)
    db.session.flush()

    return desk


def test_record_returns_created_journal_entry(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()
    occurred_at = datetime.now(
        timezone.utc
    )

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_recorded",
            occurred_at=occurred_at,
            actor_reference_id=actor.id,
            summary=(
                "A test occurrence was recorded."
            ),
            details="Additional test context.",
        )
    )

    assert isinstance(entry, JournalEntry)
    assert entry.id is not None
    assert entry.event_code == (
        "system.test_recorded"
    )
    assert entry.occurred_at == occurred_at
    assert entry.actor_reference_id == actor.id
    assert entry.actor_reference is actor
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
    actor = create_reference()

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_normalised",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
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
    actor = create_reference()

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_blank_details",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            summary=(
                "A test occurrence was recorded."
            ),
            details="   ",
        )
    )

    assert entry.details is None


def test_record_stores_subject_and_context(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()
    subject = create_reference(
        reference_type="vehicle",
        display_name="Vehicle A12",
    )
    context = create_reference(
        reference_type="incident",
        display_name="Incident INC-001",
    )

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="vehicle.arrived_on_scene",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            subject_reference_id=subject.id,
            context_reference_id=context.id,
            summary=(
                "Vehicle A12 arrived on scene."
            ),
        )
    )

    assert entry.subject_reference_id == (
        subject.id
    )
    assert entry.subject_reference is subject
    assert entry.context_reference_id == (
        context.id
    )
    assert entry.context_reference is context


def test_record_stores_desk_and_display_snapshot(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()
    root = create_root_desk()
    desk = create_desk(
        parent=root,
    )

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_desk_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            desk_id=desk.id,
            summary="A Desk occurrence was recorded.",
        )
    )

    assert entry.desk_id == desk.id
    assert entry.desk is desk
    assert entry.desk_display_name == (
        "Journal Service Desk"
    )


def test_record_without_optional_relationships(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            summary=(
                "A test occurrence was recorded."
            ),
        )
    )

    assert entry.subject_reference_id is None
    assert entry.context_reference_id is None
    assert entry.desk_id is None
    assert entry.desk_display_name is None


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
    actor = create_reference()

    with pytest.raises(
        InvalidJournalEntryError,
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code=event_code,
                occurred_at=datetime.now(
                    timezone.utc
                ),
                actor_reference_id=actor.id,
                summary=(
                    "A test occurrence was "
                    "recorded."
                ),
            )
        )


def test_record_rejects_blank_summary(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()

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
                actor_reference_id=actor.id,
                summary="   ",
            )
        )


def test_record_rejects_naive_occurred_at(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()

    with pytest.raises(
        InvalidJournalEntryError,
        match="timezone",
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code="system.test_recorded",
                occurred_at=datetime.now(),
                actor_reference_id=actor.id,
                summary=(
                    "A test occurrence was "
                    "recorded."
                ),
            )
        )


def test_record_accepts_non_utc_timezone(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()
    occurred_at = datetime.now().astimezone()

    entry = journal_service.record(
        RecordJournalEntryCommand(
            event_code="system.test_timezone",
            occurred_at=occurred_at,
            actor_reference_id=actor.id,
            summary="A timezone-aware occurrence.",
        )
    )

    assert entry.occurred_at == occurred_at


def test_record_rejects_unknown_actor_reference(
    app,
    journal_service: JournalEntryService,
) -> None:
    with pytest.raises(
        JournalReferenceNotFoundError,
        match="actor",
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code="system.test_recorded",
                occurred_at=datetime.now(
                    timezone.utc
                ),
                actor_reference_id=uuid.uuid4(),
                summary="Unknown actor.",
            )
        )


def test_record_rejects_unknown_subject_reference(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()

    with pytest.raises(
        JournalReferenceNotFoundError,
        match="subject",
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code="system.test_recorded",
                occurred_at=datetime.now(
                    timezone.utc
                ),
                actor_reference_id=actor.id,
                subject_reference_id=uuid.uuid4(),
                summary="Unknown subject.",
            )
        )


def test_record_rejects_unknown_context_reference(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()

    with pytest.raises(
        JournalReferenceNotFoundError,
        match="context",
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code="system.test_recorded",
                occurred_at=datetime.now(
                    timezone.utc
                ),
                actor_reference_id=actor.id,
                context_reference_id=uuid.uuid4(),
                summary="Unknown context.",
            )
        )


def test_record_rejects_unknown_desk(
    app,
    journal_service: JournalEntryService,
) -> None:
    actor = create_reference()

    with pytest.raises(
        DeskNotFoundError,
    ):
        journal_service.record(
            RecordJournalEntryCommand(
                event_code="system.test_recorded",
                occurred_at=datetime.now(
                    timezone.utc
                ),
                actor_reference_id=actor.id,
                desk_id=uuid.uuid4(),
                summary="Unknown Desk.",
            )
        )


def test_missing_relationship_is_rejected_before_persistence(
    app,
) -> None:
    session = Mock()
    session.get.return_value = None

    service = JournalEntryService(
        session=session,
    )

    with pytest.raises(
        JournalReferenceNotFoundError,
    ):
        service.record(
            RecordJournalEntryCommand(
                event_code="system.test_recorded",
                occurred_at=datetime.now(
                    timezone.utc
                ),
                actor_reference_id=uuid.uuid4(),
                summary="Missing actor.",
            )
        )

    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_record_rolls_back_and_translates_persistence_failure(
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
    session.commit.side_effect = SQLAlchemyError(
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
                actor_reference_id=uuid.uuid4(),
                summary="Invalid occurrence.",
            )
        )

    session.get.assert_not_called()
    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()
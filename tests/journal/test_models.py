"""Tests for persistent Event Journal models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.desks.models import Desk
from app.extensions import db
from app.journal.models import (
    JournalEntry,
    JournalReference,
)


def create_actor_reference(
    *,
    stable_key: str | None = None,
    display_name: str = "Response Connect",
) -> JournalReference:
    """Create a system actor reference for a test Journal Entry."""

    reference = JournalReference(
        reference_type="system",
        source_id=None,
        stable_key=(
            stable_key
            or f"test_system:{uuid.uuid4()}"
        ),
        display_name=display_name,
    )

    db.session.add(reference)
    db.session.flush()

    return reference


def create_reference(
    *,
    reference_type: str,
    display_name: str,
) -> JournalReference:
    """Create a Journal Reference backed by a source UUID."""

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
    """Create the root Desk used by Journal model tests."""

    root = Desk(
        code="test_journal_root",
        name="Test Journal Organisation",
        is_root=True,
        parent_id=None,
    )

    db.session.add(root)
    db.session.flush()

    return root


def create_test_desk(
    *,
    parent: Desk,
) -> Desk:
    """Create an operational Desk used by Journal model tests."""

    desk = Desk(
        code="test_journal_desk",
        name="Journal Test Desk",
        parent=parent,
        is_root=False,
    )

    db.session.add(desk)
    db.session.flush()

    return desk


def create_entry(
    *,
    event_code: str = "system.test_recorded",
    summary: str = "A test occurrence was recorded.",
    details: str | None = None,
    actor_reference: JournalReference | None = None,
    subject_reference: JournalReference | None = None,
    context_reference: JournalReference | None = None,
    desk: Desk | None = None,
) -> JournalEntry:
    """Create and flush a Journal Entry for model tests."""

    actor = (
        actor_reference
        or create_actor_reference()
    )

    entry = JournalEntry(
        event_code=event_code,
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor_reference_id=actor.id,
        subject_reference_id=(
            subject_reference.id
            if subject_reference is not None
            else None
        ),
        context_reference_id=(
            context_reference.id
            if context_reference is not None
            else None
        ),
        desk_id=(
            desk.id
            if desk is not None
            else None
        ),
        desk_display_name=(
            desk.name
            if desk is not None
            else None
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
        actor = create_actor_reference()

        entry = JournalEntry(
            event_code="desk.created",
            occurred_at=occurred_at,
            actor_reference_id=actor.id,
            summary="A Desk was created.",
            details="Created during a test.",
        )

        db.session.add(entry)
        db.session.flush()

        assert entry.event_code == "desk.created"
        assert entry.occurred_at == occurred_at
        assert entry.actor_reference_id == actor.id
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
        actor = create_actor_reference()

        entry = JournalEntry(
            event_code=None,  # type: ignore[arg-type]
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
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
        actor = create_actor_reference()

        entry = JournalEntry(
            event_code="system.test_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            summary=None,  # type: ignore[arg-type]
        )

        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_entry_requires_actor_reference(
    app,
) -> None:
    with app.app_context():
        entry = JournalEntry(
            event_code="system.test_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=None,  # type: ignore[arg-type]
            summary="Missing actor reference.",
        )

        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_entry_rejects_unknown_actor_reference(
    app,
) -> None:
    with app.app_context():
        entry = JournalEntry(
            event_code="system.test_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=uuid.uuid4(),
            summary="Unknown actor reference.",
        )

        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_entry_stores_actor_relationship(
    app,
) -> None:
    with app.app_context():
        actor = create_actor_reference(
            display_name="Nightly Scheduler",
        )

        entry = create_entry(
            actor_reference=actor,
        )

        assert entry.actor_reference_id == actor.id
        assert entry.actor_reference is actor


def test_journal_entry_subject_is_optional(
    app,
) -> None:
    with app.app_context():
        entry = create_entry()

        assert entry.subject_reference_id is None
        assert entry.subject_reference is None


def test_journal_entry_stores_subject_relationship(
    app,
) -> None:
    with app.app_context():
        subject = create_reference(
            reference_type="vehicle",
            display_name="Vehicle A12",
        )

        entry = create_entry(
            event_code="vehicle.status_changed",
            summary="Vehicle A12 changed status.",
            subject_reference=subject,
        )

        assert entry.subject_reference_id == (
            subject.id
        )
        assert entry.subject_reference is subject


def test_journal_entry_context_is_optional(
    app,
) -> None:
    with app.app_context():
        entry = create_entry()

        assert entry.context_reference_id is None
        assert entry.context_reference is None


def test_journal_entry_stores_context_relationship(
    app,
) -> None:
    with app.app_context():
        context = create_reference(
            reference_type="incident",
            display_name="Incident INC-001",
        )

        entry = create_entry(
            event_code="incident.note_added",
            summary="An incident note was added.",
            context_reference=context,
        )

        assert entry.context_reference_id == (
            context.id
        )
        assert entry.context_reference is context


def test_journal_entry_desk_is_optional(
    app,
) -> None:
    with app.app_context():
        entry = create_entry()

        assert entry.desk_id is None
        assert entry.desk is None
        assert entry.desk_display_name is None


def test_journal_entry_stores_desk_relationship_and_snapshot(
    app,
) -> None:
    with app.app_context():
        root = create_root_desk()
        desk = create_test_desk(
            parent=root,
        )

        entry = create_entry(
            event_code="vehicle.arrived_on_scene",
            summary=(
                "Vehicle A12 arrived on scene."
            ),
            desk=desk,
        )

        assert entry.desk_id == desk.id
        assert entry.desk is desk
        assert entry.desk_display_name == (
            "Journal Test Desk"
        )


def test_journal_entry_stores_actor_subject_context_and_desk(
    app,
) -> None:
    with app.app_context():
        actor = create_actor_reference(
            display_name="Dispatcher Alex Smith",
        )
        subject = create_reference(
            reference_type="vehicle",
            display_name="Vehicle A12",
        )
        context = create_reference(
            reference_type="incident",
            display_name="Incident INC-001",
        )

        root = create_root_desk()
        desk = create_test_desk(
            parent=root,
        )

        entry = create_entry(
            event_code="vehicle.arrived_on_scene",
            summary=(
                "Vehicle A12 arrived on scene."
            ),
            actor_reference=actor,
            subject_reference=subject,
            context_reference=context,
            desk=desk,
        )

        assert entry.actor_reference is actor
        assert entry.subject_reference is subject
        assert entry.context_reference is context
        assert entry.desk is desk
        assert entry.desk_display_name == (
            "Journal Test Desk"
        )


def test_journal_entry_rejects_unknown_subject_reference(
    app,
) -> None:
    with app.app_context():
        actor = create_actor_reference()

        entry = JournalEntry(
            event_code="system.test_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            subject_reference_id=uuid.uuid4(),
            summary="Unknown subject reference.",
        )

        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_entry_rejects_unknown_context_reference(
    app,
) -> None:
    with app.app_context():
        actor = create_actor_reference()

        entry = JournalEntry(
            event_code="system.test_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            context_reference_id=uuid.uuid4(),
            summary="Unknown context reference.",
        )

        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_entry_rejects_unknown_desk(
    app,
) -> None:
    with app.app_context():
        actor = create_actor_reference()

        entry = JournalEntry(
            event_code="system.test_recorded",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor_reference_id=actor.id,
            desk_id=uuid.uuid4(),
            desk_display_name="Unknown Desk",
            summary="Unknown Desk reference.",
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


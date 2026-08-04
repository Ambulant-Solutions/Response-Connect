"""Tests for the public Event Journal service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.desks import Desk
from app.extensions import db
from app.journal import (
    JournalReferenceSpec,
    JournalService,
)
from app.journal.exceptions import (
    InvalidJournalEntryError,
    InvalidJournalReferenceError,
    JournalReferenceConflictError,
)
from app.journal.models import (
    JournalEntry,
    JournalReference,
)


@pytest.fixture
def journal(
    app,
) -> JournalService:
    return JournalService(
        session=db.session,
    )


def create_root_desk() -> Desk:
    root = Desk(
        code="test_public_journal_root",
        name="Public Journal Organisation",
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
        code="test_public_journal_desk",
        name="Public Journal Desk",
        parent=parent,
        is_root=False,
    )

    db.session.add(desk)
    db.session.flush()

    return desk


def actor_spec(
    *,
    stable_key: str | None = None,
    display_name: str = "Response Connect",
) -> JournalReferenceSpec:
    return JournalReferenceSpec(
        reference_type="system",
        stable_key=(
            stable_key
            or f"test_system:{uuid.uuid4()}"
        ),
        display_name=display_name,
    )


def test_record_returns_journal_entry(
    app,
    journal: JournalService,
) -> None:
    occurred_at = datetime.now(
        timezone.utc
    )

    entry = journal.record(
        event_code="system.test_public_recorded",
        occurred_at=occurred_at,
        actor=actor_spec(),
        summary="A public Journal occurrence.",
        details="Recorded through JournalService.",
    )

    assert isinstance(entry, JournalEntry)
    assert entry.id is not None
    assert entry.event_code == (
        "system.test_public_recorded"
    )
    assert entry.occurred_at == occurred_at
    assert entry.summary == (
        "A public Journal occurrence."
    )
    assert entry.details == (
        "Recorded through JournalService."
    )


def test_record_creates_actor_reference(
    app,
    journal: JournalService,
) -> None:
    actor = actor_spec(
        stable_key="test_system:public_actor",
        display_name="Public Test Actor",
    )

    entry = journal.record(
        event_code="system.test_actor_recorded",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor,
        summary="An actor occurrence.",
    )

    reference = db.session.get(
        JournalReference,
        entry.actor_reference_id,
    )

    assert reference is not None
    assert reference.reference_type == "system"
    assert reference.stable_key == (
        "test_system:public_actor"
    )
    assert reference.display_name == (
        "Public Test Actor"
    )


def test_record_reuses_existing_actor_reference(
    app,
    journal: JournalService,
) -> None:
    actor = actor_spec(
        stable_key="test_system:reused_actor",
        display_name="Original Actor",
    )

    first = journal.record(
        event_code="system.test_first",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor,
        summary="First occurrence.",
    )

    second = journal.record(
        event_code="system.test_second",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=JournalReferenceSpec(
            reference_type="system",
            stable_key="test_system:reused_actor",
            display_name="Changed Actor Name",
        ),
        summary="Second occurrence.",
    )

    assert (
        second.actor_reference_id
        == first.actor_reference_id
    )

    reference = db.session.get(
        JournalReference,
        first.actor_reference_id,
    )

    assert reference is not None
    assert reference.display_name == (
        "Original Actor"
    )


def test_record_creates_subject_and_context_references(
    app,
    journal: JournalService,
) -> None:
    subject_id = uuid.uuid4()
    context_id = uuid.uuid4()

    entry = journal.record(
        event_code="vehicle.arrived_on_scene",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(),
        subject=JournalReferenceSpec(
            reference_type="vehicle",
            source_id=subject_id,
            display_name="Vehicle A12",
        ),
        context=JournalReferenceSpec(
            reference_type="incident",
            source_id=context_id,
            display_name="Incident INC-001",
        ),
        summary="Vehicle A12 arrived on scene.",
    )

    assert entry.subject_reference is not None
    assert entry.subject_reference.source_id == (
        subject_id
    )
    assert entry.subject_reference.display_name == (
        "Vehicle A12"
    )

    assert entry.context_reference is not None
    assert entry.context_reference.source_id == (
        context_id
    )
    assert entry.context_reference.display_name == (
        "Incident INC-001"
    )


def test_record_allows_missing_subject_and_context(
    app,
    journal: JournalService,
) -> None:
    entry = journal.record(
        event_code="system.test_without_context",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(),
        summary="An organisation-wide occurrence.",
    )

    assert entry.subject_reference_id is None
    assert entry.context_reference_id is None


def test_record_stores_desk_context(
    app,
    journal: JournalService,
) -> None:
    root = create_root_desk()
    desk = create_desk(
        parent=root,
    )

    entry = journal.record(
        event_code="system.test_desk_context",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(),
        desk_id=desk.id,
        summary="A Desk-scoped occurrence.",
    )

    assert entry.desk_id == desk.id
    assert entry.desk_display_name == (
        "Public Journal Desk"
    )


def test_record_normalises_summary_and_details(
    app,
    journal: JournalService,
) -> None:
    entry = journal.record(
        event_code="system.test_normalised_public",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(),
        summary="  Normalised summary.  ",
        details="  Normalised details.  ",
    )

    assert entry.summary == "Normalised summary."
    assert entry.details == "Normalised details."


def test_record_rejects_invalid_event_code(
    app,
    journal: JournalService,
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
    ):
        journal.record(
            event_code="INVALID",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor=actor_spec(),
            summary="Invalid occurrence.",
        )


def test_record_rejects_invalid_actor_spec(
    app,
    journal: JournalService,
) -> None:
    with pytest.raises(
        InvalidJournalReferenceError,
    ):
        journal.record(
            event_code="system.test_invalid_actor",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor=JournalReferenceSpec(
                reference_type="INVALID",
                stable_key="test_system:invalid",
                display_name="Invalid Actor",
            ),
            summary="Invalid actor.",
        )


def test_record_rejects_actor_without_identity(
    app,
    journal: JournalService,
) -> None:
    with pytest.raises(
        InvalidJournalReferenceError,
    ):
        journal.record(
            event_code="system.test_missing_identity",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor=JournalReferenceSpec(
                reference_type="system",
                display_name="Missing Identity",
            ),
            summary="Missing actor identity.",
        )


def test_record_rejects_conflicting_reference_identity(
    app,
    journal: JournalService,
) -> None:
    source_id = uuid.uuid4()

    journal.record(
        event_code="system.test_reference_created",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=JournalReferenceSpec(
            reference_type="integration",
            source_id=source_id,
            stable_key="test_integration:first",
            display_name="First Integration",
        ),
        summary="Reference created.",
    )

    with pytest.raises(
        JournalReferenceConflictError,
    ):
        journal.record(
            event_code="system.test_reference_conflict",
            occurred_at=datetime.now(
                timezone.utc
            ),
            actor=JournalReferenceSpec(
                reference_type="integration",
                source_id=source_id,
                stable_key="test_integration:second",
                display_name="Second Integration",
            ),
            summary="Reference conflict.",
        )


def test_journal_reference_spec_is_immutable() -> None:
    spec = actor_spec()

    with pytest.raises(
        AttributeError,
    ):
        spec.display_name = "Changed"  # type: ignore[misc]
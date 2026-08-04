"""Integration tests for Desk creation and the Event Journal."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy import select

from app.desks.commands import CreateDeskCommand
from app.desks.events import DeskJournalEvents
from app.desks.models import Desk
from app.desks.services import DeskService
from app.extensions import db
from app.journal import (
    JournalReferenceSpec,
    JournalService,
)
from app.journal.exceptions import JournalPersistenceError
from app.journal.models import (
    JournalEntry,
    JournalReference,
)


@pytest.fixture
def actor() -> JournalReferenceSpec:
    """Return the actor used by Desk Journal integration tests."""

    return JournalReferenceSpec.from_stable_key(
        reference_type="system",
        stable_key="test_system:desk_integration",
        display_name="Desk Integration Test",
    )


@pytest.fixture
def root_desk(
    app,
) -> Desk:
    """Create the organisation root without testing Journal integration."""

    root = Desk(
        code="organisation",
        name="Organisation",
        description="Organisation-wide operational root.",
        parent_id=None,
        is_root=True,
        is_active=True,
    )

    db.session.add(root)
    db.session.commit()

    return root


@pytest.fixture
def desk_service(
    app,
) -> DeskService:
    """Return a Desk service using the real public Journal service."""

    return DeskService(
        session=db.session,
        journal=JournalService(
            session=db.session,
        ),
    )


def create_operations_desk(
    *,
    service: DeskService,
    root: Desk,
    actor: JournalReferenceSpec,
) -> Desk:
    """Create the Desk used by the integration assertions."""

    return service.create(
        CreateDeskCommand(
            code="operations_control",
            name="Operations Control",
            description="Operational command and control.",
            parent_id=root.id,
        ),
        actor=actor,
    )


def journal_entries() -> list[JournalEntry]:
    """Return all Journal Entries in occurrence order."""

    return list(
        db.session.scalars(
            select(JournalEntry).order_by(
                JournalEntry.occurred_at,
                JournalEntry.id,
            )
        )
    )


def test_creating_desk_records_one_journal_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )

    entries = journal_entries()

    assert db.session.get(
        Desk,
        desk.id,
    ) is not None
    assert len(entries) == 1


def test_created_entry_uses_desk_created_event_code(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )

    entry = journal_entries()[0]

    assert entry.event_code == (
        DeskJournalEvents.CREATED
    )


def test_created_entry_records_actor_subject_and_desk(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )

    entry = journal_entries()[0]

    actor_reference = db.session.get(
        JournalReference,
        entry.actor_reference_id,
    )
    subject_reference = db.session.get(
        JournalReference,
        entry.subject_reference_id,
    )

    assert actor_reference is not None
    assert actor_reference.reference_type == "system"
    assert actor_reference.stable_key == (
        "test_system:desk_integration"
    )
    assert actor_reference.display_name == (
        "Desk Integration Test"
    )

    assert subject_reference is not None
    assert subject_reference.reference_type == "desk"
    assert subject_reference.source_id == desk.id
    assert subject_reference.display_name == (
        "Operations Control"
    )

    assert entry.context_reference_id is None
    assert entry.desk_id == desk.id
    assert entry.desk_display_name == (
        "Operations Control"
    )


def test_created_entry_uses_expected_summary(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )

    entry = journal_entries()[0]

    assert entry.summary == (
        "Desk 'Operations Control' was created."
    )


def test_journal_failure_rolls_back_desk_creation(
    app,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    journal = Mock(
        spec=JournalService,
    )
    journal.record.side_effect = (
        JournalPersistenceError(
            "The Journal Entry could not be recorded."
        )
    )

    service = DeskService(
        session=db.session,
        journal=journal,
    )

    with pytest.raises(
        JournalPersistenceError,
    ):
        service.create(
            CreateDeskCommand(
                code="failed_operations",
                name="Failed Operations",
                parent_id=root_desk.id,
            ),
            actor=actor,
        )

    db.session.expire_all()

    failed_desk = db.session.scalar(
        select(Desk).where(
            Desk.code == "failed_operations"
        )
    )

    assert failed_desk is None
    assert journal_entries() == []

    journal.record.assert_called_once()
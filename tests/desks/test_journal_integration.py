"""Integration tests for Desk creation and the Event Journal."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy import select

from app.desks.commands import (
    CreateDeskCommand,
    MoveDeskCommand,
    UpdateDeskCommand,
)
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

def create_child_desk(
    *,
    service: DeskService,
    parent: Desk,
    code: str,
    name: str,
    actor: JournalReferenceSpec,
) -> Desk:
    """Create a child Desk used by hierarchy integration tests."""

    return service.create(
        CreateDeskCommand(
            code=code,
            name=name,
            parent_id=parent.id,
        ),
        actor=actor,
    )

def create_lifecycle_desk(
    *,
    service: DeskService,
    root: Desk,
    actor: JournalReferenceSpec,
) -> Desk:
    """Create the Desk used by lifecycle integration tests."""

    return service.create(
        CreateDeskCommand(
            code="lifecycle_desk",
            name="Lifecycle Desk",
            description="Desk used for lifecycle tests.",
            parent_id=root.id,
        ),
        actor=actor,
    )


def commit_desk_state(
    desk: Desk,
    *,
    is_active: bool | None = None,
) -> None:
    """Persist direct test setup without emitting Journal events."""

    if is_active is not None:
        desk.is_active = is_active

    db.session.commit()


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

def journal_entries_for(
    event_code: str,
) -> list[JournalEntry]:
    """Return Journal Entries matching one event code."""

    return [
        entry
        for entry in journal_entries()
        if entry.event_code == event_code
    ]


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

def test_updating_desk_records_updated_entry(
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

    updated = desk_service.update(
        desk.id,
        UpdateDeskCommand(
            name="Operations Coordination",
            description="Updated command and control.",
        ),
        actor=actor,
    )

    entries = journal_entries_for(
        DeskJournalEvents.UPDATED
    )

    assert updated.name == (
        "Operations Coordination"
    )
    assert updated.description == (
        "Updated command and control."
    )
    assert len(entries) == 1


def test_updated_entry_uses_expected_summary(
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

    desk_service.update(
        desk.id,
        UpdateDeskCommand(
            name="Operations Coordination",
            description="Updated command and control.",
        ),
        actor=actor,
    )

    entry = journal_entries_for(
        DeskJournalEvents.UPDATED
    )[0]

    assert entry.summary == (
        "Desk 'Operations Coordination' was updated."
    )


def test_updated_entry_records_actor_subject_and_desk(
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

    desk_service.update(
        desk.id,
        UpdateDeskCommand(
            name="Operations Coordination",
            description="Updated command and control.",
        ),
        actor=actor,
    )

    entry = journal_entries_for(
        DeskJournalEvents.UPDATED
    )[0]

    actor_reference = db.session.get(
        JournalReference,
        entry.actor_reference_id,
    )
    subject_reference = db.session.get(
        JournalReference,
        entry.subject_reference_id,
    )

    assert actor_reference is not None
    assert actor_reference.stable_key == (
        "test_system:desk_integration"
    )

    assert subject_reference is not None
    assert subject_reference.reference_type == "desk"
    assert subject_reference.source_id == desk.id

    assert entry.context_reference_id is None
    assert entry.desk_id == desk.id
    assert entry.desk_display_name == (
        "Operations Coordination"
    )

def test_updated_entry_records_change_metadata(
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

    desk_service.update(
        desk.id,
        UpdateDeskCommand(
            name="Operations Coordination",
            description="Updated command and control.",
        ),
        actor=actor,
    )

    entry = journal_entries_for(
        DeskJournalEvents.UPDATED
    )[0]

    assert entry.event_metadata == {
        "changed_fields": [
            "name",
            "description",
        ],
        "previous": {
            "name": "Operations Control",
            "description": (
                "Operational command and control."
            ),
        },
        "current": {
            "name": "Operations Coordination",
            "description": (
                "Updated command and control."
            ),
        },
    }


def test_update_records_only_changed_fields(
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

    desk_service.update(
        desk.id,
        UpdateDeskCommand(
            name="Operations Coordination",
            description=desk.description,
        ),
        actor=actor,
    )

    entry = journal_entries_for(
        DeskJournalEvents.UPDATED
    )[0]

    assert entry.event_metadata == {
        "changed_fields": [
            "name",
        ],
        "previous": {
            "name": "Operations Control",
        },
        "current": {
            "name": "Operations Coordination",
        },
    }


def test_no_op_update_does_not_record_journal_entry(
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

    returned = desk_service.update(
        desk.id,
        UpdateDeskCommand(
            name=desk.name,
            description=desk.description,
        ),
        actor=actor,
    )

    assert returned.id == desk.id
    assert journal_entries_for(
        DeskJournalEvents.UPDATED
    ) == []


def test_journal_failure_rolls_back_desk_update(
    app,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    creation_service = DeskService(
        session=db.session,
        journal=JournalService(
            session=db.session,
        ),
    )

    desk = create_operations_desk(
        service=creation_service,
        root=root_desk,
        actor=actor,
    )
    desk_id = desk.id

    journal = Mock(
        spec=JournalService,
    )
    journal.record.side_effect = (
        JournalPersistenceError(
            "The Journal Entry could not be recorded."
        )
    )

    update_service = DeskService(
        session=db.session,
        journal=journal,
    )

    with pytest.raises(
        JournalPersistenceError,
    ):
        update_service.update(
            desk_id,
            UpdateDeskCommand(
                name="Failed Update",
                description="This must be rolled back.",
            ),
            actor=actor,
        )

    db.session.expire_all()

    persisted = db.session.get(
        Desk,
        desk_id,
    )

    assert persisted is not None
    assert persisted.name == "Operations Control"
    assert persisted.description == (
        "Operational command and control."
    )

    journal.record.assert_called_once()

def test_moving_desk_records_moved_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    operations = create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    patient_transport = create_child_desk(
        service=desk_service,
        parent=root_desk,
        code="patient_transport",
        name="Patient Transport",
        actor=actor,
    )
    control = create_child_desk(
        service=desk_service,
        parent=operations,
        code="control",
        name="Control",
        actor=actor,
    )

    moved = desk_service.move(
        control.id,
        MoveDeskCommand(
            parent_id=patient_transport.id,
        ),
        actor=actor,
    )

    entries = journal_entries_for(
        DeskJournalEvents.MOVED
    )

    assert moved.parent_id == patient_transport.id
    assert len(entries) == 1


def test_moved_entry_uses_expected_summary(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    operations = create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    patient_transport = create_child_desk(
        service=desk_service,
        parent=root_desk,
        code="patient_transport",
        name="Patient Transport",
        actor=actor,
    )
    control = create_child_desk(
        service=desk_service,
        parent=operations,
        code="control",
        name="Control",
        actor=actor,
    )

    desk_service.move(
        control.id,
        MoveDeskCommand(
            parent_id=patient_transport.id,
        ),
        actor=actor,
    )

    entry = journal_entries_for(
        DeskJournalEvents.MOVED
    )[0]

    assert entry.summary == (
        "Desk 'Control' was moved from "
        "'Operations Control' to 'Patient Transport'."
    )


def test_moved_entry_records_actor_subject_and_desk(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    operations = create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    patient_transport = create_child_desk(
        service=desk_service,
        parent=root_desk,
        code="patient_transport",
        name="Patient Transport",
        actor=actor,
    )
    control = create_child_desk(
        service=desk_service,
        parent=operations,
        code="control",
        name="Control",
        actor=actor,
    )

    desk_service.move(
        control.id,
        MoveDeskCommand(
            parent_id=patient_transport.id,
        ),
        actor=actor,
    )

    entry = journal_entries_for(
        DeskJournalEvents.MOVED
    )[0]

    actor_reference = db.session.get(
        JournalReference,
        entry.actor_reference_id,
    )
    subject_reference = db.session.get(
        JournalReference,
        entry.subject_reference_id,
    )

    assert actor_reference is not None
    assert actor_reference.stable_key == (
        "test_system:desk_integration"
    )

    assert subject_reference is not None
    assert subject_reference.reference_type == "desk"
    assert subject_reference.source_id == control.id

    assert entry.context_reference_id is None
    assert entry.desk_id == control.id
    assert entry.desk_display_name == "Control"


def test_moved_entry_records_parent_change_metadata(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    operations = create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    patient_transport = create_child_desk(
        service=desk_service,
        parent=root_desk,
        code="patient_transport",
        name="Patient Transport",
        actor=actor,
    )
    control = create_child_desk(
        service=desk_service,
        parent=operations,
        code="control",
        name="Control",
        actor=actor,
    )

    desk_service.move(
        control.id,
        MoveDeskCommand(
            parent_id=patient_transport.id,
        ),
        actor=actor,
    )

    entry = journal_entries_for(
        DeskJournalEvents.MOVED
    )[0]

    assert entry.event_metadata == {
        "changed_fields": [
            "parent_id",
        ],
        "previous": {
            "parent_id": str(operations.id),
            "parent_code": "operations_control",
            "parent_name": "Operations Control",
        },
        "current": {
            "parent_id": str(patient_transport.id),
            "parent_code": "patient_transport",
            "parent_name": "Patient Transport",
        },
    }


def test_move_to_current_parent_does_not_record_journal_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    operations = create_operations_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    control = create_child_desk(
        service=desk_service,
        parent=operations,
        code="control",
        name="Control",
        actor=actor,
    )

    returned = desk_service.move(
        control.id,
        MoveDeskCommand(
            parent_id=operations.id,
        ),
        actor=actor,
    )

    assert returned.parent_id == operations.id
    assert journal_entries_for(
        DeskJournalEvents.MOVED
    ) == []


def test_journal_failure_rolls_back_desk_move(
    app,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    creation_service = DeskService(
        session=db.session,
        journal=JournalService(
            session=db.session,
        ),
    )

    operations = create_operations_desk(
        service=creation_service,
        root=root_desk,
        actor=actor,
    )
    patient_transport = create_child_desk(
        service=creation_service,
        parent=root_desk,
        code="patient_transport",
        name="Patient Transport",
        actor=actor,
    )
    control = create_child_desk(
        service=creation_service,
        parent=operations,
        code="control",
        name="Control",
        actor=actor,
    )

    control_id = control.id
    original_parent_id = operations.id

    journal = Mock(
        spec=JournalService,
    )
    journal.record.side_effect = (
        JournalPersistenceError(
            "The Journal Entry could not be recorded."
        )
    )

    move_service = DeskService(
        session=db.session,
        journal=journal,
    )

    with pytest.raises(
        JournalPersistenceError,
    ):
        move_service.move(
            control_id,
            MoveDeskCommand(
                parent_id=patient_transport.id,
            ),
            actor=actor,
        )

    db.session.expire_all()

    persisted = db.session.get(
        Desk,
        control_id,
    )

    assert persisted is not None
    assert persisted.parent_id == original_parent_id

    journal.record.assert_called_once()

def test_activating_desk_records_activated_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_lifecycle_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    commit_desk_state(
        desk,
        is_active=False,
    )

    activated = desk_service.activate(
        desk.id,
        actor=actor,
    )

    entries = journal_entries_for(
        DeskJournalEvents.ACTIVATED
    )

    assert activated.is_active is True
    assert len(entries) == 1

    entry = entries[0]

    assert entry.summary == (
        "Desk 'Lifecycle Desk' was activated."
    )
    assert entry.desk_id == desk.id
    assert entry.desk_display_name == (
        "Lifecycle Desk"
    )
    assert entry.event_metadata == {
        "changed_fields": [
            "is_active",
        ],
        "previous": {
            "is_active": False,
        },
        "current": {
            "is_active": True,
        },
    }


def test_activating_active_desk_does_not_record_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_lifecycle_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )

    returned = desk_service.activate(
        desk.id,
        actor=actor,
    )

    assert returned.is_active is True
    assert journal_entries_for(
        DeskJournalEvents.ACTIVATED
    ) == []


def test_deactivating_desk_records_deactivated_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_lifecycle_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )

    deactivated = desk_service.deactivate(
        desk.id,
        actor=actor,
    )

    entries = journal_entries_for(
        DeskJournalEvents.DEACTIVATED
    )

    assert deactivated.is_active is False
    assert len(entries) == 1

    entry = entries[0]

    assert entry.summary == (
        "Desk 'Lifecycle Desk' was deactivated."
    )
    assert entry.desk_id == desk.id
    assert entry.event_metadata == {
        "changed_fields": [
            "is_active",
        ],
        "previous": {
            "is_active": True,
        },
        "current": {
            "is_active": False,
        },
    }


def test_deactivating_inactive_desk_does_not_record_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_lifecycle_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    commit_desk_state(
        desk,
        is_active=False,
    )

    returned = desk_service.deactivate(
        desk.id,
        actor=actor,
    )

    assert returned.is_active is False
    assert journal_entries_for(
        DeskJournalEvents.DEACTIVATED
    ) == []


def test_archiving_desk_records_archived_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_lifecycle_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    commit_desk_state(
        desk,
        is_active=False,
    )

    archived = desk_service.archive(
        desk.id,
        actor=actor,
    )

    entries = journal_entries_for(
        DeskJournalEvents.ARCHIVED
    )

    assert archived.archived_at is not None
    assert len(entries) == 1

    entry = entries[0]

    assert entry.summary == (
        "Desk 'Lifecycle Desk' was archived."
    )
    assert entry.desk_id == desk.id

    assert entry.event_metadata is not None
    assert entry.event_metadata[
        "changed_fields"
    ] == [
        "archived_at",
    ]
    assert entry.event_metadata[
        "previous"
    ] == {
        "archived_at": None,
    }
    assert entry.event_metadata[
        "current"
    ] == {
        "archived_at": (
            archived.archived_at.isoformat()
        ),
    }


def test_archiving_archived_desk_does_not_record_entry(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_lifecycle_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )
    commit_desk_state(
        desk,
        is_active=False,
    )

    desk_service.archive(
        desk.id,
        actor=actor,
    )

    original_entries = journal_entries_for(
        DeskJournalEvents.ARCHIVED
    )

    returned = desk_service.archive(
        desk.id,
        actor=actor,
    )

    assert returned.archived_at is not None
    assert len(
        journal_entries_for(
            DeskJournalEvents.ARCHIVED
        )
    ) == len(original_entries)


def test_lifecycle_entry_records_actor_subject_and_desk(
    app,
    desk_service: DeskService,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    desk = create_lifecycle_desk(
        service=desk_service,
        root=root_desk,
        actor=actor,
    )

    desk_service.deactivate(
        desk.id,
        actor=actor,
    )

    entry = journal_entries_for(
        DeskJournalEvents.DEACTIVATED
    )[0]

    actor_reference = db.session.get(
        JournalReference,
        entry.actor_reference_id,
    )
    subject_reference = db.session.get(
        JournalReference,
        entry.subject_reference_id,
    )

    assert actor_reference is not None
    assert actor_reference.stable_key == (
        "test_system:desk_integration"
    )

    assert subject_reference is not None
    assert subject_reference.reference_type == "desk"
    assert subject_reference.source_id == desk.id

    assert entry.context_reference_id is None
    assert entry.desk_id == desk.id
    assert entry.desk_display_name == (
        "Lifecycle Desk"
    )


def test_journal_failure_rolls_back_desk_deactivation(
    app,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    creation_service = DeskService(
        session=db.session,
        journal=JournalService(
            session=db.session,
        ),
    )

    desk = create_lifecycle_desk(
        service=creation_service,
        root=root_desk,
        actor=actor,
    )
    desk_id = desk.id

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
        service.deactivate(
            desk_id,
            actor=actor,
        )

    db.session.expire_all()

    persisted = db.session.get(
        Desk,
        desk_id,
    )

    assert persisted is not None
    assert persisted.is_active is True

    journal.record.assert_called_once()


def test_journal_failure_rolls_back_desk_archive(
    app,
    root_desk: Desk,
    actor: JournalReferenceSpec,
) -> None:
    creation_service = DeskService(
        session=db.session,
        journal=JournalService(
            session=db.session,
        ),
    )

    desk = create_lifecycle_desk(
        service=creation_service,
        root=root_desk,
        actor=actor,
    )
    desk.is_active = False
    db.session.commit()

    desk_id = desk.id

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
        service.archive(
            desk_id,
            actor=actor,
        )

    db.session.expire_all()

    persisted = db.session.get(
        Desk,
        desk_id,
    )

    assert persisted is not None
    assert persisted.archived_at is None

    journal.record.assert_called_once()
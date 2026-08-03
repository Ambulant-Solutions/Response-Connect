"""Tests for Journal Reference services."""

from __future__ import annotations

import uuid
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.journal.commands import (
    RegisterJournalReferenceCommand,
)
from app.journal.exceptions import (
    InvalidJournalReferenceError,
    JournalReferenceConflictError,
    JournalReferencePersistenceError,
)
from app.journal.models import JournalReference
from app.journal.services import (
    JournalReferenceService,
)


@pytest.fixture
def reference_service(
    app,
) -> JournalReferenceService:
    return JournalReferenceService(
        session=db.session,
    )


def test_get_or_create_creates_source_reference(
    app,
    reference_service: JournalReferenceService,
) -> None:
    source_id = uuid.uuid4()

    reference = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="vehicle",
            source_id=source_id,
            stable_key=None,
            display_name="Vehicle A12",
        )
    )

    assert isinstance(
        reference,
        JournalReference,
    )
    assert reference.id is not None
    assert reference.reference_type == "vehicle"
    assert reference.source_id == source_id
    assert reference.stable_key is None
    assert reference.display_name == "Vehicle A12"
    assert reference.created_at is not None


def test_get_or_create_creates_stable_key_reference(
    app,
    reference_service: JournalReferenceService,
) -> None:
    reference = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="system",
            source_id=None,
            stable_key="system",
            display_name="Response Connect",
        )
    )

    assert reference.reference_type == "system"
    assert reference.source_id is None
    assert reference.stable_key == "system"
    assert reference.display_name == (
        "Response Connect"
    )


def test_get_or_create_creates_reference_with_both_identities(
    app,
    reference_service: JournalReferenceService,
) -> None:
    source_id = uuid.uuid4()

    reference = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="integration",
            source_id=source_id,
            stable_key="integration:moodle",
            display_name="Moodle Integration",
        )
    )

    assert reference.source_id == source_id
    assert reference.stable_key == (
        "integration:moodle"
    )


def test_get_or_create_normalises_values(
    app,
    reference_service: JournalReferenceService,
) -> None:
    reference = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="  integration  ",
            source_id=None,
            stable_key="  integration:moodle  ",
            display_name="  Moodle Integration  ",
        )
    )

    assert reference.reference_type == (
        "integration"
    )
    assert reference.stable_key == (
        "integration:moodle"
    )
    assert reference.display_name == (
        "Moodle Integration"
    )


def test_repeated_source_registration_returns_same_reference(
    app,
    reference_service: JournalReferenceService,
) -> None:
    source_id = uuid.uuid4()

    first = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="vehicle",
            source_id=source_id,
            display_name="Vehicle A12",
        )
    )

    second = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="vehicle",
            source_id=source_id,
            display_name="Renamed Vehicle",
        )
    )

    assert second.id == first.id
    assert second.display_name == "Vehicle A12"

    references = (
        db.session.query(JournalReference)
        .filter(
            JournalReference.reference_type
            == "vehicle",
            JournalReference.source_id
            == source_id,
        )
        .all()
    )

    assert len(references) == 1


def test_repeated_stable_key_registration_returns_same_reference(
    app,
    reference_service: JournalReferenceService,
) -> None:
    first = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="scheduler",
            stable_key="scheduler:nightly",
            display_name="Nightly Scheduler",
        )
    )

    second = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="scheduler",
            stable_key="scheduler:nightly",
            display_name="Replacement Name",
        )
    )

    assert second.id == first.id
    assert second.display_name == (
        "Nightly Scheduler"
    )


def test_different_reference_types_may_share_source_id(
    app,
    reference_service: JournalReferenceService,
) -> None:
    source_id = uuid.uuid4()

    vehicle = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="vehicle",
            source_id=source_id,
            display_name="Vehicle A12",
        )
    )

    incident = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="incident",
            source_id=source_id,
            display_name="Incident 12",
        )
    )

    assert vehicle.id != incident.id


def test_different_reference_types_may_share_stable_key(
    app,
    reference_service: JournalReferenceService,
) -> None:
    system = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="system",
            stable_key="shared",
            display_name="System",
        )
    )

    integration = reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="integration",
            stable_key="shared",
            display_name="Integration",
        )
    )

    assert system.id != integration.id


def test_existing_source_with_different_stable_key_raises_conflict(
    app,
    reference_service: JournalReferenceService,
) -> None:
    source_id = uuid.uuid4()

    reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="integration",
            source_id=source_id,
            stable_key="integration:first",
            display_name="First Integration",
        )
    )

    with pytest.raises(
        JournalReferenceConflictError,
        match="stable key",
    ):
        reference_service.get_or_create(
            RegisterJournalReferenceCommand(
                reference_type="integration",
                source_id=source_id,
                stable_key="integration:second",
                display_name="Second Integration",
            )
        )


def test_existing_stable_key_with_different_source_raises_conflict(
    app,
    reference_service: JournalReferenceService,
) -> None:
    reference_service.get_or_create(
        RegisterJournalReferenceCommand(
            reference_type="integration",
            source_id=uuid.uuid4(),
            stable_key="integration:moodle",
            display_name="Moodle Integration",
        )
    )

    with pytest.raises(
        JournalReferenceConflictError,
        match="source",
    ):
        reference_service.get_or_create(
            RegisterJournalReferenceCommand(
                reference_type="integration",
                source_id=uuid.uuid4(),
                stable_key="integration:moodle",
                display_name="Other Integration",
            )
        )


@pytest.mark.parametrize(
    "command",
    [
        RegisterJournalReferenceCommand(
            reference_type="INVALID",
            source_id=uuid.uuid4(),
            display_name="Invalid",
        ),
        RegisterJournalReferenceCommand(
            reference_type="vehicle",
            source_id=None,
            stable_key=None,
            display_name="Vehicle",
        ),
        RegisterJournalReferenceCommand(
            reference_type="vehicle",
            source_id=uuid.uuid4(),
            display_name="   ",
        ),
        RegisterJournalReferenceCommand(
            reference_type="system",
            stable_key="Invalid Key",
            display_name="System",
        ),
    ],
)
def test_get_or_create_rejects_invalid_commands(
    app,
    reference_service: JournalReferenceService,
    command: RegisterJournalReferenceCommand,
) -> None:
    with pytest.raises(
        InvalidJournalReferenceError,
    ):
        reference_service.get_or_create(
            command
        )


def test_invalid_command_is_not_persisted(
    app,
) -> None:
    session = Mock()

    service = JournalReferenceService(
        session=session,
    )

    with pytest.raises(
        InvalidJournalReferenceError,
    ):
        service.get_or_create(
            RegisterJournalReferenceCommand(
                reference_type="INVALID",
                source_id=uuid.uuid4(),
                display_name="Invalid",
            )
        )

    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_persistence_failure_is_translated_and_rolled_back(
    app,
) -> None:
    session = Mock()

    session.scalar.return_value = None
    session.commit.side_effect = SQLAlchemyError(
        "Database failure"
    )

    service = JournalReferenceService(
        session=session,
    )

    with pytest.raises(
        JournalReferencePersistenceError,
        match="could not be registered",
    ):
        service.get_or_create(
            RegisterJournalReferenceCommand(
                reference_type="system",
                stable_key="system",
                display_name="Response Connect",
            )
        )

    session.add.assert_called_once()
    session.rollback.assert_called_once()
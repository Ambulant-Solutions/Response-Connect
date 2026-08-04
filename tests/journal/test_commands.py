"""Tests for immutable Event Journal commands."""

from __future__ import annotations

import uuid
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from app.journal.commands import (
    RecordJournalEntryCommand,
    RegisterJournalReferenceCommand,
)


def test_record_journal_entry_command_stores_required_fields() -> None:
    occurred_at = datetime.now(
        timezone.utc
    )
    actor_reference_id = uuid.uuid4()

    command = RecordJournalEntryCommand(
        event_code="system.test_recorded",
        occurred_at=occurred_at,
        actor_reference_id=actor_reference_id,
        summary="A test occurrence was recorded.",
    )

    assert command.event_code == (
        "system.test_recorded"
    )
    assert command.occurred_at == occurred_at
    assert command.actor_reference_id == (
        actor_reference_id
    )
    assert command.summary == (
        "A test occurrence was recorded."
    )


def test_record_journal_entry_command_defaults_optional_fields(
) -> None:
    command = RecordJournalEntryCommand(
        event_code="system.test_recorded",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor_reference_id=uuid.uuid4(),
        summary="A test occurrence was recorded.",
    )

    assert command.details is None
    assert command.subject_reference_id is None
    assert command.context_reference_id is None
    assert command.desk_id is None


def test_record_journal_entry_command_accepts_relationships(
) -> None:
    actor_reference_id = uuid.uuid4()
    subject_reference_id = uuid.uuid4()
    context_reference_id = uuid.uuid4()
    desk_id = uuid.uuid4()

    command = RecordJournalEntryCommand(
        event_code="vehicle.arrived_on_scene",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor_reference_id=actor_reference_id,
        subject_reference_id=subject_reference_id,
        context_reference_id=context_reference_id,
        desk_id=desk_id,
        summary="Vehicle A12 arrived on scene.",
        details="Arrival confirmed by control.",
    )

    assert command.actor_reference_id == (
        actor_reference_id
    )
    assert command.subject_reference_id == (
        subject_reference_id
    )
    assert command.context_reference_id == (
        context_reference_id
    )
    assert command.desk_id == desk_id
    assert command.details == (
        "Arrival confirmed by control."
    )


def test_record_journal_entry_command_is_immutable() -> None:
    command = RecordJournalEntryCommand(
        event_code="system.test_recorded",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor_reference_id=uuid.uuid4(),
        summary="A test occurrence was recorded.",
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        command.summary = "Changed"  # type: ignore[misc]


def test_register_journal_reference_command_stores_values(
) -> None:
    source_id = uuid.uuid4()

    command = RegisterJournalReferenceCommand(
        reference_type="vehicle",
        source_id=source_id,
        stable_key="vehicle:a12",
        display_name="Vehicle A12",
    )

    assert command.reference_type == "vehicle"
    assert command.source_id == source_id
    assert command.stable_key == "vehicle:a12"
    assert command.display_name == "Vehicle A12"


def test_register_journal_reference_command_defaults_optional_identity(
) -> None:
    command = RegisterJournalReferenceCommand(
        reference_type="system",
        stable_key="system",
        display_name="Response Connect",
    )

    assert command.source_id is None


def test_register_journal_reference_command_is_immutable(
) -> None:
    command = RegisterJournalReferenceCommand(
        reference_type="system",
        stable_key="system",
        display_name="Response Connect",
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        command.display_name = "Changed"  # type: ignore[misc]
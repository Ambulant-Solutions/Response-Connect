"""Tests for JournalReferenceSpec."""

from __future__ import annotations

import uuid

import pytest

from app.journal import JournalReferenceSpec


def test_from_source_creates_reference() -> None:
    source_id = uuid.uuid4()

    reference = JournalReferenceSpec.from_source(
        reference_type="desk",
        source_id=source_id,
        display_name="Operations",
    )

    assert reference.reference_type == "desk"
    assert reference.source_id == source_id
    assert reference.display_name == "Operations"
    assert reference.stable_key is None


def test_from_stable_key_creates_reference() -> None:
    reference = JournalReferenceSpec.from_stable_key(
        reference_type="system",
        stable_key="bootstrap",
        display_name="Bootstrap",
    )

    assert reference.reference_type == "system"
    assert reference.stable_key == "bootstrap"
    assert reference.display_name == "Bootstrap"
    assert reference.source_id is None


def test_reference_spec_is_immutable() -> None:
    reference = JournalReferenceSpec.from_stable_key(
        reference_type="system",
        stable_key="bootstrap",
        display_name="Bootstrap",
    )

    with pytest.raises(AttributeError):
        reference.display_name = "Changed"  # type: ignore[misc]


def test_from_source_requires_source_id() -> None:
    with pytest.raises(TypeError):
        JournalReferenceSpec.from_source(  # type: ignore[call-arg]
            reference_type="desk",
            display_name="Operations",
        )


def test_from_stable_key_requires_key() -> None:
    with pytest.raises(TypeError):
        JournalReferenceSpec.from_stable_key(  # type: ignore[call-arg]
            reference_type="system",
            display_name="Bootstrap",
        )
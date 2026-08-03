"""Tests for persistent Journal Reference models."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.journal.models import JournalReference


def create_source_reference(
    *,
    reference_type: str = "vehicle",
    source_id: uuid.UUID | None = None,
    display_name: str = "Vehicle A12",
) -> JournalReference:
    reference = JournalReference(
        reference_type=reference_type,
        source_id=source_id or uuid.uuid4(),
        stable_key=None,
        display_name=display_name,
    )

    db.session.add(reference)
    db.session.flush()

    return reference


def create_stable_key_reference(
    *,
    reference_type: str = "system",
    stable_key: str = "system",
    display_name: str = "Response Connect",
) -> JournalReference:
    reference = JournalReference(
        reference_type=reference_type,
        source_id=None,
        stable_key=stable_key,
        display_name=display_name,
    )

    db.session.add(reference)
    db.session.flush()

    return reference


def test_journal_reference_uses_uuid_identity(
    app,
) -> None:
    with app.app_context():
        reference = create_source_reference()

        assert isinstance(
            reference.id,
            uuid.UUID,
        )


def test_journal_reference_stores_source_identity(
    app,
) -> None:
    with app.app_context():
        source_id = uuid.uuid4()

        reference = create_source_reference(
            reference_type="vehicle",
            source_id=source_id,
            display_name="Vehicle A12",
        )

        assert reference.reference_type == "vehicle"
        assert reference.source_id == source_id
        assert reference.stable_key is None
        assert reference.display_name == "Vehicle A12"


def test_journal_reference_stores_stable_key_identity(
    app,
) -> None:
    with app.app_context():
        reference = create_stable_key_reference(
            reference_type="scheduler",
            stable_key="scheduler:nightly",
            display_name="Nightly Scheduler",
        )

        assert reference.reference_type == "scheduler"
        assert reference.source_id is None
        assert reference.stable_key == (
            "scheduler:nightly"
        )
        assert reference.display_name == (
            "Nightly Scheduler"
        )


def test_journal_reference_may_store_both_identity_values(
    app,
) -> None:
    with app.app_context():
        source_id = uuid.uuid4()

        reference = JournalReference(
            reference_type="integration",
            source_id=source_id,
            stable_key="integration:moodle",
            display_name="Moodle Integration",
        )

        db.session.add(reference)
        db.session.flush()

        assert reference.source_id == source_id
        assert reference.stable_key == (
            "integration:moodle"
        )


def test_journal_reference_requires_identity(
    app,
) -> None:
    with app.app_context():
        reference = JournalReference(
            reference_type="system",
            source_id=None,
            stable_key=None,
            display_name="Response Connect",
        )

        db.session.add(reference)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_reference_requires_reference_type(
    app,
) -> None:
    with app.app_context():
        reference = JournalReference(
            reference_type=None,  # type: ignore[arg-type]
            source_id=uuid.uuid4(),
            stable_key=None,
            display_name="Vehicle A12",
        )

        db.session.add(reference)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_reference_rejects_empty_reference_type(
    app,
) -> None:
    with app.app_context():
        reference = JournalReference(
            reference_type="",
            source_id=uuid.uuid4(),
            stable_key=None,
            display_name="Vehicle A12",
        )

        db.session.add(reference)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_reference_requires_display_name(
    app,
) -> None:
    with app.app_context():
        reference = JournalReference(
            reference_type="vehicle",
            source_id=uuid.uuid4(),
            stable_key=None,
            display_name=None,  # type: ignore[arg-type]
        )

        db.session.add(reference)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_reference_rejects_empty_display_name(
    app,
) -> None:
    with app.app_context():
        reference = JournalReference(
            reference_type="vehicle",
            source_id=uuid.uuid4(),
            stable_key=None,
            display_name="",
        )

        db.session.add(reference)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_source_identity_is_unique_within_reference_type(
    app,
) -> None:
    with app.app_context():
        source_id = uuid.uuid4()

        create_source_reference(
            reference_type="vehicle",
            source_id=source_id,
            display_name="Vehicle A12",
        )

        duplicate = JournalReference(
            reference_type="vehicle",
            source_id=source_id,
            stable_key=None,
            display_name="Renamed Vehicle",
        )

        db.session.add(duplicate)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_same_source_id_may_exist_for_different_reference_types(
    app,
) -> None:
    with app.app_context():
        source_id = uuid.uuid4()

        first = create_source_reference(
            reference_type="vehicle",
            source_id=source_id,
            display_name="Vehicle A12",
        )

        second = create_source_reference(
            reference_type="incident",
            source_id=source_id,
            display_name="Incident 12",
        )

        assert first.id != second.id


def test_stable_key_is_unique_within_reference_type(
    app,
) -> None:
    with app.app_context():
        create_stable_key_reference(
            reference_type="scheduler",
            stable_key="scheduler:nightly",
            display_name="Nightly Scheduler",
        )

        duplicate = JournalReference(
            reference_type="scheduler",
            source_id=None,
            stable_key="scheduler:nightly",
            display_name="Replacement Scheduler",
        )

        db.session.add(duplicate)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_same_stable_key_may_exist_for_different_reference_types(
    app,
) -> None:
    with app.app_context():
        first = create_stable_key_reference(
            reference_type="system",
            stable_key="shared",
            display_name="System Identity",
        )

        second = create_stable_key_reference(
            reference_type="integration",
            stable_key="shared",
            display_name="Integration Identity",
        )

        assert first.id != second.id


def test_stable_key_must_be_lowercase(
    app,
) -> None:
    with app.app_context():
        reference = JournalReference(
            reference_type="system",
            source_id=None,
            stable_key="System",
            display_name="Response Connect",
        )

        db.session.add(reference)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_journal_reference_sets_created_at(
    app,
) -> None:
    with app.app_context():
        reference = create_source_reference()

        db.session.refresh(reference)

        assert reference.created_at is not None


def test_journal_reference_repr_contains_identity_details(
    app,
) -> None:
    with app.app_context():
        reference = create_stable_key_reference(
            reference_type="system",
            stable_key="system",
            display_name="Response Connect",
        )

        representation = repr(reference)

        assert str(reference.id) in representation
        assert "system" in representation
        assert "Response Connect" in representation
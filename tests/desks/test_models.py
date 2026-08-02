from __future__ import annotations

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.desks.models import Desk
from app.extensions import db


def create_root_desk(
    *,
    code: str = "organisation",
    name: str = "Organisation",
) -> Desk:
    desk = Desk(
        code=code,
        name=name,
        is_root=True,
        parent_id=None,
    )

    db.session.add(desk)
    db.session.flush()

    return desk


def test_desk_uses_uuid_identity(
    app,
) -> None:
    with app.app_context():
        desk = create_root_desk()

        assert isinstance(
            desk.id,
            uuid.UUID,
        )


def test_root_desk_has_no_parent(
    app,
) -> None:
    with app.app_context():
        desk = create_root_desk()

        assert desk.is_root is True
        assert desk.parent_id is None
        assert desk.parent is None


def test_child_desk_belongs_to_parent(
    app,
) -> None:
    with app.app_context():
        root = create_root_desk()

        child = Desk(
            code="operations",
            name="Operations",
            parent=root,
            is_root=False,
        )

        db.session.add(child)
        db.session.flush()

        assert child.parent_id == root.id
        assert child.parent is root
        assert child in root.children


def test_desk_defaults_to_active(
    app,
) -> None:
    with app.app_context():
        root = create_root_desk()

        child = Desk(
            code="patient_transport",
            name="Patient Transport",
            parent=root,
        )

        db.session.add(child)
        db.session.flush()

        assert child.is_active is True
        assert child.is_root is False


def test_desk_code_must_be_unique(
    app,
) -> None:
    with app.app_context():
        root = create_root_desk()

        first = Desk(
            code="operations",
            name="Operations",
            parent=root,
        )
        second = Desk(
            code="operations",
            name="Other Operations",
            parent=root,
        )

        db.session.add_all(
            [
                first,
                second,
            ]
        )

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_only_one_root_desk_is_allowed(
    app,
) -> None:
    with app.app_context():
        create_root_desk()

        second_root = Desk(
            code="second_root",
            name="Second Root",
            is_root=True,
            parent_id=None,
        )

        db.session.add(second_root)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_root_desk_cannot_have_parent(
    app,
) -> None:
    with app.app_context():
        root = create_root_desk()

        invalid_root = Desk(
            code="invalid_root",
            name="Invalid Root",
            is_root=True,
            parent=root,
        )

        db.session.add(invalid_root)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_non_root_desk_requires_parent(
    app,
) -> None:
    with app.app_context():
        desk = Desk(
            code="orphan",
            name="Orphan Desk",
            is_root=False,
            parent_id=None,
        )

        db.session.add(desk)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_desk_cannot_be_its_own_parent(
    app,
) -> None:
    with app.app_context():
        root = create_root_desk()

        desk = Desk(
            code="operations",
            name="Operations",
            parent=root,
        )

        db.session.add(desk)
        db.session.flush()

        desk.parent_id = desk.id

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


def test_desk_reports_leaf_status(
    app,
) -> None:
    with app.app_context():
        root = create_root_desk()

        assert root.is_leaf is True

        child = Desk(
            code="operations",
            name="Operations",
            parent=root,
        )

        db.session.add(child)
        db.session.flush()

        assert root.is_leaf is False
        assert child.is_leaf is True


def test_desk_repr_contains_code_and_name(
    app,
) -> None:
    with app.app_context():
        desk = create_root_desk(
            code="company",
            name="Company Operations",
        )

        representation = repr(desk)

        assert "company" in representation
        assert "Company Operations" in representation
"""Tests for Desk hierarchy mutations."""

from __future__ import annotations

import pytest

from app.desks.commands import MoveDeskCommand
from app.desks.exceptions import DeskHierarchyError
from app.desks.models import Desk
from app.desks.services import DeskService
from app.extensions import db


@pytest.fixture
def desk_service(
    app,
) -> DeskService:
    return DeskService(
        session=db.session,
    )


def create_root() -> Desk:
    root = Desk(
        code="organisation",
        name="Organisation",
        is_root=True,
        parent_id=None,
    )
    db.session.add(root)
    db.session.flush()
    return root


def create_child(
    *,
    parent: Desk,
    code: str,
    name: str,
) -> Desk:
    desk = Desk(
        code=code,
        name=name,
        parent=parent,
        is_root=False,
    )
    db.session.add(desk)
    db.session.flush()
    return desk


def test_move_desk(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()
    operations = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )
    fleet = create_child(
        parent=root,
        code="fleet",
        name="Fleet",
    )
    child = create_child(
        parent=operations,
        code="resources",
        name="Resources",
    )

    moved = desk_service.move(
        child.id,
        MoveDeskCommand(
            parent_id=fleet.id,
        ),
    )

    assert moved.parent_id == fleet.id
    assert moved.parent is fleet


def test_root_desk_cannot_be_moved(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()
    child = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    with pytest.raises(
        DeskHierarchyError,
        match="root",
    ):
        desk_service.move(
            root.id,
            MoveDeskCommand(
                parent_id=child.id,
            ),
        )


def test_desk_cannot_move_beneath_itself(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()
    desk = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    with pytest.raises(
        DeskHierarchyError,
        match="itself",
    ):
        desk_service.move(
            desk.id,
            MoveDeskCommand(
                parent_id=desk.id,
            ),
        )


def test_desk_cannot_move_beneath_descendant(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()
    operations = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )
    patient_transport = create_child(
        parent=operations,
        code="patient_transport",
        name="Patient Transport",
    )
    devon = create_child(
        parent=patient_transport,
        code="devon_pts",
        name="Devon Patient Transport",
    )

    with pytest.raises(
        DeskHierarchyError,
        match="descendant",
    ):
        desk_service.move(
            operations.id,
            MoveDeskCommand(
                parent_id=devon.id,
            ),
        )


def test_move_to_current_parent_is_idempotent(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()
    operations = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    moved = desk_service.move(
        operations.id,
        MoveDeskCommand(
            parent_id=root.id,
        ),
    )

    assert moved.parent_id == root.id
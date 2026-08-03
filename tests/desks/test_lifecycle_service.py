"""Tests for Desk lifecycle transitions."""

from __future__ import annotations

import pytest

from app.desks.exceptions import (
    DeskLifecycleError,
)
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
    is_active: bool = True,
) -> Desk:
    desk = Desk(
        code=code,
        name=name,
        parent=parent,
        is_root=False,
        is_active=is_active,
    )

    db.session.add(desk)
    db.session.flush()

    return desk


def test_deactivate_desk(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    desk = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    result = desk_service.deactivate(
        desk.id
    )

    assert result.id == desk.id
    assert result.is_active is False
    assert result.archived_at is None


def test_deactivate_is_idempotent(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    desk = create_child(
        parent=root,
        code="operations",
        name="Operations",
        is_active=False,
    )

    result = desk_service.deactivate(
        desk.id
    )

    assert result.is_active is False


def test_root_desk_cannot_be_deactivated(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    with pytest.raises(
        DeskLifecycleError,
        match="root",
    ):
        desk_service.deactivate(
            root.id
        )


def test_desk_with_active_child_cannot_be_deactivated(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    parent = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    create_child(
        parent=parent,
        code="patient_transport",
        name="Patient Transport",
    )

    with pytest.raises(
        DeskLifecycleError,
        match="active child",
    ):
        desk_service.deactivate(
            parent.id
        )


def test_activate_desk(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    desk = create_child(
        parent=root,
        code="operations",
        name="Operations",
        is_active=False,
    )

    result = desk_service.activate(
        desk.id
    )

    assert result.is_active is True
    assert result.archived_at is None


def test_activate_is_idempotent(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    desk = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    result = desk_service.activate(
        desk.id
    )

    assert result.is_active is True


def test_cannot_activate_beneath_inactive_parent(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    parent = create_child(
        parent=root,
        code="operations",
        name="Operations",
        is_active=False,
    )

    child = create_child(
        parent=parent,
        code="patient_transport",
        name="Patient Transport",
        is_active=False,
    )

    with pytest.raises(
        DeskLifecycleError,
        match="inactive parent",
    ):
        desk_service.activate(
            child.id
        )


def test_archive_inactive_desk(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    desk = create_child(
        parent=root,
        code="operations",
        name="Operations",
        is_active=False,
    )

    result = desk_service.archive(
        desk.id
    )

    assert result.is_active is False
    assert result.archived_at is not None
    assert result.is_archived is True


def test_archive_is_idempotent(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    desk = create_child(
        parent=root,
        code="operations",
        name="Operations",
        is_active=False,
    )

    first = desk_service.archive(
        desk.id
    )
    first_archived_at = first.archived_at

    second = desk_service.archive(
        desk.id
    )

    assert second.archived_at == (
        first_archived_at
    )


def test_active_desk_cannot_be_archived(
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
        DeskLifecycleError,
        match="deactivated",
    ):
        desk_service.archive(
            desk.id
        )


def test_root_desk_cannot_be_archived(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    with pytest.raises(
        DeskLifecycleError,
        match="root",
    ):
        desk_service.archive(
            root.id
        )


def test_desk_with_unarchived_child_cannot_be_archived(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    parent = create_child(
        parent=root,
        code="operations",
        name="Operations",
        is_active=False,
    )

    create_child(
        parent=parent,
        code="patient_transport",
        name="Patient Transport",
        is_active=False,
    )

    with pytest.raises(
        DeskLifecycleError,
        match="unarchived child",
    ):
        desk_service.archive(
            parent.id
        )


def test_archived_desk_cannot_be_activated(
    app,
    desk_service: DeskService,
) -> None:
    root = create_root()

    desk = create_child(
        parent=root,
        code="operations",
        name="Operations",
        is_active=False,
    )

    desk_service.archive(
        desk.id
    )

    with pytest.raises(
        DeskLifecycleError,
        match="archived",
    ):
        desk_service.activate(
            desk.id
        )
"""Tests for Desk mutation services."""

from __future__ import annotations

import uuid

import pytest

from app.desks.commands import (
    CreateDeskCommand,
    UpdateDeskCommand,
)
from app.desks.exceptions import (
    DeskConflictError,
    DeskNotFoundError,
    InvalidDeskError,
)
from app.desks.models import Desk
from app.desks.services import DeskService
from app.extensions import db


@pytest.fixture
def desk_service(
    app,
) -> DeskService:
    """
    Return a Desk service using the application database session.

    The app fixture provides the active Flask application context and
    performs Desk cleanup between tests.
    """

    return DeskService(
        session=db.session,
    )


def test_bootstrap_root_creates_root_desk(
    app,
    desk_service: DeskService,
) -> None:
    root = desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
        description=(
            "Organisation-wide operational root."
        ),
    )

    assert isinstance(root, Desk)
    assert isinstance(root.id, uuid.UUID)
    assert root.code == "organisation"
    assert root.name == "Organisation"
    assert root.description == (
        "Organisation-wide operational root."
    )
    assert root.is_root is True
    assert root.is_active is True
    assert root.parent_id is None


def test_bootstrap_root_is_idempotent(
    app,
    desk_service: DeskService,
) -> None:
    first = desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
    )

    second = desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
    )

    assert second.id == first.id

    roots = (
        db.session.query(Desk)
        .filter(
            Desk.is_root.is_(True)
        )
        .all()
    )

    assert len(roots) == 1


def test_bootstrap_root_returns_existing_root_without_overwriting_it(
    app,
    desk_service: DeskService,
) -> None:
    original = desk_service.bootstrap_root(
        code="organisation",
        name="Original Organisation",
        description="Original description.",
    )

    returned = desk_service.bootstrap_root(
        code="different_code",
        name="Different Organisation",
        description="Replacement description.",
    )

    assert returned.id == original.id
    assert returned.code == "organisation"
    assert returned.name == "Original Organisation"
    assert returned.description == (
        "Original description."
    )


def test_create_desk(
    app,
    desk_service: DeskService,
) -> None:
    root = desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
    )

    command = CreateDeskCommand(
        code="operations",
        name="Operations",
        description="Operational services.",
        parent_id=root.id,
    )

    desk = desk_service.create(command)

    assert isinstance(desk, Desk)
    assert desk.code == "operations"
    assert desk.name == "Operations"
    assert desk.description == (
        "Operational services."
    )
    assert desk.parent_id == root.id
    assert desk.is_root is False
    assert desk.is_active is True


def test_create_normalises_desk_values(
    app,
    desk_service: DeskService,
) -> None:
    root = desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
    )

    desk = desk_service.create(
        CreateDeskCommand(
            code="  PATIENT_TRANSPORT  ",
            name="  Patient Transport  ",
            description="  Transport operations.  ",
            parent_id=root.id,
        )
    )

    assert desk.code == "patient_transport"
    assert desk.name == "Patient Transport"
    assert desk.description == (
        "Transport operations."
    )


def test_create_duplicate_code_raises_conflict(
    app,
    desk_service: DeskService,
) -> None:
    root = desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
    )

    desk_service.create(
        CreateDeskCommand(
            code="operations",
            name="Operations",
            parent_id=root.id,
        )
    )

    with pytest.raises(
        DeskConflictError,
        match="code",
    ):
        desk_service.create(
            CreateDeskCommand(
                code="OPERATIONS",
                name="Other Operations",
                parent_id=root.id,
            )
        )


def test_create_missing_parent_raises_not_found(
    app,
    desk_service: DeskService,
) -> None:
    missing_parent_id = uuid.uuid4()

    with pytest.raises(
        DeskNotFoundError,
        match="parent",
    ):
        desk_service.create(
            CreateDeskCommand(
                code="operations",
                name="Operations",
                parent_id=missing_parent_id,
            )
        )


def test_create_non_root_requires_parent(
    app,
    desk_service: DeskService,
) -> None:
    with pytest.raises(
        InvalidDeskError,
        match="parent",
    ):
        desk_service.create(
            CreateDeskCommand(
                code="operations",
                name="Operations",
                parent_id=None,
                is_root=False,
            )
        )


def test_create_cannot_create_second_root(
    app,
    desk_service: DeskService,
) -> None:
    desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
    )

    with pytest.raises(
        DeskConflictError,
        match="root",
    ):
        desk_service.create(
            CreateDeskCommand(
                code="second_root",
                name="Second Root",
                parent_id=None,
                is_root=True,
            )
        )


def test_update_desk(
    app,
    desk_service: DeskService,
) -> None:
    root = desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
    )

    desk = desk_service.create(
        CreateDeskCommand(
            code="operations",
            name="Operations",
            description="Original description.",
            parent_id=root.id,
        )
    )

    updated = desk_service.update(
        desk.id,
        UpdateDeskCommand(
            name="Operational Services",
            description="Updated description.",
        ),
    )

    assert updated.id == desk.id
    assert updated.code == "operations"
    assert updated.name == (
        "Operational Services"
    )
    assert updated.description == (
        "Updated description."
    )
    assert updated.parent_id == root.id


def test_update_normalises_editable_values(
    app,
    desk_service: DeskService,
) -> None:
    root = desk_service.bootstrap_root(
        code="organisation",
        name="Organisation",
    )

    desk = desk_service.create(
        CreateDeskCommand(
            code="operations",
            name="Operations",
            parent_id=root.id,
        )
    )

    updated = desk_service.update(
        desk.id,
        UpdateDeskCommand(
            name="  Operational Services  ",
            description="   ",
        ),
    )

    assert updated.name == (
        "Operational Services"
    )
    assert updated.description is None


def test_update_unknown_desk_raises_not_found(
    app,
    desk_service: DeskService,
) -> None:
    with pytest.raises(
        DeskNotFoundError,
    ):
        desk_service.update(
            uuid.uuid4(),
            UpdateDeskCommand(
                name="Unknown Desk",
            ),
        )
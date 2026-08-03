"""Tests for Desk query services."""

from __future__ import annotations

import uuid

import pytest

from app.desks.exceptions import (
    DeskNotFoundError,
    InvalidDeskError,
)
from app.desks.models import Desk
from app.desks.queries import DeskQueryService
from app.extensions import db


@pytest.fixture
def desk_queries(
    app,
) -> DeskQueryService:
    return DeskQueryService(
        session=db.session,
    )


def create_root(
    *,
    code: str = "organisation",
    name: str = "Organisation",
) -> Desk:
    root = Desk(
        code=code,
        name=name,
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


def test_get_returns_existing_desk(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root()

    result = desk_queries.get(root.id)

    assert result is root


def test_get_unknown_desk_raises_not_found(
    app,
    desk_queries: DeskQueryService,
) -> None:
    with pytest.raises(
        DeskNotFoundError,
    ):
        desk_queries.get(
            uuid.uuid4()
        )


def test_find_by_code_returns_existing_desk(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root(
        code="company",
        name="Company",
    )

    result = desk_queries.find_by_code(
        "  COMPANY  "
    )

    assert result is root


def test_find_by_code_returns_none_when_missing(
    app,
    desk_queries: DeskQueryService,
) -> None:
    create_root()

    result = desk_queries.find_by_code(
        "missing"
    )

    assert result is None


def test_get_by_code_returns_existing_desk(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root(
        code="company",
        name="Company",
    )

    result = desk_queries.get_by_code(
        "company"
    )

    assert result is root


def test_get_by_code_raises_when_missing(
    app,
    desk_queries: DeskQueryService,
) -> None:
    create_root()

    with pytest.raises(
        DeskNotFoundError,
        match="missing",
    ):
        desk_queries.get_by_code(
            "missing"
        )


def test_exists_returns_true_for_existing_desk(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root()

    assert desk_queries.exists(
        root.id
    ) is True


def test_exists_returns_false_for_unknown_desk(
    app,
    desk_queries: DeskQueryService,
) -> None:
    assert desk_queries.exists(
        uuid.uuid4()
    ) is False


def test_list_returns_root_first_then_name_order(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root()

    create_child(
        parent=root,
        code="training",
        name="Training",
    )
    create_child(
        parent=root,
        code="fleet",
        name="Fleet",
    )
    create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    results = desk_queries.list()

    assert [
        desk.code
        for desk in results
    ] == [
        "organisation",
        "fleet",
        "operations",
        "training",
    ]


def test_list_active_only_excludes_inactive_desks(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root()

    create_child(
        parent=root,
        code="active",
        name="Active Desk",
        is_active=True,
    )
    create_child(
        parent=root,
        code="inactive",
        name="Inactive Desk",
        is_active=False,
    )

    results = desk_queries.list(
        active_only=True
    )

    assert {
        desk.code
        for desk in results
    } == {
        "organisation",
        "active",
    }


def test_children_returns_immediate_children_only(
    app,
    desk_queries: DeskQueryService,
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

    create_child(
        parent=operations,
        code="devon_pts",
        name="Devon Patient Transport",
    )

    results = desk_queries.children(
        root.id
    )

    assert [
        desk.code
        for desk in results
    ] == [
        "fleet",
        "operations",
    ]


def test_children_active_only_excludes_inactive_children(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root()

    create_child(
        parent=root,
        code="active",
        name="Active Desk",
        is_active=True,
    )
    create_child(
        parent=root,
        code="inactive",
        name="Inactive Desk",
        is_active=False,
    )

    results = desk_queries.children(
        root.id,
        active_only=True,
    )

    assert [
        desk.code
        for desk in results
    ] == [
        "active",
    ]


def test_children_unknown_parent_raises_not_found(
    app,
    desk_queries: DeskQueryService,
) -> None:
    with pytest.raises(
        DeskNotFoundError,
    ):
        desk_queries.children(
            uuid.uuid4()
        )


def test_path_returns_root_to_requested_desk(
    app,
    desk_queries: DeskQueryService,
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

    results = desk_queries.path(
        devon.id
    )

    assert [
        desk.code
        for desk in results
    ] == [
        "organisation",
        "operations",
        "patient_transport",
        "devon_pts",
    ]


def test_path_for_root_contains_only_root(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root()

    assert desk_queries.path(
        root.id
    ) == [
        root,
    ]

def test_descendants_returns_all_descendants(
    app,
    desk_queries: DeskQueryService,
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
    create_child(
        parent=root,
        code="fleet",
        name="Fleet",
    )

    results = desk_queries.descendants(
        operations.id
    )

    assert {
        desk.code
        for desk in results
    } == {
        "patient_transport",
        "devon_pts",
    }


def test_descendants_excludes_parent(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root()

    operations = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    results = desk_queries.descendants(
        operations.id
    )

    assert operations not in results


def test_descendants_active_only_excludes_inactive(
    app,
    desk_queries: DeskQueryService,
) -> None:
    root = create_root()

    operations = create_child(
        parent=root,
        code="operations",
        name="Operations",
    )

    active = create_child(
        parent=operations,
        code="active",
        name="Active",
        is_active=True,
    )
    create_child(
        parent=operations,
        code="inactive",
        name="Inactive",
        is_active=False,
    )

    results = desk_queries.descendants(
        operations.id,
        active_only=True,
    )

    assert results == [active]


def test_descendants_unknown_desk_raises_not_found(
    app,
    desk_queries: DeskQueryService,
) -> None:
    with pytest.raises(
        DeskNotFoundError,
    ):
        desk_queries.descendants(
            uuid.uuid4()
        )
"""Tests for reading Event Journal Entries."""

from __future__ import annotations

import uuid
from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from app.desks.models import Desk
from app.extensions import db
from app.journal import (
    JournalReferenceSpec,
    JournalService,
)
from app.journal.exceptions import (
    InvalidJournalEntryError,
    JournalEntryNotFoundError,
)
from app.journal.models import JournalEntry
from app.journal.queries import (
    JournalQueryService,
    MAX_TIMELINE_LIMIT,
)


@pytest.fixture
def journal(
    app,
) -> JournalService:
    return JournalService(
        session=db.session,
    )


@pytest.fixture
def query_service(
    app,
) -> JournalQueryService:
    return JournalQueryService(
        session=db.session,
    )


def actor_spec(
    name: str,
) -> JournalReferenceSpec:
    stable_name = "_".join(
        name.strip()
        .lower()
        .split()
    )

    return JournalReferenceSpec.from_stable_key(
        reference_type="system",
        stable_key=(
            f"test_system:query:{stable_name}"
        ),
        display_name=name,
    )


def create_desk(
    *,
    code: str,
    name: str,
    parent: Desk | None = None,
) -> Desk:
    desk = Desk(
        code=code,
        name=name,
        parent=parent,
        is_root=parent is None,
        is_active=True,
    )

    db.session.add(desk)
    db.session.commit()

    return desk


def record_entry(
    *,
    journal: JournalService,
    event_code: str,
    occurred_at: datetime,
    actor: JournalReferenceSpec,
    summary: str,
    desk: Desk | None = None,
    subject: JournalReferenceSpec | None = None,
    context: JournalReferenceSpec | None = None,
) -> JournalEntry:
    return journal.record(
        event_code=event_code,
        occurred_at=occurred_at,
        actor=actor,
        subject=subject,
        context=context,
        desk_id=(
            desk.id
            if desk is not None
            else None
        ),
        summary=summary,
    )


def test_get_returns_entry_with_relationships(
    app,
    journal: JournalService,
    query_service: JournalQueryService,
) -> None:
    root = create_desk(
        code="query_root",
        name="Query Root",
    )

    entry = record_entry(
        journal=journal,
        event_code="desk.created",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec("Actor One"),
        subject=JournalReferenceSpec.from_source(
            reference_type="desk",
            source_id=root.id,
            display_name=root.name,
        ),
        desk=root,
        summary="Query Root was created.",
    )

    returned = query_service.get(
        entry.id
    )

    assert returned.id == entry.id
    assert returned.actor_reference is not None
    assert returned.subject_reference is not None
    assert returned.desk is not None


def test_get_unknown_entry_raises_not_found(
    app,
    query_service: JournalQueryService,
) -> None:
    with pytest.raises(
        JournalEntryNotFoundError,
    ):
        query_service.get(
            uuid.uuid4()
        )


def test_timeline_returns_newest_first(
    app,
    journal: JournalService,
    query_service: JournalQueryService,
) -> None:
    now = datetime.now(
        timezone.utc
    )

    record_entry(
        journal=journal,
        event_code="system.test_first",
        occurred_at=now - timedelta(minutes=2),
        actor=actor_spec("Ordering"),
        summary="First.",
    )

    record_entry(
        journal=journal,
        event_code="system.test_second",
        occurred_at=now - timedelta(minutes=1),
        actor=actor_spec("Ordering"),
        summary="Second.",
    )

    entries = query_service.timeline()

    assert [
        entry.summary
        for entry in entries
    ] == [
        "Second.",
        "First.",
    ]


def test_timeline_filters_by_desk(
    app,
    journal: JournalService,
    query_service: JournalQueryService,
) -> None:
    root = create_desk(
        code="timeline_root",
        name="Timeline Root",
    )
    child = create_desk(
        code="timeline_child",
        name="Timeline Child",
        parent=root,
    )

    record_entry(
        journal=journal,
        event_code="desk.updated",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec("Desk Filter"),
        desk=root,
        summary="Root entry.",
    )

    record_entry(
        journal=journal,
        event_code="desk.updated",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec("Desk Filter"),
        desk=child,
        summary="Child entry.",
    )

    entries = query_service.timeline(
        desk_id=child.id
    )

    assert [
        entry.summary
        for entry in entries
    ] == [
        "Child entry.",
    ]


def test_timeline_filters_by_actor_subject_and_context(
    app,
    journal: JournalService,
    query_service: JournalQueryService,
) -> None:
    actor = actor_spec(
        "Relationship Filter"
    )
    subject = JournalReferenceSpec.from_source(
        reference_type="vehicle",
        source_id=uuid.uuid4(),
        display_name="Vehicle A12",
    )
    context = JournalReferenceSpec.from_source(
        reference_type="incident",
        source_id=uuid.uuid4(),
        display_name="Incident 001",
    )

    matching = record_entry(
        journal=journal,
        event_code="vehicle.updated",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor,
        subject=subject,
        context=context,
        summary="Matching entry.",
    )

    entries = query_service.timeline(
        actor_reference_id=(
            matching.actor_reference_id
        ),
        subject_reference_id=(
            matching.subject_reference_id
        ),
        context_reference_id=(
            matching.context_reference_id
        ),
    )

    assert [
        entry.id
        for entry in entries
    ] == [
        matching.id,
    ]


def test_timeline_filters_by_event_codes(
    app,
    journal: JournalService,
    query_service: JournalQueryService,
) -> None:
    actor = actor_spec(
        "Event Filter"
    )
    now = datetime.now(
        timezone.utc
    )

    record_entry(
        journal=journal,
        event_code="desk.created",
        occurred_at=now,
        actor=actor,
        summary="Created.",
    )

    record_entry(
        journal=journal,
        event_code="desk.updated",
        occurred_at=now,
        actor=actor,
        summary="Updated.",
    )

    entries = query_service.timeline(
        event_codes=[
            "desk.updated",
        ]
    )

    assert [
        entry.summary
        for entry in entries
    ] == [
        "Updated.",
    ]


def test_timeline_filters_by_date_range(
    app,
    journal: JournalService,
    query_service: JournalQueryService,
) -> None:
    actor = actor_spec(
        "Date Filter"
    )
    now = datetime.now(
        timezone.utc
    )

    record_entry(
        journal=journal,
        event_code="system.test_old",
        occurred_at=now - timedelta(days=2),
        actor=actor,
        summary="Old.",
    )

    record_entry(
        journal=journal,
        event_code="system.test_current",
        occurred_at=now,
        actor=actor,
        summary="Current.",
    )

    entries = query_service.timeline(
        occurred_from=(
            now - timedelta(hours=1)
        ),
        occurred_to=(
            now + timedelta(hours=1)
        ),
    )

    assert [
        entry.summary
        for entry in entries
    ] == [
        "Current.",
    ]


def test_timeline_applies_limit(
    app,
    journal: JournalService,
    query_service: JournalQueryService,
) -> None:
    actor = actor_spec(
        "Limit"
    )
    now = datetime.now(
        timezone.utc
    )

    for index in range(3):
        record_entry(
            journal=journal,
            event_code="system.test_limit",
            occurred_at=(
                now
                + timedelta(seconds=index)
            ),
            actor=actor,
            summary=f"Entry {index}.",
        )

    entries = query_service.timeline(
        limit=2
    )

    assert len(entries) == 2


@pytest.mark.parametrize(
    "limit",
    [
        0,
        -1,
        MAX_TIMELINE_LIMIT + 1,
        True,
        1.5,
    ],
)
def test_timeline_rejects_invalid_limit(
    app,
    query_service: JournalQueryService,
    limit,
) -> None:
    with pytest.raises(
        ValueError,
    ):
        query_service.timeline(
            limit=limit
        )


def test_timeline_rejects_invalid_event_code(
    app,
    query_service: JournalQueryService,
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
    ):
        query_service.timeline(
            event_codes=[
                "INVALID",
            ]
        )


def test_timeline_rejects_naive_date_filter(
    app,
    query_service: JournalQueryService,
) -> None:
    with pytest.raises(
        ValueError,
        match="timezone",
    ):
        query_service.timeline(
            occurred_from=datetime.now()
        )


def test_timeline_rejects_reversed_date_range(
    app,
    query_service: JournalQueryService,
) -> None:
    now = datetime.now(
        timezone.utc
    )

    with pytest.raises(
        ValueError,
    ):
        query_service.timeline(
            occurred_from=now,
            occurred_to=(
                now - timedelta(hours=1)
            ),
        )


def test_public_service_exposes_get_and_timeline(
    app,
    journal: JournalService,
) -> None:
    entry = record_entry(
        journal=journal,
        event_code="system.test_public_query",
        occurred_at=datetime.now(
            timezone.utc
        ),
        actor=actor_spec(
            "Public Query"
        ),
        summary="Public query entry.",
    )

    returned = journal.get_entry(
        entry.id
    )
    timeline = journal.timeline(
        event_codes=[
            "system.test_public_query",
        ]
    )

    assert returned.id == entry.id
    assert [
        item.id
        for item in timeline
    ] == [
        entry.id,
    ]
"""Internal query service for the Event Journal."""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.journal.exceptions import (
    JournalEntryNotFoundError,
)
from app.journal.models import JournalEntry
from app.journal.validators import (
    validate_event_code,
)


DEFAULT_TIMELINE_LIMIT = 50
MAX_TIMELINE_LIMIT = 100


class JournalQueryService:
    """Read immutable Journal Entries."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session
        

    def get(
        self,
        entry_id: uuid.UUID,
    ) -> JournalEntry:
        """Return one Journal Entry with display relationships loaded."""

        entry = self.session.scalar(
            self._base_query().where(
                JournalEntry.id == entry_id
            )
        )

        if entry is None:
            raise JournalEntryNotFoundError(
                "The Journal Entry could not be found."
            )

        return entry

    def timeline(
        self,
        *,
        desk_id: uuid.UUID | None = None,
        actor_reference_id: uuid.UUID | None = None,
        subject_reference_id: uuid.UUID | None = None,
        context_reference_id: uuid.UUID | None = None,
        event_codes: Iterable[str] | None = None,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
        limit: int = DEFAULT_TIMELINE_LIMIT,
    ) -> list[JournalEntry]:
        """Return a filtered newest-first Journal timeline."""

        validated_limit = self._validate_limit(
            limit
        )

        query = self._base_query()

        if desk_id is not None:
            query = query.where(
                JournalEntry.desk_id == desk_id
            )

        if actor_reference_id is not None:
            query = query.where(
                JournalEntry.actor_reference_id
                == actor_reference_id
            )

        if subject_reference_id is not None:
            query = query.where(
                JournalEntry.subject_reference_id
                == subject_reference_id
            )

        if context_reference_id is not None:
            query = query.where(
                JournalEntry.context_reference_id
                == context_reference_id
            )

        validated_event_codes = (
            self._validate_event_codes(
                event_codes
            )
        )

        if validated_event_codes:
            query = query.where(
                JournalEntry.event_code.in_(
                    validated_event_codes
                )
            )

        if occurred_from is not None:
            self._validate_datetime(
                occurred_from,
                field_name="occurred_from",
            )

            query = query.where(
                JournalEntry.occurred_at
                >= occurred_from
            )

        if occurred_to is not None:
            self._validate_datetime(
                occurred_to,
                field_name="occurred_to",
            )

            query = query.where(
                JournalEntry.occurred_at
                <= occurred_to
            )

        if (
            occurred_from is not None
            and occurred_to is not None
            and occurred_from > occurred_to
        ):
            raise ValueError(
                "occurred_from must not be later "
                "than occurred_to."
            )

        query = query.order_by(
            JournalEntry.occurred_at.desc(),
            JournalEntry.recorded_at.desc(),
            JournalEntry.id.desc(),
        ).limit(
            validated_limit
        )

        return list(
            self.session.scalars(
                query
            ).unique()
        )

    @staticmethod
    def _base_query() -> Select[tuple[JournalEntry]]:
        """Return the standard Journal read query."""

        return (
            select(JournalEntry)
            .options(
                selectinload(
                    JournalEntry.actor_reference
                ),
                selectinload(
                    JournalEntry.subject_reference
                ),
                selectinload(
                    JournalEntry.context_reference
                ),
                selectinload(
                    JournalEntry.desk
                ),
            )
        )

    @staticmethod
    def _validate_limit(
        limit: int,
    ) -> int:
        if isinstance(limit, bool):
            raise ValueError(
                "Journal timeline limit must be "
                "an integer."
            )

        if not isinstance(limit, int):
            raise ValueError(
                "Journal timeline limit must be "
                "an integer."
            )

        if limit < 1:
            raise ValueError(
                "Journal timeline limit must be "
                "at least 1."
            )

        if limit > MAX_TIMELINE_LIMIT:
            raise ValueError(
                "Journal timeline limit must not "
                f"exceed {MAX_TIMELINE_LIMIT}."
            )

        return limit

    @staticmethod
    def _validate_event_codes(
        event_codes: Iterable[str] | None,
    ) -> tuple[str, ...]:
        if event_codes is None:
            return ()

        validated = tuple(
            validate_event_code(
                event_code
            )
            for event_code in event_codes
        )

        return tuple(
            dict.fromkeys(
                validated
            )
        )

    @staticmethod
    def _validate_datetime(
        value: datetime,
        *,
        field_name: str,
    ) -> None:
        if value.tzinfo is None:
            raise ValueError(
                f"{field_name} must be timezone-aware."
            )


__all__ = [
    "DEFAULT_TIMELINE_LIMIT",
    "JournalQueryService",
    "MAX_TIMELINE_LIMIT",
]
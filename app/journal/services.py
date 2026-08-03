"""Event Journal recording services."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.journal.commands import (
    RecordJournalEntryCommand,
)
from app.journal.exceptions import (
    JournalPersistenceError,
)
from app.journal.models import JournalEntry
from app.journal.validators import (
    validate_details,
    validate_event_code,
    validate_occurred_at,
    validate_summary,
)


class JournalEntryService:
    """Record immutable Journal Entries.

    Public recording methods own their database transaction unless
    explicitly documented otherwise.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def record(
        self,
        command: RecordJournalEntryCommand,
    ) -> JournalEntry:
        """Validate, persist, and return one Journal Entry."""

        event_code = validate_event_code(
            command.event_code
        )
        occurred_at = validate_occurred_at(
            command.occurred_at
        )
        summary = validate_summary(
            command.summary
        )
        details = validate_details(
            command.details
        )

        entry = JournalEntry(
            event_code=event_code,
            occurred_at=occurred_at,
            summary=summary,
            details=details,
        )

        self.session.add(entry)

        try:
            self.session.commit()
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise JournalPersistenceError(
                "The Journal Entry could not be recorded."
            ) from exc

        return entry
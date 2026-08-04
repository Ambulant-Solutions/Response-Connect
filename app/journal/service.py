"""Public service interface for the Event Journal platform."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.journal.commands import (
    RecordJournalEntryCommand,
    RegisterJournalReferenceCommand,
)
from app.journal.models import (
    JournalEntry,
    JournalReference,
)
from app.journal.services import (
    JournalEntryService,
    JournalReferenceService,
)


@dataclass(frozen=True)
class JournalReferenceSpec:
    """
    Public description of an actor, subject, or context identity.

    Business modules use this value object instead of constructing
    JournalReference models or internal registration commands directly.
    """

    reference_type: str
    display_name: str
    source_id: uuid.UUID | None = None
    stable_key: str | None = None


class JournalService:
    """
    Public interface to the system-wide Event Journal.

    Business modules should use this service rather than importing
    JournalEntryService or JournalReferenceService directly.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._reference_service = (
            JournalReferenceService(
                session=session,
            )
        )
        self._entry_service = (
            JournalEntryService(
                session=session,
            )
        )

    def record(
        self,
        *,
        event_code: str,
        occurred_at: datetime,
        actor: JournalReferenceSpec,
        summary: str,
        details: str | None = None,
        subject: JournalReferenceSpec | None = None,
        context: JournalReferenceSpec | None = None,
        desk_id: uuid.UUID | None = None,
    ) -> JournalEntry:
        """
        Record and return one immutable Journal Entry.

        Actor registration is required. Subject and context registration
        are optional. Repeated registration of the same stable identity
        returns the existing Journal Reference.
        """

        actor_reference = self._resolve_reference(
            actor
        )

        subject_reference = (
            self._resolve_reference(subject)
            if subject is not None
            else None
        )

        context_reference = (
            self._resolve_reference(context)
            if context is not None
            else None
        )

        command = RecordJournalEntryCommand(
            event_code=event_code,
            occurred_at=occurred_at,
            actor_reference_id=(
                actor_reference.id
            ),
            subject_reference_id=(
                subject_reference.id
                if subject_reference is not None
                else None
            ),
            context_reference_id=(
                context_reference.id
                if context_reference is not None
                else None
            ),
            desk_id=desk_id,
            summary=summary,
            details=details,
        )

        return self._entry_service.record(
            command
        )

    def _resolve_reference(
        self,
        reference: JournalReferenceSpec,
    ) -> JournalReference:
        """Resolve or create one stable Journal Reference."""

        command = RegisterJournalReferenceCommand(
            reference_type=(
                reference.reference_type
            ),
            source_id=reference.source_id,
            stable_key=reference.stable_key,
            display_name=reference.display_name,
        )

        return self._reference_service.get_or_create(
            command
        )


__all__ = [
    "JournalReferenceSpec",
    "JournalService",
]
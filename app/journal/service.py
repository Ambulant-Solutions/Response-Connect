"""Public service interface for the Event Journal platform."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from collections.abc import Mapping
from typing import Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.journal.commands import (
    RecordJournalEntryCommand,
    RegisterJournalReferenceCommand,
)
from app.journal.exceptions import (
    JournalPersistenceError,
)
from app.journal.models import (
    JournalEntry,
    JournalReference,
)
from app.journal.services import (
    JournalEntryService,
    JournalReferenceService,
)
from app.journal.validators import (
    validate_details,
    validate_event_code,
    validate_event_metadata,
    validate_occurred_at,
    validate_summary,
)


@dataclass(frozen=True)
class JournalReferenceSpec:
    """
    Public description of an actor, subject, or context identity.
    """

    reference_type: str
    display_name: str
    source_id: uuid.UUID | None = None
    stable_key: str | None = None

    @classmethod
    def from_source(
        cls,
        *,
        reference_type: str,
        source_id: uuid.UUID,
        display_name: str,
    ) -> "JournalReferenceSpec":
        """Create a Journal reference backed by a persistent source."""

        return cls(
            reference_type=reference_type,
            source_id=source_id,
            display_name=display_name,
        )

    @classmethod
    def from_stable_key(
        cls,
        *,
        reference_type: str,
        stable_key: str,
        display_name: str,
    ) -> "JournalReferenceSpec":
        """Create a Journal reference backed by a stable system key."""

        return cls(
            reference_type=reference_type,
            stable_key=stable_key,
            display_name=display_name,
        )


class JournalService:
    """
    Public interface to the system-wide Event Journal.

    Business modules should use this service rather than importing
    JournalEntryService or JournalReferenceService directly.

    By default, record() owns and commits the database transaction.
    Callers coordinating a wider unit of work may pass commit=False and
    then commit or roll back the shared session themselves.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

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
        event_metadata: Mapping[str, Any] | None = None,
        commit: bool = True,
    ) -> JournalEntry:
        """
        Record and return one immutable Journal Entry.

        Actor registration is required. Subject and context registration
        are optional.

        When commit is True, all Journal References and the Journal Entry
        are committed together.

        When commit is False, references and the entry are flushed to the
        caller's active transaction. The caller is responsible for the
        final commit or rollback.
        """

        # Validate Journal Entry values before creating or flushing any
        # Journal References. This prevents invalid entry data from
        # leaving partial reference records in a caller-owned transaction.
        validated_event_code = (
            validate_event_code(
                event_code
            )
        )
        validated_occurred_at = (
            validate_occurred_at(
                occurred_at
            )
        )
        validated_summary = (
            validate_summary(
                summary
            )
        )
        validated_details = (
            validate_details(
                details
            )
        )

        validated_event_metadata = (
            validate_event_metadata(
                event_metadata
            )
        )

        try:
            # Internal operations always use flush-only behaviour.
            # JournalService performs the single final commit when it
            # owns the transaction.
            actor_reference = (
                self._resolve_reference(
                    actor,
                    commit=False,
                )
            )

            subject_reference = (
                self._resolve_reference(
                    subject,
                    commit=False,
                )
                if subject is not None
                else None
            )

            context_reference = (
                self._resolve_reference(
                    context,
                    commit=False,
                )
                if context is not None
                else None
            )

            command = RecordJournalEntryCommand(
                event_code=validated_event_code,
                occurred_at=validated_occurred_at,
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
                summary=validated_summary,
                details=validated_details,
                event_metadata=validated_event_metadata,
            )

            entry = self._entry_service.record(
                command,
                commit=False,
            )

            if commit:
                self._commit()

            return entry

        except Exception:
            # JournalService rolls back only when it owns the
            # transaction. With commit=False, transaction ownership
            # remains with the caller.
            if commit:
                self._session.rollback()

            raise

    def _resolve_reference(
        self,
        reference: JournalReferenceSpec,
        *,
        commit: bool,
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
            command,
            commit=commit,
        )

    def _commit(self) -> None:
        """Commit a Journal-owned transaction."""

        try:
            self._session.commit()
        except SQLAlchemyError as exc:
            self._session.rollback()

            raise JournalPersistenceError(
                "The Journal Entry could not be "
                "recorded."
            ) from exc


__all__ = [
    "JournalReferenceSpec",
    "JournalService",
]


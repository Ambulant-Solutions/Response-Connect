"""Event Journal recording services."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from app.journal.commands import (
    RecordJournalEntryCommand,
    RegisterJournalReferenceCommand,
)
from app.journal.exceptions import (
    JournalPersistenceError,
    JournalReferenceConflictError,
    JournalReferenceNotFoundError,
    JournalReferencePersistenceError,
)
from app.journal.models import (
    JournalEntry,
    JournalReference,
)
from app.journal.validators import (
    validate_details,
    validate_event_code,
    validate_occurred_at,
    validate_reference_display_name,
    validate_reference_identity,
    validate_reference_stable_key,
    validate_reference_type,
    validate_summary,
)
from app.desks import (
    Desk,
    DeskNotFoundError,
)


class JournalEntryService:
    """Record immutable Journal Entries."""

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

        actor = self._get_reference(
            command.actor_reference_id,
            role="actor",
        )

        subject = self._get_optional_reference(
            command.subject_reference_id,
            role="subject",
        )

        context = self._get_optional_reference(
            command.context_reference_id,
            role="context",
        )

        desk = self._get_optional_desk(
            command.desk_id
        )

        entry = JournalEntry(
            event_code=event_code,
            occurred_at=occurred_at,
            actor_reference_id=actor.id,
            subject_reference_id=(
                subject.id
                if subject is not None
                else None
            ),
            context_reference_id=(
                context.id
                if context is not None
                else None
            ),
            desk_id=(
                desk.id
                if desk is not None
                else None
            ),
            desk_display_name=(
                desk.name
                if desk is not None
                else None
            ),
            summary=summary,
            details=details,
        )

        self.session.add(entry)

        try:
            self.session.commit()
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise JournalPersistenceError(
                "The Journal Entry could not be "
                "recorded."
            ) from exc

        return entry

    def _get_reference(
        self,
        reference_id: uuid.UUID,
        *,
        role: str,
    ) -> JournalReference:
        reference = self.session.get(
            JournalReference,
            reference_id,
        )

        if reference is None:
            raise JournalReferenceNotFoundError(
                f"The Journal {role} reference "
                "could not be found."
            )

        return reference

    def _get_optional_reference(
        self,
        reference_id: uuid.UUID | None,
        *,
        role: str,
    ) -> JournalReference | None:
        if reference_id is None:
            return None

        return self._get_reference(
            reference_id,
            role=role,
        )

    def _get_optional_desk(
        self,
        desk_id: uuid.UUID | None,
    ) -> Desk | None:
        if desk_id is None:
            return None

        desk = self.session.get(
            Desk,
            desk_id,
        )

        if desk is None:
            raise DeskNotFoundError(
                "The Journal Desk could not be found."
            )

        return desk

class JournalReferenceService:
    """Register stable Journal-owned identities.

    Registration is idempotent. Repeated registration of the same
    reference identity returns the existing JournalReference without
    overwriting its historical display name.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def get_or_create(
        self,
        command: RegisterJournalReferenceCommand,
    ) -> JournalReference:
        """Return an existing reference or create one."""

        reference_type = validate_reference_type(
            command.reference_type
        )
        stable_key = validate_reference_stable_key(
            command.stable_key
        )
        display_name = (
            validate_reference_display_name(
                command.display_name
            )
        )

        validate_reference_identity(
            source_id=command.source_id,
            stable_key=stable_key,
        )

        existing_by_source = (
            self._find_by_source(
                reference_type=reference_type,
                source_id=command.source_id,
            )
        )

        existing_by_stable_key = (
            self._find_by_stable_key(
                reference_type=reference_type,
                stable_key=stable_key,
            )
        )

        existing = self._resolve_existing_reference(
            source_id=command.source_id,
            stable_key=stable_key,
            existing_by_source=existing_by_source,
            existing_by_stable_key=(
                existing_by_stable_key
            ),
        )

        if existing is not None:
            return existing

        reference = JournalReference(
            reference_type=reference_type,
            source_id=command.source_id,
            stable_key=stable_key,
            display_name=display_name,
        )

        self.session.add(reference)

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()

            concurrent_reference = (
                self._find_existing(
                    reference_type=reference_type,
                    source_id=command.source_id,
                    stable_key=stable_key,
                )
            )

            if concurrent_reference is not None:
                return concurrent_reference

            raise JournalReferenceConflictError(
                "The Journal Reference could not be "
                "registered because its identity "
                "conflicts with an existing reference."
            ) from exc
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise JournalReferencePersistenceError(
                "The Journal Reference could not be "
                "registered."
            ) from exc

        return reference

    def _find_existing(
        self,
        *,
        reference_type: str,
        source_id: uuid.UUID | None,
        stable_key: str | None,
    ) -> JournalReference | None:
        existing_by_source = self._find_by_source(
            reference_type=reference_type,
            source_id=source_id,
        )

        existing_by_stable_key = (
            self._find_by_stable_key(
                reference_type=reference_type,
                stable_key=stable_key,
            )
        )

        return self._resolve_existing_reference(
            source_id=source_id,
            stable_key=stable_key,
            existing_by_source=existing_by_source,
            existing_by_stable_key=(
                existing_by_stable_key
            ),
        )

    def _find_by_source(
        self,
        *,
        reference_type: str,
        source_id: uuid.UUID | None,
    ) -> JournalReference | None:
        if source_id is None:
            return None

        return self.session.scalar(
            select(JournalReference).where(
                JournalReference.reference_type
                == reference_type,
                JournalReference.source_id
                == source_id,
            )
        )

    def _find_by_stable_key(
        self,
        *,
        reference_type: str,
        stable_key: str | None,
    ) -> JournalReference | None:
        if stable_key is None:
            return None

        return self.session.scalar(
            select(JournalReference).where(
                JournalReference.reference_type
                == reference_type,
                JournalReference.stable_key
                == stable_key,
            )
        )

    @staticmethod
    def _resolve_existing_reference(
        *,
        source_id: uuid.UUID | None,
        stable_key: str | None,
        existing_by_source: (
            JournalReference | None
        ),
        existing_by_stable_key: (
            JournalReference | None
        ),
    ) -> JournalReference | None:
        if (
            existing_by_source is not None
            and existing_by_stable_key is not None
            and existing_by_source.id
            != existing_by_stable_key.id
        ):
            raise JournalReferenceConflictError(
                "The supplied source ID and stable key "
                "identify different Journal References."
            )

        existing = (
            existing_by_source
            or existing_by_stable_key
        )

        if existing is None:
            return None

        if (
            source_id is not None
            and existing.source_id is not None
            and existing.source_id != source_id
        ):
            raise JournalReferenceConflictError(
                "The stable key is already associated "
                "with a different source ID."
            )

        if (
            stable_key is not None
            and existing.stable_key is not None
            and existing.stable_key != stable_key
        ):
            raise JournalReferenceConflictError(
                "The source ID is already associated "
                "with a different stable key."
            )

        return existing
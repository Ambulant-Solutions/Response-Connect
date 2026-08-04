"""Persistent Event Journal models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    DateTime,
    Index,
    String,
    text,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from app.desks.models import Desk
from app.extensions import db
from app.journal.constants import (
    EVENT_CODE_MAX_LENGTH,
    JOURNAL_SUMMARY_MAX_LENGTH,
    JOURNAL_DETAILS_MAX_LENGTH,
    JOURNAL_REFERENCE_TYPE_MAX_LENGTH,
    JOURNAL_REFERENCE_DISPLAY_NAME_MAX_LENGTH,
    JOURNAL_REFERENCE_STABLE_KEY_MAX_LENGTH,
    JOURNAL_REFERENCE_TYPE_PATTERN,
    JOURNAL_REFERENCE_STABLE_KEY_PATTERN,
)

class JournalReference(db.Model):
    """Stable Journal-owned identity for actors, subjects, and contexts."""

    __tablename__ = "journal_references"

    __table_args__ = (
        CheckConstraint(
            "source_id IS NOT NULL OR stable_key IS NOT NULL",
            name="ck_journal_references_identity_required",
        ),
        CheckConstraint(
            "char_length(reference_type) > 0",
            name="ck_journal_references_type_not_empty",
        ),
        CheckConstraint(
            "char_length(display_name) > 0",
            name="ck_journal_references_display_name_not_empty",
        ),
        CheckConstraint(
            "stable_key IS NULL OR stable_key = lower(stable_key)",
            name="ck_journal_references_stable_key_lowercase",
        ),
        Index(
            "uq_journal_references_type_source",
            "reference_type",
            "source_id",
            unique=True,
            postgresql_where=text("source_id IS NOT NULL"),
        ),
        Index(
            "uq_journal_references_type_stable_key",
            "reference_type",
            "stable_key",
            unique=True,
            postgresql_where=text("stable_key IS NOT NULL"),
        ),
        Index(
            "ix_journal_references_type",
            "reference_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    reference_type: Mapped[str] = mapped_column(
        String(JOURNAL_REFERENCE_TYPE_MAX_LENGTH),
        nullable=False,
    )

    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    stable_key: Mapped[str | None] = mapped_column(
        String(JOURNAL_REFERENCE_STABLE_KEY_MAX_LENGTH),
        nullable=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(JOURNAL_REFERENCE_DISPLAY_NAME_MAX_LENGTH),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<JournalReference "
            f"id={self.id!s} "
            f"type={self.reference_type!r} "
            f"display_name={self.display_name!r}>"
        )


class JournalEntry(db.Model):
    """
    An immutable record of a significant occurrence.

    Domain tables remain authoritative for current state. Journal Entries
    provide operational, audit, security, and system history.
    """

    __tablename__ = "journal_entries"

    __table_args__ = (
        CheckConstraint(
            "char_length(event_code) > 0",
            name="ck_journal_entries_event_code_not_empty",
        ),
        CheckConstraint(
            "event_code = lower(event_code)",
            name="ck_journal_entries_event_code_lowercase",
        ),
        CheckConstraint(
            "char_length(summary) > 0",
            name="ck_journal_entries_summary_not_empty",
        ),
        Index(
            "ix_journal_entries_recorded_at",
            "recorded_at",
        ),
        Index(
            "ix_journal_entries_occurred_at",
            "occurred_at",
        ),
        Index(
            "ix_journal_entries_event_code_occurred_at",
            "event_code",
            "occurred_at",
        ),
        Index(
            "ix_journal_entries_actor_occurred_at",
            "actor_reference_id",
            "occurred_at",
        ),
        Index(
            "ix_journal_entries_subject_occurred_at",
            "subject_reference_id",
            "occurred_at",
        ),
        Index(
            "ix_journal_entries_context_occurred_at",
            "context_reference_id",
            "occurred_at",
        ),
        Index(
            "ix_journal_entries_desk_occurred_at",
            "desk_id",
            "occurred_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_code: Mapped[str] = mapped_column(
        String(EVENT_CODE_MAX_LENGTH),
        nullable=False,
        index=True,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    actor_reference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "journal_references.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    subject_reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "journal_references.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    context_reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "journal_references.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    desk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "desks.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    desk_display_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    summary: Mapped[str] = mapped_column(
        String(JOURNAL_SUMMARY_MAX_LENGTH),
        nullable=False,
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    actor_reference: Mapped[JournalReference] = relationship(
        "JournalReference",
        foreign_keys=[actor_reference_id],
    )

    subject_reference: Mapped[JournalReference | None] = relationship(
        "JournalReference",
        foreign_keys=[subject_reference_id],
    )

    context_reference: Mapped[JournalReference | None] = relationship(
        "JournalReference",
        foreign_keys=[context_reference_id],
    )


    desk: Mapped[Desk | None] = relationship(
        "Desk",
        foreign_keys=[desk_id],
    )

    def __repr__(self) -> str:
        return (
            f"<JournalEntry "
            f"id={self.id!s} "
            f"event_code={self.event_code!r}>"
        )
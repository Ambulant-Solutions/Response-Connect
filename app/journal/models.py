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
)

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

    def __repr__(self) -> str:
        return (
            f"<JournalEntry "
            f"id={self.id!s} "
            f"event_code={self.event_code!r}>"
        )
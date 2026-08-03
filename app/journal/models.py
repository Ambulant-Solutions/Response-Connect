"""Persistent Event Journal models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    String,
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
"""Immutable commands for Event Journal operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RecordJournalEntryCommand:
    """Record one immutable Journal Entry."""

    event_code: str
    occurred_at: datetime
    summary: str
    details: str | None = None
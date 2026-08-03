"""Immutable commands for Event Journal operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class RegisterJournalReferenceCommand:
    """Register one stable Journal identity."""

    reference_type: str
    display_name: str
    source_id: uuid.UUID | None = None
    stable_key: str | None = None


@dataclass(frozen=True)
class RecordJournalEntryCommand:
    """Record one immutable Journal Entry."""

    event_code: str
    occurred_at: datetime
    summary: str
    details: str | None = None
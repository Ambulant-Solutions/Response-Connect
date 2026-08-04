"""Immutable commands for Event Journal operations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from collections.abc import Mapping
from typing import Any


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
    actor_reference_id: uuid.UUID
    summary: str
    details: str | None = None
    subject_reference_id: uuid.UUID | None = None
    context_reference_id: uuid.UUID | None = None
    desk_id: uuid.UUID | None = None
    event_metadata: Mapping[str, Any] | None = None


__all__ = [
    "RecordJournalEntryCommand",
    "RegisterJournalReferenceCommand",
]
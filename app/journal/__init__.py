"""Public interface for the system-wide Event Journal."""

from app.journal.exceptions import (
    InvalidJournalEntryError,
    InvalidJournalReferenceError,
    JournalEntryConflictError,
    JournalEntryNotFoundError,
    JournalEntryVisibilityError,
    JournalError,
    JournalPersistenceError,
    JournalReferenceConflictError,
    JournalReferenceNotFoundError,
    JournalReferencePersistenceError,
)
from app.journal.service import (
    JournalReferenceSpec,
    JournalService,
)


__all__ = [
    "InvalidJournalEntryError",
    "InvalidJournalReferenceError",
    "JournalEntryConflictError",
    "JournalEntryNotFoundError",
    "JournalEntryVisibilityError",
    "JournalError",
    "JournalPersistenceError",
    "JournalReferenceConflictError",
    "JournalReferenceNotFoundError",
    "JournalReferencePersistenceError",
    "JournalReferenceSpec",
    "JournalService",
]
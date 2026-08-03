"""Event Journal-specific exceptions."""

from app.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    PersistenceError,
    ResponseConnectError,
    ValidationError,
)


class JournalError(ResponseConnectError):
    """Base exception for Event Journal operations."""


class InvalidJournalEntryError(
    JournalError,
    ValidationError,
):
    """Raised when a Journal Entry is invalid."""


class JournalEntryNotFoundError(
    JournalError,
    NotFoundError,
):
    """Raised when a Journal Entry cannot be found."""


class JournalEntryVisibilityError(
    JournalError,
    PermissionDeniedError,
):
    """Raised when access to a Journal Entry is denied."""


class JournalEntryConflictError(
    JournalError,
    ConflictError,
):
    """Raised when a Journal operation conflicts with history."""


class JournalPersistenceError(
    JournalError,
    PersistenceError,
):
    """Raised when a Journal Entry cannot be persisted."""

class InvalidJournalReferenceError(
    JournalError,
    ValidationError,
):
    """Raised when a Journal Reference is invalid."""


class JournalReferenceNotFoundError(
    JournalError,
    NotFoundError,
):
    """Raised when a Journal Reference cannot be found."""


class JournalReferenceConflictError(
    JournalError,
    ConflictError,
):
    """Raised when a Journal Reference conflicts with existing identity."""


class JournalReferencePersistenceError(
    JournalError,
    PersistenceError,
):
    """Raised when a Journal Reference cannot be persisted."""


__all__ = [
    "InvalidJournalEntryError",
    "JournalEntryConflictError",
    "JournalEntryNotFoundError",
    "JournalEntryVisibilityError",
    "JournalError",
    "JournalPersistenceError",
    "InvalidJournalReferenceError",
    "JournalReferenceNotFoundError",
    "JournalReferenceConflictError",
    "JournalReferencePersistenceError",
]
"""Catalogue-specific exceptions.

These exceptions preserve catalogue-domain meaning while participating in
the shared Response Connect error hierarchy.
"""

from app.exceptions import (
    ConflictError,
    LifecycleError,
    NotFoundError,
    PersistenceError,
    ResponseConnectError,
    ValidationError,
)


class CatalogueError(ResponseConnectError):
    """Base exception for catalogue operations."""


class CatalogueRecordNotFoundError(
    CatalogueError,
    NotFoundError,
):
    """Raised when a catalogue record cannot be found."""


class InvalidCatalogueCodeError(
    CatalogueError,
    ValidationError,
):
    """Raised when a catalogue code is invalid."""


class CatalogueCodeConflictError(
    CatalogueError,
    ConflictError,
):
    """Raised when a catalogue code is already in use."""


class CatalogueNameConflictError(
    CatalogueError,
    ConflictError,
):
    """Raised when a catalogue name conflicts with another record."""


class ProtectedSystemRecordError(
    CatalogueError,
    LifecycleError,
):
    """Raised when a protected system record is modified illegally."""


class CatalogueRecordInUseError(
    CatalogueError,
    ConflictError,
):
    """Raised when a catalogue record cannot be deleted because it is in use."""


class CataloguePersistenceError(
    CatalogueError,
    PersistenceError,
):
    """Raised when catalogue state cannot be persisted."""


__all__ = [
    "CatalogueCodeConflictError",
    "CatalogueError",
    "CatalogueNameConflictError",
    "CataloguePersistenceError",
    "CatalogueRecordInUseError",
    "CatalogueRecordNotFoundError",
    "InvalidCatalogueCodeError",
    "ProtectedSystemRecordError",
]
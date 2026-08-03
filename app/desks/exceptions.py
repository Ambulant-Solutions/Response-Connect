"""Desk-specific exceptions."""

from app.exceptions import (
    ConflictError,
    LifecycleError,
    NotFoundError,
    PersistenceError,
    ResponseConnectError,
    ValidationError,
)


class DeskError(ResponseConnectError):
    """Base exception for Desk operations."""


class InvalidDeskError(
    DeskError,
    ValidationError,
):
    """Raised when Desk data is invalid."""


class DeskNotFoundError(
    DeskError,
    NotFoundError,
):
    """Raised when a Desk cannot be found."""


class DeskConflictError(
    DeskError,
    ConflictError,
):
    """Raised when a Desk conflicts with existing state."""


class DeskHierarchyError(
    DeskError,
    LifecycleError,
):
    """Raised when a Desk hierarchy operation is invalid."""


class DeskPersistenceError(
    DeskError,
    PersistenceError,
):
    """Raised when Desk state cannot be persisted."""

class DeskLifecycleError(
    DeskError,
    LifecycleError,
):
    """Raised when a Desk lifecycle transition is invalid."""


__all__ = [
    "DeskConflictError",
    "DeskError",
    "DeskHierarchyError",
    "DeskLifecycleError",
    "DeskNotFoundError",
    "DeskPersistenceError",
    "InvalidDeskError",
]
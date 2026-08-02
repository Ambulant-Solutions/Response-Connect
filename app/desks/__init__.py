"""Desk hierarchy and operational-scope platform."""

from app.desks.exceptions import (
    DeskConflictError,
    DeskError,
    DeskHierarchyError,
    DeskNotFoundError,
    DeskPersistenceError,
    InvalidDeskError,
)


__all__ = [
    "DeskConflictError",
    "DeskError",
    "DeskHierarchyError",
    "DeskNotFoundError",
    "DeskPersistenceError",
    "InvalidDeskError",
]
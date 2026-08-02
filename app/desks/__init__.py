"""Desk hierarchy and operational-scope platform."""

from app.desks.exceptions import (
    DeskConflictError,
    DeskError,
    DeskHierarchyError,
    DeskNotFoundError,
    DeskPersistenceError,
    InvalidDeskError,
)
from app.desks.models import Desk


__all__ = [
    "Desk",
    "DeskConflictError",
    "DeskError",
    "DeskHierarchyError",
    "DeskNotFoundError",
    "DeskPersistenceError",
    "InvalidDeskError",
]
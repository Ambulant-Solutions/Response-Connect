"""Desk hierarchy and operational-scope platform."""

from app.desks.commands import (
    CreateDeskCommand,
    MoveDeskCommand,
    UpdateDeskCommand,
)
from app.desks.exceptions import (
    DeskConflictError,
    DeskError,
    DeskHierarchyError,
    DeskNotFoundError,
    DeskPersistenceError,
    InvalidDeskError,
)
from app.desks.models import Desk
from app.desks.services import DeskService


__all__ = [
    "CreateDeskCommand",
    "Desk",
    "DeskConflictError",
    "DeskError",
    "DeskHierarchyError",
    "DeskNotFoundError",
    "DeskPersistenceError",
    "DeskService",
    "InvalidDeskError",
    "MoveDeskCommand",
    "UpdateDeskCommand",
]
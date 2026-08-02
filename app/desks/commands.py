"""Immutable commands for Desk operations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateDeskCommand:
    """Create a new Desk."""

    code: str
    name: str
    description: str | None = None
    parent_id: uuid.UUID | None = None
    is_root: bool = False


@dataclass(frozen=True)
class UpdateDeskCommand:
    """Update editable Desk fields."""

    name: str
    description: str | None = None


@dataclass(frozen=True)
class MoveDeskCommand:
    """Move a Desk beneath a new parent."""

    parent_id: uuid.UUID
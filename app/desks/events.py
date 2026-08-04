"""Journal event code definitions."""

from __future__ import annotations


class DeskJournalEvents:
    """Desk lifecycle Journal events."""

    CREATED = "desk.created"
    UPDATED = "desk.updated"

    MOVED = "desk.moved"

    ACTIVATED = "desk.activated"
    DEACTIVATED = "desk.deactivated"

    ARCHIVED = "desk.archived"
    RESTORED = "desk.restored"

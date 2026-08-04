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

    PROCESSING_POLICY_ASSIGNED = (
        "desk.processing_policy.assigned"
    )

    PROCESSING_POLICY_REMOVED = (
        "desk.processing_policy.removed"
    )
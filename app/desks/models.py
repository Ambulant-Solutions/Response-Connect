"""Persistent Desk models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.extensions import db


class Desk(db.Model):
    """
    An operational responsibility boundary.

    Desks form a strict hierarchy beneath one organisation-wide root Desk.
    They scope operational work, Journal Entries, dashboards, permissions,
    notifications, and future activity streams.
    """

    __tablename__ = "desks"

    __table_args__ = (
        CheckConstraint(
            """
            (
                is_root = true
                AND parent_id IS NULL
            )
            OR
            (
                is_root = false
                AND parent_id IS NOT NULL
            )
            """,
            name="ck_desks_root_parent_consistency",
        ),
        CheckConstraint(
            "parent_id IS NULL OR parent_id <> id",
            name="ck_desks_not_own_parent",
        ),
        CheckConstraint(
            "char_length(code) > 0",
            name="ck_desks_code_not_empty",
        ),
        CheckConstraint(
            "code = lower(code)",
            name="ck_desks_code_lowercase",
        ),
        CheckConstraint(
            "char_length(name) > 0",
            name="ck_desks_name_not_empty",
        ),
        Index(
            "uq_desks_single_root",
            "is_root",
            unique=True,
            postgresql_where=text("is_root = true"),
        ),
        Index(
            "ix_desks_parent_active_name",
            "parent_id",
            "is_active",
            "name",
        ),
        Index(
            "ix_desks_active_name",
            "is_active",
            "name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "desks.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    is_root: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    parent: Mapped["Desk | None"] = relationship(
        "Desk",
        remote_side="Desk.id",
        back_populates="children",
        foreign_keys=[parent_id],
    )

    children: Mapped[list["Desk"]] = relationship(
        "Desk",
        back_populates="parent",
        foreign_keys=[parent_id],
        order_by="Desk.name",
        passive_deletes=True,
    )

    @property
    def is_leaf(self) -> bool:
        """Return whether this Desk currently has no child Desks."""

        return not self.children

    def __repr__(self) -> str:
        return (
            f"<Desk "
            f"code={self.code!r} "
            f"name={self.name!r}>"
        )
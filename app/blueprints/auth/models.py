from __future__ import annotations

import uuid

from flask_login import UserMixin
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


user_roles = Table(
    "user_roles",
    db.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

role_permissions = Table(
    "role_permissions",
    db.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(db.Model):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="core")

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
    )


class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Stable internal identifier, such as admin or fleet_manager.
    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True,
    )

    # Human-readable name shown throughout the application.
    display_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="",
        server_default="",
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_system: Mapped[bool] = mapped_column(
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
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
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

    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        order_by="Permission.category, Permission.name",
    )

    users: Mapped[list["UserAccount"]] = relationship(
        "UserAccount",
        secondary=user_roles,
        back_populates="roles",
    )

    @property
    def label(self) -> str:
        return (
            self.display_name
            or self.name.replace("_", " ").title()
        )

    @property
    def permission_names(self) -> set[str]:
        return {
            permission.name
            for permission in self.permissions
        }

    def __repr__(self) -> str:
        return f"<Role {self.name!r}>"


class UserAccount(UserMixin, db.Model):
    __tablename__ = "user_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="created_by",
    )

    @property
    def display_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        if self.first_name:
            return self.first_name
        if self.last_name:
            return self.last_name
        return self.email.split("@")[0].replace(".", " ").title()

    @property
    def initials(self) -> str:
        names = [piece for piece in [self.first_name, self.last_name] if piece]
        if not names:
            return "RC"
        initials = "".join(piece[0].upper() for piece in names[:2])
        return initials or "RC"

    def has_permission(
        self,
        permission_name: str,
    ) -> bool:
        if not self.is_active:
            return False

        return any(
            permission.name == permission_name
            for role in self.roles
            if role.is_active
            for permission in role.permissions
        )

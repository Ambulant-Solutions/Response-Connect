from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Person(db.Model):
    """Shared personal identity used by accounts and HR records."""

    __tablename__ = "persons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    first_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="",
        server_default="",
    )

    middle_names: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="",
        server_default="",
    )

    last_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="",
        server_default="",
    )

    preferred_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="",
        server_default="",
    )

    user_account: Mapped["UserAccount | None"] = relationship(
        "UserAccount",
        back_populates="person",
        uselist=False,
    )

    staff_member: Mapped["StaffMember | None"] = relationship(
        "StaffMember",
        back_populates="person",
        uselist=False,
    )

    @property
    def greeting_name(self) -> str:
        return (
            self.preferred_name
            or self.first_name
            or self.last_name
        )

    @property
    def display_name(self) -> str:
        given_name = self.preferred_name or self.first_name

        return " ".join(
            part
            for part in (given_name, self.last_name)
            if part
        )

    @property
    def initials(self) -> str:
        names = [
            part
            for part in (
                self.preferred_name or self.first_name,
                self.last_name,
            )
            if part
        ]

        return "".join(
            part[0].upper()
            for part in names[:2]
        )
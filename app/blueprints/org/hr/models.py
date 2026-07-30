from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.blueprints.people.models import Person
from app.extensions import db


class StaffMember(db.Model):
    """Employment record belonging to a person."""

    __tablename__ = "staff_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )

    employee_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
    )

    employment_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        server_default="active",
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    leaving_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    person: Mapped[Person] = relationship(
        "Person",
        back_populates="staff_member",
    )
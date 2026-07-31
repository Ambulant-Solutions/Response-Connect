from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    text,
)
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

    position_assignments: Mapped[list["StaffPositionAssignment"]] = relationship(
        "StaffPositionAssignment",
        back_populates="staff_member",
    )

    clinical_grade_assignments: Mapped[
        list["StaffClinicalGradeAssignment"]
    ] = relationship(
        "StaffClinicalGradeAssignment",
        back_populates="staff_member",
    )

class JobPosition(db.Model):
    """Reusable job position defined by the organisation."""

    __tablename__ = "job_positions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
        unique=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        server_default="",
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

    staff_assignments: Mapped[list["StaffPositionAssignment"]] = relationship(
        "StaffPositionAssignment",
        back_populates="position",
    )

    def __repr__(self) -> str:
        return f"<JobPosition {self.name!r}>"

class StaffPositionAssignment(db.Model):
    """A dated assignment of a job position to a staff member."""

    __tablename__ = "staff_position_assignments"

    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_staff_position_assignments_date_order",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    staff_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "staff_members.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    position_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "job_positions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        server_default="",
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

    staff_member: Mapped[StaffMember] = relationship(
        "StaffMember",
        back_populates="position_assignments",
    )

    position: Mapped[JobPosition] = relationship(
        "JobPosition",
        back_populates="staff_assignments",
    )

    @property
    def is_current(self) -> bool:
        today = date.today()

        return (
            self.start_date <= today
            and (
                self.end_date is None
                or self.end_date >= today
            )
        )

    def __repr__(self) -> str:
        return (
            "<StaffPositionAssignment "
            f"{self.staff_member_id} -> {self.position_id}>"
        )


class ClinicalGrade(db.Model):
    """Reusable clinical grade defined by the organisation."""

    __tablename__ = "clinical_grades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
        unique=True,
    )

    abbreviation: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="",
        server_default="",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        server_default="",
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

    staff_assignments: Mapped[
        list["StaffClinicalGradeAssignment"]
    ] = relationship(
        "StaffClinicalGradeAssignment",
        back_populates="clinical_grade",
    )

    def __repr__(self) -> str:
        return f"<ClinicalGrade {self.name!r}>"

class MandatoryTrainingCourse(db.Model):
    """Mandatory training course defined by the organisation."""

    __tablename__ = "mandatory_training_courses"

    __table_args__ = (
        CheckConstraint(
            "requalification_period_years >= 1",
            name="requalification_period_years_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
        unique=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        server_default="",
    )

    requalification_period_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
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

    def __repr__(self) -> str:
        return f"<MandatoryTrainingCourse {self.name!r}>"


class StaffClinicalGradeAssignment(db.Model):
    """A dated clinical-grade assignment for a staff member."""

    __tablename__ = "staff_clinical_grade_assignments"

    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_staff_clinical_grade_assignments_date_order",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    staff_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "staff_members.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    clinical_grade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "clinical_grades.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        server_default="",
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

    staff_member: Mapped[StaffMember] = relationship(
        "StaffMember",
        back_populates="clinical_grade_assignments",
    )

    clinical_grade: Mapped[ClinicalGrade] = relationship(
        "ClinicalGrade",
        back_populates="staff_assignments",
    )

    @property
    def is_current(self) -> bool:
        today = date.today()

        return (
            self.start_date <= today
            and (
                self.end_date is None
                or self.end_date >= today
            )
        )

    def __repr__(self) -> str:
        return (
            "<StaffClinicalGradeAssignment "
            f"{self.staff_member_id} -> "
            f"{self.clinical_grade_id}>"
        )


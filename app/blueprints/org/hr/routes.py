from __future__ import annotations

from datetime import date, timedelta

from flask import render_template
from flask_login import current_user
from sqlalchemy import exists, func, or_, select

from app.blueprints.auth import permission_required
from app.blueprints.org.hr import hr_bp
from app.blueprints.org.hr.models import (
    StaffClinicalGradeAssignment,
    StaffMember,
    StaffPositionAssignment,
)
from app.extensions import db


def count_staff(*conditions) -> int:
    return (
        db.session.scalar(
            select(func.count(StaffMember.id)).where(
                *conditions
            )
        )
        or 0
    )


@hr_bp.get("/", strict_slashes=False)
@permission_required("hr:read")
def hr():
    today = date.today()
    horizon = today + timedelta(days=30)

    active_staff_conditions = (
        StaffMember.employment_status == "active",
        or_(
            StaffMember.leaving_date.is_(None),
            StaffMember.leaving_date >= today,
        ),
    )

    current_position_exists = exists(
        select(StaffPositionAssignment.id).where(
            StaffPositionAssignment.staff_member_id
            == StaffMember.id,
            StaffPositionAssignment.start_date <= today,
            or_(
                StaffPositionAssignment.end_date.is_(None),
                StaffPositionAssignment.end_date >= today,
            ),
        )
    )

    current_primary_grade_exists = exists(
        select(
            StaffClinicalGradeAssignment.id
        ).where(
            StaffClinicalGradeAssignment.staff_member_id
            == StaffMember.id,
            StaffClinicalGradeAssignment.start_date
            <= today,
            or_(
                StaffClinicalGradeAssignment.end_date.is_(
                    None
                ),
                StaffClinicalGradeAssignment.end_date
                >= today,
            ),
            StaffClinicalGradeAssignment.is_primary.is_(
                True
            ),
        )
    )

    without_position_count = count_staff(
        *active_staff_conditions,
        ~current_position_exists,
    )

    without_grade_count = count_staff(
        *active_staff_conditions,
        ~current_primary_grade_exists,
    )

    return render_template(
        "org/hr/hr.html",
        active_staff_count=count_staff(
            *active_staff_conditions
        ),
        upcoming_starter_count=count_staff(
            StaffMember.start_date > today,
            StaffMember.start_date <= horizon,
        ),
        upcoming_leaver_count=count_staff(
            StaffMember.leaving_date >= today,
            StaffMember.leaving_date <= horizon,
        ),
        without_position_count=without_position_count,
        without_grade_count=without_grade_count,
        assignment_gap_count=(
            without_position_count
            + without_grade_count
        ),
        can_configure_hr=current_user.has_permission(
            "hr:configure"
        ),
        active_org_section="hr",
    )
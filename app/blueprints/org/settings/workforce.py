from __future__ import annotations

import uuid
from datetime import date

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    url_for,
)
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.blueprints.auth import permission_required
from app.blueprints.org.settings import settings_bp
from app.blueprints.org.hr.forms import (
    JobPositionActionForm,
    JobPositionForm,
)
from app.blueprints.org.hr.models import (
    JobPosition,
    StaffPositionAssignment,
)
from app.extensions import db


def load_job_positions() -> list[JobPosition]:
    statement = (
        select(JobPosition)
        .options(
            selectinload(JobPosition.staff_assignments)
        )
        .order_by(
            JobPosition.sort_order,
            JobPosition.name,
        )
    )

    return list(
        db.session.scalars(statement).unique().all()
    )


def get_job_position_or_404(
    position_id: uuid.UUID,
) -> JobPosition:
    statement = (
        select(JobPosition)
        .where(JobPosition.id == position_id)
        .options(
            selectinload(JobPosition.staff_assignments)
        )
    )

    position = db.session.scalar(statement)

    if position is None:
        abort(404)

    return position


def validate_job_position_form(
    form: JobPositionForm,
    *,
    current_position: JobPosition | None,
) -> bool:
    name = (form.name.data or "").strip()

    statement = select(JobPosition.id).where(
        func.lower(JobPosition.name) == name.lower()
    )

    if current_position is not None:
        statement = statement.where(
            JobPosition.id != current_position.id
        )

    if db.session.scalar(statement) is not None:
        form.name.errors.append(
            "This job-position name is already in use."
        )
        return False

    return True


def apply_job_position_form(
    position: JobPosition,
    form: JobPositionForm,
) -> None:
    position.name = form.name.data.strip()
    position.description = (
        form.description.data or ""
    ).strip()
    position.sort_order = form.sort_order.data


@settings_bp.get("/workforce/job-positions")
@permission_required("hr:configure")
def job_position_index():
    return render_template(
        "org/hr/job_positions/index.html",
        positions=load_job_positions(),
        action_form=JobPositionActionForm(),
        active_org_section="hr",
    )


@settings_bp.route(
    "/workforce/job-positions/new",
    methods=["GET", "POST"],
)
@permission_required("hr:configure")
def job_position_create():
    form = JobPositionForm()

    base_valid = form.validate_on_submit()
    name_valid = False

    if form.is_submitted():
        name_valid = validate_job_position_form(
            form,
            current_position=None,
        )

    if base_valid and name_valid:
        position = JobPosition(
            is_active=True,
        )

        apply_job_position_form(position, form)
        db.session.add(position)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The job position could not be created. "
                "Check that its name is unique.",
                "danger",
            )
        else:
            flash(
                "Job position created successfully.",
                "success",
            )

            return redirect(
                url_for("org.settings.job_position_index")
            )

    return render_template(
        "org/hr/job_positions/form.html",
        form=form,
        position=None,
        active_org_section="hr",
    )


@settings_bp.route(
    "/workforce/job-positions/<uuid:position_id>/edit",
    methods=["GET", "POST"],
)
@permission_required("hr:configure")
def job_position_edit(
    position_id: uuid.UUID,
):
    position = get_job_position_or_404(position_id)
    form = JobPositionForm(obj=position)

    base_valid = form.validate_on_submit()
    name_valid = False

    if form.is_submitted():
        name_valid = validate_job_position_form(
            form,
            current_position=position,
        )

    if base_valid and name_valid:
        apply_job_position_form(position, form)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The job position could not be saved. "
                "Check that its name is unique.",
                "danger",
            )
        else:
            flash(
                "Job position updated successfully.",
                "success",
            )

            return redirect(
                url_for("org.settings.job_position_index")
            )

    return render_template(
        "org/hr/job_positions/form.html",
        form=form,
        position=position,
        active_org_section="hr",
    )


@settings_bp.post(
    "/workforce/job-positions/<uuid:position_id>/deactivate"
)
@permission_required("hr:configure")
def job_position_deactivate(
    position_id: uuid.UUID,
):
    form = JobPositionActionForm()

    if not form.validate_on_submit():
        abort(400)

    position = get_job_position_or_404(position_id)

    open_assignment_count = db.session.scalar(
        select(func.count())
        .select_from(StaffPositionAssignment)
        .where(
            StaffPositionAssignment.position_id
            == position.id,
            or_(
                StaffPositionAssignment.end_date.is_(None),
                StaffPositionAssignment.end_date
                >= date.today(),
            ),
        )
    ) or 0

    if open_assignment_count:
        flash(
            "This position cannot be deactivated while "
            "current or future staff assignments use it.",
            "danger",
        )
    else:
        position.is_active = False
        db.session.commit()

        flash(
            "Job position deactivated.",
            "success",
        )

    return redirect(
        url_for("org.settings.job_position_index")
    )


@settings_bp.post(
    "/workforce/job-positions/<uuid:position_id>/activate"
)
@permission_required("hr:configure")
def job_position_activate(
    position_id: uuid.UUID,
):
    form = JobPositionActionForm()

    if not form.validate_on_submit():
        abort(400)

    position = get_job_position_or_404(position_id)
    position.is_active = True

    db.session.commit()

    flash(
        "Job position activated.",
        "success",
    )

    return redirect(
        url_for("org.settings.job_position_index")
    )

@settings_bp.get("/workforce")
@permission_required("hr:configure")
def workforce_index():
    workforce_sections = [
        {
            "id": "structure",
            "title": "Workforce structure",
            "description": (
                "Configure the organisation-wide definitions "
                "used by staff records and assignments."
            ),
            "items": [
                {
                    "title": "Job positions",
                    "description": (
                        "Define organisational positions that "
                        "may be assigned to staff members."
                    ),
                    "icon": "tabler:briefcase",
                    "url": url_for(
                        "org.settings.job_position_index"
                    ),
                    "status": "Available",
                    "status_style": "available",
                    "meta": "Organisational structure",
                },
                {
                    "title": "Clinical grades",
                    "description": (
                        "Configure clinical grades and operational "
                        "clinical levels."
                    ),
                    "icon": "tabler:stethoscope",
                    "url": None,
                    "status": "Next",
                    "status_style": "next",
                    "meta": "Clinical workforce",
                },
                {
                    "title": "Employment statuses",
                    "description": (
                        "Configure the employment states available "
                        "for staff records."
                    ),
                    "icon": "tabler:user-cog",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Employment records",
                },
            ],
        },
    ]

    return render_template(
        "org/settings/workforce/index.html",
        workforce_sections=workforce_sections,
        active_org_section="settings",
    )
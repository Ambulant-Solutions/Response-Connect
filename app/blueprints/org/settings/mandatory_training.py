from __future__ import annotations

import uuid

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    url_for,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.blueprints.auth import permission_required
from app.blueprints.org.settings.forms import (
    MandatoryTrainingCourseActionForm,
    MandatoryTrainingCourseForm,
)
from app.blueprints.org.hr.models import (
    MandatoryTrainingCourse,
)
from app.blueprints.org.settings import settings_bp
from app.extensions import db


def load_mandatory_training_courses() -> list[
    MandatoryTrainingCourse
]:
    statement = select(
        MandatoryTrainingCourse
    ).order_by(
        MandatoryTrainingCourse.sort_order,
        MandatoryTrainingCourse.name,
    )

    return list(db.session.scalars(statement).all())


def get_mandatory_training_course_or_404(
    course_id: uuid.UUID,
) -> MandatoryTrainingCourse:
    course = db.session.get(
        MandatoryTrainingCourse,
        course_id,
    )

    if course is None:
        abort(404)

    return course


def validate_mandatory_training_course_form(
    form: MandatoryTrainingCourseForm,
    *,
    current_course: MandatoryTrainingCourse | None,
) -> bool:
    name = (form.name.data or "").strip()

    if not name:
        form.name.errors.append(
            "Enter a mandatory training course name."
        )
        return False

    statement = select(
        MandatoryTrainingCourse.id
    ).where(
        func.lower(MandatoryTrainingCourse.name)
        == name.lower()
    )

    if current_course is not None:
        statement = statement.where(
            MandatoryTrainingCourse.id
            != current_course.id
        )

    if db.session.scalar(statement) is not None:
        form.name.errors.append(
            "This mandatory training course name is "
            "already in use."
        )
        return False

    return True


def apply_mandatory_training_course_form(
    course: MandatoryTrainingCourse,
    form: MandatoryTrainingCourseForm,
) -> None:
    course.name = form.name.data.strip()
    course.description = (
        form.description.data or ""
    ).strip()
    course.requalification_period_years = (
        form.requalification_period_years.data
    )
    course.sort_order = form.sort_order.data


@settings_bp.get("/mandatory-training")
@permission_required("hr:manage_training")
def mandatory_training_course_index():
    return render_template(
        "org/settings/mandatory_training/index.html",
        courses=load_mandatory_training_courses(),
        action_form=MandatoryTrainingCourseActionForm(),
        active_org_section="settings",
    )


@settings_bp.route(
    "/mandatory-training/new",
    methods=["GET", "POST"],
)
@permission_required("hr:manage_training")
def mandatory_training_course_create():
    form = MandatoryTrainingCourseForm()

    base_valid = form.validate_on_submit()
    course_valid = False

    if form.is_submitted():
        course_valid = (
            validate_mandatory_training_course_form(
                form,
                current_course=None,
            )
        )

    if base_valid and course_valid:
        course = MandatoryTrainingCourse(
            is_active=True,
        )

        apply_mandatory_training_course_form(
            course,
            form,
        )
        db.session.add(course)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The mandatory training course could not "
                "be created. Check that its name is unique.",
                "danger",
            )
        else:
            flash(
                "Mandatory training course created "
                "successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "org.settings."
                    "mandatory_training_course_index"
                )
            )

    return render_template(
        "org/settings/mandatory_training/form.html",
        form=form,
        course=None,
        active_org_section="settings",
    )


@settings_bp.route(
    "/mandatory-training/<uuid:course_id>/edit",
    methods=["GET", "POST"],
)
@permission_required("hr:manage_training")
def mandatory_training_course_edit(
    course_id: uuid.UUID,
):
    course = get_mandatory_training_course_or_404(
        course_id
    )
    form = MandatoryTrainingCourseForm(obj=course)

    base_valid = form.validate_on_submit()
    course_valid = False

    if form.is_submitted():
        course_valid = (
            validate_mandatory_training_course_form(
                form,
                current_course=course,
            )
        )

    if base_valid and course_valid:
        apply_mandatory_training_course_form(
            course,
            form,
        )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The mandatory training course could not "
                "be saved. Check that its name is unique.",
                "danger",
            )
        else:
            flash(
                "Mandatory training course updated "
                "successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "org.settings."
                    "mandatory_training_course_index"
                )
            )

    return render_template(
        "org/settings/mandatory_training/form.html",
        form=form,
        course=course,
        active_org_section="settings",
    )


@settings_bp.post(
    "/mandatory-training/<uuid:course_id>/deactivate"
)
@permission_required("hr:manage_training")
def mandatory_training_course_deactivate(
    course_id: uuid.UUID,
):
    form = MandatoryTrainingCourseActionForm()

    if not form.validate_on_submit():
        abort(400)

    course = get_mandatory_training_course_or_404(
        course_id
    )
    course.is_active = False

    db.session.commit()

    flash(
        "Mandatory training course deactivated.",
        "success",
    )

    return redirect(
        url_for(
            "org.settings."
            "mandatory_training_course_index"
        )
    )


@settings_bp.post(
    "/mandatory-training/<uuid:course_id>/activate"
)
@permission_required("hr:manage_training")
def mandatory_training_course_activate(
    course_id: uuid.UUID,
):
    form = MandatoryTrainingCourseActionForm()

    if not form.validate_on_submit():
        abort(400)

    course = get_mandatory_training_course_or_404(
        course_id
    )
    course.is_active = True

    db.session.commit()

    flash(
        "Mandatory training course activated.",
        "success",
    )

    return redirect(
        url_for(
            "org.settings."
            "mandatory_training_course_index"
        )
    )

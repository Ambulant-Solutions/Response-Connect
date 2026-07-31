from flask import Blueprint

hr_bp = Blueprint("hr", __name__, url_prefix="/hr")

from app.blueprints.org.hr.models import (  # noqa: E402, F401
    ClinicalGrade,
    JobPosition,
    MandatoryTrainingCourse,
    StaffClinicalGradeAssignment,
    StaffMember,
    StaffPositionAssignment,
)
import app.blueprints.org.hr.routes  # noqa: E402, F401
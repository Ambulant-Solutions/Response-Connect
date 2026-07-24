from flask import Blueprint, jsonify

from app.blueprints.job_application.models import JobApplication  # noqa: F401

job_application_bp = Blueprint("job_application", __name__, url_prefix="/jobs")


@job_application_bp.get("/apply")
def apply():
    return jsonify({"message": "Recruitment application routes can be added here."}), 200


@job_application_bp.get("/vacancies")
def vacancies():
    return jsonify({"message": "Vacancy routes can be added here."}), 200

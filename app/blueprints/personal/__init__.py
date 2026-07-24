from flask import Blueprint, jsonify

from app.blueprints.personal.models import StaffMember  # noqa: F401

personal_bp = Blueprint("personal", __name__, url_prefix="/personal")


@personal_bp.get("/activities")
def activities():
    return jsonify({"message": "Personal activity routes can be added here."}), 200


@personal_bp.get("/shift-requests")
def shift_requests():
    return jsonify({"message": "Shift request routes can be added here."}), 200

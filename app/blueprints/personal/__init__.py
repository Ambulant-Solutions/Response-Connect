from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from app.blueprints.personal.models import StaffMember  # noqa: F401

personal_bp = Blueprint("personal", __name__, url_prefix="/personal")


@personal_bp.get("/")
@login_required
def personal():
    return render_template("personal/personal.html")

@personal_bp.get("/activities")
def activities():
    return jsonify({"message": "Personal activity routes can be added here."}), 200


@personal_bp.get("/shift-requests")
def shift_requests():
    return jsonify({"message": "Shift request routes can be added here."}), 200

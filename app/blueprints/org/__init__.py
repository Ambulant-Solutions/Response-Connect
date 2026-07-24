from flask import Blueprint, jsonify

from app.blueprints.org.models import Organisation  # noqa: F401

org_bp = Blueprint("org", __name__, url_prefix="/org")


@org_bp.get("/admin")
def admin():
    return jsonify({"message": "Organisation admin routes can be added here."}), 200


@org_bp.get("/settings")
def settings():
    return jsonify({"message": "Organisation settings routes can be added here."}), 200

from flask import Blueprint, jsonify

from app.blueprints.auth.models import UserAccount  # noqa: F401

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/login")
def login():
    return jsonify({"message": "Authentication entry point is ready."}), 200


@auth_bp.get("/permissions")
def permissions():
    return jsonify({"message": "Permissions routes can be added here."}), 200

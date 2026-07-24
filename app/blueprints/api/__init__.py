from flask import Blueprint, jsonify

from app.blueprints.api.models import ApiClient  # noqa: F401

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/status")
def status():
    return jsonify({"message": "API routes can be added here."}), 200


@api_bp.get("/health")
def health():
    return jsonify({"message": "API health routes can be added here."}), 200

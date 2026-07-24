from flask import Blueprint, jsonify

from app.blueprints.external.models import ExternalForm  # noqa: F401

external_bp = Blueprint("external", __name__, url_prefix="/external")


@external_bp.get("/evaluation")
def evaluation():
    return jsonify({"message": "Patient evaluation routes can be added here."}), 200


@external_bp.get("/complaints")
def complaints():
    return jsonify({"message": "Complaints routes can be added here."}), 200

from flask import Blueprint, jsonify
from sqlalchemy import text

from app.blueprints.main.models import HealthCheck  # noqa: F401
from app.extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as exc:
        return jsonify({"status": "degraded", "database": "unavailable", "error": str(exc)}), 503

from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import text

from app.blueprints.main.models import HealthCheck  # noqa: F401
from app.extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
@login_required
def index():
    return render_template("index.html")
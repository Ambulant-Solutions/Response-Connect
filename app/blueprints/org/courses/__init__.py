from flask import Blueprint

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")

import app.blueprints.org.courses.routes
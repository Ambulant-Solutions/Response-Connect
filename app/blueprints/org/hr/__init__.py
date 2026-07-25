from flask import Blueprint

hr_bp = Blueprint("hr", __name__, url_prefix="/hr")

import app.blueprints.org.hr.routes
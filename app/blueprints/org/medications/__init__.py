from flask import Blueprint

medications_bp = Blueprint("medications", __name__, url_prefix="/medications")

import app.blueprints.org.medications.routes
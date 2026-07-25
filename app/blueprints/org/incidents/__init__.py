from flask import Blueprint

incidents_bp = Blueprint("incidents", __name__, url_prefix="/incidents")

import app.blueprints.org.incidents.routes
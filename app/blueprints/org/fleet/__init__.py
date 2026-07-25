from flask import Blueprint

fleet_bp = Blueprint("fleet", __name__, url_prefix="/fleet")

import app.blueprints.org.fleet.routes
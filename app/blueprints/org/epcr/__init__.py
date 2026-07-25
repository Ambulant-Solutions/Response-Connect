from flask import Blueprint

epcr_bp = Blueprint("epcr", __name__, url_prefix="/epcr")

import app.blueprints.org.epcr.routes
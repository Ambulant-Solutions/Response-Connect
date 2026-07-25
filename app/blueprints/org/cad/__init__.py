from flask import Blueprint

cad_bp = Blueprint("cad", __name__, url_prefix="/cad")

import app.blueprints.org.cad.routes
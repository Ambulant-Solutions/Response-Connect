from flask import Blueprint

pts_bp = Blueprint("pts", __name__, url_prefix="/pts")

import app.blueprints.org.pts.routes
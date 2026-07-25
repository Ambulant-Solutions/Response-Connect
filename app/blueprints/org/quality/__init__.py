from flask import Blueprint

quality_bp = Blueprint("quality", __name__, url_prefix="/quality")

import app.blueprints.org.quality.routes
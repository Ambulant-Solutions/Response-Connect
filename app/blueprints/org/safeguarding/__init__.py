from flask import Blueprint

safeguarding_bp = Blueprint("safeguarding", __name__, url_prefix="/safeguarding")

import app.blueprints.org.safeguarding.routes
from flask import Blueprint

crm_bp = Blueprint("crm", __name__, url_prefix="/crm")

import app.blueprints.org.crm.routes
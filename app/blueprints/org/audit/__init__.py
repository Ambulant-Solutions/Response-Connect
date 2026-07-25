from flask import Blueprint

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")

import app.blueprints.org.audit.routes
from flask import Blueprint

hr_bp = Blueprint("hr", __name__, url_prefix="/hr")

from app.blueprints.org.hr.models import StaffMember  # noqa: E402, F401
import app.blueprints.org.hr.routes  # noqa: E402, F401
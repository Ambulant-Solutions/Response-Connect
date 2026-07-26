from flask import Blueprint, jsonify, render_template

from app.blueprints.org.models import Organisation  # noqa: F401

from app.blueprints.org.audit import audit_bp  # noqa: F401
from app.blueprints.org.cad import cad_bp # noqa: F401
from app.blueprints.org.courses import courses_bp # noqa: F401
from app.blueprints.org.crm import crm_bp # noqa: F401
from app.blueprints.org.epcr import epcr_bp # noqa: F401
from app.blueprints.org.events import events_bp # noqa: F401
from app.blueprints.org.fleet import fleet_bp  # noqa: F401
from app.blueprints.org.hr import hr_bp  # noqa: F401
from app.blueprints.org.incidents import incidents_bp # noqa: F401
from app.blueprints.org.medications import medications_bp  # noqa: F401
from app.blueprints.org.patients import patients_bp  # noqa: F401
from app.blueprints.org.pts import pts_bp  # noqa: F401
from app.blueprints.org.quality import quality_bp  # noqa: F401
from app.blueprints.org.reports import reports_bp  # noqa: F401
from app.blueprints.org.safeguarding import safeguarding_bp  # noqa: F401
from app.blueprints.org.scheduling import scheduling_bp  # noqa: F401
from app.blueprints.org.stock import stock_bp  # noqa: F401
from app.blueprints.org.settings import settings_bp # noqa: F401

org_bp = Blueprint("org", __name__, url_prefix="/org")

org_bp.register_blueprint(audit_bp)
org_bp.register_blueprint(cad_bp)
org_bp.register_blueprint(courses_bp)
org_bp.register_blueprint(crm_bp)
org_bp.register_blueprint(epcr_bp)
org_bp.register_blueprint(events_bp)
org_bp.register_blueprint(fleet_bp)
org_bp.register_blueprint(hr_bp)
org_bp.register_blueprint(incidents_bp)
org_bp.register_blueprint(medications_bp)
org_bp.register_blueprint(patients_bp)
org_bp.register_blueprint(pts_bp)
org_bp.register_blueprint(quality_bp)
org_bp.register_blueprint(reports_bp)
org_bp.register_blueprint(safeguarding_bp)
org_bp.register_blueprint(scheduling_bp)
org_bp.register_blueprint(settings_bp)
org_bp.register_blueprint(stock_bp)

@org_bp.get("/")
def org():
    return render_template(
        "org/org.html",
        organisation="Test Install",
        active_org_section="overview"
    )





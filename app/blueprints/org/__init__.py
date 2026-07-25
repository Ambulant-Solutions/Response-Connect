from flask import Blueprint, jsonify, render_template

from app.blueprints.org.models import Organisation  # noqa: F401

from app.blueprints.org.fleet import fleet_bp  # noqa: F401

org_bp = Blueprint("org", __name__, url_prefix="/org")

org_bp.register_blueprint(fleet_bp)

@org_bp.get("/")
def org():
    return render_template(
        "org/org.html",
        organisation="Test Install",
        active_org_section="overview",
        compliance_alert_count=4,
        vehicle_alert_count=1,
        operations_alert_count=2,
    )

@org_bp.get("/admin")
def admin():
    return jsonify({"message": "Organisation admin routes can be added here."}), 200


@org_bp.get("/settings")
def settings():
    return jsonify({"message": "Organisation settings routes can be added here."}), 200

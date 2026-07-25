from app.blueprints.org.audit import audit_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@audit_bp.get("/")
def audit():
    return render_template(
        "org/fleet/fleet.html",
        organisation="Test Install",
        active_org_section="audit")
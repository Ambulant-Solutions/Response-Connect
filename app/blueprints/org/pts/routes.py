from app.blueprints.org.pts import pts_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@pts_bp.get("/")
def pts():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="pts")
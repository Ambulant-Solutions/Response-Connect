from app.blueprints.org.scheduling import scheduling_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@scheduling_bp.get("/")
def scheduling():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="scheduling")
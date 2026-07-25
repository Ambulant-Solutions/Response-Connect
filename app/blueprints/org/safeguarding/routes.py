from app.blueprints.org.safeguarding import safeguarding_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@safeguarding_bp.get("/")
def safeguarding():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="safeguarding")
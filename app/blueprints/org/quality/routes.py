from app.blueprints.org.quality import quality_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@quality_bp.get("/")
def quality():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="quality")
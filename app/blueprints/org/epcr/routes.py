from app.blueprints.org.epcr import epcr_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@epcr_bp.get("/")
def epcr():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="epcr")
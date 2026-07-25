from app.blueprints.org.crm import crm_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@crm_bp.get("/")
def crm():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="crm")
from app.blueprints.org.patients import patients_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@patients_bp.get("/")
def patients():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="patients")
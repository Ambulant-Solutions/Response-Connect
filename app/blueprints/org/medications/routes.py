from app.blueprints.org.medications import medications_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@medications_bp.get("/")
def medications():
    return render_template(
        "org/medications/medications.html",
        organisation="Test Install",
        active_org_section="medications")
from app.blueprints.org.incidents import incidents_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@incidents_bp.get("/")
def incidents():
    return render_template(
        "org/medications/medications.html",
        organisation="Test Install",
        active_org_section="incidents")
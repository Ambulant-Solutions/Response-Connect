from app.blueprints.org.hr import hr_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@hr_bp.get("/")
def hr():
    return render_template(
        "org/hr/hr.html",
        organisation="Test Install",
        active_org_section="hr")
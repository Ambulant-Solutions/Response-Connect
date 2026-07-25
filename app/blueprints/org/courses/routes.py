from app.blueprints.org.courses import courses_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@courses_bp.get("/")
def courses():
    return render_template(
        "org/fleet/fleet.html",
        organisation="Test Install",
        active_org_section="courses")
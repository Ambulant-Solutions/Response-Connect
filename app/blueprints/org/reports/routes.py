from app.blueprints.org.reports import reports_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@reports_bp.get("/")
def reports():
    return render_template(
        "org/reports/reports.html",
        organisation="Test Install",
        active_org_section="reports")
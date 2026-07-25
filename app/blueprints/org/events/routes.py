from app.blueprints.org.events import events_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@events_bp.get("/")
def events():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="events")
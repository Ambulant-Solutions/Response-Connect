from app.blueprints.org.settings import settings_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@settings_bp.get("/")
def settings():
    return render_template(
        "org/settings/settings.html",
        organisation="Test Install",
        active_org_section="settings")
from app.blueprints.org.cad import cad_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@cad_bp.get("/")
def cad():
    return render_template(
        "org/fleet/fleet.html",
        organisation="Test Install",
        active_org_section="cad")
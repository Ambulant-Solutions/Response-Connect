from app.blueprints.org.stock import stock_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template

@stock_bp.get("/")
def stock():
    return render_template(
        "org/crm/crm.html",
        organisation="Test Install",
        active_org_section="stock")
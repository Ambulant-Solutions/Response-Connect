from flask import Blueprint, jsonify, render_template


fleet_bp = Blueprint("fleet", __name__, url_prefix="/fleet")

@fleet_bp.get("/")
def fleet():
    return "hello fleet"
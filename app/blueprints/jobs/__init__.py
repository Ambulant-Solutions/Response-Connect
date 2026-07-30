from flask import Blueprint, jsonify

from app.blueprints.jobs.models import Job

job_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


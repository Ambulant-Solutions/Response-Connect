from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)
from sqlalchemy.exc import IntegrityError
from app.blueprints.org.settings import settings_bp
from app.blueprints.auth import permission_required
from app.extensions import db

@settings_bp.get("/locations")
@permission_required("org:manage")
def location_index():
    ...


@settings_bp.route(
    "/locations/new",
    methods=["GET", "POST"],
)
@permission_required("org:manage")
def location_create():
    ...


@settings_bp.route(
    "/locations/<uuid:location_id>/edit",
    methods=["GET", "POST"],
)
@permission_required("org:manage")
def location_edit(location_id):
    ...


@settings_bp.post(
    "/locations/<uuid:location_id>/deactivate",
)
@permission_required("org:manage")
def location_deactivate(location_id):
    ...
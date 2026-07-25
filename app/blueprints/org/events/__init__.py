from flask import Blueprint

events_bp = Blueprint("events", __name__, url_prefix="/events")

import app.blueprints.org.events.routes
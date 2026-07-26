from flask import Blueprint

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

import app.blueprints.org.settings.routes, app.blueprints.org.settings.settings
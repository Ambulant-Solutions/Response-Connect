from flask import Blueprint

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

from app.blueprints.org.settings import routes  # noqa: E402, F401
from app.blueprints.org.settings import organisation  # noqa: E402, F401
from app.blueprints.org.settings import locations  # noqa: E402, F401
from app.blueprints.org.settings import location_types  # noqa: E402, F401
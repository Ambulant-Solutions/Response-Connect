from flask import Blueprint

stock_bp = Blueprint("stock", __name__, url_prefix="/stock")

import app.blueprints.org.stock.routes
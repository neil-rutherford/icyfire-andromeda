from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import article_routes, coin_routes, connection_routes, contribute_routes, message_routes
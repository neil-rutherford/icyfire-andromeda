from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import auth_routes, load_routes, rest_routes, utils
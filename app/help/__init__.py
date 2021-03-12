from flask import Blueprint

bp = Blueprint('help', __name__)

from app.help import help_routes, legal_routes
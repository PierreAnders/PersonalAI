from flask import Blueprint 

bp = Blueprint('healths', __name__)

from app.healths import routes
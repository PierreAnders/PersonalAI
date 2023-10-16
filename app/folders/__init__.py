from flask import Blueprint

bp = Blueprint('folders', __name__)

from app.folders import routes
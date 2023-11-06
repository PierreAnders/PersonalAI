from flask import Blueprint

bp = Blueprint('code', __name__)

from app.code import routes
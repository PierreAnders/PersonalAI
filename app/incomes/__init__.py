from flask import Blueprint

bp = Blueprint('incomes', __name__)

from app.incomes import routes
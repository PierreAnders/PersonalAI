from flask import Blueprint

bp = Blueprint('chats', __name__)

from app.chats import routes
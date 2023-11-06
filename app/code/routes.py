from app.code import bp
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.code.service import chat_generic

@bp.route('/AIchatGeneric/<model>', methods=['POST'])
@jwt_required()
def chat_generic_route(model):
    data = request.get_json()
    result = chat_generic(model, data)
    return jsonify(result)
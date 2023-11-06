from app.code import bp
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.code.service import chat_service

@bp.route('/chat/<model>', methods=['POST'])
@jwt_required()
def chat(model):
    data = request.get_json()
    result = chat_service(model, data)
    return jsonify(result)
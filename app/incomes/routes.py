from app.incomes import bp
from app.incomes.model import Income
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app.incomes.service import add_income_service, delete_income_service, get_all_incomes_service

@bp.route('/incomes', methods=['POST'])
@jwt_required()
def add_income():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    price = data.get("price")
    user_id = get_jwt_identity()
    
    result, status_code = add_income_service(title, description, price, user_id)
    return jsonify(result), status_code

@bp.route('/incomes/<int:income_id>', methods=['DELETE'])
@jwt_required()
def delete_income(income_id):
    user_id = get_jwt_identity()
    result, status_code = delete_income_service(income_id, user_id)
    return jsonify(result), status_code

@bp.route('/incomes', methods=['GET'])
@jwt_required()
def get_all_incomes():
    user_id = get_jwt_identity()
    incomes_data, status_code = get_all_incomes_service(user_id)
    return jsonify(incomes_data), status_code

from app.expenses import bp
from app.expenses.model import Expense
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app.expenses.service import add_expense_service, delete_expense_service, get_all_expenses_service, write_user_data

@bp.route('/expenses', methods=['POST'])
@jwt_required()
def add_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    price = data.get("price")
    user_id = get_jwt_identity()
    result, status_code = add_expense_service(title, description, price, user_id)
    write_user_data(user_id)
    return jsonify(result), status_code

@bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = get_jwt_identity()
    result, status_code = delete_expense_service(expense_id, user_id)
    write_user_data(user_id)
    return jsonify(result), status_code

@bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_all_expenses():
    user_id = get_jwt_identity()
    expenses_data, status_code = get_all_expenses_service(user_id)
    return jsonify(expenses_data), status_code

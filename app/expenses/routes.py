from app.expenses import bp 
from app.extensions import db
from app.models.expense import Expense 
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify 
from sqlalchemy.exc import IntegrityError


@bp.route('/expenses', methods=['POST'])
@jwt_required()
def add_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    price = data.get("price")

    user_id = get_jwt_identity()

    expense = Expense(title=title, description=description, price=price, user_id=user_id)

    try:
        db.session.add(expense)
        db.session.commit()
        return jsonify({"message": "Dépense ajoutée avec succès"}), 201
    except IntegrityError as e:
        db.session.rollback()
        bp.app.logger.error("Erreur de base de données lors de l'ajout de la dépense : " + str(e))
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500


@bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = get_jwt_identity()

    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"message": "Dépense non trouvée ou non autorisée"}), 404

    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({"message": "Dépense supprimée avec succès"}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500
    
    
@bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_all_expenses():
    user_id = get_jwt_identity()

    expenses = Expense.query.filter_by(user_id=user_id).all()

    expenses_data = []

    for expense in expenses:
        expenses_data.append({
            "id": expense.id,
            "title": expense.title,
            "description": expense.description,
            "price": str(expense.price) 
        })

    return jsonify(expenses_data), 200

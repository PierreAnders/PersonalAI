from app.incomes import bp 
from app.extensions import db
from app.models.income import Income 
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify 
from sqlalchemy.exc import IntegrityError


@bp.route('/incomes', methods=['POST'])
@jwt_required()
def add_income():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    price = data.get("price")

    user_id = get_jwt_identity()

    income = Income(title=title, description=description, price=price, user_id=user_id)

    try:
        db.session.add(income)
        db.session.commit()
        return jsonify({"message": "Recette ajoutée avec succès"}), 201
    except IntegrityError as e:
        db.session.rollback()
        bp.app.logger.error("Erreur de base de données lors de l'ajout de la recette : " + str(e))
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500


@bp.route('/incomes/<int:income_id>', methods=['DELETE'])
@jwt_required()
def delete_income(income_id):
    user_id = get_jwt_identity()

    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return jsonify({"message": "Recette non trouvée ou non autorisée"}), 404

    try:
        db.session.delete(income)
        db.session.commit()
        return jsonify({"message": "Recette supprimée avec succès"}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500
    
    
@bp.route('/incomes', methods=['GET'])
@jwt_required()
def get_all_incomes():
    user_id = get_jwt_identity()

    incomes = Income.query.filter_by(user_id=user_id).all()

    incomes_data = []

    for income in incomes:
        incomes_data.append({
            "id": income.id,
            "title": income.title,
            "description": income.description,
            "price": str(income.price) 
        })

    return jsonify(incomes_data), 200

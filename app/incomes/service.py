from app.extensions import db
from app.incomes.model import Income
from sqlalchemy.exc import IntegrityError


def add_income_service(title, description, price, user_id):
    income = Income(title=title, description=description, price=price, user_id=user_id)
    try:
        db.session.add(income)
        db.session.commit()
        return {"message": "Recette ajoutée avec succès"}, 201
    except IntegrityError as e:
        db.session.rollback()
        error_message = "Erreur de base de données lors de l'ajout de la recette : " + str(e)
        return {"message": error_message}, 500


def delete_income_service(income_id, user_id):
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()
    if not income:
        return {"message": "Recette non trouvée ou non autorisée"}, 404
    try:
        db.session.delete(income)
        db.session.commit()
        return {"message": "Recette supprimée avec succès"}, 200
    except IntegrityError as e:
        db.session.rollback()
        return {"message": "Erreur de base de données : " + str(e)}, 500


def get_all_incomes_service(user_id):
    incomes = Income.query.filter_by(user_id=user_id).all()
    incomes_data = []
    for income in incomes:
        incomes_data.append({
            "id": income.id,
            "title": income.title,
            "description": income.description,
            "price": str(income.price)
        })
    return incomes_data, 200

from app.extensions import db
from app.expenses.model import Expense
from sqlalchemy.exc import IntegrityError


def add_expense(title, description, price, user_id):
    expense = Expense(title=title, description=description, price=price, user_id=user_id)
    try:
        db.session.add(expense)
        db.session.commit()
        return {"message": "Dépense ajoutée avec succès"}, 201
    except IntegrityError as e:
        db.session.rollback()
        error_message = "Erreur de base de données lors de l'ajout de la dépense : " + str(e)
        return {"message": error_message}, 500


def delete_expense(expense_id, user_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return {"message": "Dépense non trouvée ou non autorisée"}, 404
    try:
        db.session.delete(expense)
        db.session.commit()
        return {"message": "Dépense supprimée avec succès"}, 200
    except IntegrityError as e:
        db.session.rollback()
        return {"message": "Erreur de base de données : " + str(e)}, 500


def get_all_expenses(user_id):
    expenses = Expense.query.filter_by(user_id=user_id).all()
    expenses_data = []
    for expense in expenses:
        expenses_data.append({
            "id": expense.id,
            "title": expense.title,
            "description": expense.description,
            "price": str(expense.price)
        })
    return expenses_data, 200

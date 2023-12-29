import os
from app.extensions import db
from app.expenses.model import Expense
from sqlalchemy.exc import IntegrityError
from app.folders.model import Folder
from sqlalchemy.orm.exc import NoResultFound


def write_user_data(user_id):
    user_subfolder_info_db = os.path.join('data', str(user_id), "Database")

    try:
        os.makedirs(user_subfolder_info_db, exist_ok=True)
        print(f"Dossier '{user_subfolder_info_db}' créé avec succès.")

        folder = Folder.query.filter_by(name='Database', user_id=user_id).first()

        if folder is None:
            folder = Folder(name='Database', user_id=user_id)
            try:
                db.session.add(folder)
                db.session.commit()
                print({"message": "Dossier ajouté avec succès"}, 201)
            except IntegrityError as e:
                db.session.rollback()
                print({"message": "Erreur de base de données : " + str(e)}, 500)
        else:
            print({"message": "Le dossier existe déjà"}, 200)

        file_path = os.path.join(user_subfolder_info_db, 'expenses.txt')

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"MES DEPENSES MENSUELLES :\n\n")
            expenses = Expense.query.filter_by(user_id=user_id).all()
            expense_number = 0
            for expense in expenses:
                expense_number += 1
                file.write(f"Dépense {expense_number}: {expense.title}, {expense.description}, {expense.price} euros\n")

    except FileExistsError:
        print(f"Le dossier '{user_subfolder_info_db}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")


def add_expense_service(title, description, price, user_id):
    expense = Expense(title=title, description=description, price=price, user_id=user_id)

    try:
        db.session.add(expense)
        db.session.commit()
        return {"message": "Dépense ajoutée avec succès"}, 201
    except IntegrityError as e:
        db.session.rollback()
        error_message = "Erreur de base de données lors de l'ajout de la dépense : " + str(e)
        return {"message": error_message}, 500


def delete_expense_service(expense_id, user_id):
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


def get_all_expenses_service(user_id):
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

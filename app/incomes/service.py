import os
from app.extensions import db
from app.incomes.model import Income
from sqlalchemy.exc import IntegrityError

def write_user_data(user_id):
    user_subfolder_info_db = os.path.join('data', str(user_id), f"info-{user_id}")
    try:
        os.makedirs(user_subfolder_info_db, exist_ok=True)
        print(f"Dossier '{user_subfolder_info_db}' créé avec succès.")
    except FileExistsError:
        print(f"Le dossier '{user_subfolder_info_db}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")
    file_path = os.path.join(user_subfolder_info_db, 'incomes.txt')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"RECETTES MENSUELLES DE L'UTILISATEUR:\n\n")
        incomes = Income.query.filter_by(user_id=user_id).all()
        income_number = 0
        for income in incomes:
            income_number += 1
            file.write(f"Dépense {income_number}: {income.title}, {income.description}, {income.price} euros\n")


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

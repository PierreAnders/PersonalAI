from app.folders.model import Folder
import os
from app.extensions import db
from sqlalchemy.exc import IntegrityError


def create_user_subfolder(user_id, name):
    subfolder = os.path.join('data', str(user_id), name)

    try:
        os.mkdir(subfolder)
        print(f"Sous-dossier '{subfolder}' créé avec succès")
    except FileExistsError:
        print(f"Le sous-dossier '{subfolder}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")


def delete_user_subfolder(user_id, name):
    subfolder = os.path.join('data', str(user_id), name)

    try:
        os.rmdir(subfolder)
        print(f"Sous-dossier '{subfolder}' supprimé avec succès")
    except FileNotFoundError:
        print(f"Le sous-dossier '{subfolder}' n'existe pas.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la suppression du dossier : {str(e)}")


def add_folder_service(name, user_id):
    folder = Folder(name=name, user_id=user_id)

    try:
        db.session.add(folder)
        db.session.commit()
        create_user_subfolder(user_id, folder.name)
        return {"message": "Dossier ajouté avec succès"}, 201
    except IntegrityError as e:
        db.session.rollback()
        return {"message": "Erreur de base de données : " + str(e)}, 500


def delete_folder_service(folder_id, user_id):
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()

    if not folder:
        return {"message": "Dossier non trouvé ou non autorisé"}, 404

    try:
        db.session.delete(folder)
        db.session.commit()
        delete_user_subfolder(user_id, folder.name)
        return {"message": "Dossier supprimé avec succès"}, 200
    except IntegrityError as e:
        db.session.rollback()
        return {"message": "Erreur de base de données : " + str(e)}, 500


def get_all_folders_service(user_id):
    folders = Folder.query.filter_by(user_id=user_id).all()
    folders_data = []

    for folder in folders:
        folders_data.append({
            "id": folder.id,
            "name": folder.name,
        })
        
    return folders_data, 200

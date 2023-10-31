from app.folders import bp 
from app.extensions import db
from app.folders.model import Folder 
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify 
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

@bp.route('/folders', methods=['POST'])
@jwt_required()
def add_folder():
    data = request.get_json()
    name = data.get("name")

    user_id = get_jwt_identity()

    folder = Folder(name=name, user_id=user_id)

    try:
        db.session.add(folder)
        db.session.commit()
        create_user_subfolder(user_id, folder.name)
        return jsonify({"message": "Dossier ajoutée avec succès"}), 201
    except IntegrityError as e:
        db.session.rollback()
        bp.app.logger.error("Erreur de base de données lors de l'ajout du dossier : " + str(e))
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500


@bp.route('/folders/<int:folder_id>', methods=['DELETE'])
@jwt_required()
def delete_folder(folder_id):
    user_id = get_jwt_identity()

    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()

    if not folder:
        return jsonify({"message": "Dossier non trouvé ou non autorisé"}), 404

    try:
        db.session.delete(folder)
        db.session.commit()
        return jsonify({"message": "Dossier supprimé avec succès"}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500
    
    
@bp.route('/folders', methods=['GET'])
@jwt_required()
def get_all_folders():
    user_id = get_jwt_identity()

    folders = Folder.query.filter_by(user_id=user_id).all()

    folders_data = []

    for folder in folders:
        folders_data.append({
            "id": folder.id,
            "name": folder.name,
        })

    return jsonify(folders_data), 200

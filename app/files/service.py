
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify, send_file
from app.extensions import db
from app.files.model import File
from app.folders.model import Folder
import os


def upload_file_service(folder_name):
    user_id = get_jwt_identity()
    user_data_folder = os.path.join('data', str(user_id), folder_name)
    uploaded_file = request.files['file']

    if uploaded_file:
        file_path = os.path.join(user_data_folder, uploaded_file.filename)
        uploaded_file.save(file_path)

        folder = Folder.query.filter_by(name=folder_name, user_id=user_id).first()

        if folder:
            file_url = f'/data/{user_id}/{folder_name}/{uploaded_file.filename}'
            new_file = File(url=file_url, folder_id=folder.id)
            db.session.add(new_file)
            db.session.commit()

            return jsonify({"message": "Fichier téléchargé avec succès."})

    return jsonify({"message": "Aucun fichier n'a été téléchargé."})


def list_user_files_service(folder_name):
    user_id = get_jwt_identity()
    user_data_folder = os.path.join('data', str(user_id), folder_name)

    if os.path.exists(user_data_folder) and os.path.isdir(user_data_folder):
        files = os.listdir(user_data_folder)
        return jsonify({"files": files})
    else:
        return jsonify({"message": f"Le dossier '{folder_name}' n'existe pas ou est vide."}), 404


def delete_user_file_service(folder_name, file_name):
    user_id = get_jwt_identity()
    user_data_folder = os.path.join('data', str(user_id), folder_name)
    file_path = os.path.join(user_data_folder, file_name)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)

        file = File.query.filter_by(url=f'/data/{user_id}/{folder_name}/{file_name}').first()
        if file:
            db.session.delete(file)
            db.session.commit()

        return jsonify({"message": f"Fichier {file_name} supprimé avec succès."})
    else:
        return jsonify({"message": f"Le fichier {file_name} n'a pas été trouvé dans le sous-dossier {folder_name}."}), 404


def download_user_file_service(folder_name, file_name):
    user_id = get_jwt_identity()
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    user_data_folder = os.path.join(root_path, 'data', str(user_id), folder_name)
    file_path = os.path.join(user_data_folder, file_name)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {file_name} n'a pas été trouvé dans le sous-dossier {folder_name}."}), 404

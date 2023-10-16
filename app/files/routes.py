from app.files import bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify, send_file
from app.extensions import db
from app.models.file import File
from app.models.folder import Folder  # Assurez-vous d'importer le modèle Folder
import os 

@bp.route('/upload/<folder_name>', methods=['POST'])
@jwt_required()
def upload_file(folder_name):
    user_id = get_jwt_identity()
    user_data_folder = os.path.join('data', str(user_id), folder_name)
    uploaded_file = request.files['file']

    if uploaded_file:
        file_path = os.path.join(user_data_folder, uploaded_file.filename)
        uploaded_file.save(file_path)

        # Obtenez l'ID du dossier associé au nom du dossier
        folder = Folder.query.filter_by(name=folder_name, user_id=user_id).first()

        if folder:
            # Créez une instance de la classe File et enregistrez-la dans la base de données
            file_url = f'/data/{user_id}/{folder_name}/{uploaded_file.filename}'  # Vous pouvez ajuster l'URL en fonction de votre structure de fichiers
            new_file = File(url=file_url, folder_id=folder.id)
            db.session.add(new_file)
            db.session.commit()

            return jsonify({"message": "Fichier téléchargé avec succès."})

    return jsonify({"message": "Aucun fichier n'a été téléchargé."})

@bp.route('/list_files/<folder_name>', methods=['GET'])
@jwt_required()
def list_user_files(folder_name):
    user_id = get_jwt_identity()
    user_data_folder = os.path.join('data', str(user_id), folder_name)

    if os.path.exists(user_data_folder) and os.path.isdir(user_data_folder):
        files = os.listdir(user_data_folder)
        return jsonify({"files": files})
    else:
        return jsonify({"message": f"Le dossier '{folder_name}' n'existe pas ou est vide."}), 404

@bp.route('/delete_user_file/<folder_name>/<filename>', methods=['DELETE'])
@jwt_required()
def delete_user_file(folder_name, filename):
    user_id = get_jwt_identity()
    user_data_folder = os.path.join('data', str(user_id), folder_name)
    file_path = os.path.join(user_data_folder, filename)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        
        # Supprimez également l'entrée de la base de données
        file = File.query.filter_by(url=f'/data/{user_id}/{folder_name}/{filename}').first()
        if file:
            db.session.delete(file)
            db.session.commit()

        return jsonify({"message": f"Fichier {filename} supprimé avec succès."})
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé dans le sous-dossier {folder_name}."}), 404

@bp.route('/download_user_file/<folder_name>/<filename>', methods=['GET'])
@jwt_required()
def download_user_file(folder_name, filename):
    user_id = get_jwt_identity()
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    user_data_folder = os.path.join(root_path, 'data', str(user_id), folder_name)
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé dans le sous-dossier {folder_name}."}), 404

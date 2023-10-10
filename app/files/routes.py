from app.files import bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify, send_file
import os 


@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    uploaded_file = request.files['file']
    if uploaded_file:
        file_path = os.path.join(user_data_folder, uploaded_file.filename)
        uploaded_file.save(file_path)
        return jsonify({"message": "Fichier téléchargé avec succès."})
    else:
        return jsonify({"message": "Aucun fichier n'a été téléchargé."})
    

@bp.route('/list_files', methods=['GET'])
@jwt_required()
def list_user_files():
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'

    if os.path.exists(user_data_folder) and os.path.isdir(user_data_folder):
        files = os.listdir(user_data_folder)
        return jsonify({"files": files})
    else:
        return jsonify({"message": "Le dossier 'data/user_id' n'existe pas ou est vide."}), 404
    

@bp.route('/read_user_file/<filename>', methods=['GET'])
@jwt_required()
def read_user_file(filename):
   
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404
    

@bp.route('/delete_user_file/<filename>', methods=['DELETE'])
@jwt_required()
def delete_user_file(filename):
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({"message": f"Fichier {filename} supprimé avec succès."})
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404


@bp.route('/download_user_file/<filename>', methods=['GET'])
@jwt_required()
def download_user_file(filename):
    user_id = get_jwt_identity()
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    user_data_folder = os.path.join(root_path, 'data', user_id)
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404
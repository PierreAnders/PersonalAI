from app.folders import bp
from app.folders.service import add_folder_service, delete_folder_service, get_all_folders_service
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify


@bp.route('/folders', methods=['POST'])
@jwt_required()
def add_folder():
    data = request.get_json()
    name = data.get("name")
    user_id = get_jwt_identity()
    response, status_code = add_folder_service(name, user_id)
    return jsonify(response), status_code


@bp.route('/folders/<int:folder_id>', methods=['DELETE'])
@jwt_required()
def delete_folder(folder_id):
    user_id = get_jwt_identity()
    response, status_code = delete_folder_service(folder_id, user_id)
    return jsonify(response), status_code


@bp.route('/folders', methods=['GET'])
@jwt_required()
def get_all_folders():
    user_id = get_jwt_identity()
    response, status_code = get_all_folders_service(user_id)
    return jsonify(response), status_code

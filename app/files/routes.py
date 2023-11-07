from app.files import bp
from flask_jwt_extended import jwt_required
from app.files.service import upload_file_service, list_user_files_service, delete_user_file_service, download_user_file_service


@bp.route('/folders/<folder_name>/files', methods=['POST'])
@jwt_required()
def upload_file(folder_name):
    return upload_file_service(folder_name)


@bp.route('/folders/<folder_name>/files', methods=['GET'])
@jwt_required()
def list_user_files(folder_name):
    return list_user_files_service(folder_name)


@bp.route('/folders/<folder_name>/files/<file_name>', methods=['DELETE'])
@jwt_required()
def delete_user_file(folder_name, file_name):
    return delete_user_file_service(folder_name, file_name)


@bp.route('/folders/<folder_name>/files/<file_name>', methods=['GET'])
@jwt_required()
def download_user_file(folder_name, file_name):
    return download_user_file_service(folder_name, file_name)
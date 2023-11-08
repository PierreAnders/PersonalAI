from app.healths import bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app.healths.service import add_or_update_health_info_service, get_health_info_service, write_user_data

@bp.route('/user_health', methods=['POST'])
@jwt_required()
def add_or_update_health_info():
    data = request.get_json()
    user_id = get_jwt_identity()
    write_user_data(user_id, data)   
    
    result, status_code = add_or_update_health_info_service(
        user_id,
        data.get("gender"),
        data.get("weight"),
        data.get("size"),
        data.get("social_security_number"),
        data.get("blood_group"),
        data.get("doctor")
    )
    return jsonify(result), status_code

@bp.route('/user_health', methods=['GET'])
@jwt_required()
def get_health_info():
    user_id = get_jwt_identity()
    health_info, status_code = get_health_info_service(user_id)
    return jsonify(health_info), status_code

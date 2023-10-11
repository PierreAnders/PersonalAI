from app.healths import bp
from app.extensions import db
from app.models.health import Health
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

@bp.route('/user_health', methods=['POST'])
@jwt_required()
def add_health_info():
    data = request.get_json()
    gender = data.get("gender")
    weight = data.get("weight")
    size = data.get("size")
    social_security_number = data.get("social_security_number")
    blood_group = data.get("blood_group")
    doctor = data.get("doctor")

    user_id = get_jwt_identity()

    health_info = Health(gender=gender, weight=weight, size=size, social_security_number=social_security_number, blood_group=blood_group, doctor=doctor, user_id=user_id)

    try:
        db.session.add(health_info)
        db.session.commit()
        return jsonify({"message": "Informations de santé enregistrées avec succès"}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500
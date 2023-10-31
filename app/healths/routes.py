from app.healths import bp
from app.extensions import db
from app.healths.model import Health
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError


@bp.route('/user_health', methods=['POST'])
@jwt_required()
def add_or_update_health_info():
    data = request.get_json()
    gender = data.get("gender")
    weight = data.get("weight")
    size = data.get("size")
    social_security_number = data.get("social_security_number")
    blood_group = data.get("blood_group")
    doctor = data.get("doctor")

    user_id = get_jwt_identity()

    # Vérifiez si des informations de santé existent pour l'utilisateur actuel
    health_info = Health.query.filter_by(user_id=user_id).first()

    if health_info:
        # Mettez à jour les données existantes
        health_info.gender = gender
        health_info.weight = weight
        health_info.size = size
        health_info.social_security_number = social_security_number
        health_info.blood_group = blood_group
        health_info.doctor = doctor
    else:
        # Si aucune donnée de santé n'existe, créez une nouvelle entrée
        health_info = Health(
            gender=gender,
            weight=weight,
            size=size,
            social_security_number=social_security_number,
            blood_group=blood_group,
            doctor=doctor,
            user_id=user_id
        )

    try:
        db.session.add(health_info)
        db.session.commit()
        return jsonify({"message": "Informations de santé enregistrées avec succès"}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500

    
@bp.route('/user_health', methods=['GET'])
@jwt_required()
def get_health_info():
    user_id = get_jwt_identity()
    health_info = Health.query.filter_by(user_id=user_id).first()
    if health_info:
        return jsonify({
            "gender": health_info.gender,
            "weight": health_info.weight,
            "size": health_info.size,
            "social_security_number": health_info.social_security_number,
            "blood_group": health_info.blood_group,
            "doctor": health_info.doctor
        }), 200
    else:
        return jsonify({"message": "Aucune information de santé trouvée"}), 404
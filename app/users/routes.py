from datetime import timedelta, datetime
from flask import request, jsonify
from app.users import bp
from app.extensions import bcrypt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.users.service import login_user_service, register_user_service, get_user_by_id_service, update_user_service
from sqlalchemy.exc import IntegrityError


@bp.route('/users/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Veuillez fournir l\'email et le mot de passe'}), 400

    try:
        new_user = register_user_service(data)
        return jsonify({'message': 'Inscription réussie'}), 201
    except IntegrityError as e:
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500 


@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    user = login_user_service(data)

    if not user or not bcrypt.check_password_hash(user.password, data.get('password')):
        return jsonify({'message': 'Email ou mot de passe incorrect'}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
    return jsonify({'access_token': access_token})


@bp.route('/users/info', methods=['GET'])
@jwt_required()
def get_user_info():
    user_id = get_jwt_identity()
    user = get_user_by_id_service(user_id)

    if user:
        birth_date_str = user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None

        return jsonify({
            "firstname": user.firstname,
            "lastname": user.lastname,
            "birth_date": birth_date_str, 
            "email": user.email,
        }), 200
    else:
        return jsonify({"message": "Aucune information utilisateur trouvée"}), 404
    

@bp.route('/users/update', methods=['PUT'])
@jwt_required()
def update_user_info():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = get_user_by_id_service(user_id)

    try:
        update_user_service(user, data)

        user_json = {
            "firstname": user.firstname,
            "lastname": user.lastname,
            "birth_date": user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None,
            "email": user.email
        }
        return jsonify({"message": "Informations mises à jour avec succès", "user": user_json}), 200
    except IntegrityError as e:
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500
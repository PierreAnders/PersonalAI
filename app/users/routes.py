from flask import request, jsonify
from app.users import bp
from app.extensions import db, bcrypt
from app.users.model import User
import os
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta, datetime


def create_user_folder(user_id):
    user_data_folder = os.path.join('data', str(user_id))
    try:
      os.mkdir(user_data_folder)
      print(f"Dossier '{user_data_folder}' créé avec succès.")
    except FileExistsError:
        print(f"Le dossier '{user_data_folder}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")


@bp.route('/users/register', methods=['POST'])
def register():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    birth_date = data.get('birth_date')
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Veuillez fournir l\'email et le mot de passe'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(firstname=firstname, lastname=lastname, birth_date=birth_date, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    create_user_folder(new_user.id)

    return jsonify({'message': 'Inscription réussie'}), 201


@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Email ou mot de passe incorrect'}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))

    return jsonify({'access_token': access_token})


@bp.route('/users/info', methods=['GET'])
@jwt_required()
def get_user_info():
    user_id = get_jwt_identity()
    user_info = User.query.filter_by(id=user_id).first()
    if user_info:
        # Convertissez la date de naissance en une chaîne au format 'YYYY-MM-DD'
        birth_date_str = user_info.birth_date.strftime('%Y-%m-%d') if user_info.birth_date else None

        return jsonify({
            "firstname": user_info.firstname,
            "lastname": user_info.lastname,
            "birth_date": birth_date_str,  # Renvoie la date au format 'YYYY-MM-DD'
            "email": user_info.email,
        }), 200
    else:
        return jsonify({"message": "Aucune information utilisateur trouvée"}), 404
    

@bp.route('/users/update', methods=['PUT'])
@jwt_required()
def update_user_info():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    birth_date_str = data.get('birth_date')  # La date en tant que chaîne
    email = data.get('email')

    user_id = get_jwt_identity()

    user_info = User.query.filter_by(id=user_id).first()

    user_info.firstname = firstname
    user_info.lastname = lastname

    # Convertissez la chaîne de date en objet de date
    try:
        user_info.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Format de date invalide"}), 400

    user_info.email = email

    try:
        db.session.add(user_info)
        db.session.commit()
        return jsonify({"message": "Informations mises à jour avec succès"}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500
from flask import request, jsonify
from app.users import bp
from app.extensions import db, bcrypt
from app.models.user import User
import os
from flask_jwt_extended import create_access_token
# from flask_cors import cross_origin


@bp.route('/register', methods=['POST'])
# @cross_origin(origin='http://127.0.0.1:3000')
def register():
    data = request.get_json()
    nom = data.get('nom')
    email = data.get('email')
    mot_de_passe = data.get('mot_de_passe')

    if not nom or not email or not mot_de_passe:
        return jsonify({'message': 'Veuillez fournir le nom, l\'email et le mot de passe'}), 400

    hashed_password = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')
    new_user = User(nom=nom, email=email, mot_de_passe=hashed_password)

    db.session.add(new_user)
    db.session.commit()
    user_id = new_user.id
    user_data_folder = os.path.join('data', str(user_id))

    try:
      os.mkdir(user_data_folder)
      print(f"Dossier '{user_data_folder}' créé avec succès.")
    except FileExistsError:
        print(f"Le dossier '{user_data_folder}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")

    return jsonify({'message': 'Inscription réussie'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    mot_de_passe = data.get('mot_de_passe')

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.mot_de_passe, mot_de_passe):
        return jsonify({'message': 'Email ou mot de passe incorrect'}), 401

    access_token = create_access_token(identity=user.id)

    return jsonify({'access_token': access_token})
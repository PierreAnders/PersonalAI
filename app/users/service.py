import os
from app.extensions import db, bcrypt
from app.users.model import User
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt_identity


def create_directory(directory_path):
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Dossier '{directory_path}' créé avec succès.")
    except FileExistsError:
        print(f"Le dossier '{directory_path}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")


# Création du dossier de l'utilisateur avec son uuid
def create_user_folder(user_id):
    user_data_folder = os.path.join('data', str(user_id))
    create_directory(user_data_folder)


# Création d'un sous-dossier avec ses informations dans un fichier texte 'user.txt'
def write_user_data(user_id, data):
    user_subfolder_info_db = os.path.join('data', str(user_id), f"info-{user_id}")
    create_directory(user_subfolder_info_db)

    file_path = os.path.join(user_subfolder_info_db, 'user.txt')

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("INFORMATIONS GENERALES DE L'UTILISATEUR:\n\n")
            file.write(f"Je m'appelle {data['firstname']} {data['lastname']}.\n")
            file.write(f"Je suis né le {data['birth_date']}.\n")
            file.write(f"Mon adresse mail est: {data['email']}.\n")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'écriture des données de l'utilisateur dans le fichier : {str(e)}")


def register_user_service(data):
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    birth_date = data.get('birth_date')
    email = data.get('email')
    password = data.get('password')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(firstname=firstname, lastname=lastname, birth_date=birth_date, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    create_user_folder(new_user.id)

    return new_user


def login_user_service(data):
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    return user


def get_user_by_id_service(user_id):
    user = User.query.filter_by(id=user_id).first()

    return user


def update_user_service(user, data):
    user_id = get_jwt_identity()
    write_user_data(user_id, data)
    
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    birth_date_str = data.get('birth_date')
    email = data.get('email')

    user.firstname = firstname
    user.lastname = lastname
    user.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
    user.email = email

    db.session.add(user)
    db.session.commit()
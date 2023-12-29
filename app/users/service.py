import os
from app.extensions import db, bcrypt
from app.users.model import User
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt_identity
from app.folders.model import Folder
from sqlalchemy.orm.exc import NoResultFound


# def create_directory(directory_path):
#     try:
#         os.makedirs(directory_path, exist_ok=True)
#         print(f"Dossier '{directory_path}' créé avec succès.")
#     except FileExistsError:
#         print(f"Le dossier '{directory_path}' existe déjà.")
#     except Exception as e:
#         print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")


# Création du dossier de l'utilisateur avec son uuid
def create_user_folder(user_id):
    user_data_folder = os.path.join('data', str(user_id))
    create_directory(user_data_folder)


def write_user_data(user_id, data):
    user_subfolder_info_db = os.path.join('data', str(user_id), "Database")

    try:
        os.makedirs(user_subfolder_info_db, exist_ok=True)
        print(f"Dossier '{user_subfolder_info_db}' créé avec succès.")

        folder = Folder.query.filter_by(name='Database', user_id=user_id).first()

        if folder is None:
            folder = Folder(name='Database', user_id=user_id)
            try:
                db.session.add(folder)
                db.session.commit()
                print({"message": "Dossier ajouté avec succès"}, 201)
            except IntegrityError as e:
                db.session.rollback()
                print({"message": "Erreur de base de données : " + str(e)}, 500)
        else:
            print({"message": "Le dossier existe déjà"}, 200)

        file_path = os.path.join(user_subfolder_info_db, 'user.txt')
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("MES INFORMATIONS GENERALES :\n\n")
            file.write(f"Je m'appelle {data['firstname']} {data['lastname']}.\n")
            file.write(f"Je suis né le {data['birth_date']}.\n")
            file.write(f"Mon adresse mail est: {data['email']}.\n")

    except FileExistsError:
        print(f"Le dossier '{user_subfolder_info_db}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")


def register_user_service(data):
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    birth_date = data.get('birth_date')
    email = data.get('email')
    password = data.get('password')

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(firstname=firstname, lastname=lastname, birth_date=birth_date, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        create_user_folder(new_user.id)

        return new_user

    except IntegrityError as e:
        db.session.rollback()
        raise ValueError("Cette adresse e-mail est déjà utilisée.") from e
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Une erreur s'est produite lors de l'inscription : {str(e)}") from e


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
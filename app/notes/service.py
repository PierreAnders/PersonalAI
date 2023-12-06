import os
from app.folders.model import Folder
from app.extensions import db


def create_user_notes_folder(user_id):
    user_subfolder_notes = os.path.join('data', str(user_id), "Notes")

    try:
        if not os.path.exists(user_subfolder_notes):
            os.makedirs(user_subfolder_notes)
            add_notes_folder_in_db(user_id)
            print(f"Dossier '{user_subfolder_notes}' créé avec succès.")
        else:
            print(f"Le dossier '{user_subfolder_notes}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")


def add_notes_folder_in_db(user_id):
    folder = Folder(name="Notes", user_id=user_id)

    try:
        db.session.add(folder)
        db.session.commit()
        return {"message": "Nom du dossier ajouté dans la base de donnée"}, 201
    except IntegrityError as e:
        db.session.rollback()
        return {"message": "Erreur de base de données : " + str(e)}, 500


def add_note_service(title, content, user_id):
    try:
        create_user_notes_folder(user_id)
        user_subfolder_notes = os.path.join('data', str(user_id), f"Notes")

        file_path = os.path.join(user_subfolder_notes, f'{title}.html')

        with open(file_path, 'w', encoding='utf-8') as file:
            # file.write(f"{title} :\n\n")
            file.write(f"{content}\n")

        print(f"Note '{title}' ajoutée avec succès.")
        return {"message": f"Note '{title}' ajoutée avec succès."}, 200
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'ajout de la note : {str(e)}")
        return {"error": f"Erreur lors de l'ajout de la note : {str(e)}"}, 500

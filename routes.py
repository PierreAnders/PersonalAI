from flask import Blueprint, request, jsonify, send_file
from models import db, User, AgentInformation
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from glob import glob
import openai

bp = Blueprint('main', __name__)
bcrypt = Bcrypt()

chat_histories = {}

@bp.route('/register', methods=['POST'])
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

@bp.route('/agent_info', methods=['POST'])
@jwt_required()
def add_agent_info():
    data = request.get_json()
    nom = data.get("nom")
    objectif = data.get("objectif")

    user_id = get_jwt_identity()

    agent_info = AgentInformation(nom=nom, objectif=objectif, user_id=user_id)

    try:
        db.session.add(agent_info)
        db.session.commit()
        return jsonify({"message": "Informations de l'agent enregistrées avec succès"}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500

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

def get_user_info(user_id):
    """
    Cette fonction récupère les informations de l'utilisateur à partir de la base de données.
    Args:
        user_id (int): L'identifiant de l'utilisateur.
    Returns:
        dict: Un dictionnaire contenant les informations de l'utilisateur (nom et objectif).
    """
    user = User.query.filter_by(id=user_id).first()

    if user:

        user_info = {
            "nom": user.nom,
            "objectif": None
        }

        for agent_info in user.user_info:
            user_info["objectif"] = agent_info.objectif
            break

        return user_info
    else:
        return {"nom": "Utilisateur inconnu", "objectif": None}

@bp.route('/AIchatWithData', methods=['POST'])
@jwt_required()
def chat():
    
    PERSIST = False

    if PERSIST and os.path.exists("persist"):
      print("Reusing index...\n")
      vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
      index = VectorStoreIndexWrapper(vectorstore=vectorstore)
    else:
      user_id = get_jwt_identity()
      user_data_folder = f'data/{user_id}/'
      subdirs = glob(user_data_folder)

      loaders = []
      for subdir in subdirs:
          loader = DirectoryLoader(subdir)
          loaders.append(loader)
      if PERSIST:
        index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders(loaders)
      else: 
        index = VectorstoreIndexCreator().from_loaders(loaders)

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-3.5-turbo"), # gpt-3.5-turbo-16k, gpt-4 ...
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),)

    data = request.get_json()
    session_id = data.get("session_id")
    query = data.get("query")

    # user_id = get_jwt_identity()
    # user_info = get_user_info(user_id)
    # current_date = datetime.date.today().strftime('%Y-%m-%d')
    # query = f"Nom de l'utilisateur: {user_info['nom']}. Objectif de l'utilisateur : {user_info['objectif']}. Date du jour : {current_date}. {query}"

    chat_history = chat_histories.get(session_id, [])

    result = chain({"question": query, "chat_history": chat_history})

    chat_history.append((query, result['answer']))
    chat_histories[session_id] = chat_history

    return jsonify(result)

@bp.route('/AIchatGeneric', methods=['POST'])
@jwt_required()
def chat_generic():
    data = request.get_json()
    session_id = data.get("session_id")
    query = data.get("query")

    chat_history = chat_histories.get(session_id, [])
    chat_history.append((query, ""))

    messages = [{"role": "user", "content": msg} for msg, _ in chat_history]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages)

    assistant_reply = response["choices"][0]["message"]["content"]
    
    chat_history[-1] = (query, assistant_reply)
    chat_histories[session_id] = chat_history

    return jsonify({"answer": assistant_reply})

@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    uploaded_file = request.files['file']
    if uploaded_file:
        file_path = os.path.join(user_data_folder, uploaded_file.filename)
        uploaded_file.save(file_path)
        return jsonify({"message": "Fichier téléchargé avec succès."})
    else:
        return jsonify({"message": "Aucun fichier n'a été téléchargé."})
    
@bp.route('/list_files', methods=['GET'])
@jwt_required()
def list_user_files():
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'

    if os.path.exists(user_data_folder) and os.path.isdir(user_data_folder):
        files = os.listdir(user_data_folder)
        return jsonify({"files": files})
    else:
        return jsonify({"message": "Le dossier 'data/user_id' n'existe pas ou est vide."}), 404
    
@bp.route('/read_user_file/<filename>', methods=['GET'])
@jwt_required()
def read_user_file(filename):
   
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404
    
@bp.route('/delete_user_file/<filename>', methods=['DELETE'])
@jwt_required()
def delete_user_file(filename):
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({"message": f"Fichier {filename} supprimé avec succès."})
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404

@bp.route('/download_user_file/<filename>', methods=['GET'])
@jwt_required()
def download_user_file(filename):
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404
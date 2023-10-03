from flask_migrate import Migrate
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from flasgger import Swagger
import openai
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from glob import glob

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from config import Config

import uuid
import datetime

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config.from_object(Config)

# app.config['SECRET_KEY'] = "50c34e5139cb598bf297a67910047d29a422b1bd828557ec"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:3568@localhost/mia'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

swagger = Swagger(app)
CORS(app)

# PERSIST = False

# if PERSIST and os.path.exists("persist"):
#   print("Reusing index...\n")
#   vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
#   index = VectorStoreIndexWrapper(vectorstore=vectorstore)
# else:
#   # subdirs = glob('data/*/') 
#   subdirs = glob('data/user_id/')

#   loaders = []
#   for subdir in subdirs:
#       loader = DirectoryLoader(subdir)
#       loaders.append(loader)
#   if PERSIST:
#     index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders(loaders)
#   else: 
#     index = VectorstoreIndexCreator().from_loaders(loaders)


# chain = ConversationalRetrievalChain.from_llm(
#     llm=ChatOpenAI(model="gpt-3.5-turbo"), # gpt-3.5-turbo-16k, gpt-4 ...
#     retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),)

chat_histories = {}

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    nom = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    date_de_creation = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    user_info = db.relationship('AgentInformation', backref='user', lazy=True)

class AgentInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    objectif = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    def __init__(self, nom, objectif, user_id):
        self.nom = nom
        self.objectif = objectif
        self.user_id = user_id

@app.route('/agent_info', methods=['POST'])
@jwt_required()
def add_agent_info():
    data = request.get_json()
    nom = data.get("nom")
    objectif = data.get("objectif")

    # Obtenez l'identité de l'utilisateur à partir du jeton JWT
    user_id = get_jwt_identity()

    # Créez une nouvelle instance d'AgentInformation liée à l'utilisateur
    agent_info = AgentInformation(nom=nom, objectif=objectif, user_id=user_id)

    try:
        db.session.add(agent_info)
        db.session.commit()
        return jsonify({"message": "Informations de l'agent enregistrées avec succès"}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "Erreur de base de données : " + str(e)}), 500
    
@app.route('/register', methods=['POST'])
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

@app.route('/login', methods=['POST'])
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
        # Si l'utilisateur existe, récupérez son nom et son objectif
        user_info = {
            "nom": user.nom,
            "objectif": None  # Par défaut, l'objectif est None
        }

        # Parcourez la liste d'AgentInformation liée à l'utilisateur
        for agent_info in user.user_info:
            user_info["objectif"] = agent_info.objectif
            break  # Sortez de la boucle après avoir trouvé le premier objectif (si présent)

        return user_info
    else:
        # Si l'utilisateur n'existe pas, retournez un dictionnaire vide ou une valeur par défaut
        return {"nom": "Utilisateur inconnu", "objectif": None}

@app.route('/AIchatWithData', methods=['POST'])
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

@app.route('/AIchatGeneric', methods=['POST'])
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

@app.route('/upload', methods=['POST'])
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
    
@app.route('/list_files', methods=['GET'])
@jwt_required()
def list_user_files():
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'

    if os.path.exists(user_data_folder) and os.path.isdir(user_data_folder):
        files = os.listdir(user_data_folder)
        return jsonify({"files": files})
    else:
        return jsonify({"message": "Le dossier 'data/user_id' n'existe pas ou est vide."}), 404
    
@app.route('/read_user_file/<filename>', methods=['GET'])
@jwt_required()
def read_user_file(filename):
   
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404
    
@app.route('/delete_user_file/<filename>', methods=['DELETE'])
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

@app.route('/download_user_file/<filename>', methods=['GET'])
@jwt_required()
def download_user_file(filename):
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/'
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

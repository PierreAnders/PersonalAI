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

import uuid
import datetime

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = "50c34e5139cb598bf297a67910047d29a422b1bd828557ec"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:3568@localhost/mia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
swagger = Swagger(app)
CORS(app)

PERSIST = False

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  # subdirs = glob('data/*/') 
  subdirs = glob('data/user_id/')

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
    """
    Cette API permet à l'utilisateur de saisir les informations de l'agent, y compris le nom et l'objectif.
    ---
    tags:
      - Agent Information API
    parameters:
    - in: body
      name: body
      schema:
        type: object
        properties:
          nom:
            type: string
            description: Le nom de l'agent
          objectif:
            type: string
            description: L'objectif de l'agent
        required:
          - nom
    responses:
      201:
        description: Informations de l'agent enregistrées avec succès
    """
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
    """
    Cette API permet à l'utilisateur de s'inscrire en fournissant un nom d'utilisateur, un email et un mot de passe.
    ---
    tags:
      - Authentification API
    parameters:
    - in: body
      name: body
      schema:
        type: object
        properties:
          nom:
            type: string
            description: Le nom de l'utilisateur
          email:
            type: string
            description: L'adresse email de l'utilisateur
          mot_de_passe:
            type: string
            description: Le mot de passe de l'utilisateur
        required:
          - nom
          - email
          - mot_de_passe
    responses:
      201:
        description: Inscription réussie
      400:
        description: Erreur de requête en cas de champs manquants
    """
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

    return jsonify({'message': 'Inscription réussie'}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Cette API permet à l'utilisateur de se connecter en fournissant un email et un mot de passe.
    ---
    tags:
      - Authentification API
    parameters:
    - in: body
      name: body
      schema:
        type: object
        properties:
          email:
            type: string
            description: L'adresse email de l'utilisateur
          mot_de_passe:
            type: string
            description: Le mot de passe de l'utilisateur
        required:
          - email
          - mot_de_passe
    responses:
      200:
        description: Connexion réussie
      401:
        description: Échec de la connexion en raison d'informations incorrectes
    """
    data = request.get_json()
    email = data.get('email')
    mot_de_passe = data.get('mot_de_passe')

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.mot_de_passe, mot_de_passe):
        return jsonify({'message': 'Email ou mot de passe incorrect'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token})

# @app.route('/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     """
#     Cette API représente une ressource protégée nécessitant une authentification.
#     ---
#     tags:
#       - Authentification API
#     responses:
#       200:
#         description: Ressource protégée
#       401:
#         description: Échec de l'authentification
#     """
#     return jsonify({'message': 'Ressource protégée'})

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
    """
    Cette API lance une conversation avec le bot
    ---
    tags:
      - Chat API
    parameters:
    - in: body
      name: body
      schema:
        type: object
        properties:
          session_id:
            type: string
            description: L'ID de la session
          query:
            type: string
            description: La question posée par l'utilisateur
        required:
          - session_id
          - query
    responses:
      200:
        description: Réponse du bot
    """
    data = request.get_json()
    session_id = data.get("session_id")
    query = data.get("query")

    user_id = get_jwt_identity()

    user_info = get_user_info(user_id)

    current_date = datetime.date.today().strftime('%Y-%m-%d')

    query = f"Nom de l'utilisateur: {user_info['nom']}. Objectif de l'utilisateur : {user_info['objectif']}. Date du jour : {current_date}. {query}"

    chat_history = chat_histories.get(session_id, [])

    result = chain({"question": query, "chat_history": chat_history})

    chat_history.append((query, result['answer']))
    chat_histories[session_id] = chat_history

    return jsonify(result)


@app.route('/AIchatGeneric', methods=['POST'])
@jwt_required()
def chat_generic():
    """
    Cette API lance une conversation avec le chatbot générique
    ---
    tags:
      - Chat API
    parameters:
    - in: body
      name: body
      schema:
        type: object
        properties:
          session_id:
            type: string
            description: L'ID de la session
          query:
            type: string
            description: La question posée par l'utilisateur
        required:
          - session_id
          - query
    responses:
      200:
        description: Réponse du chatbot générique
    """
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
    """
    Cette API permet à l'utilisateur d'ajouter des fichiers au dossier "data"
    ---
    tags:
      - Upload API
    parameters:
    - in: formData
      name: file
      type: file
      required: true
      description: Le fichier à télécharger dans le dossier "data"
    responses:
      200:
        description: Fichier téléchargé avec succès
    """
    uploaded_file = request.files['file']
    if uploaded_file:
        file_path = os.path.join("data/user_id", uploaded_file.filename)
        uploaded_file.save(file_path)
        return jsonify({"message": "Fichier téléchargé avec succès."})
    else:
        return jsonify({"message": "Aucun fichier n'a été téléchargé."})
    
@app.route('/list_files', methods=['GET'])
@jwt_required()
def list_user_files():
    """
    Cette API affiche la liste de tous les fichiers de l'utilisateur dans le dossier "data/user_id"
    ---
    tags:
      - List User Files API
    responses:
      200:
        description: Liste des fichiers de l'utilisateur
      404:
        description: Le dossier 'data/user_id' n'existe pas ou est vide
    """
    user_data_folder = "data/user_id"
    if os.path.exists(user_data_folder) and os.path.isdir(user_data_folder):
        files = os.listdir(user_data_folder)
        return jsonify({"files": files})
    else:
        return jsonify({"message": "Le dossier 'data/user_id' n'existe pas ou est vide."}), 404
    
@app.route('/read_user_file/<filename>', methods=['GET'])
@jwt_required()
def read_user_file(filename):
    """
    Cette API permet à l'utilisateur de lire le contenu d'un fichier du dossier "data/user_id"
    ---
    tags:
      - Read User File API
    parameters:
    - in: path
      name: filename
      type: string
      required: true
      description: Le nom du fichier à lire
    responses:
      200:
        description: Contenu du fichier
      404:
        description: Le fichier n'a pas été trouvé
    """
    user_data_folder = "data/user_id"
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404
    
@app.route('/delete_user_file/<filename>', methods=['DELETE'])
# @jwt_required()
def delete_user_file(filename):
    """
    Cette API permet à l'utilisateur de supprimer un fichier du dossier "data/user_id"
    ---
    tags:
      - Delete User File API
    parameters:
    - in: path
      name: filename
      type: string
      required: true
      description: Le nom du fichier à supprimer
    responses:
      200:
        description: Fichier supprimé avec succès
      404:
        description: Le fichier n'a pas été trouvé
    """
    user_data_folder = "data/user_id"
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({"message": f"Fichier {filename} supprimé avec succès."})
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404

@app.route('/download_user_file/<filename>', methods=['GET'])
# @jwt_required()
def download_user_file(filename):
    """
    Cette API permet à l'utilisateur de télécharger un fichier du dossier "data/user_id"
    ---
    tags:
      - Download User File API
    parameters:
    - in: path
      name: filename
      type: string
      required: true
      description: Le nom du fichier à télécharger
    responses:
      200:
        description: Téléchargement du fichier
      404:
        description: Le fichier n'a pas été trouvé
    """
    user_data_folder = "data/user_id"
    file_path = os.path.join(user_data_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": f"Le fichier {filename} n'a pas été trouvé."}), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

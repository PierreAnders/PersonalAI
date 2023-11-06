###################
# CODE REFACTO --> Service 
###################
from app.chats import bp
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.chats.service import chat_with_data_service

@bp.route('/chatWithData/<model>', methods=['POST'])
@jwt_required()
def chat_with_data(model):
    data = request.get_json()
    result = chat_with_data_service(model, data)
    return jsonify(result)

###################
# CODE V2 
###################

# from app.chats import bp
# import os
# from flask import request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from langchain.vectorstores import Chroma
# from langchain.indexes.vectorstore import VectorStoreIndexWrapper
# from glob import glob
# from langchain.document_loaders import DirectoryLoader
# from langchain.indexes import VectorstoreIndexCreator
# from langchain.chains import ConversationalRetrievalChain
# from langchain.chat_models import ChatOpenAI
# from langchain.embeddings import OpenAIEmbeddings
# import openai
# from dotenv import load_dotenv

# load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")

# chat_histories = {}

# @bp.route('/AIchatWithData/<model>', methods=['POST'])
# @jwt_required()
# def chat(model):
#     PERSIST = False

#     index = get_or_create_index(PERSIST)

#     chain = create_conversational_chain(model, index)

#     data = request.get_json()
#     session_id = data.get("session_id")
#     query = data.get("query")

#     chat_history = get_chat_history(session_id, chat_histories)
#     result = generate_response(chain, query, chat_history)

#     update_chat_history(session_id, chat_history, query, result['answer'])

#     return jsonify(result)

# def get_or_create_index(persist):
#     if persist and os.path.exists("persist"):
#         vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
#         index = VectorStoreIndexWrapper(vectorstore=vectorstore)
#     else:
#         user_id = get_jwt_identity()
#         user_data_folder = f'data/{user_id}/'
#         subdirs = [folder.path for folder in os.scandir(user_data_folder) if folder.is_dir()]
#         loaders = [DirectoryLoader(subdir) for subdir in subdirs]
#         if persist:
#             index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders(loaders)
#         else:
#             index = VectorstoreIndexCreator().from_loaders(loaders)
#     return index

# def create_conversational_chain(model, index):
#     chain = ConversationalRetrievalChain.from_llm(
#         llm=ChatOpenAI(model=model),
#         retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
#     )
#     return chain

# def get_chat_history(session_id, chat_histories):
#     chat_history = chat_histories.get(session_id, [])
#     return chat_history

# def generate_response(chain, query, chat_history):
#     result = chain({"question": query, "chat_history": chat_history})
#     return result

# def update_chat_history(session_id, chat_history, query, answer):
#     chat_history.append((query, answer))
#     chat_histories[session_id] = chat_history


###################
# ANCIEN CODE 
###################

# from app.chats import bp
# import os
# from flask import request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from langchain.vectorstores import Chroma
# from langchain.indexes.vectorstore import VectorStoreIndexWrapper
# from glob import glob
# from langchain.document_loaders import DirectoryLoader
# from langchain.indexes import VectorstoreIndexCreator
# from langchain.chains import ConversationalRetrievalChain
# from langchain.chat_models import ChatOpenAI
# from langchain.embeddings import OpenAIEmbeddings
# import openai
# # import datetime
# from dotenv import load_dotenv

# load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")

# @bp.route('/AIchatWithData/<model>', methods=['POST'])
# @jwt_required()
# def chat(model):
    
#     # Création de l'historique de chat
#     chat_histories = {}

#     PERSIST = False

#     # Si la persistance est activé et si l'index a déjà été créé
#     if PERSIST and os.path.exists("persist"):
#       print("Reusing index...\n")
#       # Création d'un stockage de vecteurs Chroma avec persistance 
#       # et OpenAIEmbeddings comme fonction d'incorporation 
#       vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
#       # Création d'une enveloppe VectorStoreIndexWrapper(Langchain class) avec le vectorstore
#       index = VectorStoreIndexWrapper(vectorstore=vectorstore)
#     else:
#       # Obtention de l'ID de l'utilisateur à partir du jeton JWT
#       user_id = get_jwt_identity()
#       # Création du chemin du dossier de données de l'utilisateur
#       user_data_folder = f'data/{user_id}/'
#       # Obtention d'une liste de sous-dossiers
#       subdirs = [folder.path for folder in os.scandir(user_data_folder) if folder.is_dir()]

#       # Création d'un liste vide pour stocker les chargeurs 
#       loaders = []
#       # Parcours des sous-dossiers pour créer un chargeur pour chacun d'eux
#       for subdir in subdirs:
#           loader = DirectoryLoader(subdir)
#           loaders.append(loader)
#       if PERSIST:
#         # Si la persistance est activé --> création de l'index avec persistance 
#         # en utilisant VectorstoreIndexCreator (Langchain class)
#         index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders(loaders)
#         # Si la persistance est désactivée --> création de l'index sans persistance
#       else: 
#         index = VectorstoreIndexCreator().from_loaders(loaders)

#     # Création d'une instance de la classe ConversationalRetrievalChain
#     # pour gérer les conversations et récupérer des informations pertinentes 
#     # en fonction du modèle de langage et du récupérateur fournis.

#     # llm crée une instance de la classe ChatOpenAI avec comme modèle gpt-4
    
#     # Retriever représente le composant récupérateur de la chaîne, 
#     # responsable de la récupération d'informations pertinentes
#     # en appelant index.vectorstore.as_retriever() pour convertir 
#     # le stockage de vecteurs en un récupérateur.

#     # search_kwarks indique que seul un résultat doit être extrait.

#     chain = ConversationalRetrievalChain.from_llm(
#         llm=ChatOpenAI(model=model), # or gpt-3.5-turbo, gpt-3.5-turbo-16k ...
#         retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),)

#     # Extraire et parser le contenu du JSON dans data
#     data = request.get_json()
#     # session_id pourrait permettre de créer une fonctionnalité 
#     # d'historiques de session de chat
#     session_id = data.get("session_id")
#     query = data.get("query")

#     # user_id = get_jwt_identity()
#     # user_info = get_user_info(user_id)
#     # current_date = datetime.date.today().strftime('%Y-%m-%d')
#     # query = f"Nom de l'utilisateur: {user_info['nom']}. Objectif de l'utilisateur : {user_info['objectif']}. Date du jour : {current_date}. {query}"

#     # Récupération de l'historique de chat de la session
#     chat_history = chat_histories.get(session_id, [])

#     # Intégration de la question et de l'historique de la conversation dans la chaîne
#     # Génération de la réponse
#     result = chain({"question": query, "chat_history": chat_history})

#     # Ajoute un tuple avec la question et la réponse dans l'historique de conversation
#     chat_history.append((query, result['answer']))
#     # Mise à jour de l'historique de la conversation
#     chat_histories[session_id] = chat_history

#     # Retourne la réponse générée par la chaine sous forme de JSON
#     return jsonify(result)

# @bp.route('/AIchatGeneric/<model>', methods=['POST'])
# @jwt_required()
# def chat_generic(model):
    
#     chat_histories = {}

#     data = request.get_json()
#     session_id = data.get("session_id")
#     query = data.get("query")

#     chat_history = chat_histories.get(session_id, [])
#     chat_history.append((query, ""))

#     messages = [{"role": "user", "content": msg} for msg, _ in chat_history]

#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages)

#     assistant_reply = response["choices"][0]["message"]["content"]
    
#     chat_history[-1] = (query, assistant_reply)
#     chat_histories[session_id] = chat_history

#     return jsonify({"answer": assistant_reply})
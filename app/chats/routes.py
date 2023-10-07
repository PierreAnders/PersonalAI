from app.chats import bp
import os
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from langchain.vectorstores import Chroma
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from glob import glob
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
import openai
from dotenv import load_dotenv
# import datetime

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

@bp.route('/AIchatWithData', methods=['POST'])
@jwt_required()
def chat():
    
    chat_histories = {}

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
    
    chat_histories = {}

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
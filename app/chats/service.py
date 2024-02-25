import os
import sys
from flask_jwt_extended import get_jwt_identity
from langchain.vectorstores import Chroma
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from glob import glob
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
import openai
from openai import OpenAI
from dotenv import load_dotenv
import datetime
from app.users.model import User

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_histories = {}


def write_date(user_id):
    user_subfolder_info_db = os.path.join('data', str(user_id), f"info-{user_id}")
    try:
        os.makedirs(user_subfolder_info_db, exist_ok=True)
        print(f"Dossier '{user_subfolder_info_db}' créé avec succès.")
    except FileExistsError:
        print(f"Le dossier '{user_subfolder_info_db}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du dossier : {str(e)}")
    file_path = os.path.join(user_subfolder_info_db, 'date.txt')
    print(datetime.date.today())
    current_date = datetime.date.today().strftime('%Y-%m-%d')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"INFORMATIONS DU JOUR:\n\n")
        file.write(f"Nous sommes aujourd'hui le {current_date}")
        

def chat_with_data_service(model, data, folder):

    user_id = get_jwt_identity()
    write_date(user_id)

    index = get_or_create_index(folder)

    chain = create_conversational_chain(model, index)

    session_id = data.get("session_id")
    query = data.get("query")

    chat_history = get_chat_history(session_id, chat_histories)

    result = generate_response(chain, query, chat_history)

    update_chat_history(session_id, chat_history, query, result['answer'])

    return result


def get_or_create_index(folder):
   
    user_id = get_jwt_identity()
    user_data_folder = f'data/{user_id}/{folder}/'
  
    loader = [DirectoryLoader(user_data_folder)]

    index = VectorstoreIndexCreator().from_loaders(loader)

    return index


def create_conversational_chain(model, index):
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model=model),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )
    return chain


def get_chat_history(session_id, chat_histories):
    chat_history = chat_histories.get(session_id, [])
    return chat_history


def generate_response(chain, query, chat_history):
    result = chain({"question": query, "chat_history": chat_history})
    return result


def update_chat_history(session_id, chat_history, query, answer):
    chat_history.append((query, answer))
    chat_histories[session_id] = chat_history


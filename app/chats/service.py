import os
from flask_jwt_extended import get_jwt_identity
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

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_histories = {}

def chat(model, data):
    PERSIST = False

    index = get_or_create_index(PERSIST)

    chain = create_conversational_chain(model, index)

    session_id = data.get("session_id")
    query = data.get("query")

    chat_history = get_chat_history(session_id, chat_histories)
    result = generate_response(chain, query, chat_history)

    update_chat_history(session_id, chat_history, query, result['answer'])

    return result

def get_or_create_index(persist):
    if persist and os.path.exists("persist"):
        vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)
    else:
        user_id = get_jwt_identity()
        user_data_folder = f'data/{user_id}/'
        subdirs = [folder.path for folder in os.scandir(user_data_folder) if folder.is_dir()]
        loaders = [DirectoryLoader(subdir) for subdir in subdirs]
        if persist:
            index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders(loaders)
        else:
            index = VectorstoreIndexCreator().from_loaders(loaders)
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

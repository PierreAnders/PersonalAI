
from flask import Flask, request, jsonify
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

def create_app():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    app = Flask(__name__)
    swagger = Swagger(app)
    CORS(app)
    
    # Load configuration from environment
    app.config['PERSIST'] = os.getenv('PERSIST', default=False)

    # Initialize the application
    initialize_app(app)

    return app

def initialize_app(app):
    if app.config['PERSIST'] and os.path.exists("persist"):
        print("Reusing index...\n")
        vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)
    else:
        subdirs = glob('data/*/')
        loaders = []
        for subdir in subdirs:
            loader = DirectoryLoader(subdir)
            loaders.append(loader)
        
        if app.config['PERSIST']:
            index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders(loaders)
        else: 
            index = VectorstoreIndexCreator().from_loaders(loaders)
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-3.5-turbo"), # gpt-3.5-turbo-16k ...
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )
    
    # Store the chat histories in the application context
    app.chat_histories = {}

    @app.route('/chat', methods=['POST'])
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

        chat_history = app.chat_histories.get(session_id, [])

        result = chain({"question": query, "chat_history": chat_history})

        chat_history.append((query, result['answer']))
        app.chat_histories[session_id] = chat_history

        return jsonify(result)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

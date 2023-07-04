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

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY


app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = False

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  loader = DirectoryLoader("data/")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo-16k"),
    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

# Historique de la conversation stocké par session_id
chat_histories = {}

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

    chat_history = chat_histories.get(session_id, [])

    result = chain({"question": query, "chat_history": chat_history})

    chat_history.append((query, result['answer']))
    chat_histories[session_id] = chat_history

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)

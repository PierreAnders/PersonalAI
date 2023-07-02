from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import constants
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

app = Flask(__name__)
CORS(app)

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Initialisez le chargeur et l'index ici
loader = DirectoryLoader(".", glob="*.txt")
index = VectorstoreIndexCreator().from_loaders([loader])

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get("query")

    # Obtenez la réponse du bot en utilisant l'index
    result = index.query(query, llm=ChatOpenAI())

    # Pour cet exemple, nous supposons que 'result' est un dictionnaire qui contient une clé 'answer' avec la réponse du bot.
    # Modifiez ceci en fonction de la structure réelle de votre 'result'.
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

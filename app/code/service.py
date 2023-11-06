import os
from flask_jwt_extended import get_jwt_identity
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_histories = {}

def chat_generic(model, data):

    session_id = data.get("session_id")
    query = data.get("query")

    chat_history = chat_histories.get(session_id, [])
    chat_history.append((query, ""))

    messages = [{"role": "user", "content": msg} for msg, _ in chat_history]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages)

    assistant_reply = response["choices"][0]["message"]["content"]

    chat_history[-1] = (query, assistant_reply)
    chat_histories[session_id] = chat_history

    return {"answer": assistant_reply}
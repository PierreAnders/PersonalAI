import os
from flask_jwt_extended import get_jwt_identity
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_histories = {}

# !!! CODE BON !!!

def chat_service(model, data):

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


# def chat_service(model, data):
#     user_id = get_jwt_identity()
#     session_id = user_id

#     query = data.get("query")
#     print('query :', query) 

#     chat_history = chat_histories.get(session_id, [])
#     print('chat_history avant append :', chat_history)

#     chat_history.append((query, ""))
#     print('chat_history après append :', chat_history)

#     messages = [{"role": "user", "content": msg} for msg, _ in chat_history]
#     print('messages :', messages)

#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages)
#     print('response :', response)

#     assistant_reply = response["choices"][0]["message"]["content"]
#     print('assistant_reply :', assistant_reply)

#     chat_history[-1] = (query, assistant_reply)
#     print('chat_history après update :', chat_history)
#     chat_histories[session_id] = chat_history   
#     print('chat_histories après update :', chat_histories)
    
#     return {"answer": assistant_reply}
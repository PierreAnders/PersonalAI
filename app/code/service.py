from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# Initialize a dictionary to store chat histories for different sessions
chat_histories = {}

def chat_service(model, data):
    session_id = data.get("session_id")
    query = data.get("query")

    # Retrieve the chat history for the current session, or initialize it
    history = chat_histories.get(session_id, [
        {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."}
    ])

    # Append the new user query to the history
    history.append({"role": "user", "content": query})

    # Call the OpenAI API to get the completion
    completion = client.chat.completions.create(
        model=model,
        messages=history,
        temperature=0.7,
        stream=True,
    )

    # Extract the response
    assistant_reply = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            assistant_reply += chunk.choices[0].delta.content

    # Update the history with the assistant's reply
    history.append({"role": "assistant", "content": assistant_reply})

    # Save the updated history back to the chat_histories dictionary
    chat_histories[session_id] = history

    return {"answer": assistant_reply}
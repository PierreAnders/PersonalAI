import requests

BRIDGE_IP = "192.168.1.42"  # Remplacez par l'adresse IP de votre pont Hue
USERNAME = "nOez7af0EvYhENQjbYiUXbIWQ2iRRaJu5HD-8TCw"  # Remplacez par votre nom d'utilisateur autorisé

def set_light_state(light_id, on):
    url = f"http://{BRIDGE_IP}/api/{USERNAME}/lights/{light_id}/state"
    body = {"on": on}
    requests.put(url, json=body)

#     [
#     {
#         "success": {
#             "username": "nOez7af0EvYhENQjbYiUXbIWQ2iRRaJu5HD-8TCw"
#         }
#     }
# ]
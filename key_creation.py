import os

# Générer une clé secrète aléatoire
secret_key = os.urandom(24)

# Convertir la clé en une chaîne hexadécimale pour l'utiliser dans votre application Flask
secret_key_hex = secret_key.hex()

print("Votre clé secrète Flask générée aléatoirement :")
print(secret_key_hex)

# Votre clé secrète Flask générée aléatoirement :
# 50c34e5139cb598bf297a67910047d29a422b1bd828557ec
from cryptography.fernet import Fernet
import binascii
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération de la clé Fernet à partir des variables d'environnement
FERNET_KEY = os.getenv('FERNET_KEY')

# Encodage de la clé en tant que bytes
cipher_suite = Fernet(FERNET_KEY.encode())

# Fonction pour chiffrer les données
def encrypt_data(data):
    # Convertir la chaîne de données en bytes, puis chiffrer avec Fernet
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

# Fonction pour déchiffrer les données
def decrypt_data(hex_data):
    hex_data_no_prefix = hex_data[2:]  # Exclure le préfixe "0x"
    
    try:
        # Convertir le texte hexadécimal en données binaires
        binary_data = bytes.fromhex(hex_data_no_prefix)
        # Déchiffrer les données binaires avec Fernet, puis décoder en UTF-8
        decrypted_data = cipher_suite.decrypt(binary_data).decode()
        return decrypted_data
    except binascii.Error as e:
        # Gérer les erreurs lors du décodage du texte hexadécimal
        print(f"Error decoding hex data: {str(e)}")

from cryptography.fernet import Fernet
import binascii

key = b'5r41A3eWfP6AyRPG0xcozjhCyxR298T8h4m0Q2_xcNM='
cipher_suite = Fernet(key)

def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    print(f"Encrypted data: {encrypted_data}")
    return encrypted_data

def decrypt_data(hex_data):
    hex_data_no_prefix = hex_data[2:]  # Exclure le préfixe "0x"
    try:
        binary_data = bytes.fromhex(hex_data_no_prefix)
        decrypted_data = cipher_suite.decrypt(binary_data).decode()
        print(f"Decrypted data: {decrypted_data}")
        return decrypted_data
    except binascii.Error as e:
        print(f"Error decoding hex data: {str(e)}")


# # Importer les modules nécessaires
# from cryptography.fernet import Fernet
# import binascii

# # Clé de chiffrement Fernet préalablement générée
# key = b'5r41A3eWfP6AyRPG0xcozjhCyxR298T8h4m0Q2_xcNM='

# # Créer une instance de la classe Fernet avec la clé
# cipher_suite = Fernet(key)

# # Fonction pour chiffrer les données
# def encrypt_data(data):
#     # Convertir la chaîne de données en bytes, puis chiffrer avec Fernet
#     encrypted_data = cipher_suite.encrypt(data.encode())
#     # Afficher les données chiffrées
#     print(f"Encrypted data: {encrypted_data}")
#     # Renvoyer les données chiffrées
#     return encrypted_data

# # Fonction pour déchiffrer les données
# def decrypt_data(hex_data):
#     # Exclure le préfixe "0x" du texte hexadécimal
#     hex_data_no_prefix = hex_data[2:]
#     try:
#         # Convertir le texte hexadécimal en données binaires
#         binary_data = bytes.fromhex(hex_data_no_prefix)
#         # Déchiffrer les données binaires avec Fernet, puis décoder en UTF-8
#         decrypted_data = cipher_suite.decrypt(binary_data).decode()
#         # Afficher les données déchiffrées
#         print(f"Decrypted data: {decrypted_data}")
#         # Renvoyer les données déchiffrées
#         return decrypted_data
#     except binascii.Error as e:
#         # Gérer les erreurs lors du décodage du texte hexadécimal
#         print(f"Error decoding hex data: {str(e)}")

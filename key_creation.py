import os
secret_key = os.urandom(24)
secret_key_hex = secret_key.hex()
print("Clé secrète Flask :", secret_key_hex)


from cryptography.fernet import Fernet
key = Fernet.generate_key()
print("Clé secrète Fernet :", key)
import os

secret_key = os.urandom(24)

secret_key_hex = secret_key.hex()

print("Clé secrète Flask :", secret_key_hex)
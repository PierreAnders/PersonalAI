from utils.cryptography import decrypt_data

hex_data = "674141414141426c5463595433387478374164417945374b36596b472d6b4748642d427a49444f7364457861636b353456765056327457496647332d63542d6e466a524e6d5364336f6550434a5a716254456b337447416450536e35536d583379513d3d"

# Exclure le préfixe "\x"
binary_data = bytes.fromhex(hex_data)
try:
    decrypted_data = decrypt_data(binary_data)
    print("Decrypted data:", decrypted_data)
except Exception as e:
    print("Error:", e)

from app.extensions import db
from app.healths.model import Health
from sqlalchemy.exc import IntegrityError


def add_or_update_health_info_service(user_id, gender, weight, size, social_security_number, blood_group, doctor):
    
    health_info = Health.query.filter_by(user_id=user_id).first()

    if health_info:
        health_info.gender = gender
        health_info.weight = weight
        health_info.size = size
        health_info.social_security_number = social_security_number
        health_info.blood_group = blood_group
        health_info.doctor = doctor
    else:
        health_info = Health(
            gender=gender,
            weight=weight,
            size=size,
            social_security_number=social_security_number,
            blood_group=blood_group,
            doctor=doctor,
            user_id=user_id
        )

    try:
        db.session.add(health_info)
        db.session.commit()
        return {"message": "Informations de santé enregistrées avec succès"}, 201
    except IntegrityError as e:
        db.session.rollback()
        return {"message": "Erreur de base de données : " + str(e)}, 500


def get_health_info_service(user_id):
    health_info = Health.query.filter_by(user_id=user_id).first()
    if health_info:
        return {
            "gender": health_info.gender,
            "weight": health_info.weight,
            "size": health_info.size,
            "social_security_number": health_info.social_security_number,
            "blood_group": health_info.blood_group,
            "doctor": health_info.doctor
        }, 200
    else:
        return {"message": "Aucune information de santé trouvée"}, 404



# from Crypto.Cipher import AES
# from base64 import b64encode, b64decode

# KEY = 'my super secret key'.rjust(32)  # this should be stored securely and never be hard-coded

# def encrypt_aes(raw):
#     cipher = AES.new(KEY, AES.MODE_ECB)
#     return b64encode(cipher.encrypt(raw.rjust(16)))

# def decrypt_aes(enc):
#     cipher = AES.new(KEY, AES.MODE_ECB)
#     return cipher.decrypt(b64decode(enc)).strip()

# def add_or_update_health_info_service(user_id, gender, weight, size, social_security_number, blood_group, doctor):
    
#     health_info = Health.query.filter_by(user_id=user_id).first()

#     encrypted_ssn = encrypt_aes(social_security_number)

#     if health_info:
#         health_info.gender = gender
#         health_info.weight = weight
#         health_info.size = size
#         health_info.social_security_number = encrypted_ssn
#         health_info.blood_group = blood_group
#         health_info.doctor = doctor
#     else:
#         health_info = Health(
#             gender=gender,
#             weight=weight,
#             size=size,
#             social_security_number=encrypted_ssn,
#             blood_group=blood_group,
#             doctor=doctor,
#             user_id=user_id
#         )

#     try:
#         db.session.add(health_info)
#         db.session.commit()
#         return {"message": "Informations de santé enregistrées avec succès"}, 201
#     except IntegrityError as e:
#         db.session.rollback()
#         return {"message": "Erreur de base de données : " + str(e)}, 500

# def get_health_info_service(user_id):
#     health_info = Health.query.filter_by(user_id=user_id).first()
#     if health_info:
#         decrypted_ssn = decrypt_aes(health_info.social_security_number)
#         return {
#             "gender": health_info.gender,
#             "weight": health_info.weight,
#             "size": health_info.size,
#             "social_security_number": decrypted_ssn,
#             "blood_group": health_info.blood_group,
#             "doctor": health_info.doctor
#         }, 200
#     else:
#         return {"message": "Aucune information de santé trouvée"}, 404

# pip install cryptography !!! 
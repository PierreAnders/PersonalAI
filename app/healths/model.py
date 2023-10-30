from app.extensions import db

class Health(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(255), nullable=True)
    weight = db.Column(db.Numeric(5, 2), nullable=True)
    size = db.Column(db.Numeric(3, 2), nullable=True)
    social_security_number = db.Column(db.String(255), nullable=True)
    blood_group = db.Column(db.String(255), nullable=True)
    doctor = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    def __init__(self, gender, weight, size, social_security_number, blood_group, doctor, user_id):
        self.gender = gender
        self.weight = weight
        self.size = size
        self.social_security_number = social_security_number
        self.blood_group = blood_group
        self.doctor = doctor
        self.user_id = user_id

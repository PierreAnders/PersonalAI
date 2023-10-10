from app.extensions import db
from app.models.expense import Expense
from app.models.income import Income
from app.models.health import Health
import uuid

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, unique=True)
    firstname = db.Column(db.String(255), nullable=True)
    lastname = db.Column(db.String(255), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_de_creation = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    user_expense = db.relationship('Expense', backref='user', lazy=True)
    user_income = db.relationship('Income', backref='user', lazy=True)
    user_health = db.relationship('Health', backref='user', lazy=True)

    def __init__(self, firstname, lastname, birth_date, email, password):
        self.id = str(uuid.uuid4())
        self.firstname = firstname
        self.lastname = lastname
        self.birth_date = birth_date
        self.email = email
        self.password = password

# class Expense(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255), nullable=True)
#     description = db.Column(db.String(255), nullable=True)
#     price = db.Column(db.Decimal(10,2), nullable=True)
#     user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

#     def __init__(self, title, description, price):
#         self.title = title
#         self.description = description
#         self.price = price

# class Income(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255), nullable=True)
#     description = db.Column(db.String(255), nullable=True)
#     price = db.Column(db.Decimal(10,2), nullable=True)
#     user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

#     def __init__(self, title, description, price):
#         self.title = title
#         self.description = description
#         self.price = price

# class Health(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     gender = db.Column(db.String(255), nullable=True)
#     weight = db.Column(db.Decimal(5, 2), nullable=True)
#     size = db.Column(db.Decimal(3, 2), nullable=True)
#     social_security_number = db.Column(db.String(255), nullable=True)
#     blood_group = db.Column(db.String(255), nullable=True)
#     doctor = db.Column(db.String(255), nullable=True)
#     user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

#     def __init__(self, gender, weight, size, social_security_number, blood_group, doctor, user_id):
#         self.gender = gender
#         self.weight = weight
#         self.size = size
#         self.social_security_number = social_security_number
#         self.blood_group = blood_group
#         self.doctor = doctor
#         self.user_id = user_id

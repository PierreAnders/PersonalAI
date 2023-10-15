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
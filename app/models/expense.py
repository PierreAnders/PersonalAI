from app.extensions import db
from sqlalchemy import types

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Numeric(10,2), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    def __init__(self, title, description, price):
        self.title = title
        self.description = description
        self.price = price
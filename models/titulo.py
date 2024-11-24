from flask_login import UserMixin
from app import db

class Titulo(db.Model):
    __tablename__ = 'Titulos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(256), nullable=False)
    productora_id = db.Column(db.Integer, nullable=False)
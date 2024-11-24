from flask_login import UserMixin
from app import db

class Impresion(db.Model, UserMixin):
    __tablename__ = 'Impresiones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Integer, nullable=False)
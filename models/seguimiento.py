from flask_login import UserMixin
from app import db

class Seguimiento(db.Model, UserMixin):
    __tablename__ = 'Seguimientos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    cantidad_visto = db.Column(db.Integer, nullable=False)
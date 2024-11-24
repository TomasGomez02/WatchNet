from flask_login import UserMixin
from app import db

class ListaReproduccion(db.Model, UserMixin):
    __tablename__ = 'ListaReproduccion'
    id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    titulos = db.Column(db.ARRAY(db.Integer), nullable=False)
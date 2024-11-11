from flask_login import UserMixin
from app import db

class Usuario(db.Model, UserMixin):
    __tablename__ = 'Usuarios'
    id = db.Column(db.Integer, primary_key=True)
    info_login_id = db.Column(db.Integer, unique=True, nullable=False)
    usuarios_seguidos = db.Column(db.ARRAY(db.Integer), nullable=True)
    productoras_seguidas = db.Column(db.ARRAY(db.Integer), nullable=True)
    productoras_seguidas = db.Column(db.ARRAY(db.Integer), nullable=True)


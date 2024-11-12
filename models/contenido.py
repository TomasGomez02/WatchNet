from flask_login import UserMixin
from app import db

class Contenido(db.Model):
    __tablename__ = 'Contenidos'
    id = db.Column(db.Integer, primary_key=True)
    titulo_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.Integer, nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
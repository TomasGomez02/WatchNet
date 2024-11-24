from flask_login import UserMixin
from app import db

class Comentario(db.Model, UserMixin):
    __tablename__= 'Comentarios'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Timestamp, nullable=False)

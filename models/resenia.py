from flask_login import UserMixin
from app import db

class Resenia(db.Model, UserMixin):
    __tablename__ = 'Reseñas'
    id = db.Column(db.Integer, primary_key=True)
    puntuacion = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)
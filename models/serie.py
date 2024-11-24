from flask_login import UserMixin
from app import db

class Serie(db.Model, UserMixin):
    __tablename__ = 'Series'
    id = db.Column(db.Integer, primary_key=True)
    titulo_id = db.Column(db.Integer, unique=True, nullable=False)
    fecha_inicio = db.Column(db.Timestamp, nullable=False)
    fecha_fin = db.Column(db.Timestamp, nullable=False)
    episodios= db.Column(db.ARRAY(db.Integer), nullable=False)
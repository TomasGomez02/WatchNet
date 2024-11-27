from flask_login import UserMixin
from app import db
from models.tipo_contenido import TipoContenido
from sqlalchemy import Enum 


class Contenido(db.Model, UserMixin):
    __tablename__ = 'Contenidos'
    id = db.Column(db.Integer, primary_key=True)
    titulo_id = db.Column(db.Integer, unique=True, nullable=False)
    tipo = db.Column(Enum(TipoContenido), nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)

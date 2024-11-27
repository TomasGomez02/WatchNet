from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Comentario(db.Model, UserMixin):
    __tablename__= 'Comentarios'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)

class Episodio(db.Model, UserMixin):
    __tablename__ = 'Episodios'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.Text, nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
    orden = db.Column(db.Integer, nullable=False)
    fecha_emision = db.Column(db.Date, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)

class Impresion(db.Model, UserMixin):
    __tablename__ = 'Impresiones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Integer, nullable=False)


class Entidad(db.Model, UserMixin):
    __abstract__ = True  

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    contraseña = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str):
        self.contraseña = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.contraseña, password)

class Productora(Entidad):
    __tablename__ = 'Productoras'

class Usuario(Entidad):
    __tablename__ = 'Usuarios'

class Resenia(db.Model, UserMixin):
    __tablename__ = 'Reseñas'
    id = db.Column(db.Integer, primary_key=True)
    puntuacion = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)

class Seguimiento(db.Model, UserMixin):
    __tablename__ = 'Seguimientos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    cantidad_visto = db.Column(db.Integer, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)

class Titulo(db.Model):
    __tablename__ = 'Titulos'
    id = db.Column(db.Integer, primary_key=True)
    productora_id = db.Column(db.Integer, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    titulo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.Boolean, nullable=False)
    
class Relacione(db.Model):
    __tablename__ = 'Relaciones'
    seguidor = db.Column(db.Integer, primary_key=True)
    seguido = db.Column(db.Integer, primary_key=True)

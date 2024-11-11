from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class InfoLogin(db.Model, UserMixin):
    __tablename__ = 'InfoLogin'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    contraseña = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str):
        self.contraseña = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.contraseña, password)
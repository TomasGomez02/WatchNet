from flask_login import UserMixin
from app import db

class Productora(db.Model, UserMixin):
    __tablename__ = 'Productoras'
    id = db.Column(db.Integer, primary_key=True)
    info_login_id = db.Column(db.Integer, unique=True, nullable=False)
    series_id = db.Column(db.ARRAY(db.Integer), nullable=False)
    contenidos_id = db.Column(db.ARRAY(db.Integer), nullable=False)
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from resources.crear_resenia import CrearResenia
from resources.login import SignUp
from resources.login import Login
from resources.login import Productora_SignUp
from resources.user_profile import UserProfile
from resources.productora_profile import ProductoraProfile
from resources.nuevo_contenido import NuevoContenido
from resources.index import Index
from models.models import db
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE, TOKEN_KEY


def create_app(testing=False):
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Index, '/')
    api.add_resource(SignUp, '/signup')
    api.add_resource(Productora_SignUp, '/productora/signup')
    api.add_resource(Login, '/login', '/')
    api.add_resource(UserProfile, '/user')
    api.add_resource(ProductoraProfile, '/productora')
    api.add_resource(NuevoContenido, '/productora/nuevoContenido')
    api.add_resource(CrearResenia, '/usuario/nuevaResenia')

    if not testing:
        URI = f'postgresql://{DB_DATABASE}.{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    else:
        URI = 'sqlite://testing.db'
        
    app.config['SQLALCHEMY_DATABASE_URI'] = URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = TOKEN_KEY

    db.init_app(app)
    
    return app

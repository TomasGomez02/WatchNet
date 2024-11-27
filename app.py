from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from resources.usuario import usuario_bp
from resources.productora import productora_bp
from resources.index import Index
from models.models import db
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE, TOKEN_KEY


def create_app(testing=False):
    """
    Crea y configura una instancia de la aplicación Flask.

    Esta función inicializa la aplicación Flask, configura los blueprints para las rutas
    de los usuarios y productoras, y configura la base de datos según el entorno. 

    Parámetros
    ----------
    testing : bool, opcional
        Indica si la aplicación debe ser configurada para pruebas (por defecto es False).
        Si se establece en `True`, se utiliza una base de datos SQLite temporal para las pruebas.

    Retorna
    -------
    app : Flask
        Una instancia de la aplicación Flask configurada con todos los blueprints.
    """
    app = Flask(__name__)
    api = Api(app)

    app.register_blueprint(usuario_bp, url_prefix='/user')
    app.register_blueprint(productora_bp, url_prefix='/producer')
    api.add_resource(Index, '/')

    if not testing:
        URI = f'postgresql://{DB_DATABASE}.{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    else:
        URI = 'sqlite://testing.db'
        
    app.config['SQLALCHEMY_DATABASE_URI'] = URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = TOKEN_KEY

    db.init_app(app)
    
    return app

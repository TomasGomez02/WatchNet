import os

from flask import Flask
from flask_restful import Api
from resources.usuario import usuarioAPI_bp
from resources.productora import productoraAPI_bp
from resources.tituloAPI import titulo_bp
from front.user import usuario_bp
from front.producer import producer_bp
from resources.index import Index
from models.models import DataBase
from flasgger import Swagger

try:
    from config import DB_URI, TOKEN_KEY
except ModuleNotFoundError:
    DB_URI = os.getenv('DB_URI', "sqlite:///database.db")
    TOKEN_KEY = os.getenv('TOKEN_KEY', "please-set-up-a-proper-key")

db = DataBase().db

def create_app(local=False, local_path=''):
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
    swagger = Swagger(app)

    app.register_blueprint(usuario_bp, url_prefix='/user')
    app.register_blueprint(producer_bp, url_prefix='/producer')
    app.register_blueprint(usuarioAPI_bp, url_prefix='/api/user')
    app.register_blueprint(productoraAPI_bp, url_prefix='/api/producer')
    app.register_blueprint(titulo_bp, url_prefix='/api/titulo')
    api.add_resource(Index, '/')

    if not local:
        URI = DB_URI
    else:
        URI = f'sqlite:///{local_path}'
        
    app.config['SQLALCHEMY_DATABASE_URI'] = URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = TOKEN_KEY

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app

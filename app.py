from flask import Flask
from flask_restful import Api
from resources.usuario import usuario_bp
from resources.productora import productora_bp
from resources.index import Index
from models.models import db
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE, TOKEN_KEY

def create_app(local=False, local_path=''):
    app = Flask(__name__)
    api = Api(app)

    app.register_blueprint(usuario_bp, url_prefix='/user')
    app.register_blueprint(productora_bp, url_prefix='/producer')
    api.add_resource(Index, '/')

    if not local:
        URI = f'postgresql://{DB_DATABASE}.{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    else:
        URI = f'sqlite:///{local_path}'
        
    app.config['SQLALCHEMY_DATABASE_URI'] = URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = TOKEN_KEY

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app

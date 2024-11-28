import sys
import os
import tempfile
from datetime import date
import pytest

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.models import TipoTitulo, DataBase
from app import create_app


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    app = create_app(local=True, local_path=db_path)
    app.config.update({
        'TESTING': True,
    })

    yield app

    db = DataBase().db
    with app.app_context():
        db.session.remove()
        db.engine.dispose()

    os.unlink(db_path)

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.text_cli_runner()

class AuthActions(object):
    def __init__(self, client, type='user'):
        self._client = client
        self._type = type

    def signup(self, email='test', username='test', password='test'):
        return self._client.post(
            f'/api/{self._type}/signup',
            data={'email': email, 'username': username, 'password': password}
        )

    def login(self, email='test', password='test'):
        return self._client.post(
            f'/api/{self._type}/login',
            data={'email': email, 'password': password}
        )
    
    def init(self, email='test', username='test', password='test'):
        self.signup(email, username, password)
        self.login(email, password)
    
    def logout(self):
        return self._client.delete(f'/api/{self._type}/login')
    
class TitleActions:
    def __init__(self, client):
        self._client = client

    def create_series(self, 
               titulo='test', 
               fecha_inicio=date(2000, 1, 1), 
               fecha_fin=date(2000, 1, 1), 
               tipo: TipoTitulo=TipoTitulo.SERIE):
        return self._client.post('/api/titulo/',
                                 json={
                                     'titulo': titulo,
                                     'fecha_inicio': fecha_inicio.isoformat(),
                                     'fecha_fin': fecha_fin.isoformat(),
                                     'tipo': tipo.value
                                 })
    
    def create_movie(self, 
               titulo='test', 
               fecha_inicio=date(2000, 1, 1), 
               fecha_fin=date(2000, 1, 1), 
               tipo: TipoTitulo=TipoTitulo.PELICULA,
               duracion: int=60):
        return self._client.post('/api/titulo/',
                                 json={
                                     'titulo': titulo,
                                     'fecha_inicio': fecha_inicio.isoformat(),
                                     'fecha_fin': fecha_fin.isoformat(),
                                     'tipo': tipo.value,
                                     'duracion': duracion
                                 })
    
    def read(self, titulo_id):
        return self._client.get(f'/api/titulo/{titulo_id}')
    
    def delete(self, titulo_id):
        return self._client.delete(f'/api/titulo/{titulo_id}')
    
    def create_review(self, titulo_id, data):
        return self._client.post(f'/api/titulo/{titulo_id}/review',
                                 json=data)

@pytest.fixture()
def auth(client):
    return AuthActions(client)

@pytest.fixture()
def auth_prod(client):
    return AuthActions(client, 'producer')

@pytest.fixture()
def titles(client):
    return TitleActions(client)
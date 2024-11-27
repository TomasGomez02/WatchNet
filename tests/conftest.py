import sys
import os
import tempfile

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app, db

@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    app = create_app(local=True, local_path=db_path)
    app.config.update({
        'TESTING': True,
    })

    yield app

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
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/user/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):
        return self._client.delete('/user/login')
    
@pytest.fixture()
def auth(client):
    return AuthActions(client)
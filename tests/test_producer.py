import pytest
from flask import session

def test_prod_signup(client, auth_prod):
    response = client.post('/api/producer/', json={})
    assert response.status_code == 400

    response = auth_prod.signup()
    assert response.status_code == 200

@pytest.mark.parametrize(('email', 'username', 'password', 'message'), (
        ('', '', '', b'Falta data'),
        ('a', '', '', b'Falta data'),
        ('a', 'a', '', b'Falta data')
))
def test_prod_register_validate_input(client, email, username, password, message):
    response = client.post(
        '/api/producer/',
        json={'email': email, 'username': username, 'password': password}
    )
    assert message in response.data

def test_prod_register_validate_existing(client):
    client.post(
        '/api/producer/',
        json={'email': 'test', 'username': 'test', 'password': 'test'}
    )

    response = client.post(
        '/api/producer/',
        json={'email': 'test', 'username': 'test', 'password': 'test'}
    )
    assert b'Email ya esta registrado' in response.data

    response = client.post(
        '/api/producer/',
        json={'email': 'a', 'username': 'test', 'password': 'test'}
    )
    assert b'Username ya existe' in response.data
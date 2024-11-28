import pytest
from flask import session

def test_prod_signup(client, auth_prod):
    response = client.get('/producer/signup')
    assert response.status_code == 200

    response = auth_prod.signup()
    assert response.status_code == 200

@pytest.mark.parametrize(('email', 'username', 'password', 'message'), (
        ('', '', '', b'Falta data'),
        ('a', '', '', b'Falta data'),
        ('a', 'a', '', b'Falta data')
))
def test_prod_register_validate_input(client, email, username, password, message):
    response = client.post(
        '/producer/signup',
        data={'email': email, 'username': username, 'password': password}
    )
    assert message in response.data

def test_prod_register_validate_existing(client):
    client.post(
        '/producer/signup',
        data={'email': 'test', 'username': 'test', 'password': 'test'}
    )

    response = client.post(
        '/producer/signup',
        data={'email': 'test', 'username': 'test', 'password': 'test'}
    )
    assert b'Email ya esta registrado' in response.data

    response = client.post(
        '/producer/signup',
        data={'email': 'a', 'username': 'test', 'password': 'test'}
    )
    assert b'Username ya existe' in response.data

def test_prod_profile(client, auth_prod):
    auth_prod.signup()
    auth_prod.login()
    response = client.get('/producer/')
    assert response.status_code == 200
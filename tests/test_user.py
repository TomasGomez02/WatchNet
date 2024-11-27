import pytest
from flask import session

def test_user_signup(client, auth):
    response = client.get('/user/signup')
    assert response.status_code == 200

    response = client.post(
        '/user/signup',
        data={'email': 'test', 'username': 'test', 'password': 'test'}
    )
    assert response.status_code == 200

@pytest.mark.parametrize(('email', 'username', 'password', 'message'), (
        ('', '', '', b'Falta data'),
        ('a', '', '', b'Falta data'),
        ('a', 'a', '', b'Falta data')
))
def test_register_validate_input(client, email, username, password, message):
    response = client.post(
        '/user/signup',
        data={'email': email, 'username': username, 'password': password}
    )
    assert message in response.data

def test_register_validate_existing(client):
    client.post(
        '/user/signup',
        data={'email': 'test', 'username': 'test', 'password': 'test'}
    )

    response = client.post(
        '/user/signup',
        data={'email': 'test', 'username': 'test', 'password': 'test'}
    )
    assert b'Email ya esta registrado' in response.data

    response = client.post(
        '/user/signup',
        data={'email': 'a', 'username': 'test', 'password': 'test'}
    )
    assert b'Username ya existe' in response.data

def test_login(client, auth):
    auth.signup()

    response = client.get('/user/login')
    assert response.status_code == 200

    with client:
        response = client.post(
            '/user/login',
            data={'email': 'test', 'password': 'test'},
            follow_redirects=True
        )
        assert session['auth_token'] is not None
    assert len(response.history) == 1
    assert response.request.path == '/user/'

@pytest.mark.parametrize(('email', 'password', 'message'), (
        ('', '', b'Falta data'),
        ('', 'a', b'Falta data'),
        ('a', '', b'Falta data'),
        ('a', 'a', b'Login info incorrect'),
        ('test', 'a', b'Login info incorrect')
))
def test_login_validate(client, auth, email, password, message):
    auth.signup()
    with client:
        response = auth.login(email, password)
        assert message in response.data
        assert not 'auth_token' in session

def test_logout(client, auth):
    auth.signup()

    with client:
        auth.login()
        auth.logout()
        assert 'auth_token' not in session

def test_user_profile(client, auth):
    auth.signup()
    auth.login()
    response = client.get('/user/')
    assert response.status_code == 200


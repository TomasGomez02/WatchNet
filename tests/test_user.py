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

def test_follow(client, auth):
    auth.init()
    auth.init('test2', 'test2', 'test2')

    response = client.post('/user/follow', json={
                               'seguido_id': 1
                           })
    assert response.status_code == 200

def test_follow_self(client, auth):
    auth.init()

    response = client.post('/user/follow', json={
                               'seguido_id': 1
                           })
    assert response.status_code == 403

def test_follow_inexistent(client, auth):
    auth.init()

    response = client.post('/user/follow', json={
                               'seguido_id': 2
                           })
    assert response.status_code == 404

def test_follow_already(client, auth):
    auth.init()
    auth.init('test2', 'test2', 'test2')

    client.post('/user/follow', json={
                               'seguido_id': 2
                           })

    response = client.post('/user/follow', json={
                               'seguido_id': 2
                           })
    assert response.status_code == 403

def test_follow_get_following(client, auth):
    auth.init()
    auth.init('test2', 'test2', 'test2')
    auth.init('test3', 'test3', 'test3')

    client.post('/user/follow', json={
                               'seguido_id': 1
                           })
    client.post('/user/follow', json={
                               'seguido_id': 2
                           })

    response = client.get('/user/follow', json={})
    data = response.get_json()
    assert response.status_code == 200
    assert 'seguidos' in data
    assert len(data['seguidos']) == 2
    
def test_follow_get_followers(client, auth):
    auth.init()
    auth.init('test2', 'test2', 'test2')
    client.post('/user/follow', json={
                               'seguido_id': 1
                           })
    
    auth.init('test3', 'test3', 'test3')
    client.post('/user/follow', json={
                               'seguido_id': 1
                           })
    
    auth.login()

    response = client.get('/user/follow', json={
        'type': 'follower'
    })
    data = response.get_json()
    assert response.status_code == 200
    assert 'seguidores' in data
    assert len(data['seguidores']) == 2
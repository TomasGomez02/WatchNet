import pytest

def test_user_signup(client):
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
def test_user_authentication(client, auth):
    response = client.get('/user/home')
    assert response.status_code == 401

    auth.signup()
    auth.login()
    response = client.get('/user/home')
    assert response.status_code == 200

    auth.logout()
    response = client.get('/user/home')
    assert response.status_code == 401

    with client.session_transaction() as session:
        session['auth_token'] = 0
    response = client.get('/user/home')
    assert response.status_code == 403

def test_prod_authentication(client, auth_prod):
    response = client.get('/producer/home')
    assert response.status_code == 401

    auth_prod.signup()
    auth_prod.login()
    response = client.get('/producer/home')
    assert response.status_code == 200

    auth_prod.logout()
    response = client.get('/producer/home')
    assert response.status_code == 401

    with client.session_transaction() as session:
        session['auth_token'] = 0
    response = client.get('/producer/home')
    assert response.status_code == 403

def test_crossed_authentication(client, auth, auth_prod):
    auth.signup()
    auth.login()
    response = client.get('/producer/home')
    assert response.status_code == 401
    auth.logout()

    auth_prod.signup()
    auth_prod.login()
    response = client.get('/user/home')
    assert response.status_code == 401
    auth_prod.logout()
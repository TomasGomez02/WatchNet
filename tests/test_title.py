from datetime import date

def test_title_create(titles, auth_prod):
    assert titles.create_series().status_code == 401

    auth_prod.init()

    assert titles.create_series().status_code == 200

def test_title_read(titles, auth_prod):
    assert titles.read(1).status_code == 404

    auth_prod.init()

    titles.create_series(titulo='testing')
    response = titles.read(1)
    assert b'testing' in response.data and response.status_code == 200

def test_title_delete(titles, auth_prod):
    auth_prod.init()

    assert titles.delete(1).status_code == 404

    titles.create_series()
    assert titles.delete(1).status_code == 200

ep_data = {
        'titulo': 'test',
        'duracion': 30,
        'orden': 1,
        'fecha_emision': date(2000, 1, 1).isoformat()
    }

ep_data2 = {
        'titulo': 'test2',
        'duracion': 30,
        'orden': 2,
        'fecha_emision': date(2000, 1, 1).isoformat()
    }

def test_episode_create(client, titles, auth_prod):
    auth_prod.init()

    response = client.post(f'/api/titulo/{1}/episodes', json=ep_data)
    assert response.status_code == 404

    auth_prod.init('test2', 'test2', 'test2')
    titles.create_series()

    auth_prod.logout()
    auth_prod.login()

    response = client.post(f'/api/titulo/{1}/episodes', json=ep_data)
    assert response.status_code == 401

    titles.create_series()
    response = client.post(f'/api/titulo/{2}/episodes', json=ep_data)
    assert response.status_code == 200

def test_episode_get(client, titles, auth_prod):
    auth_prod.init()
    ep_route = f'/api/titulo/{1}/episodes'

    assert client.get(ep_route).status_code == 404

    titles.create_series()
    client.post(f'/api/titulo/{1}/episodes', json=ep_data)
    client.post(f'/api/titulo/{1}/episodes', json=ep_data2)

    response = client.get(ep_route) 
    assert response.status_code == 200
    assert b'episodios' in response.data 
    data = response.get_json()
    assert len(data['episodios']) == 2

    response = client.get(ep_route + f'/{1}')

    assert response.status_code == 200 
    assert b'episodio' in response.data
    data = response.get_json()
    assert data['episodio']['titulo'] == 'test'

def test_episode_delete(client, titles, auth_prod):
    ep_route = f'/api/titulo/{1}/episodes'
    auth_prod.init()

    assert client.delete(ep_route + f'/{1}').status_code == 404

    auth_prod.logout()
    auth_prod.init('test2', 'test2', 'test2')
    titles.create_series()
    response = client.post(f'/api/titulo/{1}/episodes', json=ep_data)

    auth_prod.logout()
    auth_prod.login()

    assert client.delete(ep_route + f'/{1}').status_code == 401

    auth_prod.logout()
    auth_prod.login('test2', 'test2')

    assert client.delete(ep_route + f'/{1}').status_code == 200
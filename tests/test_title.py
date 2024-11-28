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

review_data = {
        'texto': 'test',
        'puntuacion': 1
    }
review_data2 = {
        'texto': 'test2',
        'puntuacion': 3
    }

def test_review_create(client, titles, auth_prod, auth):
    route = '/api/titulo/{id}/review'
    
    auth_prod.init()
    titles.create_movie()

    auth.init()

    response = client.post(route.format(id=2), json=review_data)
    assert response.status_code == 404

    response = client.post(route.format(id=1), json=review_data)
    assert response.status_code == 200

def test_review_get(client, titles, auth_prod, auth):
    auth_prod.init()
    route = f'/api/titulo/{1}/review'

    assert client.get(route).status_code == 404

    titles.create_series()

    auth.init()
    client.post(route, json=review_data)
    client.post(route, json=review_data2)

    response = client.get(route) 
    assert response.status_code == 200
    assert b'reviews' in response.data 
    data = response.get_json()
    assert len(data['reviews']) == 2

    response = client.get(route + f'/{1}')

    assert response.status_code == 200 
    assert b'review' in response.data
    data = response.get_json()
    assert data['review']['texto'] == 'test'

def test_review_delete(client, titles, auth_prod, auth):
    route = '/api/titulo/{id}/review'
    data = {
        'texto': 'test',
        'puntuacion': 1
    }

    auth_prod.init()
    titles.create_movie()

    auth.init()

    response = client.delete(route.format(id=1) + '/1')
    assert response.status_code == 404

    client.post(route.format(id=1), json=data)

    auth.init('test2', 'test2', 'test2')

    response = client.delete(route.format(id=1) + '/1')
    assert response.status_code == 403

    auth.login()

    response = client.delete(route.format(id=1) + '/1')
    assert response.status_code == 200

def test_comment_create(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/comentario'
    text = {
        'texto': 'test'
    }

    auth_prod.init()
    titles.create_movie()
    auth.init()

    response = client.post(route, json=text)
    assert response.status_code == 404

    titles.create_review(1, review_data)

    response = client.post(route, json={})
    assert response.status_code == 400

    response = client.post(route, json=text)
    assert response.status_code == 200

def test_comment_get(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/comentario'
    text = {
        'texto': 'test'
    }
    text2 = {
        'texto': 'test2'
    }

    response = client.get(route)
    assert response.status_code == 404

    auth_prod.init()
    titles.create_movie()

    response = client.get(route)
    assert response.status_code == 404

    auth.init()
    titles.create_review(1, review_data)

    client.post(route, json=text)
    client.post(route, json=text2)

    response = client.get(route + f'/{4}')
    assert response.status_code == 404


    response = client.get(route) 
    assert response.status_code == 200
    assert b'comments' in response.data 
    data = response.get_json()
    assert len(data['comments']) == 2

    response = client.get(route + f'/{1}')

    assert response.status_code == 200 
    assert b'comment' in response.data
    data = response.get_json()
    assert data['comment']['texto'] == 'test'

def test_comment_delete(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/comentario'
    text = {
        'texto': 'test'
    }

    auth_prod.init()
    titles.create_movie()
    auth.init()
    titles.create_review(1, review_data)

    response = client.delete(route + f'/{1}')
    assert response.status_code == 404

    response = client.post(route, json=text)

    auth.init('test2', 'test2', 'test2')
    response = client.delete(route + f'/{1}')
    assert response.status_code == 403

    auth.login()
    response = client.delete(route + f'/{1}')
    assert response.status_code == 200

def test_impresion_create_successful(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/impresion'
    test_val = {
        'valor': 1
    }

    auth_prod.init()
    titles.create_movie()
    auth.init()
    titles.create_review(1, review_data)

    assert client.post(route, json=test_val).status_code == 200

def test_impresion_create_invalid(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/impresion'
    test_val = {
        'valor': 5
    }

    auth_prod.init()
    titles.create_movie()
    auth.init()
    titles.create_review(1, review_data)

    assert client.post(route, json=test_val).status_code == 400

def test_impression_review_notfound(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/impresion'
    test_val = {
        'valor': 1
    }

    auth_prod.init()
    titles.create_movie()
    auth.init()

    assert client.post(route, json=test_val).status_code == 404

def test_impression_already_done(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/impresion'
    test_val = {
        'valor': 1
    }

    auth_prod.init()
    titles.create_movie()
    auth.init()
    titles.create_review(1, review_data)
    client.post(route, json=test_val)

    assert client.post(route, json=test_val).status_code == 400

def test_impression_delete(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/impresion'
    test_val = {
        'valor': 1
    }

    auth_prod.init()
    titles.create_movie()
    auth.init()
    titles.create_review(1, review_data)
    client.post(route, json=test_val)

    assert client.delete(route).status_code == 200

def test_impression_delete_fail(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/impresion'

    auth_prod.init()
    titles.create_movie()
    auth.init()
    titles.create_review(1, review_data)

    assert client.delete(route).status_code == 404

def test_impression_get(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/impresion'
    test_val = {
        'valor': 1
    }
    test_val2 = {
        'valor': -1
    }

    auth_prod.init()
    titles.create_movie()
    auth.init()
    titles.create_review(1, review_data)
    client.post(route, json=test_val)
    auth.init('test2', 'test2', 'test2')
    client.post(route, json=test_val2)

    response = client.get(route)
    assert response.status_code == 200
    imp = response.get_json()['impresiones']
    assert len(imp) == 2
    total = sum([i['valor'] for i in imp])
    assert total == 0

def test_impression_get_fail(client, titles, auth_prod, auth):
    route = f'/api/titulo/{1}/review/{1}/impresion'

    auth_prod.init()
    assert client.get(route).status_code == 404

    titles.create_movie()
    auth.init()

    assert client.get(route).status_code == 404
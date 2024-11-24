from flask_restful import Resource
from flask import request, make_response
from flask.templating import render_template
from app import db, token_required, app
from models.info_login import InfoLogin
from models.productora import Productora
from models.titulo import Titulo
from models.contenido import Contenido

class NuevoContenido(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json()

        info_login = InfoLogin.query.filter_by(nombre_usuario=current_user).first()
        productora = Productora.query.filter_by(info_login_id=info_login.id).first()

        nombre = data['nombre_contenido']
        titulo = Titulo(nombre=nombre, productora_id=productora.id)
        db.session.add(titulo)
        db.session.flush()

        fecha_publicacion = data['fecha_publicacion']
        tipo = data['tipo']
        duracion = data['duracion']

        contenido = Contenido(titulo_id=titulo.id, 
                              fecha_publicacion=fecha_publicacion,
                              tipo=tipo, 
                              duracion=duracion)
        db.session.add(contenido)
        db.session.flush()

        contenidos = productora.contenidos_id
        if contenidos:
            productora.contenidos_id += [contenido.id]
        else:
            productora.contenidos_id = [contenido.id]

        db.session.commit()

        return {'message': 'Contenido añadido'}, 201
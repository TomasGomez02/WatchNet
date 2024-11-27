from flask import request
from flask_login import current_user
from flask_restful import Resource
from datetime import datetime, timezone
from auth import token_required
from models.models import db, Resenia, Usuario, Titulo

class CrearResenia(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json()

        info_login = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not info_login:
            return {'message': 'Usuario no encontrado'}, 404

        usuario = Usuario.query.filter_by(info_login_id=info_login.id).first()
        if not usuario:
            return {'message': 'Usuario no encontrado en la tabla Usuarios'}, 404

        nombre_contenido = data['nombre_contenido']
        contenido = Titulo.query.filter_by(nombre=nombre_contenido).first()
        if not contenido:
            return {'message': f'Contenido "{nombre_contenido}" no encontrado'}, 404

        puntuacion = data['puntuacion']
        texto = data['texto']
        fecha_publicacion = datetime.now(timezone.utc)

        # Crear la reseña con los datos proporcionados
        resenia = Resenia(
            usuario_id=usuario.id, 
            puntuacion=puntuacion,
            texto=texto,
            titulo_id=contenido.id, 
            fecha_publicacion=fecha_publicacion
        )
        db.session.add(resenia)
        db.session.commit()

        return {'message': 'Reseña añadida con éxito'}, 201

      
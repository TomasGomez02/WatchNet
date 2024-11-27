from datetime import datetime, timezone
from flask import request
from flask_restful import Resource
from app import token_required, db
from models.comentario import Comentario
from models.info_login import InfoLogin
from models.resenia import Resenia
from models.usuario import Usuario

class Comentar(Resource):
    @token_required
    def post(self, current_user, resenia_id):
        data = request.get_json()

        texto = data['texto']
        if not texto:
            return {'message': 'El texto del comentario es obligatorio'}, 400

        resenia = Resenia.query.filter_by(id=resenia_id).first()
        if not resenia:
            return {'message': 'Reseña no encontrada'}, 404

        info_login = InfoLogin.query.filter_by(nombre_usuario=current_user).first()
        if not info_login:
            return {'message': 'Usuario no encontrado'}, 404

        usuario = Usuario.query.filter_by(info_login_id=info_login.id).first()
        if not usuario:
            return {'message': 'Usuario no encontrado en la tabla Usuarios'}, 404

        # Crear el comentario y asociarlo a la reseña
        comentario = Comentario(
            texto=texto,
            usuario_id=usuario.id,
            resenia_id=resenia.id, 
            fecha_publicacion=datetime.now(timezone.utc)
        )

        db.session.add(comentario)
        db.session.commit()

        return {'message': 'Comentario agregado con éxito'}, 201

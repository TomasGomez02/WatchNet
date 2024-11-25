from flask import request
from flask_login import current_user
from flask_restful import Resource
from datetime import datetime, timezone
from app import token_required, db
from models.info_login import InfoLogin
from models.resenia import Resenia
from models.usuario import Usuario



class CrearResenia(Resource):
    @token_required
    def post(self):
        try:
            # Obtener los datos enviados en el cuerpo de la solicitud
            data = request.get_json()

            # Validar que los datos requeridos estén presentes
            puntuacion = data.get('puntuacion')
            texto = data.get('texto')
            titulo_id = data.get('titulo_id')

            if not puntuacion or not texto or not titulo_id:
                return {'message': 'Faltan datos requeridos'}, 400

            # Obtener el usuario actual a partir de su nombre de usuario
            info_login = InfoLogin.query.filter_by(nombre_usuario=current_user).first()
            if not info_login:
                return {'message': 'Usuario no encontrado'}, 404

            usuario = Usuario.query.filter_by(info_login_id=info_login.id).first()
            if not usuario:
                return {'message': 'Usuario no encontrado en la base de datos'}, 404

            # Crear la reseña con los datos proporcionados
            fecha_publicacion = datetime.now(timezone.utc)
            resenia = Resenia(
                usuario_id=usuario.id, 
                puntuacion=puntuacion,
                texto=texto, 
                titulo_id=titulo_id,
                fecha_publicacion=fecha_publicacion
            )

            # Agregar la reseña a la base de datos
            db.session.add(resenia)
            db.session.commit()

            return {'message': 'Reseña añadida con éxito'}, 201

        except Exception as e:
            db.session.rollback()
            return {'message': f'Error: {str(e)}'}, 500

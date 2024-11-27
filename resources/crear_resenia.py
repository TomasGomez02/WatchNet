from flask import request
from flask_login import current_user
from flask_restful import Resource
from datetime import datetime, timezone
from auth import token_required
from models.models import db, InfoLogin, Resenia, Usuario

class CrearResenia(Resource):
    @token_required
    def post(self):
        data = request.get_json()
        
        info_login = InfoLogin.query.filter_by(nombre_usuario=current_user).first()
        usuario = Usuario.query.filter_by(info_login_id=info_login.id).first()
        
        puntuacion=data['puntuacion']
        texto=data['texto']
        titulo_id=data['titulo_id']
        duracion=data['duracion']
        fecha_publicacion= datetime.now(timezone.utc)
        
        resenia = Resenia(usuario_id=usuario.id, 
                        puntuacion= puntuacion,
                        texto=texto, 
                        titulo_id=titulo_id,
                        duracion=duracion,
                        fecha_publicacion=fecha_publicacion
                        )
              
        db.session.add(resenia)
        db.session.commit()

        return {'message': 'Reseña añadida con éxito'}, 201

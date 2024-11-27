from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, make_response, redirect, url_for, session
from flask_restful import Api, Resource
from models.models import Titulo, Usuario, Reseña, db, Productora, TipoTitulo, Episodio
from auth import token_required

titulo_bp = Blueprint('titulo', __name__)
titulo_api = Api(titulo_bp)

def create_epsidode(titulo: str, duracion: int, orden: int, fecha_emision: datetime.date, titulo_id: int):
    new_episode = Episodio(titulo=titulo,
                           duracion=duracion,
                           orden=orden,
                           fecha_emision=fecha_emision,
                           titulo_id=titulo_id)
    db.session.add(new_episode)

class TituloAPI(Resource):
    @token_required(user_type='producer')
    def post(self, current_user):
        data = request.get_json()

        productora = Productora.query.filter_by(nombre_usuario=current_user).first()

        fecha_inicio = datetime.fromisoformat(data['fecha_inicio']).date()
        fecha_fin = datetime.fromisoformat(data['fecha_fin']).date()
        titulo = data['titulo']
        tipo = TipoTitulo(data['tipo'])

        nuevo_titulo = Titulo(fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        titulo=titulo, 
                        tipo=tipo,
                        productora_id=productora.id)
        
        db.session.flush()
        db.session.add(nuevo_titulo)
        
        if nuevo_titulo.tipo == TipoTitulo.PELICULA:
            create_epsidode(nuevo_titulo.titulo,
                            data['duracion'],
                            orden=1,
                            fecha_emision=fecha_inicio,
                            titulo_id=nuevo_titulo.id)
        
        db.session.commit()

        return {'message': 'Titulo añadido'}, 200
    
    def get(self, titulo_id):
        titulo = Titulo.query.filter_by(id=int(titulo_id)).first()

        if not titulo:
            return {'error': 'Titulo no encontrado'}, 404
        
        data = titulo.serialize()

        return {'titulo': data}, 200
    
    @token_required(user_type='producer')
    def delete(self, current_user, titulo_id):
        titulo = Titulo.query.filter_by(id=int(titulo_id)).first()

        if not titulo:
            return {'error': 'Titulo no encontrado'}, 404
        
        productora = Productora.query.filter_by(nombre_usuario=current_user).first()
        
        if titulo.productora_id != productora.id:
            return {'error': 'No Autorizado'}, 401
        
        db.session.delete(titulo)
        db.session.commit()

        return {'message': 'Titulo eliminado'}, 200
    
class EpisodioAPI(Resource):
    @token_required('producer')
    def post(self, current_user, titulo_id):
        data = request.get_json()

        productora = Productora.query.filter_by(nombre_usuario=current_user).first()
        titulo = Titulo.query.filter_by(id=titulo_id).first()

        if not titulo:
            return {'error': 'Title not found'}, 404
        if titulo.productora_id != productora.id:
            return {'error': 'Not authorized'}, 401

        ep_titulo = data['titulo']
        duracion = data['duracion']
        orden = data['orden']
        fecha_emision = datetime.fromisoformat(data['fecha_emision']).date()

        if Episodio.query.filter_by(titulo_id=titulo.id, orden=orden).first():
            return {'error': 'Episodio ya existe'}, 403

        create_epsidode(ep_titulo,
                        duracion,
                        orden,
                        fecha_emision,
                        titulo.id)

        db.session.commit()

        return {'message': 'Episodio añadido'}, 200
    
    def get(self, titulo_id, orden=None):
        titulo = Titulo.query.filter_by(id=titulo_id).first()

        if not titulo:
            return {'error': 'Title not found'}, 404
        
        if orden is None:
            episodios = Episodio.query.filter_by(titulo_id=titulo.id)
            return {'episodios': [episodio.serialize() for episodio in episodios]}, 200
        
        episodio = Episodio.query.filter_by(titulo_id=titulo.id, orden=orden).first()
        if not episodio:
            return {'error': 'Episode not found'}, 404
        
        return {'episodio': episodio.serialize()}, 200

    @token_required(user_type='producer')
    def delete(self, current_user, titulo_id, orden):
        episodio = Episodio.query.filter_by(titulo_id=titulo_id, orden=orden).first()

        if not episodio:
            return {'error': 'Episodio no encontrado'}, 404
        
        titulo = Titulo.query.filter_by(id=titulo_id).first()
        productora = Productora.query.filter_by(nombre_usuario=current_user).first()

        if not titulo or not productora:
            return {'error': 'Something went wrong'}, 404
        
        if titulo.productora_id != productora.id:
            return {'error': 'No Autorizado'}, 401
        
        db.session.delete(episodio)
        db.session.commit()

        return {'message': 'Episodio eliminado'}, 200
    
class ReseñaAPI(Resource):
    @token_required(user_type='user')
    def post(self, current_user, titulo_id):
        data = request.get_json()

        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario:
            return {'message': 'Usuario no encontrado en la base de datos'}, 404

        titulo = Titulo.query.filter_by(id=titulo_id).first()
        if not titulo:
            return {'message': f'Contenido no encontrado'}, 404

        puntuacion = data['puntuacion']
        texto = data['texto']
     
        resenia = Reseña(
            usuario_id=usuario.id, 
            puntuacion=puntuacion,
            texto=texto,
            titulo_id=titulo.id, 
            fecha_publicacion= datetime.now(timezone.utc)
        )
        db.session.add(resenia)
        db.session.commit()

        return {'message': 'Reseña añadida con éxito'}, 200
    
    @token_required(user_type='user')
    def delete(self, current_user, resenia_id):
        resenia = Reseña.query.filter_by(id=resenia_id).first()

        if not resenia:
            return {'message': 'Reseña no encontrada'}, 404

        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario or resenia.usuario_id != usuario.id:
            return {'message': 'No tienes permiso para eliminar esta reseña'}, 403

        db.session.delete(resenia)
        db.session.commit()

        return {'message': 'Reseña eliminada con éxito'}, 200 


    
titulo_api.add_resource(TituloAPI, '/', '/<int:titulo_id>')
titulo_api.add_resource(EpisodioAPI, '/<int:titulo_id>/episodes', 
                        '/<int:titulo_id>/episodes/<int:orden>')
titulo_api.add_resource(ReseñaAPI, '/<str:current_user>/titulos/<int:titulo_id>/reseña')
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, make_response, redirect, url_for, session
from flask_restful import Api, Resource
from models.models import Comentario, Impresion, Titulo, Usuario, Reseña, db, Productora, TipoTitulo, Episodio
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
    """
    Clase que maneja el manejo de titulos por parte de una productora.

    """
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
        
        db.session.add(nuevo_titulo)
        db.session.flush()
        
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
    """
    Clase que maneja la reseñas para un título específico.

    """
    @token_required(user_type='user')
    def post(self, current_user, titulo_id):
        """
        Método para crear una nueva reseña para un título específico.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        titulo_id : int
            El ID del título para el que se desea crear la reseña.

        Returns
        --------
        dict
            Un diccionario con un mensaje de error y código de estado 404 si no se encuentra al usuario 
            o al título. Si la reseña se crea con éxito, se devuelve un mensaje de éxito con el código 200.
        """
        data = request.get_json()

        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario:
            return {'message': 'Usuario no encontrado en la base de datos'}, 404

        titulo = Titulo.query.filter_by(id=titulo_id).first()
        if not titulo:
            return {'message': f'Titulo no encontrado'}, 404

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
    
    def get(self, titulo_id, review_id=None):
        titulo = Titulo.query.filter_by(id=titulo_id).first()

        if not titulo:
            return {'error': 'Title not found'}, 404
        
        if review_id is None:
            reviews = Reseña.query.filter_by(titulo_id=titulo.id)
            return {'reviews': [review.serialize() for review in reviews]}, 200
        
        review = Reseña.query.filter_by(titulo_id=titulo.id, id=review_id).first()
        if not review:
            return {'error': 'Review not found'}, 404
        
        return {'review': review.serialize()}, 200
    
    @token_required(user_type='user')
    def delete(self, current_user, titulo_id, review_id):
        """
        Método para eliminar una reseña específica.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        resenia_id : int
            El ID de la reseña que se desea eliminar.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de error y código de estado 404 si no se encuentra la reseña. 
            Si el usuario no tiene permiso para eliminarla, se devuelve un mensaje de error con código 403.
            Si la reseña se elimina con éxito, se devuelve un mensaje de éxito con código 200.
        """
        resenia = Reseña.query.filter_by(id=review_id, titulo_id=titulo_id).first()

        if not resenia:
            return {'message': 'Reseña no encontrada'}, 404

        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario or resenia.usuario_id != usuario.id:
            return {'message': 'No tienes permiso para eliminar esta reseña'}, 403

        db.session.delete(resenia)
        db.session.commit()

        return {'message': 'Reseña eliminada con éxito'}, 200 
    
class ComentarioAPI(Resource):
    """
    Clase que maneja la creación de comentarios sobre una reseña.
    """
    @token_required(user_type='user')
    def post(self, current_user, titulo_id, review_id):
        """
        Método para agregar un comentario a una reseña.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        resenia_id : int
            El ID de la reseña sobre la que se quiere comentar.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de error y código de estado 400 si el texto del comentario está vacío. 
            Si la reseña o el usuario no se encuentran, se devuelve un mensaje de error con código 404.
            Si el comentario se agrega con éxito, se devuelve un mensaje de éxito con código 200.
        """
        data = request.get_json()

        if not 'texto' in data:
            return {'message': 'El texto del comentario es obligatorio'}, 400
        texto = data['texto']

        resenia = Reseña.query.filter_by(id=review_id).first()
        if not resenia:
            return {'message': 'Reseña no encontrada'}, 404

        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario:
            return {'message': 'Usuario no encontrado en la base de datos'}, 404

        comentario = Comentario(
                        texto=texto,
                        usuario_id=usuario.id,
                        resenia_id=resenia.id, 
                        fecha_publicacion=datetime.now(timezone.utc)
                    )

        db.session.add(comentario)
        db.session.commit()

        return {'message': 'Comentario agregado con éxito'}, 200
    
    def get(self, titulo_id, review_id, comentario_id=None):
        titulo = Titulo.query.filter_by(id=titulo_id).first()

        if not titulo:
            return {'error': 'Title not found'}, 404
        
        review = Reseña.query.filter_by(id=review_id).first()

        if not review:
            return {'error': 'Review not found'}, 404
        
        if comentario_id is None:
            comments = Comentario.query.filter_by(resenia_id=review.id)
            return {'comments': [comment.serialize() for comment in comments]}, 200
        
        comment = Comentario.query.filter_by(resenia_id=review.id, id=comentario_id).first()
        if not comment:
            return {'error': 'Comment not found'}, 404
        
        return {'comment': comment.serialize()}, 200
    
    @token_required(user_type='user')
    def delete(self, current_user, titulo_id, review_id, comentario_id):
        """
        Método para eliminar una comentario.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        comentario_id : int
            El ID del comentario que se desea eliminar.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de error y código de estado 404 si no se encuentra la reseña. 
            Si el usuario no tiene permiso para eliminarla, se devuelve un mensaje de error con código 403.
            Si la reseña se elimina con éxito, se devuelve un mensaje de éxito con código 200.
        """
        comentario = Comentario.query.filter_by(id=comentario_id).first()

        if not comentario:
            return {'message': 'Comentario no encontrado'}, 404

        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario or comentario.usuario_id != usuario.id:
            return {'message': 'No es posible eliminar este comentario'}, 403

        db.session.delete(comentario)
        db.session.commit()

        return {'message': 'Comentario eliminado con éxito'}, 200
    
class ImpresionAPI(Resource):
    """
    Clase que maneja la acción de puntuar una reseña.

    """
    @token_required(user_type='user')
    def post(self, current_user, titulo_id, review_id):
        """
        Método para puntuar una reseña.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        resenia_id : int
            El ID de la reseña que se desea puntuar.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de error y código de estado 400 si el valor de la puntuación es inválido 
            o si el usuario ya ha puntuado la reseña. Si la reseña o el usuario no se encuentran, se devuelve un 
            mensaje de error con código 404. Si la puntuación se agrega con éxito, se devuelve un mensaje de éxito 
            con código 200.
        """
        data = request.get_json()
        valor = data['valor']

        if valor not in [1, -1]:
            return {'message': 'El valor debe ser 1 (like) o -1 (dislike).'}, 400

        resenia = Reseña.query.filter_by(id=review_id).first()
        if not resenia:
            return {'message': 'Reseña no encontrada'}, 404

        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario:
            return {'message': 'Usuario no encontrado en la base de datos'}, 404
        
        impresion_existente = Impresion.query.filter_by(usuario_id=usuario.id, resenia_id=resenia.id).first()
        if impresion_existente:
            return {'message': 'Ya has puntuado esta reseña anteriormente.'}, 400

        impresion = Impresion(
            usuario_id=usuario.id,
            resenia_id=resenia.id,
            valor=valor)

        db.session.add(impresion)
        db.session.commit()

        return {'message': f'Has dado un {"like" if valor == 1 else "dislike"} a la reseña.'}, 200
    
    def get(self, titulo_id, review_id):
        titulo = Titulo.query.filter_by(id=titulo_id).first()

        if not titulo:
            return {'error': 'Title not found'}, 404
        
        review = Reseña.query.filter_by(id=review_id).first()

        if not review:
            return {'error': 'Review not found'}, 404
        
        impresions = Impresion.query.filter_by(resenia_id=review.id)
        return {'impresiones': [impresion.serialize() for impresion in impresions]}, 200
    
    @token_required(user_type='user')
    def delete(self, current_user, titulo_id, review_id):
        """
        Método para eliminar un puntaje previamente dado a una reseña.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        resenia_id : int
            El ID de la reseña de la cual se desea eliminar el puntaje.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de error y código de estado 404 si el usuario o la reseña no se encuentran, 
            o si el usuario no ha puntuado la reseña. Si la puntuación se elimina con éxito, se devuelve un mensaje 
            de éxito con código de estado 200.
        """
        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario:
            return {'message': 'Usuario no encontrado en la base de datos'}, 404

        resenia = Reseña.query.filter_by(id=review_id).first()
        if not resenia:
            return {'message': 'Reseña no encontrada'}, 404

        impresion = Impresion.query.filter_by(usuario_id=usuario.id, resenia_id=resenia.id).first()
        if not impresion:
            return {'message': 'No has puntuado esta reseña.'}, 404

        db.session.delete(impresion)
        db.session.commit()

        return {'message': 'Puntuación eliminada con éxito.'}, 200

titulo_api.add_resource(TituloAPI, '/', '/<int:titulo_id>')
titulo_api.add_resource(EpisodioAPI, '/<int:titulo_id>/episodes', 
                        '/<int:titulo_id>/episodes/<int:orden>')
titulo_api.add_resource(ReseñaAPI, '/<int:titulo_id>/review', 
                        '/<int:titulo_id>/review/<int:review_id>')
titulo_api.add_resource(ComentarioAPI, '/<int:titulo_id>/review/<int:review_id>/comentario', 
                        '/<int:titulo_id>/review/<int:review_id>/comentario/<int:comentario_id>')
titulo_api.add_resource(ImpresionAPI, '/<int:titulo_id>/review/<int:review_id>/impresion')
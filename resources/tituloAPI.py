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
    Manage titles for a production company.
    """

    @token_required(user_type='producer')
    def post(self, current_user):
        """
        Create a new title.
        ---
        tags:
          - Titles
        summary: Create a title
        description: Create a new title for a production company. Requires authentication as a producer.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  titulo:
                    type: string
                    example: "My Movie"
                    description: The title of the movie or series.
                  fecha_inicio:
                    type: string
                    format: date
                    example: "2023-01-01"
                    description: The start date of the title.
                  fecha_fin:
                    type: string
                    format: date
                    example: "2023-12-31"
                    description: The end date of the title.
                  tipo:
                    type: string
                    enum: [PELICULA, SERIE]
                    example: "PELICULA"
                    description: The type of the title (movie or series).
                  duracion:
                    type: integer
                    example: 120
                    description: The duration of the movie (required for movies only).
        responses:
          200:
            description: Title created successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Titulo añadido"
          401:
            description: Unauthorized.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "No Autorizado"
          400:
            description: Bad request. Invalid input data.
        """
        data = request.get_json()

        productora = Productora.query.filter_by(nombre_usuario=current_user).first()

        fecha_inicio = datetime.fromisoformat(data['fecha_inicio']).date()
        fecha_fin = datetime.fromisoformat(data['fecha_fin']).date()
        titulo = data['titulo']
        tipo = TipoTitulo(data['tipo'])

        nuevo_titulo = Titulo(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            titulo=titulo, 
            tipo=tipo,
            productora_id=productora.id
        )
        
        db.session.add(nuevo_titulo)
        db.session.flush()
        
        if nuevo_titulo.tipo == TipoTitulo.PELICULA:
            create_epsidode(
                nuevo_titulo.titulo,
                data['duracion'],
                orden=1,
                fecha_emision=fecha_inicio,
                titulo_id=nuevo_titulo.id
            )
        
        db.session.commit()

        return {'message': 'Titulo añadido'}, 200

    def get(self, titulo_id):
        """
        Retrieve a title by its ID.
        ---
        tags:
          - Titles
        summary: Get a title
        description: Fetch details of a specific title by its ID.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title to retrieve.
        responses:
          200:
            description: Title details retrieved successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    titulo:
                      type: object
                      description: Serialized title data.
          404:
            description: Title not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "Titulo no encontrado"
        """
        titulo = Titulo.query.filter_by(id=int(titulo_id)).first()

        if not titulo:
            return {'error': 'Titulo no encontrado'}, 404
        
        data = titulo.serialize()

        return {'titulo': data}, 200

    @token_required(user_type='producer')
    def delete(self, current_user, titulo_id):
        """
        Delete a title.
        ---
        tags:
          - Titles
        summary: Delete a title
        description: Delete a title by its ID. Requires authentication as a producer.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title to delete.
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for producer authentication.
        responses:
          200:
            description: Title deleted successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Titulo eliminado"
          401:
            description: Unauthorized. The producer does not have access to delete this title.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "No Autorizado"
          404:
            description: Title not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "Titulo no encontrado"
        """
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
    """
    Manage episodes of a title.
    """

    @token_required('producer')
    def post(self, current_user, titulo_id):
        """
        Create a new episode.
        ---
        tags:
          - Episodes
        summary: Add a new episode
        description: Create a new episode for a specific title. Requires authentication as a producer.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title to which the episode belongs.
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for producer authentication.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  titulo:
                    type: string
                    example: "Episode 1"
                    description: The title of the episode.
                  duracion:
                    type: integer
                    example: 45
                    description: The duration of the episode in minutes.
                  orden:
                    type: integer
                    example: 1
                    description: The order of the episode in the series.
                  fecha_emision:
                    type: string
                    format: date
                    example: "2023-01-01"
                    description: The release date of the episode.
        responses:
          200:
            description: Episode added successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Episodio añadido"
          401:
            description: Unauthorized. The producer does not have access to this title.
          403:
            description: Episode already exists.
          404:
            description: Title not found.
        """
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

        create_epsidode(ep_titulo, duracion, orden, fecha_emision, titulo.id)

        db.session.commit()

        return {'message': 'Episodio añadido'}, 200

    def get(self, titulo_id, orden=None):
        """
        Retrieve episodes of a title.
        ---
        tags:
          - Episodes
        summary: Get episodes
        description: Retrieve all episodes for a title or a specific episode by its order.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title whose episodes are to be retrieved.
          - in: path
            name: orden
            required: false
            schema:
              type: integer
            description: The order of the specific episode to retrieve.
        responses:
          200:
            description: Episodes retrieved successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    episodios:
                      type: array
                      items:
                        type: object
                        description: Serialized episode data.
          404:
            description: Title or episode not found.
        """
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
        """
        Delete an episode.
        ---
        tags:
          - Episodes
        summary: Delete an episode
        description: Delete a specific episode by its order. Requires authentication as a producer.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title to which the episode belongs.
          - in: path
            name: orden
            required: true
            schema:
              type: integer
            description: The order of the episode to delete.
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for producer authentication.
        responses:
          200:
            description: Episode deleted successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Episodio eliminado"
          401:
            description: Unauthorized. The producer does not have access to delete this episode.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "No Autorizado"
          404:
            description: Episode not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "Episodio no encontrado"
        """
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
    Manage reviews for a title.
    """

    @token_required(user_type='user')
    def post(self, current_user, titulo_id):
        """
        Add a new review.
        ---
        tags:
          - Reviews
        summary: Add a review
        description: Add a review for a specific title. Requires authentication as a user.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title to which the review is being added.
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for user authentication.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  puntuacion:
                    type: integer
                    example: 4
                    description: The rating for the title (1-5 scale).
                  texto:
                    type: string
                    example: "Amazing title!"
                    description: The text of the review.
        responses:
          200:
            description: Review added successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Reseña añadida con éxito"
          404:
            description: Title or user not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Titulo no encontrado"
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
            fecha_publicacion=datetime.now(timezone.utc)
        )
        db.session.add(resenia)
        db.session.commit()

        return {'message': 'Reseña añadida con éxito'}, 200

    def get(self, titulo_id, review_id=None):
        """
        Retrieve reviews.
        ---
        tags:
          - Reviews
        summary: Get reviews
        description: Retrieve all reviews for a title or a specific review by its ID.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title whose reviews are being retrieved.
          - in: path
            name: review_id
            required: false
            schema:
              type: integer
            description: The ID of the specific review to retrieve.
        responses:
          200:
            description: Reviews retrieved successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    reviews:
                      type: array
                      items:
                        type: object
                        description: Serialized review data.
                    review:
                      type: object
                      description: Serialized review data (for a single review).
          404:
            description: Title or review not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "Title not found"
        """
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
        Delete a specific review.
        ---
        tags:
          - Reviews
        summary: Delete a review
        description: Delete a specific review for a given title. Requires authentication as a user.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title associated with the review.
          - in: path
            name: review_id
            required: true
            schema:
              type: integer
            description: The ID of the review to delete.
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for user authentication.
        responses:
          200:
            description: Review successfully deleted.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Reseña eliminada con éxito"
          403:
            description: User does not have permission to delete this review.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "No tienes permiso para eliminar esta reseña"
          404:
            description: Review not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Reseña no encontrada"
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
    Manage comments on reviews.
    """

    @token_required(user_type='user')
    def post(self, current_user, titulo_id, review_id):
        """
        Add a comment to a review.
        ---
        tags:
          - Comments
        summary: Add a comment
        description: Add a comment to a specific review. Requires authentication as a user.
        parameters:
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for user authentication.
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title associated with the review.
          - in: path
            name: review_id
            required: true
            schema:
              type: integer
            description: The ID of the review to which the comment is being added.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  texto:
                    type: string
                    example: "Great review!"
                    description: The content of the comment.
        responses:
          200:
            description: Comment successfully added.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Comentario agregado con éxito"
          400:
            description: Invalid input or missing data.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "El texto del comentario es obligatorio"
          404:
            description: Review or user not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Reseña no encontrada"
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
        """
        Retrieve comments for a review.
        ---
        tags:
          - Comments
        summary: Get comments
        description: Retrieve all comments for a specific review or a single comment by its ID.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title associated with the review.
          - in: path
            name: review_id
            required: true
            schema:
              type: integer
            description: The ID of the review for which comments are being retrieved.
          - in: path
            name: comentario_id
            required: false
            schema:
              type: integer
            description: The ID of the specific comment to retrieve.
        responses:
          200:
            description: Comments retrieved successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    comments:
                      type: array
                      items:
                        type: object
                        description: Serialized comment data.
                    comment:
                      type: object
                      description: Serialized comment data for a specific comment.
          404:
            description: Title, review, or comment not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "Title not found"
        """
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
        Delete a comment.
        ---
        tags:
          - Comments
        summary: Delete a comment
        description: Delete a specific comment for a review. Requires authentication as a user.
        parameters:
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for user authentication.
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title associated with the review.
          - in: path
            name: review_id
            required: true
            schema:
              type: integer
            description: The ID of the review associated with the comment.
          - in: path
            name: comentario_id
            required: true
            schema:
              type: integer
            description: The ID of the comment to delete.
        responses:
          200:
            description: Comment deleted successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Comentario eliminado con éxito"
          403:
            description: User not authorized to delete this comment.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "No es posible eliminar este comentario"
          404:
            description: Comment not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Comentario no encontrado"
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
    Manage ratings (likes or dislikes) for reviews.
    """

    @token_required(user_type='user')
    def post(self, current_user, titulo_id, review_id):
        """
        Add a rating to a review.
        ---
        tags:
          - Ratings
        summary: Add a rating
        description: Add a like or dislike rating to a specific review. Requires authentication as a user.
        parameters:
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for user authentication.
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title associated with the review.
          - in: path
            name: review_id
            required: true
            schema:
              type: integer
            description: The ID of the review to rate.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  valor:
                    type: integer
                    enum: [1, -1]
                    example: 1
                    description: The rating value (1 for like, -1 for dislike).
        responses:
          200:
            description: Rating successfully added.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Has dado un like a la reseña."
          400:
            description: Invalid rating value or duplicate rating.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "El valor debe ser 1 (like) o -1 (dislike)."
          404:
            description: Review or user not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Reseña no encontrada."
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
        """
        Retrieve ratings for a review.
        ---
        tags:
          - Ratings
        summary: Get ratings
        description: Retrieve all ratings for a specific review.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title associated with the review.
          - in: path
            name: review_id
            required: true
            schema:
              type: integer
            description: The ID of the review for which ratings are being retrieved.
        responses:
          200:
            description: Ratings retrieved successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    impresiones:
                      type: array
                      items:
                        type: object
                        description: Serialized rating data.
          404:
            description: Title or review not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      example: "Title not found."
        """
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
        Delete a rating from a review.
        ---
        tags:
          - Ratings
        summary: Delete a rating
        description: Remove a rating (like or dislike) from a specific review. Requires authentication as a user.
        parameters:
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for user authentication.
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title associated with the review.
          - in: path
            name: review_id
            required: true
            schema:
              type: integer
            description: The ID of the review associated with the rating.
        responses:
          200:
            description: Rating successfully deleted.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Puntuación eliminada con éxito."
          403:
            description: User not authorized to delete this rating.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "No tienes permiso para eliminar esta puntuación."
          404:
            description: Rating not found.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Puntuación no encontrada."
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
from flask import request, make_response, redirect, url_for, session, Blueprint
from flask_restful import Resource, Api
from flask.templating import render_template
from models.models import  Episodio, EstadoTitulo, Relacion, Reseña, Seguimiento, Titulo, DataBase, Usuario
from auth import generate_token, token_required

usuarioAPI_bp = Blueprint('usuarioAPI', __name__)
usuario_api = Api(usuarioAPI_bp)

db = DataBase().db

class UserAPI(Resource):
    """
    Manage user login operations.
    """
    def post(self):
        """
        Register a new user.
        ---
        tags:
          - Authentication
        summary: User registration
        description: Registers a new user with a username, email, and password.
        requestBody:
          required: true
          content:
            application/x-www-form-urlencoded:
              schema:
                type: object
                properties:
                  email:
                    type: string
                    example: "user@example.com"
                  username:
                    type: string
                    example: "newuser"
                  password:
                    type: string
                    example: "securepassword"
        responses:
          200:
            description: User successfully registered.
          400:
            description: Missing or already registered data.
        """
        data = request.get_json()
        email = data['email']
        password = data['password']
        username = data['username']

        if not username or not email or not password:
            return {'error': 'Falta data'}, 400

        if Usuario.query.filter_by(email=email).first():
            return {'error': 'Email ya esta registrado'}, 400

        if Usuario.query.filter_by(nombre_usuario=username).first():
            return {'error': 'Username ya existe'}, 400

        new_login = Usuario(nombre_usuario=username, email=email)
        new_login.set_password(password)

        db.session.add(new_login)
        db.session.commit()

        token = generate_token(new_login.nombre_usuario, 'user')
        session['auth_token'] = token

        return {'message': 'Usuario registrado'}, 200
    
    def get(self):
        """
        Authenticate a user during login.
        ---
        tags:
          - Authentication
        summary: User login
        description: Authenticates a user with their email and password.
        requestBody:
          required: true
          content:
            application/x-www-form-urlencoded:
              schema:
                type: object
                properties:
                  email:
                    type: string
                    example: "user@example.com"
                  password:
                    type: string
                    example: "securepassword"
        responses:
          302:
            description: Redirects to the user profile page on successful login.
          400:
            description: Missing or incorrect credentials.
        """
        data = request.get_json()
        email = data['email']
        password = data['password']

        if not email or not password:
            return {'error': 'Falta data'}, 403

        login_info = Usuario.query.filter_by(email=email).first()

        if not login_info or not login_info.check_password(password):
            return {'error': 'Login info incorrect.'}, 403
        
        token = generate_token(login_info.nombre_usuario, 'user')
        session['auth_token'] = token

        return {'message': 'User verified successfully'}, 200
    
    def delete(self):
        """
        Log out the current user.
        ---
        tags:
          - Authentication
        summary: User logout
        description: Logs out the currently authenticated user and redirects to the homepage.
        responses:
          302:
            description: Redirect to homepage after logout.
        """
        session.pop('auth_token', None)
        return redirect(url_for('index'))
    
class SeguirAPI(Resource):
    """
    Manage user follow operations.
    """
    @token_required(user_type='user')
    def post(self, current_user):
        """
        Follow another user.
        ---
        tags:
          - Follows
        summary: Follow a user
        description: Allows the authenticated user to follow another user by their ID.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  seguido_id:
                    type: integer
                    example: 2
        responses:
          200:
            description: User successfully followed.
          403:
            description: Operation not allowed (e.g., trying to follow oneself or already following).
          404:
            description: User to follow not found.
        """
        data = request.get_json()
        seguido_id = data['seguido_id']
        seguidor = Usuario.query.filter_by(nombre_usuario=current_user).first()
        seguido = Usuario.query.filter_by(id=seguido_id).first()
        if not seguido:
            return {'message': 'El usuario que intentas seguir no existe'}, 404
        
        #Verifico que no se siga a si mismo
        if seguidor.id == seguido.id:
            return {'message': 'Operación no válida'}, 403

        #Verifico si ya se siguen
        relacion_existente = Relacion.query.filter_by(seguidor=seguidor.id, seguido=seguido.id).first()
        if relacion_existente:
            return {'message': 'Ya sigues a este usuario'}, 403

        nueva_relacion = Relacion(seguidor=seguidor.id, seguido=seguido.id)

        db.session.add(nueva_relacion)
        db.session.commit()

        return {'message': 'Ahora sigues a este usuario con éxito'}, 200
    
    @token_required(user_type='user')
    def get(self, current_user):  
        """
        Retrieve the list of followers or followings.
        ---
        tags:
          - Follows
        summary: Get followers or followings
        description: Fetches the list of followers or followings for the authenticated user.
        requestBody:
          required: false
          content:
            application/json:
              schema:
                type: object
                properties:
                  type:
                    type: string
                    enum: [follower, following]
        responses:
          200:
            description: List of followers or followings retrieved.
          404:
            description: User not found.
        """  
        user = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not user:
            return {'error': 'Usuario actual no existe'}, 404
        
        data = request.get_json()
        if 'type' in data and data['type'] == 'follower':
            seguidores = Relacion.query.filter_by(seguido=user.id)
            return {'seguidores': [seguidor.seguidor for seguidor in seguidores]}, 200
        seguidos = Relacion.query.filter_by(seguidor=user.id)
        return {'seguidos': [seguido.seguido for seguido in seguidos]}, 200
        
    
    @token_required(user_type='user')
    def delete(self, current_user, seguido_id):
        """
        Unfollow a user.
        ---
        tags:
          - Follows
        summary: Unfollow a user
        description: Allows the authenticated user to unfollow another user by their ID.
        parameters:
          - in: path
            name: seguido_id
            required: true
            schema:
              type: integer
            description: The ID of the user to unfollow.
        responses:
          200:
            description: User successfully unfollowed.
          404:
            description: User or follow relationship not found.
        """
        seguidor = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not seguidor:
            return {'message': 'Usuario no encontrado'}, 404

        seguido = Usuario.query.filter_by(id=seguido_id).first()
        if not seguido:
            return {'message': 'El usuario no existe'}, 404

        relacion = Relacion.query.filter_by(seguidor=seguidor.id, seguido=seguido.id).first()
        if not relacion:
            return {'message': 'No estás siguiendo a este usuario'}, 400

        db.session.delete(relacion)
        db.session.commit()

        return {'message': f'Has dejado de seguir a {seguido.nombre_usuario}'}, 200

class WatchlistAPI(Resource):
    """
    Manage following titles.
    """
    @token_required(user_type='user')
    def post(self, current_user, user):
        """
        Follow a title.
        ---
        tags:
          - Titles
        summary: Follow a title
        description: Allows the authenticated user to follow a specific title by its ID.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title to follow.
        responses:
          200:
            description: Title successfully followed.
          400:
            description: Already following the title.
          404:
            description: Title not found.
        """
        if current_user != user:
            return {'error': 'Access denied'}, 401
        
        usuario = Usuario.query.filter_by(nombre_usuario=user).first()
        data = request.get_json()
        if 'titulo_id' not in data:
            return {'error': 'Title is required'}, 403
        titulo_id = data['titulo_id']

        titulo = Titulo.query.filter_by(id=titulo_id).first()
        if not titulo:
            return {'error': 'Título no encontrado'}, 404
        
        seguimiento = Seguimiento.query.filter_by(usuario_id=usuario.id, titulo_id=titulo.id).first()

        if seguimiento:
            return {'message': 'Ya estás siguiendo este título'}, 403
        
        estado = EstadoTitulo(data['estado']) if 'estado' in data else EstadoTitulo.SIN_COMENZAR
        cantidad_visto = data['cantidad_visto'] if 'cantidad_visto' in data else 0

        episodios = Episodio.query.filter_by(titulo_id=titulo.id)

        if cantidad_visto > episodios.count():
            return {'error': 'Invalid cantidad_visto'}, 403
        
        nuevo_seguimiento = Seguimiento(
            usuario_id=usuario.id,
            estado=estado,  # 1=activo, 0=terminado
            resenia_id=None,  
            cantidad_visto=cantidad_visto,
            titulo_id=titulo.id
        )

        db.session.add(nuevo_seguimiento)
        db.session.commit()

        return {'message': 'Título seguido con éxito'}, 200
    
    @token_required(user_type='user')
    def put(self, current_user, titulo_id):
        """
        Update title follow status.
        ---
        tags:
          - Titles
        summary: Update title follow
        description: Updates the status and view count for a title being followed by the authenticated user.
        parameters:
          - in: path
            name: titulo_id
            required: true
            schema:
              type: integer
            description: The ID of the title to update.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  estado:
                    type: integer
                    example: 1
                    description: Status of the follow (1 = active, 0 = completed).
                  cantidad_visto:
                    type: integer
                    example: 10
                    description: Number of episodes watched.
        responses:
          200:
            description: Follow status updated successfully.
          404:
            description: Title not found or not being followed.
        """
        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()

        titulo = Titulo.query.filter_by(id=titulo_id).first()
        if not titulo:
            return {'message': 'Título no encontrado'}, 404

        seguimiento = Seguimiento.query.filter_by(usuario_id=usuario.id, titulo_id=titulo.id).first()
        if not seguimiento:
            return {'message': 'No estás siguiendo este título'}, 400  

        data = request.get_json()
        estado = data['estado', seguimiento.estado]  # Si no se pasa, se mantiene el actual
        cantidad_visto = data['cantidad_visto', seguimiento.cantidad_visto]  

        # Actualizar el seguimiento
        seguimiento.estado = estado
        seguimiento.cantidad_visto = cantidad_visto

        db.session.commit()
        return {'message': 'Seguimiento actualizado con éxito'}, 200
    
class PerfilUsuario(Resource):
    """
    Clase para gestionar el perfil de un usuario. 
    Permite consultar información personal, reseñas y series seguidas.

    """
    @token_required
    def get(self, current_user, seccion=None):
        """
        Metodo para obtener información del perfil del usuario.

        Parámetros
        -----------
        current_user (str): El nombre de usuario autenticado.
        seccion (str, opcional): Sección del perfil a consultar. 
            Valores permitidos: 'resenias', 'titulos', 'info', o None para obtener todo el perfil.

        Retorno
        -----------
        dict: Información de la sección solicitada o del perfil completo.
        int: Código de estado HTTP.
        """
        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()

        if seccion == 'resenias':
            return self.obtener_resenias(usuario.id)
        elif seccion == 'titulos':
            return self.obtener_titulos(usuario.id)
        elif seccion == 'info':
            return self.obtener_info(usuario.id)
        elif seccion is None:
            return self.obtener_perfil_completo(usuario.id)
        else:
            return {'message': 'Sección no válida'}, 400

    def obtener_resenias(self, usuario_id):
        """
        Obtiene todas las reseñas realizadas por el usuario.

        Parámetros
        --------
        usuario_id (int): ID del usuario.

        Retorno
        --------
        dict: Reseñas del usuario.
        """
        resenias = Reseña.query.filter_by(usuario_id=usuario_id).all()
        resenias_data = [{'id': r.id, 'puntuacion': r.puntuacion, 'texto': r.texto, 'fecha': r.fecha_publicacion.isoformat()} for r in resenias]
        return {'reseñas': resenias_data}

    def obtener_titulos(self, usuario_id):
        """
        Obtiene todas los titulos seguidos por el usuario.

        Parámetros
        --------
        usuario_id (int): ID del usuario.

        Retorno
        --------
        dict: Titulos seguidos por el usuario.
        """
        series = Seguimiento.query.filter_by(usuario_id=usuario_id).all()
        series_data = [{'titulo_id': s.titulo_id, 'estado': s.estado, 'cantidad_visto': s.cantidad_visto} for s in series]
        return {'series_vistas': series_data}

    def obtener_info(self, usuario_id):
        """
        Obtiene la informacion del usuario.

        Parámetros
        --------
        usuario_id (int): ID del usuario.

        Retorno
        --------
        dict: Informacion del usuario.
        """
        usuario = Usuario.query.get(usuario_id)
        info_data = {'nombre_usuario': usuario.nombre_usuario, 'email': usuario.email}
        return {'usuario': info_data}

    def obtener_perfil_completo(self, usuario_id):
        """
        Obtiene toda la informacion correspondiente al perfil del usuario.

        Parámetros
        --------
        usuario_id (int): ID del usuario.

        Retorno
        --------
        dict: Informacion del perfil del usuario.
        """
        info = self.obtener_info(usuario_id)
        resenias = self.obtener_resenias(usuario_id)
        series = self.obtener_titulos(usuario_id)
        
        return {
            'usuario': info['usuario'],
            'reseñas': resenias['reseñas'],
            'series_vistas': series['series_vistas']
        }, 200

usuario_api.add_resource(UserAPI, '/')
usuario_api.add_resource(SeguirAPI, '/follow',
                         '/follow/<int:seguido_id>')
usuario_api.add_resource(WatchlistAPI, '/<string:user>/watchlist',
                         '/<string:user>/watchlist/<int:watch_id>')
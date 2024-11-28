from datetime import datetime, timezone
from flask import request, make_response, redirect, url_for, session, Blueprint
from flask_restful import Resource, Api
from flask.templating import render_template
from models.models import Comentario, Impresion, Relacion, Reseña, Seguimiento, Titulo, db, Usuario
from auth import generate_token, token_required

usuario_bp = Blueprint('usuario', __name__)
usuario_api = Api(usuario_bp)

class Login(Resource):
    """
    Clase que maneja las operaciones de inicio de sesión de un usuario.

    """
    def post(self):
        """
        Método para autenticar a un usuario durante el inicio de sesión.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de error y código de estado 400 si falta información o las credenciales son incorrectas.
        redirect
            Si las credenciales son correctas, se redirige al perfil del usuario.
        """
        data = request.form
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Falta data'}, 400

        login_info = Usuario.query.filter_by(email=email).first()

        if not login_info or not login_info.check_password(password):
            return {'error': 'Login info incorrect.'}, 400
        
        token = generate_token(login_info.nombre_usuario, 'user')
        session['auth_token'] = token

        return redirect(url_for('usuario.userprofile', current_user=login_info.nombre_usuario))
    
    def get(self):
        """
        Método para obtener la página de inicio de sesión.

        Retorna
        --------
        response
            Una respuesta que contiene el HTML de la página de inicio de sesión.
        """
        response = make_response(render_template('login.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
    def delete(self):
        """
        Método para cerrar sesión.

        Retorna
        -------
        Response
            Una redirección a la página principal después de cerrar sesión.
        """
        session.pop('auth_token', None)
        return redirect(url_for('index'))
    
class SignUp(Resource):
    """
    Clase que maneja el registro de un nuevo usuario.

    """
    def post(self):
        """
        Método para registrar un nuevo usuario.

        Retorna
        -------
        dict
            Un diccionario con un mensaje de error si los datos son incorrectos o ya existen, 
            o un mensaje de éxito si el registro fue exitoso.
        
        Excepciones
        -----------
        400
            Si falta algún dato requerido o si el correo electrónico o el nombre de usuario ya están registrados.
        200
            Si el usuario fue registrado correctamente.
        """
        data = request.form
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

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

        return {'message': 'Usuario registrado'}, 200
    
    def get(self):
        response = make_response(render_template('signup.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class UserProfile(Resource):
    """
    Clase que maneja la visualización y actualización del perfil de un usuario.

    """
    @token_required(user_type='user')
    def get(self, current_user):
        """
        Método para obtener el perfil del usuario.

        Parámetros
        ----------
        current_user : str
            Nombre del usuario actual que está autenticado, extraído del token JWT.

        Retorna
        -------
        response : Response
            Respuesta con la plantilla HTML del perfil del usuario.
        """
        response = make_response(render_template('user_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response
    
class SeguirAPI(Resource):
    """
    Clase que maneja la acción de seguir a otro usuario.

    """
    @token_required(user_type='user')
    def post(self, current_user):
        """
        Método para seguir a un usuario.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        seguido_id : int
            El ID del usuario que se desea seguir.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de éxito y código de estado 201 si el seguimiento fue exitoso.
            En caso de error, devuelve un mensaje con código de estado 400 o 404 según corresponda.
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
        Método para dejar de seguir a un usuario.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        seguido_id : int
            El ID del usuario que se desea dejar de seguir.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de éxito y código de estado 201 si el seguimiento fue exitoso.
            En caso de error, devuelve un mensaje con código de estado 400 o 404 según corresponda.
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

class SeguirTitulo(Resource):
    """
    Clase que maneja la accion de seguir un titulo.
    """
    @token_required(user_type='user')
    def post(self, current_user, titulo_id):
        """
        Método para seguir un título.

        Parámetros
        -----------
        current_user : str
            El nombre de usuario del usuario autenticado, obtenido del token.
        titulo_id : int
            El ID del título que se desea seguir.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de éxito y código de estado 200 si el seguimiento fue exitoso.
            En caso de error, devuelve un mensaje con código de estado 400 o 404 según corresponda.
        """
        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()

        titulo = Titulo.query.filter_by(id=titulo_id).first()
        if not titulo:
            return {'message': 'Título no encontrado'}, 404
        
        seguimiento = Seguimiento.query.filter_by(usuario_id=usuario.id, titulo_id=titulo.id).first()

        if seguimiento:
            return {'message': 'Ya estás siguiendo este título'}, 400  
        
        nuevo_seguimiento = Seguimiento(
            usuario_id=usuario.id,
            estado=1,  # 1=activo, 0=terminado
            resenia_id=None,  
            cantidad_visto=0,  # Inicialmente 0
            titulo_id=titulo.id
        )

        db.session.add(nuevo_seguimiento)
        db.session.commit()

        return {'message': 'Título seguido con éxito'}, 200
    
    @token_required(user_type='user')
    def put(self, current_user, titulo_id):
        """
        Actualiza el estado y la cantidad vista de un seguimiento de título.

        Parámetros
        -----------
        current_user : str
            Nombre de usuario autenticado.
        titulo_id : int
            ID del título cuyo seguimiento se quiere actualizar.

        Retorna
        --------
        dict
            Mensaje de éxito o error con el código de estado correspondiente.
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

usuario_api.add_resource(Login, '/login')
usuario_api.add_resource(SignUp, '/signup')
usuario_api.add_resource(UserProfile, '/')
usuario_api.add_resource(SeguirAPI, '/follow',
                         '/follow/<int:seguido_id>')
#usuario_api.add_resource(SeguirTitulo, '/<str:current_user>/<int:titulo_id>')
#usuario_api.add_resource(ActualizarSeguimiento, '/<str:current_user>/<int:titulo_id>')

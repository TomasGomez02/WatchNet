from datetime import datetime, timezone
from flask import request, make_response, redirect, url_for, session, Blueprint
from flask_restful import Resource, Api
from flask.templating import render_template
from models.models import Comentario, Impresion, Relacion, Resenia, Seguimiento, Titulo, db, Usuario
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
        
        token = generate_token(login_info.nombre_usuario)
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
            return {'error': 'Email ya está registrado'}, 400

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
    @token_required
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
    
class CrearResenia(Resource):
    """
    Clase que maneja la creación de reseñas para un título específico.

    """
    @token_required
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
            return {'message': f'Contenido no encontrado'}, 404

        puntuacion = data['puntuacion']
        texto = data['texto']
     
        resenia = Resenia(
            usuario_id=usuario.id, 
            puntuacion=puntuacion,
            texto=texto,
            titulo_id=titulo.id, 
            fecha_publicacion= datetime.now(timezone.utc)
        )
        db.session.add(resenia)
        db.session.commit()

        return {'message': 'Reseña añadida con éxito'}, 200
    
class EliminarResenia(Resource):
    """
    Clase que maneja la eliminación de una reseña.

    """
    @token_required
    def delete(self, current_user, resenia_id):
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
        resenia = Resenia.query.filter_by(id=resenia_id).first()

        if not resenia:
            return {'message': 'Reseña no encontrada'}, 404

        usuario = Usuario.query.filter_by(nombre_usuario=current_user).first()
        if not usuario or resenia.usuario_id != usuario.id:
            return {'message': 'No tienes permiso para eliminar esta reseña'}, 403

        db.session.delete(resenia)
        db.session.commit()

        return {'message': 'Reseña eliminada con éxito'}, 200

class Comentar(Resource):
    """
    Clase que maneja la creación de comentarios sobre una reseña.
    """
    @token_required
    def post(self, current_user, resenia_id):
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

        texto = data['texto']
        if not texto:
            return {'message': 'El texto del comentario es obligatorio'}, 400

        resenia = Resenia.query.filter_by(id=resenia_id).first()
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
class EliminarComentario(Resource):
    """
    Clase que maneja la eliminación de un comentario.

    """
    @token_required
    def delete(self, current_user, comentario_id):
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

class PuntuarResenia(Resource):
    """
    Clase que maneja la acción de puntuar una reseña.

    """
    def post(self, current_user, resenia_id):
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

        resenia = Resenia.query.filter_by(id=resenia_id).first()
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
    
class EliminarPuntaje(Resource):
    """
    Clase que maneja la acción de eliminar un puntaje de una reseña.

    """
    @token_required
    def delete(self, current_user, resenia_id):
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

        resenia = Resenia.query.filter_by(id=resenia_id).first()
        if not resenia:
            return {'message': 'Reseña no encontrada'}, 404

        impresion = Impresion.query.filter_by(usuario_id=usuario.id, resenia_id=resenia.id).first()
        if not impresion:
            return {'message': 'No has puntuado esta reseña.'}, 404

        db.session.delete(impresion)
        db.session.commit()

        return {'message': 'Puntuación eliminada con éxito.'}, 200
    
class SeguirUsuario(Resource):
    """
    Clase que maneja la acción de seguir a otro usuario.

    """
    @token_required
    def post(self, current_user, seguido_id):
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
        seguidor = Usuario.query.filter_by(nombre_usuario=current_user).first()
        seguido = Usuario.query.filter_by(id=seguido_id).first()
        if not seguido:
            return {'message': 'El usuario que intentas seguir no existe'}, 404
        
        #Verifico que no se siga a si mismo
        if seguidor.id == seguido.id:
            return {'message': 'Operación no válida'}, 400

        #Verifico si ya se siguen
        relacion_existente = Relacion.query.filter_by(seguidor=seguidor.id, seguido=seguido.id).first()
        if relacion_existente:
            return {'message': 'Ya sigues a este usuario'}, 400

        nueva_relacion = Relacion(seguidor=seguidor.id, seguido=seguido.id)

        db.session.add(nueva_relacion)
        db.session.commit()

        return {'message': 'Ahora sigues a este usuario con éxito'}, 201
    
class DejarDeSeguir(Resource):
    """
    Clase que maneja la acción de dejar de seguir a otro usuario.

    """
    @token_required
    def post(self, current_user, seguido_id):
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
    @token_required
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
    
class ActualizarSeguimiento(Resource):
    """
    Clase que maneja la accion de actualizar el seguimiento de un titulo.

    """
    @token_required
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
        resenias = Resenia.query.filter_by(usuario_id=usuario_id).all()
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
usuario_api.add_resource(CrearResenia, '/<str:current_user>/titulos/<int:titulo_id>/crearResenia')
usuario_api.add_resource(EliminarResenia, '/<str:current_user>/resenias/<resenia_id>/eliminar')
usuario_api.add_resource(Comentar, '/<str:current_user>/<int:resenia_id>/agregarComentario')
usuario_api.add_resource(EliminarComentario, '/<str:current_user>/comentarios/<comentario_id>')
usuario_api.add_resource(PuntuarResenia, '/<str:current_user>/resenias/<resenia_id>/puntuar')
usuario_api.add_resource(EliminarResenia, '/<str:current_user>/resenias/<resenia_id>/eliminarPuntaje')
usuario_api.add_resource(SeguirUsuario, '/<str:current_user>/<str:seguido_id>')   #No se si estan bien pero algo asi serian
usuario_api.add_resource(DejarDeSeguir, '/<str:current_user>/<str:seguido_id>')
usuario_api.add_resource(SeguirTitulo, '/<str:current_user>/<int:titulo_id>')
usuario_api.add_resource(ActualizarSeguimiento, '/<str:current_user>/<int:titulo_id>')
usuario_api.add_resource(PerfilUsuario, '/<str:current_user>/info')

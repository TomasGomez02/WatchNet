from datetime import datetime, timezone
from flask import request, make_response, redirect, url_for, session, Blueprint
from flask_restful import Resource, Api
from flask.templating import render_template
from models.models import Comentario, Impresion, Relacion, Resenia, Seguimiento, Titulo, db, Usuario
from auth import generate_token, token_required

usuario_bp = Blueprint('usuario', __name__)
usuario_api = Api(usuario_bp)

class Login(Resource):
    def post(self):
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
        response = make_response(render_template('login.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
    def delete(self):
        session.pop('auth_token', None)
        return redirect(url_for('index'))
    
class SignUp(Resource):
    def post(self):
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
    @token_required
    def get(self, current_user):
        response = make_response(render_template('user_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response
    
class CrearResenia(Resource):
    @token_required
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
    @token_required
    def delete(self, current_user, resenia_id):
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
    @token_required
    def post(self, current_user, resenia_id):
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
    @token_required
    def delete(self, current_user, comentario_id):

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
    def post(self, current_user, resenia_id):
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
    @token_required
    def delete(self, current_user, resenia_id):

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
    @token_required
    def post(self, current_user, seguido_id):
        
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
    @token_required
    def post(self, current_user, seguido_id):
        
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
    @token_required
    def post(self, current_user, titulo_id):

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
    @token_required
    def put(self, current_user, titulo_id):

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

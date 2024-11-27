from typing import Type

from flask import Blueprint, request, make_response, redirect, url_for, session
from flask_restful import Api, Resource
from flask.templating import render_template
from models.models import Titulo, db, Productora, Usuario, Entidad
from auth import generate_token, token_required

productora_bp = Blueprint('productora', __name__)
productora_api = Api(productora_bp)

class Login(Resource):
    """
    Clase que maneja las operaciones de inicio de sesión para una productora.

    """
    def post(self):
        """
        Método para iniciar sesión.

        Retorna
        -------
        dict
            Un diccionario con un mensaje de error si los datos son incorrectos o faltan, o una redirección 
            a la página de perfil de la productora si el inicio de sesión es exitoso.
        
        Excepciones
        -----------
        400
            Si el correo electrónico o la contraseña están vacíos o son incorrectos.
        """
        data = request.form
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Falta data'}, 400

        login_info = Productora.query.filter_by(email=email).first()

        if not login_info or not login_info.check_password(password):
            return {'error': 'Login info incorrect.'}, 400
        
        token = generate_token(login_info.nombre_usuario)
        session['auth_token'] = token

        return redirect(url_for('productora.productoraprofile', current_user=login_info.nombre_usuario))
    
    def get(self):
        """
        Método para obtener la página de inicio de sesión.

        Retorna
        -------
        Response
            Una respuesta que contiene el HTML de la página de inicio de sesión.
        """
        response = make_response(render_template('login_prod.html'))
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
    Clase que maneja el registro de una nueva productora.

    """
    def post(self):
        """
        Método para registrar una nueva productora.

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

        if Productora.query.filter_by(email=email).first():
            return {'error': 'Email ya está registrado'}, 400

        if Productora.query.filter_by(nombre_usuario=username).first():
            return {'error': 'Username ya existe'}, 400

        new_login = Productora(nombre_usuario=username, email=email)
        new_login.set_password(password)

        db.session.add(new_login)
        db.session.commit()

        return {'message': 'Usuario registrado'}, 200
    
    def get(self):
        """
        Método para obtener la página de registro.

        Retorna
        -------
        Response
            Una respuesta que contiene el HTML de la página de registro.
        """
        response = make_response(render_template('signup_prod.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class ProductoraProfile(Resource):
    """
    Clase que maneja la visualización y actualización del perfil de una productora.

    """
    @token_required
    def get(self, current_user):
        """
        Método para obtener el perfil de la productora.

        Parámetros
        ----------
        current_user : str
            Nombre del usuario actual que está autenticado, extraído del token JWT.

        Retorna
        -------
        response : Response
            Respuesta con la plantilla HTML del perfil de la productora.
        """
        response = make_response(render_template('productora_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response
    
    def post(self):
        """
        Método para manejar una solicitud POST en el perfil de la productora.

        Retorna
        -------
        dict
            Un diccionario con un mensaje de confirmación y el código de estado HTTP 201.
        """
        return {'message': 'hi'}, 201
    
class NuevoTitulo(Resource):
    """
    Clase que maneja la creación de un nuevo título por parte de una productora.

    """
    @token_required
    def post(self, current_user):
        """
        Método para crear un nuevo título en la base de datos.

        Parámetros
        -----------
        current_user : str
            Nombre del usuario autenticado, extraído del token JWT.

        Retorna
        --------
        dict
            Un diccionario con un mensaje de confirmación y el código de estado HTTP 200.
        """
        data = request.get_json()

        productora = Productora.query.filter_by(nombre_usuario=current_user).first()

        fecha_inicio = data['fecha_inicio']
        fecha_fin = data['fecha_fin']
        titulo = data['Titulo']
        #duracion = data['duracion']
        tipo = data['tipo']

        titulo = Titulo(fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        titulo= titulo, 
                        tipo =tipo,
                        productora_id= productora.id)
        
        db.session.add(titulo)
        db.session.commit()

        return {'message': 'Contenido añadido'}, 200
    
# class NuevoEpisodio(Resource):
#     @token_required
#     def post(self, current_user):
#         data = request.get_json()

#         productora = Productora.query.filter_by(nombre_usuario=current_user).first()

#         # Obtener el nombre de la serie y crear el título
#         nombre = data['nombre_serie']
#         titulo = Titulo(nombre=nombre, productora_id=productora.id)
#         db.session.add(titulo)
#         db.session.flush()  

#         # Obtener las fechas de inicio y fin de la serie
#         fecha_inicio = data['fecha_inicio']
#         fecha_fin = data['fecha_fin']

#         # Obtener los IDs de episodios desde el JSON
#         episodios = data['episodios']  # Lista de episodios (IDs de episodios)

#         # Verificar que todos los episodios existan y sean tipo=EPISODIO (con valor 2)
#         for episodio_id in episodios:
#             episodio = Contenido.query.filter_by(id=episodio_id).first()
#             if not episodio:
#                 return {'message': f'Episodio con ID {episodio_id} no existe.'}, 400
#             if episodio.tipo != TipoContenido.EPISODIO.value:  # Verificar si el tipo es EPISODIO
#                 return {'message': f'Episodio con ID {episodio_id} no es de tipo EPISODIO.'}, 400

#         # Crear la serie
#         serie = Serie(titulo_id=titulo.id, 
#                       fecha_inicio=fecha_inicio,
#                       fecha_fin=fecha_fin,
#                       episodios=episodios)
#         db.session.add(serie)
#         db.session.flush()  # Para obtener el id de la serie recién creada

#         # Agregar la serie a la lista de series de la productora
#         if productora.series_id:
#             productora.series_id.append(serie.id)
#         else:
#             productora.series_id = [serie.id]

#         db.session.commit()

#         return {'message': 'Serie añadida con éxito'}, 201

    
productora_api.add_resource(Login, '/login')
productora_api.add_resource(SignUp, '/signup')
productora_api.add_resource(ProductoraProfile, '/')
productora_api.add_resource(NuevoTitulo, '/<str:current_user>/agregarTitulo')
# productora_api.add_resource(NuevoEpisodio, '/<str:current_user>/agregarEpisodio')
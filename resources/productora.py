from flask import Blueprint, request, make_response, redirect, url_for, session
from flask_restful import Api, Resource
from flask.templating import render_template
from models.models import Titulo, db, Productora
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
        
        token = generate_token(login_info.nombre_usuario, 'producer')
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
            return {'error': 'Email ya esta registrado'}, 400

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
    @token_required(user_type='producer')
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
    
productora_api.add_resource(Login, '/login')
productora_api.add_resource(SignUp, '/signup')
productora_api.add_resource(ProductoraProfile, '/')
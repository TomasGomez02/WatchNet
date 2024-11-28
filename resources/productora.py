from flask import Blueprint, request, make_response, redirect, url_for, session
from flask_restful import Api, Resource
from flask.templating import render_template
from models.models import Titulo, db, Productora
from auth import generate_token, token_required

productora_bp = Blueprint('productora', __name__)
productora_api = Api(productora_bp)

class Login(Resource):
    """
    Handles login operations for producers.
    """
    def post(self):
        """
        Log in a producer.
        ---
        tags:
          - Producers
        summary: Log in a producer
        description: Authenticate a producer using their email and password.
        requestBody:
          required: true
          content:
            application/x-www-form-urlencoded:
              schema:
                type: object
                properties:
                  email:
                    type: string
                    example: producer@example.com
                  password:
                    type: string
                    example: securepassword
        responses:
          302:
            description: Redirect to the producer profile page after successful login.
          400:
            description: Missing or incorrect login data.
          500:
            description: Server error.
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
        Display the login page.
        ---
        tags:
          - Producers
        summary: Display the login page
        description: Returns the HTML template for the producer login page.
        responses:
          200:
            description: HTML content of the login page.
            content:
              text/html:
                schema:
                  type: string
          500:
            description: Server error.
        """
        response = make_response(render_template('login_prod.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
    def delete(self):
        """
        Log out a producer.
        ---
        tags:
          - Producers
        summary: Log out a producer
        description: Logs out the producer and clears their session token.
        responses:
          302:
            description: Redirect to the home page after logout.
          500:
            description: Server error.
        """
        session.pop('auth_token', None)
        return redirect(url_for('index'))
    
class SignUp(Resource):
    """
    Handles registration of a new producer.
    """
    def post(self):
        """
        Register a new producer.
        ---
        tags:
          - Producers
        summary: Register a new producer
        description: Register a new producer with email, username, and password.
        requestBody:
          required: true
          content:
            application/x-www-form-urlencoded:
              schema:
                type: object
                properties:
                  email:
                    type: string
                    example: producer@example.com
                  username:
                    type: string
                    example: newproducer
                  password:
                    type: string
                    example: securepassword
        responses:
          200:
            description: Producer successfully registered.
          400:
            description: Missing data or duplicate email/username.
          500:
            description: Server error.
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
        Display the signup page.
        ---
        tags:
          - Producers
        summary: Display the signup page
        description: Returns the HTML template for the producer signup page.
        responses:
          200:
            description: HTML content of the signup page.
            content:
              text/html:
                schema:
                  type: string
          500:
            description: Server error.
        """
        response = make_response(render_template('signup_prod.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class ProductoraProfile(Resource):
    """
    Handles the producer's profile view and updates.
    """
    @token_required(user_type='producer')
    def get(self, current_user):
        """
        Get the producer profile page.
        ---
        tags:
          - Producers
        summary: Get the producer profile
        description: Returns the HTML template for the producer profile page.
        parameters:
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for producer authentication.
        responses:
          200:
            description: HTML content of the producer profile page.
            content:
              text/html:
                schema:
                  type: string
          401:
            description: Unauthorized access.
          500:
            description: Server error.
        """
        response = make_response(render_template('productora_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response
    
    def post(self):
        """
        Update the producer profile.
        ---
        tags:
          - Producers
        summary: Update the producer profile
        description: Handles updates to the producer's profile data.
        responses:
          201:
            description: Profile successfully updated.
          500:
            description: Server error.
        """
        return {'message': 'hi'}, 201
    
productora_api.add_resource(Login, '/login')
productora_api.add_resource(SignUp, '/signup')
productora_api.add_resource(ProductoraProfile, '/')
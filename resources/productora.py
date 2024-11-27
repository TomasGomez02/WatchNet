from flask import Blueprint, request, make_response, redirect, url_for, session
from flask_restful import Api, Resource
from flask.templating import render_template
from models.models import Titulo, db, Productora
from auth import generate_token, token_required

productora_bp = Blueprint('productora', __name__)
productora_api = Api(productora_bp)

class Login(Resource):
    def post(self):
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
        response = make_response(render_template('login_prod.html'))
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
        response = make_response(render_template('signup_prod.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class ProductoraProfile(Resource):
    @token_required(user_type='producer')
    def get(self, current_user):
        response = make_response(render_template('productora_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response
    
    def post(self):
        return {'message': 'hi'}, 201
    
productora_api.add_resource(Login, '/login')
productora_api.add_resource(SignUp, '/signup')
productora_api.add_resource(ProductoraProfile, '/')
from flask import request, make_response, redirect, url_for, session, Blueprint
from flask_restful import Resource, Api
from flask.templating import render_template
from models.models import db, Usuario
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
    @token_required
    def get(self, current_user):
        response = make_response(render_template('user_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response

usuario_api.add_resource(Login, '/login')
usuario_api.add_resource(SignUp, '/signup')
usuario_api.add_resource(UserProfile, '/')
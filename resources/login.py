from flask import request, make_response, redirect, url_for, session
from flask_restful import Resource
from flask.templating import render_template
from models.models import db, InfoLogin, Productora, Usuario
from auth import generate_token

class Login(Resource):
    def post(self):
        data = request.form
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Falta data'}, 400

        login_info = InfoLogin.query.filter_by(email=email).first()

        if not login_info or not login_info.check_password(password):
            return {'error': 'Login info incorrect.'}, 400
        
        token = generate_token(login_info.nombre_usuario)
        session['auth_token'] = token
        usuario = Usuario.query.filter_by(info_login_id=login_info.id).first()

        if usuario:
            return redirect(url_for('userprofile', current_user=login_info.nombre_usuario))
        else:
            return redirect(url_for('productoraprofile', current_user=login_info.nombre_usuario))
    
    def get(self):
        response = make_response(render_template('login.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class SignUp(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = data['password']

        if not username or not email or not password:
            return {'error': 'Falta data'}, 400

        if InfoLogin.query.filter_by(email=email).first():
            return {'error': 'Email ya está registrado'}, 400

        if InfoLogin.query.filter_by(nombre_usuario=username).first():
            return {'error': 'Username ya existe'}, 400

        new_login = InfoLogin(nombre_usuario=username, email=email)
        new_login.set_password(password)
        db.session.add(new_login)

        new_user = Usuario(info_login_id=InfoLogin.query.filter_by(email=email).first().id)
        db.session.add(new_user)

        db.session.commit()

        return {'message': 'Usuario registrado'}, 201
    
    def get(self):
        response = make_response(render_template('signup.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class Productora_SignUp(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = data['password']

        if not username or not email or not password:
            return {'error': 'Falta data'}, 400

        if InfoLogin.query.filter_by(email=email).first():
            return {'error': 'Email ya está registrado'}, 400

        if InfoLogin.query.filter_by(nombre_usuario=username).first():
            return {'error': 'Username ya existe'}, 400

        new_login = InfoLogin(nombre_usuario=username, email=email)
        new_login.set_password(password)
        db.session.add(new_login)

        new_produc = Productora(info_login_id=InfoLogin.query.filter_by(email=email).first().id)
        db.session.add(new_produc)

        db.session.commit()

        return {'message': 'Productora registrada'}, 201
    
    def get(self):
        response = make_response(render_template('prod_signup.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class Logout(Resource):
    def post(self):
        session.pop('auth_token', None)
        return redirect(url_for('index'))
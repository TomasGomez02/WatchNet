from flask_restful import Resource
from flask import request, make_response
from flask.templating import render_template
from models.info_login import InfoLogin
from models.usuario import Usuario
from app import db

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']

        if not email or not password:
            return {'error': 'Falta data'}, 400

        login_info = InfoLogin.query.filter_by(email=email).first()

        if not login_info or not login_info.check_password(password):
            return {'error': 'Login info incorrect.'}, 400
        
        return {'message': 'Login successful', 'name': login_info.nombre_usuario}, 201
    
    def get(self):
        response = make_response(render_template('login.html'))
        response.headers["Content-Type"] = "text/html"
        return response
from flask_restful import Resource
from flask import request, make_response
from flask.templating import render_template
from models.info_login import InfoLogin
from models.productora import Productora
from app import db

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
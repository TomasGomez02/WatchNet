from flask import request, make_response, redirect, url_for, jsonify
from flask_restful import Resource
from flask.templating import render_template
from models.info_login import InfoLogin
from models.usuario import Usuario
from app import db, generate_token, api

class Login(Resource):
    @api.representation('text/plain')
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']

        if not email or not password:
            return {'error': 'Falta data'}, 400

        login_info = InfoLogin.query.filter_by(email=email).first()

        if not login_info or not login_info.check_password(password):
            return {'error': 'Login info incorrect.'}, 400
        
        token = generate_token(login_info.nombre_usuario)
        usuario = Usuario.query.filter_by(info_login_id=login_info.id).first()

        response = jsonify({"redirect_url": url_for('userprofile', current_user=login_info.nombre_usuario)})
        response.status = 302
        response.set_cookie('auth_token', token)
        #response.headers["Content-Type"] = "text/html"
        print('?')
        return response
    
    def get(self):
        response = make_response(render_template('login.html'))
        response.headers["Content-Type"] = "text/html"
        return response
from flask_restful import Resource
from flask import request
from models.user import User
from app import db

class Login(Resource):
    def post(self):
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        nuevo_usuario = User(name=name, email=email)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return {}
    
    def get(self):
        email = request.args.get('email')
        user = User.query.filter_by(email=email).first()
        return {'name': user.name}
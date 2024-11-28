from flask import request, make_response, redirect, url_for, session, Blueprint, current_app
from flask_restful import Resource, Api
from flask.templating import render_template

producer_bp = Blueprint('producer', __name__)
producer_api = Api(producer_bp)

class Login(Resource):
    def post(self):
        data = request.form
        email = data.get('email')
        password = data.get('password')

        parsed_data = {
            'email': email,
            'password': password
        }

        with current_app.test_client() as client:
            response = client.get('/api/user', json=parsed_data)

            if response.status_code == 200:
                return redirect(url_for('usuario.home'))
            
            else:
                return request.data

    def get(self):
        response = make_response(render_template('login.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class Signup(Resource):
    def post(self):
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        parsed_data = {
            'username': username,
            'email': email,
            'password': password
        }

        with current_app.test_client() as client:
            response = client.post('/api/user', json=parsed_data)

            if response.status_code == 200:
                return redirect(url_for('usuario.home'))
            
            else:
                return request.data

    def get(self):
        response = make_response(render_template('signup.html'))
        response.headers["Content-Type"] = "text/html"
        return response

class Logout(Resource):
    def post(self):
        session.pop('auth_token', None)
        return redirect(url_for('index'))
    
producer_api.add_resource(Login, '/login')
producer_api.add_resource(Signup, '/signup')
producer_api.add_resource(Logout, '/logout')
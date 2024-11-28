from flask import request, make_response, redirect, url_for, session, Blueprint, current_app
from flask_restful import Resource, Api
from flask.templating import render_template

from auth import token_required

usuario_bp = Blueprint('usuario', __name__)
usuario_api = Api(usuario_bp)

class Login(Resource):
    def post(self):
        data = request.form
        email = str(data.get('email'))
        password = str(data.get('password'))

        parsed_data = {
            'email': email,
            'password': password
        }

        with current_app.test_client() as client:
            response = client.get('/api/user/', json=parsed_data)

            if response.status_code == 200:
                print('success')
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
    
class Home(Resource):
    """
    Manage user profile.
    """
    @token_required(user_type='user')
    def get(self, current_user):
        """
        Get the user profile.
        ---
        tags:
          - Profile
        summary: Get user profile
        description: Fetches the profile information for the authenticated user.
        parameters:
          - in: header
            name: Authorization
            required: true
            schema:
              type: string
            description: Bearer token for user authentication.
        responses:
          200:
            description: HTML content of the user profile page.
            content:
              text/html:
                schema:
                  type: string
        """
        response = make_response(render_template('user_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response


usuario_api.add_resource(Login, '/login')
usuario_api.add_resource(Signup, '/signup')
usuario_api.add_resource(Logout, '/logout')
usuario_api.add_resource(Home, '/home')
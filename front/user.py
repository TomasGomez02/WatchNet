from flask import request, make_response, redirect, url_for, session, Blueprint, current_app
from flask_restful import Resource, Api
from flask.templating import render_template

from resources.usuario import UserAPI
from auth import token_required

usuario_bp = Blueprint('usuario', __name__)
usuario_api = Api(usuario_bp)

class Login(Resource):
    def post(self):
        data = request.get_json()
        res = UserAPI()

        with current_app.test_request_context(
            '/api/user/', json=data, method='GET'
        ) as client:
            response = res.get()
            token = session['auth_token']

        session['auth_token'] = token

        if response[1] == 200:
            return redirect(url_for('usuario.home'))
        
        else:
            return response

    def get(self):
        response = make_response(render_template('login.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class Signup(Resource):
    def post(self):
        data = request.get_json()
        res = UserAPI()

        with current_app.test_request_context(
            '/api/user/', json=data, method='POST'
        ) as client:
            response = res.post()
            token = session['auth_token']

        session['auth_token'] = token

        if response[1] == 200:
            return redirect(url_for('usuario.home'))
        
        else:
            return response


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
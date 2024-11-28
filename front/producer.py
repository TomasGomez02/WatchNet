from flask import request, make_response, redirect, url_for, session, Blueprint, current_app
from flask_restful import Resource, Api
from flask.templating import render_template

from auth import token_required
from resources.productora import ProducerAPI

producer_bp = Blueprint('producer', __name__)
producer_api = Api(producer_bp)

class Login(Resource):
    def post(self):
        data = request.get_json()
        res = ProducerAPI()

        with current_app.test_request_context(
            '/api/producer/', json=data, method='GET'
        ) as client:
            response = res.get()
            token = session['auth_token']

        session['auth_token'] = token

        if response[1] == 200:
            return redirect(url_for('producer.home'))
        
        else:
            return response

    def get(self):
        response = make_response(render_template('login.html'))
        response.headers["Content-Type"] = "text/html"
        return response

    def get(self):
        response = make_response(render_template('login_prod.html'))
        response.headers["Content-Type"] = "text/html"
        return response
    
class Signup(Resource):
    def post(self):
        data = request.get_json()
        res = ProducerAPI()

        with current_app.test_request_context(
            '/api/producer/', json=data, method='POST'
        ) as client:
            response = res.post()
            token = session['auth_token']

        session['auth_token'] = token

        if response[1] == 200:
            return redirect(url_for('producer.home'))
        
        else:
            return response

    def get(self):
        response = make_response(render_template('signup_prod.html'))
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
    @token_required(user_type='producer')
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
        response = make_response(render_template('productora_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response

    
producer_api.add_resource(Login, '/login')
producer_api.add_resource(Signup, '/signup')
producer_api.add_resource(Logout, '/logout')
producer_api.add_resource(Home, '/home')
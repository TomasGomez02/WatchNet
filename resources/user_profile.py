from flask_restful import Resource
from flask import make_response
from flask.templating import render_template
from auth import token_required

class UserProfile(Resource):
    @token_required
    def get(self, current_user):
        response = make_response(render_template('user_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response
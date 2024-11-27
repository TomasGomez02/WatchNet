from flask_restful import Resource
from flask import request, make_response
from flask.templating import render_template
from auth import token_required

class ProductoraProfile(Resource):
    @token_required
    def get(self, current_user):
        print('!!')
        response = make_response(render_template('productora_profile.html', current_user=current_user))
        response.headers["Content-Type"] = "text/html"
        return response
    
    def post(self):
        return {'message': 'hi'}, 201
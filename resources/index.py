from flask import request, make_response, redirect, url_for, session
from flask_restful import Resource
from flask.templating import render_template


class Index(Resource):
    def get(self):
        response = make_response(render_template('index.html'))
        response.headers["Content-Type"] = "text/html"
        return response
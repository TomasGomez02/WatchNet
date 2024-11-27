from flask import request, make_response, redirect, url_for, session
from flask_restful import Resource
from flask.templating import render_template


class Index(Resource):
    def get(self):
        return redirect(url_for('login'))
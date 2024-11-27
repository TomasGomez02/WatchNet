from flask_restful import Resource
from flask import request, make_response
from flask.templating import render_template
from auth import token_required
from models.models import db, Usuario, Productora, Titulo


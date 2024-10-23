from flask_restful import Resource
from models.user import User
from app import db

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
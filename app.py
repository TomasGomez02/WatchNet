from flask import Flask, request, jsonify, make_response
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import datetime, timedelta, timezone
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE, TOKEN_KEY

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_DATABASE}.{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = TOKEN_KEY

db = SQLAlchemy(app)

def generate_token(username):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=15) 
    token = jwt.encode({
            'username': username,
            'exp': expiration
        }, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Decorador para proteger rutas
def token_required(f):
    def decorated(*args, **kwargs):
        token = request.cookies.get('auth_token')
        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)
        try:
            print('a')
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            print('ab')
            user = data['username']
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({'message': 'Token has expired!'}), 403)
        except jwt.InvalidTokenError:
            return make_response(jsonify({'message': 'Invalid token!'}), 403)
        return f(*args, user)
    return decorated
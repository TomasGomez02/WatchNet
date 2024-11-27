from datetime import datetime, timedelta, timezone
from typing import Literal

from flask import jsonify, make_response, session
import jwt
from config import TOKEN_KEY

def generate_token(username, user_type: Literal['user', 'producer']):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=15) 
    token = jwt.encode({
            'username': username,
            'user_type': user_type,
            'exp': expiration
        }, TOKEN_KEY, algorithm='HS256')
    return token

# Decorador para proteger rutas
def token_required(user_type: Literal['user', 'producer']):
    def decorator(func):
        def decorated(*args, **kwargs):
            if 'auth_token' not in session:
                return make_response(jsonify({'message': 'Token is missing!'}), 401)
            token = session['auth_token']
            try:
                data = jwt.decode(token, TOKEN_KEY, algorithms=['HS256'])
                if data['user_type'] != user_type:
                    return make_response(jsonify({'message': 'Incorrect role'}), 401)
                user = data['username']
            except jwt.ExpiredSignatureError:
                return make_response(jsonify({'message': 'Token has expired!'}), 403)
            except jwt.InvalidTokenError:
                return make_response(jsonify({'message': 'Invalid token!'}), 403)
            return func(*args, current_user=user, **kwargs)
        return decorated
    return decorator
from datetime import datetime, timedelta, timezone

from flask import jsonify, make_response, session
import jwt
from config import TOKEN_KEY

def generate_token(username):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=15) 
    token = jwt.encode({
            'username': username,
            'exp': expiration
        }, TOKEN_KEY, algorithm='HS256')
    return token

# Decorador para proteger rutas
def token_required(f):
    def decorated(*args, **kwargs):
        token = session['auth_token']
        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)
        try:
            data = jwt.decode(token, TOKEN_KEY, algorithms=['HS256'])
            user = data['username']
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({'message': 'Token has expired!'}), 403)
        except jwt.InvalidTokenError:
            return make_response(jsonify({'message': 'Invalid token!'}), 403)
        return f(*args, current_user=user, **kwargs)
    return decorated
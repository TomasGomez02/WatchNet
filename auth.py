from datetime import datetime, timedelta, timezone
from typing import Literal
import os

from flask import jsonify, make_response, session
import jwt
try:
    from config import TOKEN_KEY
except ModuleNotFoundError:
    TOKEN_KEY = os.getenv('TOKEN_KEY', "please-set-up-a-proper-key")

def generate_token(username, user_type: Literal['user', 'producer']):
    """
    Generate a JWT token for a given user.
    ---
    tags:
      - Authentication
    summary: Generate JWT token
    description: Creates a JSON Web Token (JWT) for a user, signed using the HS256 algorithm, with an expiration time of 15 minutes. The token contains the username, user type, and expiration date.
    parameters:
      - in: query
        name: username
        required: true
        schema:
          type: string
        description: The username for which the token is being generated.
      - in: query
        name: user_type
        required: true
        schema:
          type: string
          enum: [user, producer]
        description: The type of user (either 'user' or 'producer').
    responses:
      200:
        description: JWT token generated successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
                  description: The generated JWT token.
      500:
        description: An error occurred during token generation.
    """
    expiration = datetime.now(timezone.utc) + timedelta(minutes=30) 
    token = jwt.encode({
            'username': username,
            'user_type': user_type,
            'exp': expiration
        }, TOKEN_KEY, algorithm='HS256')
    return token

# Decorador para proteger rutas
def token_required(user_type: Literal['user', 'producer']):
    """
    Decorator to protect routes requiring JWT authentication with role validation.
    ---
    tags:
      - Authentication
    summary: Protect route with JWT authentication and user role validation
    description: Ensures that the route is protected by checking that a valid JWT token is present in the session. The token is verified for the correct user type (either 'user' or 'producer'). If the token is missing, expired, invalid, or the role does not match, an appropriate error is returned. If the token is valid and the role is correct, the original function is executed, passing the username from the token as an argument.
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
        description: Bearer token required for authentication.
    responses:
      401:
        description: Token is missing or the user role is incorrect.
      403:
        description: Token has expired or is invalid.
      200:
        description: The original function is executed after successful token validation and user role check.
    """
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

from datetime import datetime, timedelta, timezone
from typing import Literal

from flask import jsonify, make_response, session
import jwt
from config import TOKEN_KEY

def generate_token(username, user_type: Literal['user', 'producer']):
    """
    Genera un token JWT para un usuario dado.

    El token tiene un tiempo de expiración de 15 minutos desde el momento en que se genera. 
    Se utiliza el algoritmo HS256 para firmar el token, y el token contiene el nombre de usuario
    y la fecha de expiración.

    Parámetros
    ----------
    username : str
        El nombre de usuario para el cual se genera el token.

    Retorna
    -------
    str
        Un token JWT que incluye el nombre de usuario y la fecha de expiración.
    
    Excepciones
    ------
    Exception
        Si ocurre un error durante la creación del token, se lanzará una excepción.
    """
    expiration = datetime.now(timezone.utc) + timedelta(minutes=15) 
    token = jwt.encode({
            'username': username,
            'user_type': user_type,
            'exp': expiration
        }, TOKEN_KEY, algorithm='HS256')
    return token

# Decorador para proteger rutas
def token_required(user_type: Literal['user', 'producer']):
"""
    Decorador para proteger las rutas que requieren autenticación con token JWT.

    Este decorador asegura que la ruta esté protegida, verificando que el token JWT esté presente
    en la sesión y que sea válido. Si el token no está presente, ha expirado o es inválido, 
    se devuelve un error correspondiente. Si el token es válido, se ejecuta la función original
    pasando el nombre de usuario del token como argumento.

    Parámetros
    ----------
    f : function
        La función de vista o ruta a la que se aplicará el decorador.

    Retorna
    -------
    function
        La función decorada que realiza la validación del token antes de ejecutar la función original.
    
    Excepciones
    ------
    UnauthorizedError
        Si el token está ausente o es inválido, se retorna un mensaje de error con el código 401 o 403.
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

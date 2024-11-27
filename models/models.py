from abc import ABC
from datetime import date
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Serializable:
    def serialize(self):
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if type(value) == date:
                value = value.isoformat()
            elif type(value) == TipoTitulo:
                value = value.value
            data[column.name] = value
        return data

class Comentario(db.Model, Serializable):
    """
    Modelo que representa los comentarios realizados por usuarios en reseñas.

    ...

    Atributos
    ----------
    id : int
        ID único del comentario.
    texto : str
        Contenido del comentario.
    usuario_id : int
        ID del usuario que hizo el comentario.
    resenia_id : int
        ID de la reseña asociada al comentario.
    fecha_publicacion : date
        Fecha en la que se publicó el comentario.
    """
    __tablename__= 'Comentarios'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)

class Episodio(db.Model, Serializable):
    """
    Modelo que representa un episodio de una serie.

    ...

    Atributos
    ----------
    id : int
        ID único del episodio.
    titulo : str
        Título del episodio.
    duracion : int
        Duración del episodio en minutos.
    orden : int
        Orden del episodio dentro de la serie.
    fecha_emision : date
        Fecha de emisión del episodio.
    titulo_id : int
        ID del título o serie al que pertenece el episodio.
    """
    __tablename__ = 'Episodios'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.Text, nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
    orden = db.Column(db.Integer, nullable=False)
    fecha_emision = db.Column(db.Date, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)

class Impresion(db.Model, Serializable):
    """
    Clase utilizada para representar una impresión (like o dislike) en una reseña.

    ...

    Atributos
    ----------
    id : int
        ID único de la impresión.
    usuario_id : int
        ID del usuario que realiza la impresión.
    resenia_id : int
        ID de la reseña a la que se asocia la impresión.
    valor : int
        Valor de la impresión (1 representa un 'like' y -1 un 'dislike')
    """

    __tablename__ = 'Impresiones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Integer, nullable=False)


class Entidad(db.Model, UserMixin, Serializable):
    """
    Clase base abstracta utilizada para definir atributos comunes entre usuarios y productoras.

    ...

    Atributos
    ----------
    id : int
        ID único de la entidad.
    nombre_usuario : str
        Nombre de la entidad.
    email : str
        Correo electrónico de la entidad.
    contraseña : str
        Contraseña encriptada de la entidad.
    """
    __abstract__ = True  

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    contraseña = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str):
        """
        Encripta y almacena la contraseña del usuario.

        Parámetros
        ----------
        password : str
            Contraseña.
        """
        self.contraseña = generate_password_hash(password)

    def check_password(self, password: str):
        """
        Verifica si la contraseña proporcionada coincide con la almacenada.

        Parámetros
        ----------
        password : str
            Contraseña a verificar.

        Retorna
        -------
        bool
            True si la contraseña coincide, False en caso contrario.
        """
        return check_password_hash(self.contraseña, password)

class Productora(Entidad):
    """
    Clase utilizada para representar una Productora.

    Hereda de la clase Entidad.
    """
    __tablename__ = 'Productoras'

class Usuario(Entidad):
    """
    Clase utilizada para representar un Usuario.

    Hereda de la clase Entidad.
    """
    __tablename__ = 'Usuarios'

class Reseña(db.Model, Serializable):
    """
    Modelo que representa una reseña realizada por un usuario.

    ...

    Atributos
    ----------
    id : int
        ID único de la reseña.
    puntuacion : int
        Puntuación otorgada en la reseña.
    texto : str
        Contenido de la reseña.
    usuario_id : int
        ID del usuario que realizó la reseña.
    titulo_id : int
        ID del título reseñado.
    fecha_publicacion : date
        Fecha en que se publicó la reseña.
    """
    __tablename__ = 'Reseñas'
    id = db.Column(db.Integer, primary_key=True)
    puntuacion = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)

class Seguimiento(db.Model, Serializable):
    """
    Modelo que representa el seguimiento de un usuario a un título.

    Almacena información sobre el progreso de un usuario en relación con
    un título que está siguiendo, incluyendo el estado del seguimiento, la cantidad
    de episodios o capítulos vistos, y la reseña asociada.

    ...

    Atributos
    ----------
    id : int
        ID único del seguimiento.
    usuario_id : int
        ID del usuario que está siguiendo el título.
    estado : int
        Estado del seguimiento.
    resenia_id : int
        ID de la reseña asociada al seguimiento.
    cantidad_visto : int
        Cantidad de episodios vistos hasta el momento.
    titulo_id : int
        ID del título que el usuario está siguiendo.
    """

    __tablename__ = 'Seguimientos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    cantidad_visto = db.Column(db.Integer, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)

class TipoTitulo(Enum):
    PELICULA = 'PELICULA'
    SERIE = 'SERIE'

    def __str__(self):
        return self.value

class Titulo(db.Model, Serializable):
    """
    Modelo que representa un título en la base de datos.

    ...

    Atributos
    ----------
    id : int
        ID único del título.
    productora_id : int
        ID de la productora asociada al título.
    fecha_inicio : date
        Fecha en la que comenzó la emisión del título.
    fecha_fin : date
        Fecha en la que finalizó la emisión del título.
    titulo : str
        El nombre del título.
    tipo : bool
        Tipo de título: 1 si es una serie, 0 si es una película.
    """
    __tablename__ = 'Titulos'
    id = db.Column(db.Integer, primary_key=True)
    productora_id = db.Column(db.Integer, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    titulo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.Enum(TipoTitulo), nullable=False)
    
class Relacion(db.Model, Serializable):
    """
    Modelo que representa la relación de seguimiento entre dos usuarios.

    ...

    Atributos
    ----------
    seguidor : int
        ID del usuario que sigue a otro usuario.
    seguido : int
        ID del usuario que es seguido por otro usuario.
    """

    __tablename__ = 'Relaciones'
    seguidor = db.Column(db.Integer, primary_key=True)
    seguido = db.Column(db.Integer, primary_key=True)

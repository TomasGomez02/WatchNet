from abc import ABC
from datetime import date
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class DataBase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataBase, cls).__new__(cls, *args, **kwargs)
            cls._instance._db = SQLAlchemy()
        return cls._instance

    @property
    def db(self):
        return self._instance._db

database = DataBase()
db = database.db

class Serializable:
    """
    Class used to represent an entity that can be serialized into a dictionary.
    ---
    tags:
    - Serialization
    summary: Represents a serializable entity that converts its attributes into a dictionary.
    description: This class provides a method to serialize an object by converting its attributes into a dictionary format. It handles special cases for date and `TipoTitulo` types, converting them to appropriate formats.
    """

    def serialize(self):
        """
        Converts the object's attributes into a dictionary, with special handling for `date` and `TipoTitulo` types.
        ---
        tags:
        - Serialization
        summary: Serializes the object's attributes into a dictionary format.
        description: This method iterates over all columns of the object and converts their values into a dictionary. Special handling is applied to `date` types, converting them to ISO 8601 format, and `TipoTitulo` types, converting them to their corresponding string values.

        Parameters:
        -----------
        None

        Returns:
        --------
        dict
            A dictionary where the keys are the attribute names and the values are the corresponding attribute values, with special formatting for `date` and `TipoTitulo`.
        """
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if type(value) == date:
                value = value.isoformat()
            elif type(value) == TipoTitulo or type(value) == EstadoTitulo:
                value = value.value
            data[column.name] = value
        return data

class Comentario(db.Model, Serializable):
    """
    Model representing comments made by users on reviews.
    ---
    tags:
      - Comments
    summary: Represents user comments on reviews
    description: This model stores information about user comments associated with reviews. Each comment is linked to a specific user and review, with details such as the comment content, publication date, and user information.

    Attributes:
    -----------
    id : int
        The unique identifier of the comment.
    texto : str
        The content of the comment.
    usuario_id : int
        The ID of the user who made the comment.
    resenia_id : int
        The ID of the review associated with the comment.
    fecha_publicacion : date
        The date when the comment was published.
    """
    __tablename__= 'Comentarios'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)

class Episodio(db.Model, Serializable):
    """
    Model representing an episode of a series.
    ---
    tags:
      - Episodes
    summary: Represents an episode in a series
    description: This model stores information about episodes within a series, including the episode's title, duration, order, release date, and the series to which it belongs.

    Attributes:
    -----------
    id : int
        The unique identifier of the episode.
    titulo : str
        The title of the episode.
    duracion : int
        The duration of the episode in minutes.
    orden : int
        The order of the episode within the series.
    fecha_emision : date
        The release date of the episode.
    titulo_id : int
        The ID of the title or series to which the episode belongs.
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
    Class used to represent a like or dislike on a review.
    ---
    tags:
      - Impressions
    summary: Represents a like or dislike on a review
    description: This class stores the information about a user's like or dislike (impression) on a review. A like is represented by a value of 1, while a dislike is represented by a value of -1.

    Attributes:
    -----------
    id : int
        The unique identifier of the impression.
    usuario_id : int
        The ID of the user who made the impression.
    resenia_id : int
        The ID of the review to which the impression is associated.
    valor : int
        The value of the impression (1 for 'like', -1 for 'dislike').
    """
    __tablename__ = 'Impresiones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    resenia_id = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Integer, nullable=False)


class Entidad(db.Model, UserMixin, Serializable):
    """
    Class used to represent a like or dislike on a review.
    ---
    tags:
      - Impressions
    summary: Represents a like or dislike on a review
    description: This class stores the information about a user's like or dislike (impression) on a review. A like is represented by a value of 1, while a dislike is represented by a value of -1.

    Attributes:
    -----------
    id : int
        The unique identifier of the impression.
    usuario_id : int
        The ID of the user who made the impression.
    resenia_id : int
        The ID of the review to which the impression is associated.
    valor : int
        The value of the impression (1 for 'like', -1 for 'dislike').
    """
    __abstract__ = True  

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    contraseña = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str):
        """
        Encrypts and stores the user's password.
        ---
        tags:
        - User
        summary: Encrypt and store a user's password securely.
        description: This method encrypts the provided password using a secure hashing algorithm and stores it in the entity's password field.

        parameters:
        - in: body
            name: password
            required: true
            schema:
            type: string
            description: The password to be encrypted and stored.
            
        responses:
        200:
            description: Password encrypted and stored successfully.
        """
        self.contraseña = generate_password_hash(password)

    def check_password(self, password: str):
        """
        Verifies if the provided password matches the stored one.
        ---
        tags:
        - User
        summary: Verify if the provided password matches the stored password.
        description: This method checks if the given password matches the encrypted password stored in the entity. It is used for authentication purposes.

        parameters:
        - in: body
            name: password
            required: true
            schema:
            type: string
            description: The password to verify against the stored one.

        responses:
        200:
            description: Password verification successful. Returns True if the password matches, otherwise False.
        """
        return check_password_hash(self.contraseña, password)

class Productora(Entidad):
    """
    Class used to represent a Producer.

    Inherits from the Entidad class.

    """
    __tablename__ = 'Productoras'

class Usuario(Entidad):
    """
    Class used to represent a User.

    Inherits from the Entidad class.

    """
    __tablename__ = 'Usuarios'

class Reseña(db.Model, Serializable):
    """
    Class used to represent a review made by a user.
    ---
    tags:
    - Reviews
    summary: Represents a review made by a user on a title (e.g., movie, series, book).
    description: This class stores the information about a user's review on a title. It includes the user's rating, the content of the review, the user who wrote the review, and the date it was published.

    Attributes:
    -----------
    id : int
        The unique identifier of the review.
    puntuacion : int
        The rating given in the review, typically a value between 1 and 5.
    texto : str
        The content of the review, where the user shares their opinion on the title.
    usuario_id : int
        The ID of the user who wrote the review.
    titulo_id : int
        The ID of the title (e.g., movie, series, book) that is being reviewed.
    fecha_publicacion : date
        The date when the review was published.
    """
    __tablename__ = 'Reseñas'
    id = db.Column(db.Integer, primary_key=True)
    puntuacion = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)

class EstadoTitulo(Enum):
    COMPLETO = 'COMPLETO'
    ACTIVO = 'ACTIVO'
    SIN_COMENZAR = 'SIN_COMENZAR'

    def __str__(self):
        return self.value

class Seguimiento(db.Model, Serializable):
    """
    Class used to represent a user's progress tracking of a title.
    ---
    tags:
    - Tracking
    summary: Represents the progress of a user following a title (e.g., a movie, series, or book).
    description: This class stores information about a user's progress while following a title, including the status of the tracking, the number of episodes or chapters watched, and the associated review.

    Attributes:
    -----------
    id : int
        The unique identifier of the progress tracking.
    usuario_id : int
        The ID of the user who is following the title.
    estado : int
        The current status of the tracking (e.g., ongoing, completed, etc.).
    resenia_id : int
        The ID of the review associated with the progress tracking.
    cantidad_visto : int
        The number of episodes or chapters the user has watched so far.
    titulo_id : int
        The ID of the title (e.g., movie, series, book) that the user is tracking.
    """
    __tablename__ = 'Seguimientos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Enum(EstadoTitulo), nullable=False)
    resenia_id = db.Column(db.Integer, nullable=True)
    cantidad_visto = db.Column(db.Integer, nullable=False)
    titulo_id = db.Column(db.Integer, nullable=False)

class TipoTitulo(Enum):
    PELICULA = 'PELICULA'
    SERIE = 'SERIE'

    def __str__(self):
        return self.value

class Titulo(db.Model, Serializable):
    """
    Class used to represent a title in the database.
    ---
    tags:
    - Titles
    summary: Represents a title (movie or series) in the database.
    description: This class stores information about a title, including its unique ID, associated producer, start and end dates, title name, and type (whether it is a series or a movie).

    Attributes:
    -----------
    id : int
        The unique identifier of the title.
    productora_id : int
        The ID of the producer associated with the title.
    fecha_inicio : date
        The start date of the title's airing or release.
    fecha_fin : date
        The end date of the title's airing or release.
    titulo : str
        The name of the title (e.g., the name of the movie or series).
    tipo : bool
        The type of title: 1 if it is a series, 0 if it is a movie.
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
    Class used to represent the following relationship between two users.
    ---
    tags:
    - Relationships
    summary: Represents the following relationship between two users.
    description: This class stores information about a user following another user, including the follower's and the followed user's IDs.

    Attributes:
    -----------
    seguidor : int
        The ID of the user who follows another user.
    seguido : int
        The ID of the user being followed by another user.
    """
    __tablename__ = 'Relaciones'
    seguidor = db.Column(db.Integer, primary_key=True)
    seguido = db.Column(db.Integer, primary_key=True)

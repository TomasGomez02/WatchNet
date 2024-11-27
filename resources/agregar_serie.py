from flask import request
from flask_restful import Resource
from app import token_required,db
from models.contenido import Contenido
from models.info_login import InfoLogin
from models.productora import Productora
from models.serie import Serie
from models.tipo_contenido import TipoContenido
from models.titulo import Titulo

class NuevaSerie(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json()

        # Obtener la información de la productora a partir del usuario actual
        info_login = InfoLogin.query.filter_by(nombre_usuario=current_user).first()
        productora = Productora.query.filter_by(info_login_id=info_login.id).first()

        # Obtener el nombre de la serie y crear el título
        nombre = data['nombre_serie']
        titulo = Titulo(nombre=nombre, productora_id=productora.id)
        db.session.add(titulo)
        db.session.flush()  

        # Obtener las fechas de inicio y fin de la serie
        fecha_inicio = data['fecha_inicio']
        fecha_fin = data['fecha_fin']

        # Obtener los IDs de episodios desde el JSON
        episodios = data['episodios']  # Lista de episodios (IDs de episodios)

        # Verificar que todos los episodios existan y sean tipo=EPISODIO (con valor 2)
        for episodio_id in episodios:
            episodio = Contenido.query.filter_by(id=episodio_id).first()
            if not episodio:
                return {'message': f'Episodio con ID {episodio_id} no existe.'}, 400
            if episodio.tipo != TipoContenido.EPISODIO.value:  # Verificar si el tipo es EPISODIO
                return {'message': f'Episodio con ID {episodio_id} no es de tipo EPISODIO.'}, 400

        # Crear la serie
        serie = Serie(titulo_id=titulo.id, 
                      fecha_inicio=fecha_inicio,
                      fecha_fin=fecha_fin,
                      episodios=episodios)
        db.session.add(serie)
        db.session.flush()  # Para obtener el id de la serie recién creada

        # Agregar la serie a la lista de series de la productora
        if productora.series_id:
            productora.series_id.append(serie.id)
        else:
            productora.series_id = [serie.id]

        db.session.commit()

        return {'message': 'Serie añadida con éxito'}, 201

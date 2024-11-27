from app import app, db, api
from resources.agregar_comentario import Comentar
from resources.agregar_serie import NuevaSerie
from resources.crear_resenia import CrearResenia
from resources.singup import SignUp
from resources.login import Login
from resources.prod_signup import Productora_SignUp
from resources.user_profile import UserProfile
from resources.productora_profile import ProductoraProfile
from resources.nuevo_contenido import NuevoContenido
from flask.templating import render_template


#api.add_resource(HelloWorld, '/')
api.add_resource(SignUp, '/signup')
api.add_resource(Productora_SignUp, '/productora/signup')
api.add_resource(Login, '/login')
api.add_resource(UserProfile, '/user', '/user/<string:current_user>')
api.add_resource(ProductoraProfile, '/productora', '/productora/<string:current_user>')
api.add_resource(NuevoContenido, '/productora/<string:current_user>/nuevoContenido')
api.add_resource(CrearResenia, '/user/<string:current_user>/nuevaResenia')
api.add_resource(Comentar, '/user/<string:current_user>/<int:resenia_id>/agregarComentario')
api.add_resource(NuevaSerie, '/productora/<string:current_user>/nuevaSerie')



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__': 
    app.run(debug=True)
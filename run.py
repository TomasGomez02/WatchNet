from app import app, db, api
from models.user import User
from resources.hello_world import HelloWorld
from resources.login import Login


#api.add_resource(HelloWorld, '/')
api.add_resource(Login, '/login')



if __name__ == '__main__': 
    app.run(debug=True)
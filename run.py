from app import app, db, api
from resources.singup import SignUp
from resources.login import Login
from resources.prod_signup import Productora_SignUp
from resources.user_profile import UserProfile
from flask.templating import render_template


#api.add_resource(HelloWorld, '/')
api.add_resource(SignUp, '/signup')
api.add_resource(Productora_SignUp, '/productora/signup')
api.add_resource(Login, '/login')
api.add_resource(UserProfile, '/user/<string:current_user>')

@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__': 
    app.run(debug=True)
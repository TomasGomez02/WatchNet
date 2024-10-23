from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from config import DB_PASSWORD

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres.usgghxxkxvuesclhvvyn:{DB_PASSWORD}@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
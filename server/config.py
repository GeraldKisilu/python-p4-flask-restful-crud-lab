from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
api = Api()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    api.init_app(app)
    bcrypt.init_app(app)
    
    with app.app_context():
        # Import parts of our application
        from models import User, Recipe, Plant
        # Create database tables for our data models
        db.create_all()

    return app

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

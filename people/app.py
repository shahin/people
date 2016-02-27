import os

from flask import Flask
from flask_restful import Api
from flask.ext.sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ.get('PEOPLE_CONFIG', 'config.DevConfig'))
    db = SQLAlchemy(app)
    return app, db

app, db = create_app()
api = Api(app)

# load resources and API routes when app is imported
import resources

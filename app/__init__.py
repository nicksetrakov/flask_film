from flask import Flask
from flask_login import LoginManager

from context_processors import custom
from app.database import db
from app.config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:21305@localhost/film'
app.context_processor(custom.links)
db.init_app(app)
manager = LoginManager(app)

from app import models, routes


with app.app_context():
    db.create_all()

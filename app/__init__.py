from flask import Flask
from flask_login import LoginManager

from app.database import db
from app.config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:21305@localhost/film'
db.init_app(app)
manager = LoginManager(app)


from app import models, routes, admin


with app.app_context():
    db.create_all()



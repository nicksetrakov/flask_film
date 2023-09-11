# Import necessary modules and classes
from flask import Flask
from flask_login import LoginManager
from app.database import db
from app.config import Config

# Create a Flask application instance
app = Flask(__name__)

# Load configuration settings from the Config class
app.config.from_object(Config)

# Set the SQLALCHEMY_DATABASE_URI configuration for the database connection
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:21305@localhost/film'

# Initialize the database with the Flask app
db.init_app(app)

# Create a LoginManager instance and associate it with the Flask app
manager = LoginManager(app)

# Import application models, routes, and admin configurations
from app import models, routes, admin   # noqa: F401, E402

# Create the database tables within the application context
with app.app_context():
    db.create_all()

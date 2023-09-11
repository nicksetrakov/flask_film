# Import the 'os' module for working with file paths and environment variables
import os

# Create a configuration class named 'Config' for the Flask app
class Config(object):
    # Define a secret key for the application to enhance security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'any_key'

    # Define the URI for connecting to the PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:21305@127.0.0.1/film.db'

    # Define the upload folder path for storing uploaded poster images
    UPLOAD_FOLDER = r'D:\pythonProject\flask_film\app\static\poster'

    # Define a set of allowed file extensions for uploaded images
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

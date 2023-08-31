import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'any_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:21305@127.0.0.1/film.db'
    UPLOAD_FOLDER = r'D:\pythonProject\flask_film\static\poster'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

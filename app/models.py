from app.database import db
from datetime import datetime
from flask_login import UserMixin
from app import manager
from transliterate import translit
from sqlalchemy.orm import column_property

film_genre = db.Table(
    'film_genre',
    db.Column('film_id', db.Integer, db.ForeignKey('film.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    films = db.relationship('Film', backref='user')
    roles = db.Column(db.String(128), nullable=True, default='user')

    def __repr__(self):
        return '<User %r>' % self.username


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    films = db.relationship('Film', secondary='film_genre', back_populates='genres')

    def __repr__(self):
        return self.name


class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    translit_name = db.Column(db.String(200), nullable=False)
    genres = db.relationship('Genre', secondary='film_genre', back_populates='films')
    release_year = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    director = db.Column(db.String(100), default='unknown')
    description = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=False)
    poster = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Film %r>' % self.name

    @staticmethod
    def before_insert(mapper, connection, target):
        if target.name:
            target.translit_name = translit(target.name, 'ru', reversed=True)

    @staticmethod
    def before_update(mapper, connection, target):
        if target.name:
            target.translit_name = translit(target.name, 'ru', reversed=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')
    film = db.relationship('Film', backref='comments')


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

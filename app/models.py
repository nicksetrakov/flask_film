from app.database import db
from datetime import datetime
from flask_login import UserMixin
from app import manager
from transliterate import translit

# Define a many-to-many relationship table between films and genres
film_genre = db.Table(
    'film_genre',
    db.Column('film_id', db.Integer, db.ForeignKey('film.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
)


class User(db.Model, UserMixin):
    # User model representing registered users
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)  # User's unique username
    password = db.Column(db.String(255), nullable=False)  # User's hashed password
    email = db.Column(db.String(50), unique=True, nullable=False)  # User's unique email address
    films = db.relationship('Film', backref='user')  # Relationship with films created by the user
    roles = db.Column(db.String(128), nullable=True, default='user')  # User's role, default is 'user'

    def __repr__(self):
        return '<User %r>' % self.username


class Genre(db.Model):
    # Genre model representing film genres
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)  # Name of the genre
    films = db.relationship('Film', secondary='film_genre',
                            back_populates='genres')  # Relationship with films in this genre

    def __repr__(self):
        return self.name


class Film(db.Model):
    # Film model representing movies in the database
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # Name of the film
    translit_name = db.Column(db.String(200), nullable=False)  # Transliterated film name
    genres = db.relationship('Genre', secondary='film_genre', back_populates='films')  # Relationship with genres
    release_year = db.Column(db.Integer, nullable=False)  # Release year of the film
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Date when the film record was created
    director = db.Column(db.String(100), default='unknown')  # Director of the film
    description = db.Column(db.Text, nullable=True)  # Description of the film
    rating = db.Column(db.Float, nullable=False)  # Rating of the film
    poster = db.Column(db.String(200), nullable=False)  # Filename of the film's poster image
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who added the film

    def __repr__(self):
        return '<Film %r>' % self.name

    @staticmethod
    def before_insert(mapper, connection, target):
        # Generate a transliterated name for the film based on its title
        if target.name:
            target.translit_name = translit(target.name, 'ru', reversed=True)

    @staticmethod
    def before_update(mapper, connection, target):
        # Update the transliterated name if the film's title changes
        if target.name:
            target.translit_name = translit(target.name, 'ru', reversed=True)


class Comment(db.Model):
    # Comment model representing comments on films
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'),
                        nullable=False)  # Film that the comment is associated with
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who posted the comment
    text = db.Column(db.Text, nullable=False)  # Content of the comment
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when the comment was posted

    user = db.relationship('User', backref='comments')  # Relationship with the user who posted the comment
    film = db.relationship('Film', backref='comments')  # Relationship with the film that received the comment


@manager.user_loader
def load_user(user_id):
    # Load a user by their ID for Flask-Login
    return User.query.get(user_id)

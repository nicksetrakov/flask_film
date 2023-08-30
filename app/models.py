from app.database import db
from datetime import datetime
from flask_login import UserMixin
from app import manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    director = db.Column(db.String(50), default='unknown')
    about = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Text, nullable=True)
    poster = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return '<Film %r>' % self.id


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.id


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
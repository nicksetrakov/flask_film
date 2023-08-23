from database import db
from datetime import datetime


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

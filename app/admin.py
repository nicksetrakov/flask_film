from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

from app.models import Film, User, Genre
from app.database import db
from app import app

admin = Admin(app, template_mode='bootstrap4')

admin.add_view(ModelView(Film, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Genre, db.session))

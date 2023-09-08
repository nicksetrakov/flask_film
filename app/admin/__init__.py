from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import app
from app.admin.admin import DashBoardView, FilmModelView
from app.database import db
from app.models import Film, User, Genre

admin = Admin(app, template_mode='bootstrap4', index_view=DashBoardView())

admin.add_view(FilmModelView(Film, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Genre, db.session))

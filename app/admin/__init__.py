# Import the necessary modules and classes
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app
from app.admin.admin import DashBoardView, FilmModelView
from app.database import db
from app.models import Film, User, Genre, Comment

# Create an instance of the Flask-Admin extension
admin = Admin(app, template_mode='bootstrap4', index_view=DashBoardView())

# Add views for the specified models to the Flask-Admin interface
admin.add_view(FilmModelView(Film, db.session))    # View for the Film model
admin.add_view(ModelView(User, db.session))        # View for the User model
admin.add_view(ModelView(Genre, db.session))      # View for the Genre model
admin.add_view(ModelView(Comment, db.session))    # View for the Comment model

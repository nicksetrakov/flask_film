# Import necessary modules and classes
from flask import redirect, url_for, request, flash
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from werkzeug.utils import secure_filename
from transliterate import translit
import os
from datetime import datetime
from app import app
from app.models import User, Film, Genre
from app.forms import FilmForm
from app.database import db
from app.utils import allowed_file


# Create a custom dashboard view for the Flask-Admin interface
class DashBoardView(AdminIndexView):
    @expose('/')
    def add_data_db(self):
        user_count = User.query.count()
        film_count = Film.query.count()
        return self.render('admin/index.html', user_count=user_count, film_count=film_count)

    def is_accessible(self):
        # Check if the current user is authenticated and has the 'admin' role
        return current_user.is_authenticated and 'admin' in current_user.roles

    def inaccessible_callback(self, name, **kwargs):
        # Redirect the user to the login page if they don't have access to the admin panel
        return redirect(url_for('index'))


# Create a custom view for the Film model in Flask-Admin
class FilmModelView(ModelView):

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = FilmForm()
        available_genres = Genre.query.all()  # Get all available genres from the database
        form.genres.choices = [(genre.id, genre.name) for genre in available_genres]
        if request.method == 'POST' and form.validate_on_submit():
            new_film = Film(
                name=form.name.data,
                translit_name=translit(form.name.data, 'ru', reversed=True),
                release_year=form.release_year.data,
                director=form.director.data,
                description=form.description.data,
                rating=form.rating.data,
                user_id=current_user.id
            )
            poster = form.poster.data
            if poster and allowed_file(poster.filename):
                filename = secure_filename(poster.filename)
                if '.' not in filename:
                    filename = f'default.{filename}'
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                poster_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                poster.save(poster_path)
                new_film.poster = unique_filename
                selected_genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
                new_film.genres.extend(selected_genres)
            try:
                db.session.add(new_film)
                db.session.commit()
                return redirect(url_for('film_page', film_name=new_film.translit_name))
            except Exception as e:
                flash(f'An error occurred: {str(e)}')
        return self.render('admin/create_film.html', form=form, available_genres=available_genres)

    # Define the columns to be displayed in the list view of the Film model
    column_list = ('name', 'genres', 'release_year', 'date', 'director', 'description_partial', 'rating')

    # Define labels for the columns in the list view
    column_labels = {
        'name': 'Название',
        'genres': 'Жанры',
        'release_year': 'Год релиза',
        'date': 'Дата создания записи',
        'director': 'Режиссёр',
        'description_partial': 'Описание(часть)',
        'rating': 'Рейтинг',
    }

    # Define columns that can be searched in the list view
    column_searchable_list = ('name', 'director')

    # Define columns that can be filtered in the list view
    column_filters = ('name', 'date', 'rating')

    # Define sortable columns and default sorting order
    column_sortable_list = ('name', 'release_year', 'director', 'rating', 'genres', 'date')
    column_default_sort = ('date', True)

    def _description_partial(self, context, model, name):
        # This function is called to format the 'description' field in the list view
        # In this case, it displays only the first 50 characters
        return model.description[:50] if model.description else ''

    # Use the custom formatter for the 'description_partial' column
    column_formatters = {
        'description_partial': _description_partial
    }

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


class DashBoardView(AdminIndexView):
    @expose('/')
    def add_data_db(self):
        user_count = User.query.count()
        film_count = Film.query.count()
        return self.render('admin/index.html', user_count=user_count, film_count=film_count)

    def is_accessible(self):
        # Проверьте, является ли текущий пользователь аутентифицированным и имеет роль 'admin'
        return current_user.is_authenticated and 'admin' in current_user.roles

    def inaccessible_callback(self, name, **kwargs):
        # Если текущий пользователь не имеет доступ к админ-панели, перенаправьте его на страницу входа
        return redirect(url_for('index'))


class FilmModelView(ModelView):

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = FilmForm()
        available_genres = Genre.query.all()  # Получить все доступные жанры из базы данных
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
                    filename = f'deffault.{filename}'
                extension = filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                poster_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                poster.save(poster_path)
                new_film.poster = unique_filename
                selected_genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
                print(selected_genres)
                print(form.genres.data)
                new_film.genres.extend(selected_genres)
            try:
                db.session.add(new_film)
                db.session.commit()
                return redirect(url_for('film_page', film_name=new_film.translit_name))
            except Exception as e:
                flash(f'Произошла ошибка: {str(e)}')
        return self.render('admin/create_film.html', form=form, available_genres=available_genres)

    column_list = ('name', 'genres', 'release_year', 'date', 'director', 'description_partial', 'rating')

    column_labels = {
        'name': 'Название',
        'genres': 'Жанры',
        'release_year': 'Год релиза',
        'date': 'Дата создания записи',
        'director': 'Режиссёр',
        'description_partial': 'Описание(часть)',
        'rating': 'Рейтинг',
    }

    column_searchable_list = ('name', 'director')

    column_filters = ('name', 'date', 'rating')

    column_sortable_list = ('name', 'release_year', 'director', 'rating', 'genres', 'date')
    column_default_sort = ('date', True)  # Сортировка по умолчанию по столбцу в порядке убывания


    def _description_partial(view, context, model, name):
        # Эта функция будет вызываться для форматирования поля description
        # В данном случае, она выводит только первые 50 символов
        return model.description[:50] if model.description else ''

    column_formatters = {
        'description_partial': _description_partial
    }

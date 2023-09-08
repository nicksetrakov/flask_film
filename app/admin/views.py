from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from flask import current_app
from wtforms.fields import SelectMultipleField
from wtforms import widgets

from app.models import Genre
from app.forms import FilmForm


class FilmModelView(ModelView):
    column_list = ('name', 'release_year', 'director', 'genres')

    # Используйте SelectMultipleField с виджетом Select2Widget
    form_overrides = {
        'genres': SelectMultipleField(
    'Genres',
    widget=Select2Widget(multiple=True),
    coerce=int
)
    }

    def on_model_change(self, form, model, is_created):
        with current_app.app_context():
        # Обновите модель с учетом выбранных жанров
            model.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()

from wtforms import BooleanField, StringField, PasswordField, validators, SubmitField, TextAreaField, FloatField, \
    IntegerField, SelectField, FileField, SelectMultipleField, widgets
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange

from app.models import User
from app.utils import allowed_file


class RegistrationForm(FlaskForm):
    # User registration form
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email-адрес', validators=[DataRequired(), Length(min=4, max=25), Email()])
    password = PasswordField('Придумайте пароль',
                             validators=[DataRequired(), Length(min=4, max=25),
                                         EqualTo('confirm', message='Пароли должны совпадать')])
    confirm = PasswordField('Повторите пароль')
    accept_tos = BooleanField('Я принимаю TOS', [validators.DataRequired()])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different one.')


class MessageForm(FlaskForm):
    # Message form
    name = StringField('Name: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')


class FilmForm(FlaskForm):
    # Form for adding a new film
    name = StringField('Название фильма:', validators=[DataRequired()])
    genres = SelectMultipleField('Жанр:', choices=[], coerce=int, option_widget=widgets.CheckboxInput(),
                                 widget=widgets.ListWidget(prefix_label=False), render_kw={'size': 5})
    release_year = IntegerField('Дата выхода:', validators=[DataRequired(), NumberRange(min=1800, max=2100)])
    director = StringField('Режиссер:', validators=[DataRequired()])
    description = TextAreaField('Описание:')
    rating = FloatField('Рейтинг:', validators=[DataRequired(), NumberRange(min=0, max=10)])
    poster = FileField('Обложка:')

    def validate_poster(self, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError('Invalid file format. Supported formats: png, jpg, jpeg, gif')


class LoginForm(FlaskForm):
    # User login form
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Пароль',
                             validators=[DataRequired(), Length(min=4, max=25)])
    submit = SubmitField('Авторизация')


class CommentForm(FlaskForm):
    # Comment form
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class SearchForm(FlaskForm):
    # Search form
    choices = [('title', 'Название фильма'),
               ('genres', 'Жанры'),
               ('release_date', 'Дата выпуска'),
               ('rating', 'Рейтинг'),
               ('director', 'Режиссёр')]

    criterion = SelectField('Выберите критерий поиска', choices=choices)
    keyword = StringField('Ключевое слово', validators=[DataRequired()])

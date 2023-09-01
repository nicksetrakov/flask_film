from wtforms import BooleanField, StringField, PasswordField, validators, SubmitField, TextAreaField, FloatField, \
    IntegerField, SelectField, FileField, SelectMultipleField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from app.models import User
from app.utils import allowed_file


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email-адрес', validators=[DataRequired(), Length(min=4, max=25), Email()])
    password = PasswordField('Придумайте пароль',
        validators=[DataRequired(), Length(min=4, max=25), EqualTo('confirm', message='Пароли должны совпадать')])
    confirm = PasswordField('Повторите пароль')
    accept_tos = BooleanField('Я принимаю TOS', [validators.DataRequired()])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Этот никнейм уже занят. Пожалуйста придумайте другой.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован. Пожалуйста используйте другой.')


class MessageForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')


class FilmForm(FlaskForm):
    title = StringField('Название фильма:', validators=[DataRequired()])
    genres = SelectMultipleField('Жанр:', coerce=int)
    release_year = IntegerField('Дата выхода:', validators=[DataRequired(), NumberRange(min=1800, max=2100)])
    director = StringField('Режиссер:', validators=[DataRequired()])
    description = TextAreaField('Описание:')
    rating = FloatField('Рейтинг:', validators=[DataRequired(), NumberRange(min=0, max=10)])
    poster = FileField('Обложка:')

    def validate_poster(self, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError('Неверный формат файла. Доустпные форматы: png, jpg, jpeg, gif')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Пароль',
                             validators=[DataRequired(), Length(min=4, max=25)])
    submit = SubmitField('Авторизация')


class SearchForm(FlaskForm):
    search_query = StringField('Search')
    sort_by = SelectField('Sort By', choices=[('rating', 'Rating'), ('release_year', 'Release Year')])

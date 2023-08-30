from wtforms import BooleanField, StringField, PasswordField, validators, SubmitField, TextAreaField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


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


class AddFilmForm(FlaskForm):
    pass


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Пароль',
                             validators=[DataRequired(), Length(min=4, max=25)])
    submit = SubmitField('Авторизация')
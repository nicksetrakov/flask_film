from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email
from wtforms import Form, BooleanField, StringField, PasswordField, validators


class MessageForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegistrationForm(Form):
    username = StringField('Имя пользователя', [validators.Length(min=4, max=25)])
    email = StringField('Email-адрес', [validators.Length(min=6, max=35)])
    password = PasswordField('Придумайте пароль', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Пароли должны совпадать')
    ])
    confirm = PasswordField('Повторите пароль')
    accept_tos = BooleanField('Я принимаю TOS', [validators.DataRequired()])
    submit = SubmitField('Регистрация')
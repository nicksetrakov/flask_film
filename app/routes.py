from flask import render_template, request, redirect, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user

from app.database import db
from app import app
from app.forms import RegistrationForm, LoginForm
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hash_pwd = generate_password_hash(password)

        new_user = User(username=username, password=hash_pwd, email=email)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))
        except:
            flash('Произошла ошибка')
    return render_template('registration.html', form=form)


@app.route('/add-film')
@login_required
def add_film():
    return render_template('about-us.html')


@app.route('/films')
def films():
    return render_template('articles.html')


@app.route('/contact_us')
def contact_us():
    return render_template('contact-us.html')


@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')


@app.route('/login', methods=['get', 'post'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    form = LoginForm()

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')

            return redirect(next_page)
        else:
            flash('Логин либо пароль не правильны')
    else:
        flash('Заполните поля')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['get', 'post'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)
    else:
        return response
# @app.route('/', methods=['get', 'post'])
# def index():
#     server_message = ''
#     client_message = ''
#     if request.method == 'POST':
#         client_message = request.form.get('message')
#
#     if client_message == 'hi':
#         server_message = 'Hello'
#     elif client_message != '':
#         server_message = 'How are you?'
#     return render_template('index1.html', message=server_message)


# @app.route('/message/', methods=['get', 'post'])
# def message():
#     form = MessageForm()
#     if form.validate_on_submit():
#         name = form.name.data
#         email = form.email.data
#         message = form.message.data
#         print(name)
#         print(email)
#         print(message)
#         print('\n Data received. Now redirecting...')
#         return redirect(url_for('message'))
#     return render_template('message.html', form=form)


# @app.route('/<put>/')
# def index(put):
#     text = f'Ваше число {put}, умноженное на 2: {put * 2}'
#     return render_template(index1.html,
#                            number=put * 2,
#                            text=text)

from flask import render_template, request, redirect, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user

import os
from datetime import datetime

from app.database import db
from app import app
from app.forms import RegistrationForm, LoginForm, FilmForm
from app.models import User, Film
from app.utils import allowed_file


@app.route('/')
@app.route('/index')
def index():
    films = Film.query.order_by(Film.date).limit(3).all()
    return render_template('index.html', films=films)


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


@app.route('/add-film', methods=['Get', 'Post'])
@login_required
def add_film():
    form = FilmForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_film = Film(
            name=form.title.data,
            genre=form.genres.data,
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
        try:
            db.session.add(new_film)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            flash('Произошла ошибка')
    return render_template('add_film.html', form=form)


@app.route('/edit_film/<int:film_id>', methods=['GET', 'POST'])
@login_required
def edit_film(film_id):
    film = Film.query.get_or_404(film_id)
    if film.user != current_user and not current_user.is_admin:
        return flash('You do not have permission to edit this film.', 'danger')

    form = FilmForm(obj=film)
    if form.validate_on_submit():
        form.populate_obj(film)
        try:
            db.session.commit()
            return redirect(url_for('film_page', film_id=film_id))
        except:
            flash('Произошла ошибка')
    return render_template('edit_film.html', form=form, film=film)


@app.route('/films')
def films():
    return render_template('articles.html')


@app.route('/film/<int:film_id>')
def film_page(film_id):
    return render_template('film.html')


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
            if next_page == None:
                return redirect(url_for('index'))
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

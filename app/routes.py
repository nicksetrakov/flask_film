from flask import render_template, request, redirect, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from transliterate import translit

import os
from datetime import datetime

from app.database import db
from app import app
from app.forms import RegistrationForm, LoginForm, FilmForm
from app.models import User, Film, Genre
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
    available_genres = Genre.query.all()  # Получить все доступные жанры из базы данных
    form.genres.choices = [(genre.id, genre.name) for genre in available_genres]
    if request.method == 'POST' and form.validate_on_submit():
        new_film = Film(
            name=form.title.data,
            translit_name=translit(form.title.data, 'ru', reversed=True),
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
    return render_template('add_film.html', form=form, available_genres=available_genres)


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
            return redirect(url_for('film_page', film_name=film.translit_name))
        except:
            flash('Произошла ошибка')
    return render_template('edit_film.html', form=form, film=film)


@app.route('/film/<string:film_name>')
def film_page(film_name):
    film = Film.query.filter_by(translit_name=film_name).first()
    return render_template('film.html', film=film)


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
            flash('Неправильное имя пользователя или пароль', 'danger')
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

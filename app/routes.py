from flask import render_template, request, redirect, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from transliterate import translit
from sqlalchemy import desc, or_
from flask_paginate import Pagination, get_page_parameter

import os
from datetime import datetime

from app.database import db
from app import app
from app.forms import RegistrationForm, LoginForm, FilmForm, CommentForm, SearchForm
from app.models import User, Film, Genre, Comment
from app.utils import allowed_file


@app.route('/')
@app.route('/index')
def index():
    per_page = 10
    page = request.args.get('page', type=int, default=1)
    pagination = Film.query.order_by(desc(Film.date)).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('index.html', pagination=pagination)


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
            new_film.genres.extend(selected_genres)
        try:
            db.session.add(new_film)
            db.session.commit()
            return redirect(url_for('film_page', film_translit_name=new_film.translit_name))
        except Exception as e:
            flash(f'Произошла ошибка: {str(e)}')
    return render_template('add_film.html', form=form, available_genres=available_genres)


@app.route('/edit_film/<string:film_translit_name>', methods=['GET', 'POST'])
@login_required
def edit_film(film_translit_name):
    film = Film.query.filter_by(translit_name=film_translit_name).first()

    if film.user != current_user and not current_user.roles == 'admin':
        flash('Только администратор либо создатель поста может редактировать', 'danger')
        return redirect(url_for('film_page', film_translit_name=film.translit_name))  # Замените 'some_other_route' на вашу целевую страницу

    form = FilmForm(obj=film)
    available_genres = Genre.query.all()  # Получить все доступные жанры из базы данных
    form.genres.choices = [(genre.id, genre.name) for genre in available_genres]
    if film.genres:
        form.genres.data = [genre.id for genre in film.genres]
    if request.method == 'POST' and form.validate_on_submit():
        form.genres.data = [int(genre_id) for genre_id in request.form.getlist('genres')]
        # Обновление постера, если пользователь загрузил новый постер
        poster = form.poster.data
        if poster and allowed_file(poster.filename):
            # Очистите старый постер, если он существует
            if film.poster:
                old_poster_path = os.path.join(app.config['UPLOAD_FOLDER'], film.poster)
                if os.path.exists(old_poster_path):
                    os.remove(old_poster_path)

            filename = secure_filename(poster.filename)
            if '.' not in filename:
                filename = f'default.{filename}'
            extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            poster.save(poster_path)
            film.poster = unique_filename
        # Очистите текущие жанры фильма
        film.genres.clear()

        # Добавьте новые жанры к фильму
        selected_genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
        for genre in selected_genres:
            film.genres.append(genre)
        film.translit_name = translit(form.name.data, 'ru', reversed=True)

        # Обновление остальных данных фильма
        film.name = form.name.data,
        film.translit_name = translit(form.name.data, 'ru', reversed=True),
        film.release_year = form.release_year.data,
        film.director = form.director.data,
        film.description = form.description.data,
        film.rating = form.rating.data,
        film.user_id = current_user.id

        try:
            db.session.commit()
            return redirect(url_for('film_page', film_name=film.translit_name))
        except Exception as e:
            flash(f'Произошла ошибка: {str(e)}', 'danger')

    return render_template('edit_film.html', form=form, film=film, available_genres=available_genres)


@app.route('/film/<string:film_translit_name>')
def film_page(film_translit_name):
    film = Film.query.filter_by(translit_name=film_translit_name).first()
    comments = Comment.query.filter_by(film_id=film.id)
    form = CommentForm()
    page = request.args.get('page', type=int, default=1)
    pagination = comments.paginate(per_page=10, page=page, error_out=False)
    return render_template('film.html', film=film, form=form, comments=comments, pagination=pagination)


@app.route('/add_comment/<string:film_translit_name>', methods=['POST'])
def add_comment(film_translit_name):
    film = Film.query.filter_by(translit_name=film_translit_name).first()
    form = CommentForm()

    if form.validate_on_submit():
        # Получаем текст комментария из формы
        comment_text = form.text.data

        # Создаем новый комментарий и добавляем его в базу данных
        new_comment = Comment(
            film_id=film.id,
            user_id=current_user.id,
            text=comment_text
        )

        db.session.add(new_comment)
        db.session.commit()

        # Редирект на страницу фильма или другую необходимую страницу после добавления комментария
        return redirect(url_for('film_page', film_translit_name=film.translit_name))

        # Если форма не прошла валидацию, вернуть пользователя на предыдущую страницу или выполнить другую логику
    flash('Ошибка валидации формы', 'danger')
    return redirect(request.referrer)


@app.route('/delete_film/<string:film_translit_name>', methods=['POST'])
@login_required
def delete_film(film_translit_name):
    film = Film.query.filter_by(translit_name=film_translit_name).first()

    if not film:
        flash('Фильм не найден.', category='danger')
        return redirect(url_for('index'))

    if film.user != current_user and not current_user.roles == 'admin':
        flash('Вы не можете удалить этот фильм.', category='danger')
        return redirect(url_for('film_page', film_translit_name=film.translit_name))

    try:
        # Удалите постер фильма, если он существует
        if film.poster:
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], film.poster)
            if os.path.exists(poster_path):
                os.remove(poster_path)

        # Удалите фильм из базы данных
        db.session.delete(film)
        db.session.commit()
        flash('Фильм успешно удален.', category='success')
    except Exception as e:
        flash(f'Произошла ошибка при удалении фильма: {str(e)}', category='danger')

    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search_film():
    form = SearchForm()
    query = request.args.get('query')  # Получить запрос из параметра 'query'
    films = Film.query.filter(or_(Film.name.ilike(f'%{query}%'), Film.name.ilike(f'{query}%')))
    if request.method == 'POST' and form.validate():
        criterion = form.criterion.data
        keyword = form.keyword.data

        # Составьте SQL-запрос в зависимости от выбранного критерия
        if criterion == 'title':
            films = Film.query.filter(Film.name.ilike(f'%{keyword}%'))
        elif criterion == 'genres':
            films = Film.query.filter(or_(*[Film.genres.any(Genre.name.ilike(f'%{keyword}%'))]))
        elif criterion == 'release_date':
            films = Film.query.filter(Film.release_year == keyword)
        elif criterion == 'rating':
            films = Film.query.filter(Film.rating == keyword)
        elif criterion == 'director':
            films = Film.query.filter(Film.director.ilike(f'%{keyword}%'))

    page = request.args.get('page', type=int, default=1)
    per_page = 10

    pagination = films.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('search_results.html', query=query, form=form, pagination=pagination)


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

# Import necessary modules and classes for the application
from flask import render_template, request, redirect, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from transliterate import translit
from sqlalchemy import desc, or_

import os
from datetime import datetime

# Import database models and forms from the app
from app.database import db
from app import app
from app.forms import RegistrationForm, LoginForm, FilmForm, CommentForm, SearchForm
from app.models import User, Film, Genre, Comment
from app.utils import allowed_file


@app.route('/')
@app.route('/index')
def index():
    # Route for displaying a list of films
    per_page = 10
    page = request.args.get('page', type=int, default=1)

    # Paginate the films in descending order of release year
    pagination = Film.query.order_by(desc(Film.release_year)).paginate(page=page, per_page=per_page, error_out=False)

    # Render the HTML template with pagination data
    return render_template('index.html', pagination=pagination)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    # Route for user registration
    form = RegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Handle registration form submission
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Hash the user's password before storing it
        hash_pwd = generate_password_hash(password)

        # Create a new User object
        new_user = User(username=username, password=hash_pwd, email=email)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Ваш аккаунт создан!', 'success')
            return redirect(url_for('login'))
        except:
            flash('Произошла ошибка')

    return render_template('registration.html', form=form)


@app.route('/add-film', methods=['GET', 'POST'])
@login_required
def add_film():
    # Route for adding a new film
    form = FilmForm()

    # Get available genres from the database
    available_genres = Genre.query.order_by(Genre.name).all()

    # Populate the genre choices in the form
    form.genres.choices = [(genre.id, genre.name) for genre in available_genres]

    if request.method == 'POST' and form.validate_on_submit():
        # Handle film addition form submission
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
                filename = f'default.{filename}'

            # Generate a unique filename and save the poster
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            poster.save(poster_path)
            new_film.poster = unique_filename

            # Associate selected genres with the new film
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
    # Route for editing an existing film
    film = Film.query.filter_by(translit_name=film_translit_name).first()

    if film.user != current_user and not current_user.roles == 'admin':
        flash('Только администратор или создатель могут редактировать', 'danger')
        return redirect(url_for('film_page', film_translit_name=film.translit_name))

    form = FilmForm(obj=film)

    # Get available genres from the database
    available_genres = Genre.query.all()

    # Populate the genre choices in the form
    form.genres.choices = [(genre.id, genre.name) for genre in available_genres]

    if film.genres:
        form.genres.data = [genre.id for genre in film.genres]

    if request.method == 'POST' and form.validate_on_submit():
        form.genres.data = [int(genre_id) for genre_id in request.form.getlist('genres')]

        poster = form.poster.data
        if poster and allowed_file(poster.filename):
            if film.poster:
                old_poster_path = os.path.join(app.config['UPLOAD_FOLDER'], film.poster)
                if os.path.exists(old_poster_path):
                    os.remove(old_poster_path)

            filename = secure_filename(poster.filename)
            if '.' not in filename:
                filename = f'default.{filename}'

            # Generate a unique filename and save the new poster
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            poster.save(poster_path)
            film.poster = unique_filename

        # Clear the current genres associated with the film
        film.genres.clear()

        # Associate selected genres with the film
        selected_genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
        for genre in selected_genres:
            film.genres.append(genre)

        # Update other film details
        film.translit_name = translit(form.name.data, 'ru', reversed=True)
        film.name = form.name.data
        film.release_year = form.release_year.data
        film.director = form.director.data
        film.description = form.description.data
        film.rating = form.rating.data
        film.user_id = current_user.id

        try:
            db.session.commit()
            return redirect(url_for('film_page', film_translit_name=film.translit_name))
        except Exception as e:
            flash(f'Произошла ошибка: {str(e)}', 'danger')

    return render_template('edit_film.html', form=form, film=film, available_genres=available_genres)


@app.route('/film/<string:film_translit_name>')
def film_page(film_translit_name):
    # Route for displaying a film's details and comments
    film = Film.query.filter_by(translit_name=film_translit_name).first()
    comments = Comment.query.filter_by(film_id=film.id)
    form = CommentForm()
    page = request.args.get('page', type=int, default=1)

    # Paginate the comments
    pagination = comments.paginate(per_page=10, page=page, error_out=False)

    return render_template('film.html', film=film, form=form, comments=comments, pagination=pagination)


@app.route('/add_comment/<string:film_translit_name>', methods=['POST'])
def add_comment(film_translit_name):
    # Route for adding a comment to a film
    film = Film.query.filter_by(translit_name=film_translit_name).first()
    form = CommentForm()

    if form.validate_on_submit():
        comment_text = form.text.data

        # Create a new Comment object
        new_comment = Comment(
            film_id=film.id,
            user_id=current_user.id,
            text=comment_text
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('film_page', film_translit_name=film.translit_name))

    flash('Form validation error', 'danger')
    return redirect(request.referrer)


@app.route('/delete_film/<string:film_translit_name>', methods=['POST'])
@login_required
def delete_film(film_translit_name):
    # Route for deleting a film
    film = Film.query.filter_by(translit_name=film_translit_name).first()
    comments = Comment.query.filter_by(film_id=film.id).all()

    if not film:
        flash('Фильм не найден.', category='danger')
        return redirect(url_for('index'))

    if film.user != current_user and not current_user.roles == 'admin':
        flash('Вы не можете удалить этот фильм.', category='danger')
        return redirect(url_for('film_page', film_translit_name=film.translit_name))

    try:
        if film.poster:
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], film.poster)
            if os.path.exists(poster_path):
                os.remove(poster_path)

        for comment in comments:
            db.session.delete(comment)

        db.session.delete(film)
        db.session.commit()
        flash('Фильм успешно удален.', category='success')
    except Exception as e:
        flash(f'Произошла ошибка при удалении фильма: {str(e)}', category='danger')

    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search_film():
    # Route for searching films
    form = SearchForm()
    query = request.args.get('query')
    films = Film.query.filter(or_(Film.name.ilike(f'%{query}%'), Film.name.ilike(f'{query}%')))

    if request.method == 'POST' and form.validate():
        criterion = form.criterion.data
        keyword = form.keyword.data

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

    # Paginate the search results
    pagination = films.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('search_results.html', query=query, form=form, pagination=pagination)


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    form = LoginForm()

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')
            if next_page is None:
                return redirect(url_for('index'))
            return redirect(next_page)
        else:
            flash('Неправильное имя пользователя или пароль', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
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

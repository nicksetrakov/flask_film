from flask import Flask, render_template, request, redirect, url_for
from config import *
from flask_sqlalchemy import SQLAlchemy
from database import db
from models import Film
from context_processors import custom


app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:21305@localhost/film'
app.context_processor(custom.links)
db.init_app(app)



@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/about-us')
def about_us():
    return render_template('about-us.html')


@app.route('/articles')
def articles():
    return render_template('articles.html')


@app.route('/contact_us')
def contact_us():
    return render_template('contact-us.html')


@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)

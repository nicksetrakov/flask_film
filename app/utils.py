from app import app
from markupsafe import Markup
from transliterate import translit


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def transliterate_filter(s):
    return Markup(translit(s, 'ru', reversed=True))


app.jinja_env.filters['translit'] = transliterate_filter

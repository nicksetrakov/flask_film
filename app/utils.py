# Import the Flask application instance 'app', Markup class, and the 'translit' function
# These imports are necessary for creating utility functions and filters.
from app import app
from markupsafe import Markup
from transliterate import translit


# Define a function 'allowed_file' to check if a file has an allowed extension.
def allowed_file(filename):
    # Check if the filename contains a dot ('.') and its extension is in the list of allowed extensions.
    # The list of allowed extensions is defined in the Flask app's configuration ('ALLOWED_EXTENSIONS').
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Define a filter function 'transliterate_filter' to transliterate text from Cyrillic to Latin characters.
def transliterate_filter(s):
    # Use the 'translit' function to perform transliteration on the input string 's'.
    # 'translit' takes the input string, source language ('ru' for Russian), and 'reversed=True' to convert to Latin.
    transliterated_text = translit(s, 'ru', reversed=True)

    # Wrap the transliterated text in a 'Markup' object for safe rendering in templates.
    return Markup(transliterated_text)


# Register the 'transliterate_filter' function as a filter named 'translit' in the Jinja2 environment.
app.jinja_env.filters['translit'] = transliterate_filter

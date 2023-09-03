from flask_principal import Principal, Permission, RoleNeed
from flask_login import current_user
from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from app.models import Film, User, Genre, film_genre
from app.database import db
from app import app


class MyAdminView(AdminIndexView):
    def is_accessible(self):
        # Проверьте, является ли текущий пользователь аутентифицированным и имеет роль 'admin'
        return current_user.is_authenticated and 'admin' in current_user.roles

    def inaccessible_callback(self, name, **kwargs):
        # Если текущий пользователь не имеет доступ к админ-панели, перенаправьте его на страницу входа
        return redirect(url_for('index'))


admin = Admin(app, template_mode='bootstrap4', index_view=MyAdminView())

admin.add_view(ModelView(Film, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Genre, db.session))


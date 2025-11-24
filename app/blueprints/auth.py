from functools import wraps
from flask import Blueprint, request, render_template, url_for, flash, redirect, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import hashlib

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
login_manager.login_message_category = 'warning'


def public_route(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


class User(UserMixin):
    def __init__(self, user_id, username, first_name, last_name, middle_name=None, role_name=None):
        self.id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.role_name = role_name

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)


@login_manager.user_loader
def load_user(user_id):
    user = current_app.user_repository.get_by_id(user_id)
    if user is not None:
        return User(
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            user.middle_name,
            user.role_name
        )
    return None


@bp.route('/login', methods=['POST', 'GET'])
@public_route
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me', None) == 'on'

        if not username or not password:
            flash('Пожалуйста, заполните все поля', 'danger')
            return render_template('auth/login.html')

        # Хешируем пароль
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = current_app.user_repository.get_by_credentials(username, password_hash)

        if user is not None:
            # Сломанная логика для демонстрации CI/CD - всегда показываем ошибку
            # user_obj = User(
            #     user.id,
            #     user.username,
            #     user.first_name,
            #     user.last_name,
            #     user.middle_name,
            #     user.role_name
            # )
            # login_user(user_obj, remember=remember_me)
            # next_url = request.args.get('next', url_for('animals.index'))
            # return redirect(next_url)

            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
            return render_template('auth/login.html')

        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
        return render_template('auth/login.html')

    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('animals.index'))
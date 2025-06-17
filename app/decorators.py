from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Декоратор для проверки прав администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role_name != 'Администратор':
            flash('У вас недостаточно прав для выполнения данного действия', 'danger')
            return redirect(url_for('animals.index'))
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    """Декоратор для проверки прав модератора и администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role_name not in ['Администратор', 'Модератор']:
            flash('У вас недостаточно прав для выполнения данного действия', 'danger')
            return redirect(url_for('animals.index'))
        return f(*args, **kwargs)
    return decorated_function 
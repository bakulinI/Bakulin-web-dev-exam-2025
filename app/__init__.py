import os
from flask import Flask, redirect, url_for
import markdown

from .blueprints import animals
from .db import DBConnector
from .repositories import UserRepository
from .repositories.animal_repository import AnimalRepository
from .repositories.photo_repository import PhotoRepository
from .repositories.adoption_repository import AdoptionRepository

db = DBConnector()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    app.config.from_pyfile(config_path, silent=False)
    if test_config:
        app.config.from_mapping(test_config)

    db.init_app(app)
    app.db = db

    from .blueprints.auth import login_manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    app.user_repository = UserRepository(db)
    app.animal_repository = AnimalRepository(db)
    app.photo_repository = PhotoRepository(db)
    app.adoption_repository = AdoptionRepository(db)

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.animals import bp as animals_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(animals_bp)

    animals.init_app(app)

    @app.template_filter('markdown')
    def markdown_filter(text):
        if text:
            return markdown.markdown(text, extensions=['extra', 'codehilite'])
        return ''
    #фильтр для отображения месяцев в правильном формате
    @app.template_filter('pluralize')
    def pluralize_filter(number, one, few, many):
        n = abs(int(number))
        if n % 10 == 1 and n % 100 != 11:
            return one
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return few
        else:
            return many

    upload_folder = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    @app.route('/')
    def index():
        return redirect(url_for('animals.index'))

    return app
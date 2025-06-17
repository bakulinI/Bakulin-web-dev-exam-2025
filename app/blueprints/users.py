from flask import Blueprint
from app.repositories import UserRepository
from app.db import db

bp = Blueprint('users', __name__)
user_repository = UserRepository(db)
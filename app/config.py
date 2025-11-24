import os

# Database configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'bakulinexam')

# Flask configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
TESTING = False

# Upload configuration
UPLOAD_FOLDER = 'app/static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
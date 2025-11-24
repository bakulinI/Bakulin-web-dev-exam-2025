import pytest
import os
from app import create_app
from app.db import DBConnector

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    test_config = {
        'TESTING': True,
        'MYSQL_HOST': os.getenv('MYSQL_HOST', 'localhost'),
        'MYSQL_USER': os.getenv('MYSQL_USER', 'test_user'),
        'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD', 'test_password'),
        'MYSQL_DATABASE': os.getenv('MYSQL_DATABASE', 'test_db'),
        'SECRET_KEY': 'test_secret_key',
        'UPLOAD_FOLDER': '/tmp/test_uploads'
    }

    app = create_app(test_config)

    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db_connector(app):
    """Database connector for tests."""
    return app.db

@pytest.fixture
def init_database(db_connector):
    """Initialize test database with schema."""
    # This would normally load the schema, but for simplicity we'll assume it's set up
    # In a real scenario, you'd run the schema SQL here
    pass
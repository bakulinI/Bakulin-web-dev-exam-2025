from flask import current_app
import mysql.connector
from mysql.connector import Error


    def __init__(self):
        self.app = None
        self._connection = None

    def init_app(self, app):
        self.app = app

        @app.teardown_appcontext
        def close_db_connection(error):
            if self._connection is not None:
                self._connection.close()
                self._connection = None

    def get_config(self):
        return {
            'user': self.app.config['MYSQL_USER'],
            'password': self.app.config['MYSQL_PASSWORD'],
            'host': self.app.config['MYSQL_HOST'],
            'database': self.app.config['MYSQL_DATABASE'],
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_general_ci',
            'use_unicode': True
        }

    def connect(self):
        try:
            if self._connection is None or not self._connection.is_connected():
                self._connection = mysql.connector.connect(**self.get_config())
            return self._connection
        except Error as e:
            current_app.logger.error(f"Errors connecting to MySQL: {str(e)}")
            raise

db = DBConnector()

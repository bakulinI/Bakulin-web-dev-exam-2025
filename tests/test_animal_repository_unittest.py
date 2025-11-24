import unittest
from unittest.mock import Mock, patch
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.repositories.animal_repository import AnimalRepository

class TestAnimalRepository(unittest.TestCase):
    def setUp(self):
        self.db_connector = Mock()
        self.repo = AnimalRepository(self.db_connector)

    def test_create_animal(self):
        """Test creating a new animal."""
        # Mock the database connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        self.db_connector.connect.return_value = mock_connection

        animal_data = {
            'name': 'Test Dog',
            'description': 'A friendly test dog',
            'age_months': 24,
            'breed': 'Labrador',
            'gender': 'male',
            'status': 'available'
        }

        result = self.repo.create(animal_data)

        self.assertEqual(result, 1)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_get_by_id(self):
        """Test retrieving an animal by ID."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Test Dog',
            'description': 'A friendly test dog',
            'age_months': 24,
            'breed': 'Labrador',
            'gender': 'male',
            'status': 'available',
            'adoption_count': 0,
            'photo_filename': 'test.jpg'
        }
        self.db_connector.connect.return_value.cursor.return_value = mock_cursor

        result = self.repo.get_by_id(1)

        self.assertEqual(result['id'], 1)
        self.assertEqual(result['name'], 'Test Dog')
        mock_cursor.execute.assert_called_once()

if __name__ == '__main__':
    unittest.main()
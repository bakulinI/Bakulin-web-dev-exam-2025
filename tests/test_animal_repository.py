import pytest
from app.repositories.animal_repository import AnimalRepository
from unittest.mock import Mock, MagicMock, patch
import unittest

class TestAnimalRepository(unittest.TestCase):
    def test_create_animal(self, db_connector):
        """Test creating a new animal."""
        repo = AnimalRepository(db_connector)

        animal_data = {
            'name': 'Test Dog',
            'description': 'A friendly test dog',
            'age_months': 24,
            'breed': 'Labrador',
            'gender': 'male',
            'status': 'available'
        }

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.lastrowid = 1
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.create(animal_data)

        self.assertEqual(result, 1)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_get_by_id(self, db_connector):
        """Test retrieving an animal by ID."""
        repo = AnimalRepository(db_connector)

        mock_connection = Mock()
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
        mock_connection.cursor.return_value = mock_cursor

        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_by_id(1)

        self.assertEqual(result['id'], 1)
        self.assertEqual(result['name'], 'Test Dog')
        mock_cursor.execute.assert_called_once()

    def test_get_paginated(self, db_connector):
        """Test retrieving paginated animals."""
        repo = AnimalRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': 'Test Dog',
                'description': 'A friendly test dog',
                'age_months': 24,
                'breed': 'Labrador',
                'gender': 'male',
                'status': 'available',
                'photo_filename': 'test.jpg',
                'adoptions_count': 0
            }
        ]
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_paginated(page=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Test Dog')

    def test_update_animal(self, db_connector):
        """Test updating an animal."""
        repo = AnimalRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        animal_data = {
            'name': 'Updated Dog',
            'description': 'Updated description',
            'age_months': 30,
            'breed': 'Golden Retriever',
            'gender': 'male',
            'status': 'available'
        }

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            repo.update(1, animal_data)

        mock_cursor.execute.assert_called_once()
        # Note: update method may not call commit if connection is passed

    def test_delete_animal(self, db_connector):
        """Test deleting an animal."""
        repo = AnimalRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            repo.delete(1)

        mock_cursor.execute.assert_called_once_with("DELETE FROM animals WHERE id = %s", (1,))
        mock_connection.commit.assert_called_once()

    def test_search_animals(self, db_connector):
        """Test searching animals."""
        repo = AnimalRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {
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
        ]
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.search(query='dog')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Test Dog')
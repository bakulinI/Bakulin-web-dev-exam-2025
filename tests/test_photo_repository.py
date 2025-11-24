import pytest
from app.repositories.photo_repository import PhotoRepository
from unittest.mock import Mock, patch
import unittest

class TestPhotoRepository(unittest.TestCase):
    def test_create_photo(self, db_connector):
        """Test creating a new photo record."""
        repo = PhotoRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.lastrowid = 1
        mock_connection.cursor.return_value = mock_cursor

        photo_data = {
            'animal_id': 1,
            'filename': 'test.jpg',
            'mime_type': 'image/jpeg'
        }

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.create(photo_data)

        self.assertEqual(result, 1)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_get_by_animal_id(self, db_connector):
        """Test retrieving photos by animal ID."""
        repo = PhotoRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'filename': 'test1.jpg',
                'mime_type': 'image/jpeg',
                'animal_id': 1
            },
            {
                'id': 2,
                'filename': 'test2.jpg',
                'mime_type': 'image/jpeg',
                'animal_id': 1
            }
        ]
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_by_animal_id(1)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['filename'], 'test1.jpg')
        self.assertEqual(result[1]['filename'], 'test2.jpg')

    def test_delete_photo(self, db_connector):
        """Test deleting a photo record."""
        repo = PhotoRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.delete(1)

        self.assertEqual(result, True)
        mock_cursor.execute.assert_called_once_with("DELETE FROM animal_photos WHERE id = %s", (1,))
        mock_connection.commit.assert_called_once()
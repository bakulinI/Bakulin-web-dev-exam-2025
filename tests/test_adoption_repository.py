import pytest
from app.repositories.adoption_repository import AdoptionRepository
from unittest.mock import Mock, patch
import unittest

class TestAdoptionRepository(unittest.TestCase):
    def test_create_adoption(self, db_connector):
        """Test creating a new adoption request."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.lastrowid = 1
        mock_connection.cursor.return_value = mock_cursor

        adoption_data = {
            'animal_id': 1,
            'user_id': 1,
            'contact_info': 'test@example.com'
        }

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.create(adoption_data)

        self.assertEqual(result, 1)
        # Should execute 3 queries: INSERT adoption, UPDATE animal status, UPDATE other adoptions
        self.assertEqual(mock_cursor.execute.call_count, 3)
        self.assertEqual(mock_connection.commit.call_count, 3)

    def test_get_by_id(self, db_connector):
        """Test retrieving an adoption by ID."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'animal_id': 1,
            'user_id': 1,
            'contact_info': 'test@example.com',
            'status': 'pending',
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser'
        }
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_by_id(1)

        self.assertEqual(result['id'], 1)
        self.assertEqual(result['status'], 'pending')

    def test_get_by_user_and_animal(self, db_connector):
        """Test retrieving adoption by user and animal."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'animal_id': 1,
            'user_id': 1,
            'contact_info': 'test@example.com',
            'status': 'pending'
        }
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_by_user_and_animal(1, 1)

        self.assertEqual(result['id'], 1)

    def test_update_status_accepted(self, db_connector):
        """Test updating adoption status to accepted."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            repo.update_status(1, 'accepted')

        # Should execute 3 queries: UPDATE status, UPDATE animal, UPDATE other adoptions
        self.assertEqual(mock_cursor.execute.call_count, 3)
        self.assertEqual(mock_connection.commit.call_count, 1)

    def test_update_status_rejected(self, db_connector):
        """Test updating adoption status to rejected."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            repo.update_status(1, 'rejected')

        # Should execute 1 query: UPDATE status
        self.assertEqual(mock_cursor.execute.call_count, 1)
        self.assertEqual(mock_connection.commit.call_count, 1)

    def test_get_by_animal_id(self, db_connector):
        """Test retrieving adoptions by animal ID."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'animal_id': 1,
                'user_id': 1,
                'contact_info': 'test@example.com',
                'status': 'pending',
                'first_name': 'Test',
                'last_name': 'User',
                'username': 'testuser'
            }
        ]
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_by_animal_id(1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 1)

    def test_get_by_user_id(self, db_connector):
        """Test retrieving adoptions by user ID."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'animal_id': 1,
                'user_id': 1,
                'contact_info': 'test@example.com',
                'status': 'pending',
                'animal_name': 'Test Dog'
            }
        ]
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_by_user_id(1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['animal_name'], 'Test Dog')
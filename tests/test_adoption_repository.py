import pytest
from app.repositories.adoption_repository import AdoptionRepository
from unittest.mock import Mock

class TestAdoptionRepository:
    def test_create_adoption(self, db_connector):
        """Test creating a new adoption request."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        db_connector.connect.return_value = mock_connection

        adoption_data = {
            'animal_id': 1,
            'user_id': 1,
            'contact_info': 'test@example.com'
        }

        result = repo.create(adoption_data)

        assert result == 1
        # Should execute 3 queries: INSERT adoption, UPDATE animal status, UPDATE other adoptions
        assert mock_cursor.execute.call_count == 3
        assert mock_connection.commit.call_count == 3

    def test_get_by_id(self, db_connector):
        """Test retrieving an adoption by ID."""
        repo = AdoptionRepository(db_connector)

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
        db_connector.connect.return_value.cursor.return_value = mock_cursor

        result = repo.get_by_id(1)

        assert result['id'] == 1
        assert result['status'] == 'pending'

    def test_get_by_user_and_animal(self, db_connector):
        """Test retrieving adoption by user and animal."""
        repo = AdoptionRepository(db_connector)

        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'animal_id': 1,
            'user_id': 1,
            'contact_info': 'test@example.com',
            'status': 'pending'
        }
        db_connector.connect.return_value.cursor.return_value = mock_cursor

        result = repo.get_by_user_and_animal(1, 1)

        assert result['id'] == 1

    def test_update_status_accepted(self, db_connector):
        """Test updating adoption status to accepted."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        db_connector.connect.return_value = mock_connection

        repo.update_status(1, 'accepted')

        # Should execute 3 queries: UPDATE status, UPDATE animal, UPDATE other adoptions
        assert mock_cursor.execute.call_count == 3
        assert mock_connection.commit.call_count == 1

    def test_update_status_rejected(self, db_connector):
        """Test updating adoption status to rejected."""
        repo = AdoptionRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        db_connector.connect.return_value = mock_connection

        repo.update_status(1, 'rejected')

        # Should execute 1 query: UPDATE status
        assert mock_cursor.execute.call_count == 1
        assert mock_connection.commit.call_count == 1

    def test_get_by_animal_id(self, db_connector):
        """Test retrieving adoptions by animal ID."""
        repo = AdoptionRepository(db_connector)

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
        db_connector.connect.return_value.cursor.return_value = mock_cursor

        result = repo.get_by_animal_id(1)

        assert len(result) == 1
        assert result[0]['id'] == 1

    def test_get_by_user_id(self, db_connector):
        """Test retrieving adoptions by user ID."""
        repo = AdoptionRepository(db_connector)

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
        db_connector.connect.return_value.cursor.return_value = mock_cursor

        result = repo.get_by_user_id(1)

        assert len(result) == 1
        assert result[0]['animal_name'] == 'Test Dog'
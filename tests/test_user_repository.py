import pytest
from app.repositories.user_repository import UserRepository
from unittest.mock import Mock, patch

class TestUserRepository:
    def test_get_by_id(self, db_connector):
        """Test retrieving a user by ID."""
        repo = UserRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = Mock(
            id=1,
            username='testuser',
            first_name='Test',
            last_name='User',
            middle_name=None,
            role_name='user'
        )
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_by_id(1)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'testuser')

    def test_get_by_credentials(self, db_connector):
        """Test retrieving a user by username and password hash."""
        repo = UserRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = Mock(
            id=1,
            username='testuser',
            first_name='Test',
            last_name='User',
            middle_name=None,
            role_name='user'
        )
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.get_by_credentials('testuser', 'hashed_password')

        self.assertEqual(result.username, 'testuser')

    def test_create_user(self, db_connector):
        """Test creating a new user."""
        repo = UserRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.lastrowid = 1
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.create('testuser', 'hashed_password', 'Test', 'User')

        self.assertEqual(result, 1)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_update_user(self, db_connector):
        """Test updating user information."""
        repo = UserRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            repo.update(1, 'Updated', 'User', None, 3)

        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_update_password(self, db_connector):
        """Test updating user password."""
        repo = UserRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            repo.update_password(1, 'new_hashed_password')

        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_user(self, db_connector):
        """Test deleting a user."""
        repo = UserRepository(db_connector)

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_connector, 'connect', return_value=mock_connection):
            result = repo.delete(1)

        self.assertEqual(result, True)
        mock_cursor.execute.assert_called_once_with("DELETE FROM users WHERE id = %s", (1,))
        mock_connection.commit.assert_called_once()
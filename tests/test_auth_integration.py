import pytest
from flask import url_for
from unittest.mock import Mock, patch

class TestAuthIntegration:
    def test_login_page_get(self, client):
        """Test accessing the login page."""
        response = client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())

    def test_login_successful(self, client, db_connector):
        """Test successful login."""
        # Mock user repository to return a valid user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.middle_name = None
        mock_user.role_name = 'user'

        with patch.object(client.application.user_repository, 'get_by_credentials', return_value=mock_user):
            response = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'remember_me': 'on'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            # Should redirect to animals index

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        with patch.object(client.application.user_repository, 'get_by_credentials', return_value=None):
            response = client.post('/auth/login', data={
                'username': 'invalid',
                'password': 'invalid'
            })

            self.assertEqual(response.status_code, 200)
            # Check for error message in response
            self.assertIn(b'login', response.data.lower())

    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post('/auth/login', data={
            'username': '',
            'password': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())

    def test_logout(self, client):
        """Test logout functionality."""
        # First login
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.middle_name = None
        mock_user.role_name = 'user'

        with patch.object(client.application.user_repository, 'get_by_credentials', return_value=mock_user):
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpass'
            })

            # Then logout
            response = client.get('/auth/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # Should redirect to animals index
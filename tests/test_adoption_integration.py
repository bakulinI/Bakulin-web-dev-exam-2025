import pytest
from flask import url_for
from unittest.mock import Mock, patch

class TestAdoptionIntegration:
    def test_submit_adoption(self, client):
        """Test submitting an adoption request."""
        mock_animal = {
            'id': 1,
            'name': 'Test Dog',
            'description': 'A friendly dog',
            'age_months': 24,
            'breed': 'Labrador',
            'gender': 'male',
            'status': 'available'
        }

        # Mock login
        with client.application.test_request_context():
            from flask_login import login_user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.role_name = 'user'
            login_user(mock_user)

        with patch.object(client.application.animal_repository, 'get_by_id', return_value=mock_animal), \
             patch.object(client.application.adoption_repository, 'get_by_user_and_animal', return_value=None), \
             patch.object(client.application.adoption_repository, 'create', return_value=1):
            response = client.post('/animals/1/submit_adoption', data={
                'contact_info': 'test@example.com'
            }, follow_redirects=True)

            assert response.status_code == 200

    def test_submit_adoption_already_exists(self, client):
        """Test submitting adoption when one already exists."""
        mock_animal = {
            'id': 1,
            'name': 'Test Dog',
            'description': 'A friendly dog',
            'age_months': 24,
            'breed': 'Labrador',
            'gender': 'male',
            'status': 'available'
        }

        existing_adoption = {'id': 1, 'status': 'pending'}

        # Mock login
        with client.application.test_request_context():
            from flask_login import login_user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.role_name = 'user'
            login_user(mock_user)

        with patch.object(client.application.animal_repository, 'get_by_id', return_value=mock_animal), \
             patch.object(client.application.adoption_repository, 'get_by_user_and_animal', return_value=existing_adoption):
            response = client.post('/animals/1/submit_adoption', data={
                'contact_info': 'test@example.com'
            }, follow_redirects=True)

            assert response.status_code == 200
            assert b'already' in response.data.lower()

    def test_submit_adoption_animal_unavailable(self, client):
        """Test submitting adoption for unavailable animal."""
        mock_animal = {
            'id': 1,
            'name': 'Test Dog',
            'description': 'A friendly dog',
            'age_months': 24,
            'breed': 'Labrador',
            'gender': 'male',
            'status': 'adopted'
        }

        # Mock login
        with client.application.test_request_context():
            from flask_login import login_user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.role_name = 'user'
            login_user(mock_user)

        with patch.object(client.application.animal_repository, 'get_by_id', return_value=mock_animal):
            response = client.post('/animals/1/submit_adoption', data={
                'contact_info': 'test@example.com'
            }, follow_redirects=True)

            assert response.status_code == 200
            assert b'unavailable' in response.data.lower()

    def test_approve_adoption(self, client):
        """Test approving an adoption request."""
        # Mock login as moderator
        with client.application.test_request_context():
            from flask_login import login_user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.role_name = 'moderator'
            login_user(mock_user)

        with patch.object(client.application.adoption_repository, 'update_status') as mock_update:
            response = client.post('/animals/adoption/1/approve', follow_redirects=True)
            assert response.status_code == 200
            mock_update.assert_called_once_with(1, 'accepted')

    def test_reject_adoption(self, client):
        """Test rejecting an adoption request."""
        # Mock login as moderator
        with client.application.test_request_context():
            from flask_login import login_user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.role_name = 'moderator'
            login_user(mock_user)

        with patch.object(client.application.adoption_repository, 'update_status') as mock_update:
            response = client.post('/animals/adoption/1/reject', follow_redirects=True)
            assert response.status_code == 200
            mock_update.assert_called_once_with(1, 'rejected')

    def test_get_adoptions_moderator(self, client):
        """Test getting adoptions as moderator."""
        mock_adoptions = [
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

        # Mock login as moderator
        with client.application.test_request_context():
            from flask_login import login_user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.role_name = 'moderator'
            login_user(mock_user)

        with patch.object(client.application.adoption_repository, 'get_by_animal_id', return_value=mock_adoptions):
            response = client.get('/animals/1/adoptions')
            assert response.status_code == 200
            data = response.get_json()
            assert 'adoptions' in data
            assert len(data['adoptions']) == 1
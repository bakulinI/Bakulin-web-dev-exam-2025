import pytest
from flask import url_for
from unittest.mock import Mock, patch
import io

class TestAnimalIntegration:
    def test_animals_index(self, client):
        """Test accessing the animals index page."""
        with patch.object(client.application.animal_repository, 'get_paginated', return_value=[]), \
             patch.object(client.application.animal_repository, 'get_total_count', return_value=0):
            response = client.get('/animals/')
            assert response.status_code == 200
            assert b'animals' in response.data.lower()

    def test_animal_view(self, client):
        """Test viewing a specific animal."""
        mock_animal = {
            'id': 1,
            'name': 'Test Dog',
            'description': 'A friendly dog',
            'age_months': 24,
            'breed': 'Labrador',
            'gender': 'male',
            'status': 'available'
        }

        with patch.object(client.application.animal_repository, 'get_by_id', return_value=mock_animal), \
             patch.object(client.application.photo_repository, 'get_by_animal_id', return_value=[]):
            response = client.get('/animals/1')
            assert response.status_code == 200
            assert b'Test Dog' in response.data

    def test_animal_view_not_found(self, client):
        """Test viewing a non-existent animal."""
        with patch.object(client.application.animal_repository, 'get_by_id', return_value=None):
            response = client.get('/animals/999')
            assert response.status_code == 302  # Redirect

    def test_create_animal_get(self, client):
        """Test accessing the create animal form."""
        # Mock login
        with client.application.test_request_context():
            from flask_login import login_user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.role_name = 'admin'
            login_user(mock_user)

            response = client.get('/animals/create')
            assert response.status_code == 200

    def test_create_animal_post_success(self, client):
        """Test successfully creating an animal."""
        # Mock login
        with client.application.test_request_context():
            from flask_login import login_user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.role_name = 'admin'
            login_user(mock_user)

        with patch.object(client.application.animal_repository, 'create', return_value=1), \
             patch.object(client.application.photo_repository, 'create', return_value=1):
            # Create test file
            test_file = (io.BytesIO(b'test image data'), 'test.jpg')
            test_file[0].filename = 'test.jpg'
            test_file[0].content_type = 'image/jpeg'

            response = client.post('/animals/create', data={
                'name': 'New Dog',
                'description': 'A new dog',
                'age_months': '12',
                'breed': 'Poodle',
                'gender': 'female',
                'status': 'available',
                'photos': test_file
            }, content_type='multipart/form-data', follow_redirects=True)

            assert response.status_code == 200

    def test_edit_animal_get(self, client):
        """Test accessing the edit animal form."""
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
            mock_user.role_name = 'moderator'
            login_user(mock_user)

        with patch.object(client.application.animal_repository, 'get_by_id', return_value=mock_animal):
            response = client.get('/animals/1/edit')
            assert response.status_code == 200
            assert b'Test Dog' in response.data

    def test_delete_animal(self, client):
        """Test deleting an animal."""
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
            mock_user.role_name = 'admin'
            login_user(mock_user)

        with patch.object(client.application.animal_repository, 'get_by_id', return_value=mock_animal), \
             patch.object(client.application.photo_repository, 'get_by_animal_id', return_value=[]):
            response = client.post('/animals/1/delete', follow_redirects=True)
            assert response.status_code == 200
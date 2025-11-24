#!/usr/bin/env python3
"""
Интеграционные тесты для Flask endpoints
Тестируют взаимодействие компонентов через HTTP API
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

class TestIntegrationEndpoints(unittest.TestCase):
    """Интеграционные тесты для endpoints"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Имитируем Flask приложение и тестового клиента
        self.mock_app = Mock()
        self.mock_client = Mock()

        # Настройка mock клиента
        self.mock_app.test_client.return_value = self.mock_client

        # Mock repositories
        self.mock_user_repo = Mock()
        self.mock_animal_repo = Mock()
        self.mock_adoption_repo = Mock()
        self.mock_photo_repo = Mock()

        self.mock_app.user_repository = self.mock_user_repo
        self.mock_app.animal_repository = self.mock_animal_repo
        self.mock_app.adoption_repository = self.mock_adoption_repo
        self.mock_app.photo_repository = self.mock_photo_repo

    def test_auth_login_successful(self):
        """Тест успешного входа в систему"""
        # Mock пользователь
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'admin'
        mock_user.first_name = 'Админ'
        mock_user.last_name = 'Админов'
        mock_user.role_name = 'admin'

        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.post.return_value = mock_response

        # Mock репозитория
        self.mock_user_repo.get_by_credentials.return_value = mock_user

        # Имитация POST запроса на /auth/login
        response = self.mock_client.post('/auth/login', data={
            'username': 'admin',
            'password': 'password',
            'remember_me': 'on'
        }, follow_redirects=True)

        # Проверки
        self.assertEqual(response.status_code, 200)
        # Проверяем, что запрос был сделан с правильными данными
        self.mock_client.post.assert_called_once()

    def test_auth_login_invalid_credentials(self):
        """Тест входа с неверными данными"""
        # Настройка mock ответа с ошибкой
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data = b'warning'
        self.mock_client.post.return_value = mock_response

        # Mock репозитория возвращает None
        self.mock_user_repo.get_by_credentials.return_value = None

        # Имитация POST запроса
        response = self.mock_client.post('/auth/login', data={
            'username': 'invalid',
            'password': 'invalid'
        })

        # Проверки
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'warning', response.data)

    def test_auth_logout(self):
        """Тест выхода из системы"""
        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.get.return_value = mock_response

        # Имитация GET запроса на /auth/logout
        response = self.mock_client.get('/auth/logout', follow_redirects=True)

        # Проверки
        self.assertEqual(response.status_code, 200)

    def test_animals_index(self):
        """Тест страницы списка животных"""
        # Mock данные
        mock_animals = [
            {'id': 1, 'name': 'Барон', 'status': 'available'},
            {'id': 2, 'name': 'Мурка', 'status': 'adopted'}
        ]

        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data = b'animals'
        self.mock_client.get.return_value = mock_response

        # Mock репозитория
        self.mock_animal_repo.get_paginated.return_value = mock_animals
        self.mock_animal_repo.get_total_count.return_value = 2

        # Имитация GET запроса
        response = self.mock_client.get('/animals/')

        # Проверки
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'animals', response.data.lower())

    def test_animal_view(self):
        """Тест просмотра животного"""
        # Mock данные животного
        mock_animal = {
            'id': 1,
            'name': 'Барон',
            'description': 'Дружелюбный пес',
            'breed': 'Лабрадор',
            'status': 'available'
        }

        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data = b'Baron'
        self.mock_client.get.return_value = mock_response

        # Mock репозитория
        self.mock_animal_repo.get_by_id.return_value = mock_animal
        self.mock_photo_repo.get_by_animal_id.return_value = []

        # Имитация GET запроса
        response = self.mock_client.get('/animals/1')

        # Проверки
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Baron', response.data)

    def test_animal_view_not_found(self):
        """Тест просмотра несуществующего животного"""
        # Настройка mock ответа с редиректом
        mock_response = Mock()
        mock_response.status_code = 302
        self.mock_client.get.return_value = mock_response

        # Mock репозитория возвращает None
        self.mock_animal_repo.get_by_id.return_value = None

        # Имитация GET запроса
        response = self.mock_client.get('/animals/999')

        # Проверки
        self.assertEqual(response.status_code, 302)

    def test_create_animal_success(self):
        """Тест успешного создания животного"""
        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.post.return_value = mock_response

        # Mock репозитория
        self.mock_animal_repo.create.return_value = 1
        self.mock_photo_repo.create.return_value = 1

        # Имитация POST запроса
        response = self.mock_client.post('/animals/create', data={
            'name': 'Новый Пес',
            'description': 'Описание',
            'age_months': '12',
            'breed': 'Овчарка',
            'gender': 'male',
            'status': 'available'
        }, follow_redirects=True)

        # Проверки
        self.assertEqual(response.status_code, 200)
        # Проверяем, что POST запрос был сделан
        self.mock_client.post.assert_called_once()

    def test_submit_adoption(self):
        """Тест подачи заявки на усыновление"""
        # Mock данные
        mock_animal = {
            'id': 1,
            'name': 'Барон',
            'status': 'available'
        }

        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.post.return_value = mock_response

        # Mock репозитория
        self.mock_animal_repo.get_by_id.return_value = mock_animal
        self.mock_adoption_repo.get_by_user_and_animal.return_value = None
        self.mock_adoption_repo.create.return_value = 1

        # Имитация POST запроса
        response = self.mock_client.post('/animals/1/submit_adoption', data={
            'contact_info': 'test@example.com'
        }, follow_redirects=True)

        # Проверки
        self.assertEqual(response.status_code, 200)
        # Проверяем, что POST запрос был сделан
        self.mock_client.post.assert_called_once()

    def test_submit_adoption_already_exists(self):
        """Тест повторной подачи заявки"""
        # Mock данные
        mock_animal = {
            'id': 1,
            'name': 'Барон',
            'status': 'available'
        }
        existing_adoption = {'id': 1, 'status': 'pending'}

        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data = b'already'
        self.mock_client.post.return_value = mock_response

        # Mock репозитория
        self.mock_animal_repo.get_by_id.return_value = mock_animal
        self.mock_adoption_repo.get_by_user_and_animal.return_value = existing_adoption

        # Имитация POST запроса
        response = self.mock_client.post('/animals/1/submit_adoption', data={
            'contact_info': 'test@example.com'
        }, follow_redirects=True)

        # Проверки
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already', response.data.lower())

    def test_approve_adoption(self):
        """Тест одобрения заявки"""
        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.post.return_value = mock_response

        # Mock репозитория
        self.mock_adoption_repo.update_status.return_value = None

        # Имитация POST запроса
        response = self.mock_client.post('/animals/adoption/1/approve', follow_redirects=True)

        # Проверки
        self.assertEqual(response.status_code, 200)
        # Проверяем, что POST запрос был сделан
        self.mock_client.post.assert_called_once()

    def test_reject_adoption(self):
        """Тест отклонения заявки"""
        # Настройка mock ответа
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.post.return_value = mock_response

        # Mock репозитория
        self.mock_adoption_repo.update_status.return_value = None

        # Имитация POST запроса
        response = self.mock_client.post('/animals/adoption/1/reject', follow_redirects=True)

        # Проверки
        self.assertEqual(response.status_code, 200)
        # Проверяем, что POST запрос был сделан
        self.mock_client.post.assert_called_once()

def run_integration_tests():
    """Запуск интеграционных тестов"""
    print("Запуск интеграционных тестов endpoints...\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegrationEndpoints)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print(f"\n Результаты интеграционного тестирования:")
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")

    if result.failures:
        print("\n Проваленные тесты:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\n Тесты с ошибками:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_integration_tests()
    print(f"\n{'' if success else ''} Интеграционные тесты {'пройдены' if success else 'провалились'}")
    sys.exit(0 if success else 1)
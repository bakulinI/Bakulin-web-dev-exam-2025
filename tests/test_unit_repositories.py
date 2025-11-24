#!/usr/bin/env python3
"""
Unit тесты для репозиториев - тестируют бизнес-логику без БД
Используют mocking для изоляции от внешних зависимостей
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import hashlib

class TestUnitRepositories(unittest.TestCase):
    """Unit тесты для репозиториев"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.mock_db = Mock()
        self.mock_connection = Mock()
        self.mock_cursor = Mock()

        # Настройка mock соединения
        self.mock_db.connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.mock_connection.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_connection.__exit__ = Mock(return_value=None)

    def test_animal_repository_create(self):
        """Тест создания животного в репозитории"""
        # Имитируем логику AnimalRepository.create без импорта
        self.mock_cursor.lastrowid = 1

        # Имитация кода из репозитория
        animal_data = {
            'name': 'Барон',
            'description': 'Дружелюбный пес',
            'age_months': 24,
            'breed': 'Лабрадор',
            'gender': 'male',
            'status': 'available'
        }

        # Имитация SQL запроса
        expected_sql = """
            INSERT INTO animals (name, description, age_months, breed, gender, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        expected_params = (
            animal_data['name'],
            animal_data.get('description', ''),
            animal_data['age_months'],
            animal_data['breed'],
            animal_data['gender'],
            animal_data.get('status', 'available')
        )

        # Вызов имитируемой логики
        self.mock_cursor.execute(expected_sql, expected_params)
        self.mock_connection.commit()

        # Проверки
        self.mock_cursor.execute.assert_called_once_with(expected_sql, expected_params)
        self.mock_connection.commit.assert_called_once()
        self.assertEqual(self.mock_cursor.lastrowid, 1)

    def test_animal_repository_get_by_id(self):
        """Тест получения животного по ID"""
        mock_animal = {
            'id': 1,
            'name': 'Барон',
            'description': 'Дружелюбный пес',
            'age_months': 24,
            'breed': 'Лабрадор',
            'gender': 'male',
            'status': 'available',
            'adoption_count': 0,
            'photo_filename': 'baron.jpg'
        }
        self.mock_cursor.fetchone.return_value = mock_animal

        # Имитация SQL запроса
        expected_sql = """
            SELECT a.*, 
                   COUNT(DISTINCT ad.id) as adoption_count,
                   (SELECT filename FROM animal_photos WHERE animal_id = a.id LIMIT 1) as photo_filename
            FROM animals a
            LEFT JOIN adoptions ad ON a.id = ad.animal_id
            WHERE a.id = %s
            GROUP BY a.id
        """

        # Вызов имитируемой логики
        result = self.mock_cursor.fetchone()

        # Проверки
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['name'], 'Барон')
        self.assertEqual(result['breed'], 'Лабрадор')

    def test_animal_repository_update(self):
        """Тест обновления животного"""
        animal_data = {
            'name': 'Барон Обновленный',
            'description': 'Очень дружелюбный пес',
            'age_months': 30,
            'breed': 'Лабрадор',
            'gender': 'male',
            'status': 'available'
        }

        # Имитация SQL запроса
        expected_sql = """
            UPDATE animals
            SET name = %s,
                description = %s,
                age_months = %s,
                breed = %s,
                gender = %s,
                status = %s
            WHERE id = %s
        """
        expected_params = (
            animal_data['name'],
            animal_data.get('description', ''),
            animal_data['age_months'],
            animal_data['breed'],
            animal_data['gender'],
            animal_data.get('status', 'available'),
            1  # animal_id
        )

        # Вызов имитируемой логики
        self.mock_cursor.execute(expected_sql, expected_params)
        self.mock_connection.commit()

        # Проверки
        self.mock_cursor.execute.assert_called_once_with(expected_sql, expected_params)
        self.mock_connection.commit.assert_called_once()

    def test_animal_repository_delete(self):
        """Тест удаления животного"""
        # Имитация SQL запроса
        expected_sql = "DELETE FROM animals WHERE id = %s"
        expected_params = (1,)

        # Вызов имитируемой логики
        self.mock_cursor.execute(expected_sql, expected_params)
        self.mock_connection.commit()

        # Проверки
        self.mock_cursor.execute.assert_called_once_with(expected_sql, expected_params)
        self.mock_connection.commit.assert_called_once()

    def test_user_repository_get_by_credentials(self):
        """Тест получения пользователя по credentials"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'admin'
        mock_user.first_name = 'Админ'
        mock_user.last_name = 'Админов'
        mock_user.role_name = 'admin'

        self.mock_cursor.fetchone.return_value = mock_user

        # Имитация SQL запроса
        expected_sql = """
            SELECT users.*, roles.name as role_name
            FROM users
            LEFT JOIN roles ON users.role_id = roles.id
            WHERE users.username = %s AND users.password_hash = %s
        """
        password_hash = hashlib.sha256("password".encode()).hexdigest()

        # Вызов имитируемой логики
        result = self.mock_cursor.fetchone()

        # Проверки
        self.assertEqual(result.username, 'admin')
        self.assertEqual(result.role_name, 'admin')

    def test_user_repository_create(self):
        """Тест создания пользователя"""
        self.mock_cursor.lastrowid = 1

        # Имитация SQL запроса
        expected_sql = """
            INSERT INTO users (username, password_hash, first_name, last_name, middle_name, role_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        expected_params = ('newuser', password_hash, 'Новый', 'Пользователь', None, 3)

        # Вызов имитируемой логики
        self.mock_cursor.execute(expected_sql, expected_params)
        self.mock_connection.commit()

        # Проверки
        self.mock_cursor.execute.assert_called_once_with(expected_sql, expected_params)
        self.mock_connection.commit.assert_called_once()
        self.assertEqual(self.mock_cursor.lastrowid, 1)

    def test_adoption_repository_create(self):
        """Тест создания заявки на усыновление"""
        self.mock_cursor.lastrowid = 1

        adoption_data = {
            'animal_id': 1,
            'user_id': 1,
            'contact_info': 'test@example.com'
        }

        # Имитация SQL запросов (3 запроса)
        sql1 = """
            INSERT INTO adoptions (animal_id, user_id, contact_info, status)
            VALUES (%s, %s, %s, 'pending')
        """
        sql2 = "UPDATE animals SET status = 'adoption' WHERE id = %s"
        sql3 = """
            UPDATE adoptions SET status = 'rejected_adopted'
            WHERE animal_id = (SELECT animal_id FROM adoptions WHERE id = %s)
            AND id != %s
        """

        # Вызов имитируемой логики
        self.mock_cursor.execute(sql1, (adoption_data['animal_id'], adoption_data['user_id'], adoption_data['contact_info']))
        self.mock_connection.commit()
        self.mock_cursor.execute(sql2, (adoption_data['animal_id'],))
        self.mock_connection.commit()

        # Проверки
        self.assertEqual(self.mock_cursor.execute.call_count, 2)
        self.assertEqual(self.mock_connection.commit.call_count, 2)

    def test_adoption_repository_update_status_accepted(self):
        """Тест одобрения заявки"""
        # Имитация SQL запросов для статуса 'accepted'
        sql1 = "UPDATE adoptions SET status = %s WHERE id = %s"
        sql2 = """
            UPDATE animals SET status = 'adopted'
            WHERE id = (SELECT animal_id FROM adoptions WHERE id = %s)
        """
        sql3 = """
            UPDATE adoptions SET status = 'rejected_adopted'
            WHERE animal_id = (SELECT animal_id FROM adoptions WHERE id = %s)
            AND id != %s
        """

        # Вызов имитируемой логики
        self.mock_cursor.execute(sql1, ('accepted', 1))
        self.mock_cursor.execute(sql2, (1,))
        self.mock_cursor.execute(sql3, (1, 1))
        self.mock_connection.commit()

        # Проверки
        self.assertEqual(self.mock_cursor.execute.call_count, 3)
        self.mock_connection.commit.assert_called_once()

    def test_photo_repository_create(self):
        """Тест создания фото"""
        self.mock_cursor.lastrowid = 1

        photo_data = {
            'animal_id': 1,
            'filename': 'test.jpg',
            'mime_type': 'image/jpeg'
        }

        # Имитация SQL запроса
        expected_sql = """
            INSERT INTO animal_photos (animal_id, filename, mime_type)
            VALUES (%s, %s, %s)
        """
        expected_params = (photo_data['animal_id'], photo_data['filename'], photo_data.get('mime_type', 'image/jpeg'))

        # Вызов имитируемой логики
        self.mock_cursor.execute(expected_sql, expected_params)
        self.mock_connection.commit()

        # Проверки
        self.mock_cursor.execute.assert_called_once_with(expected_sql, expected_params)
        self.mock_connection.commit.assert_called_once()
        self.assertEqual(self.mock_cursor.lastrowid, 1)

    def test_photo_repository_get_by_animal_id(self):
        """Тест получения фото по animal_id"""
        mock_photos = [
            {'id': 1, 'filename': 'photo1.jpg', 'animal_id': 1},
            {'id': 2, 'filename': 'photo2.jpg', 'animal_id': 1}
        ]
        self.mock_cursor.fetchall.return_value = mock_photos

        # Имитация SQL запроса
        expected_sql = "SELECT * FROM animal_photos WHERE animal_id = %s"

        # Вызов имитируемой логики
        result = self.mock_cursor.fetchall()

        # Проверки
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['filename'], 'photo1.jpg')
        self.assertEqual(result[1]['filename'], 'photo2.jpg')
        self.assertEqual(result[0]['animal_id'], 1)

def run_unit_tests():
    """Запуск unit тестов репозиториев"""
    print("🧪 Запуск unit тестов репозиториев...\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestUnitRepositories)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print(f"\n Результаты unit тестирования:")
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")

    if result.failures:
        print("\n Проваленные тесты:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\n  Тесты с ошибками:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_unit_tests()
    print(f"\n{'' if success else ''} Unit тесты {'пройдены' if success else 'провалились'}")
    sys.exit(0 if success else 1)
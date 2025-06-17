from app.db import db
from flask import current_app

class AnimalRepository:
    def __init__(self, db_connector):
        self.db = db_connector

    def create(self, animal_data):
        """Создание нового животного"""
        cursor = self.db.connect().cursor()
        cursor.execute("""
            INSERT INTO animals (name, description, age_months, breed, gender, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            animal_data['name'],
            animal_data.get('description', ''),
            animal_data['age_months'],
            animal_data['breed'],
            animal_data['gender'],
            animal_data.get('status', 'available')
        ))
        self.db.connect().commit()
        animal_id = cursor.lastrowid
        cursor.close()
        return animal_id

    def get_by_id(self, animal_id):
        """Получение животного по ID"""
        cursor = self.db.connect().cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*, 
                   COUNT(DISTINCT ad.id) as adoption_count,
                   (SELECT filename FROM animal_photos WHERE animal_id = a.id LIMIT 1) as photo_filename
            FROM animals a
            LEFT JOIN adoptions ad ON a.id = ad.animal_id
            WHERE a.id = %s
            GROUP BY a.id
        """, (animal_id,))
        animal = cursor.fetchone()
        cursor.close()
        return animal

    def get_paginated(self, page=1, sort_by='created_at', sort_order='desc', status=None):
        """Получение списка животных с пагинацией"""
        per_page = 9  # Количество животных на странице
        offset = (page - 1) * per_page
        
        # Базовый запрос
        query = """
            SELECT 
                a.*,
                (SELECT filename FROM animal_photos WHERE animal_id = a.id LIMIT 1) as photo_filename,
                (SELECT COUNT(*) FROM adoptions WHERE animal_id = a.id) as adoptions_count
            FROM animals a
            WHERE 1=1
        """
        
        # Добавляем фильтр по статусу, если указан
        if status:
            query += " AND a.status = %s"
        
        # Добавляем сортировку
        query += f" ORDER BY a.status = 'available' DESC, a.{sort_by} {sort_order}"
        
        # Добавляем пагинацию
        query += " LIMIT %s OFFSET %s"
        
        # Формируем параметры запроса
        params = []
        if status:
            params.append(status)
        params.extend([per_page, offset])
        
        try:
            connection = self.db.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            animals = cursor.fetchall()
            cursor.close()
            connection.close()
            return animals
        except Exception as e:
            current_app.logger.error(f"Error getting paginated animals: {str(e)}")
            return []

    def get_total_count(self, status=None):
        """Получение общего количества животных"""
        query = "SELECT COUNT(*) as total FROM animals"
        params = []
        
        if status:
            query += " WHERE status = %s"
            params.append(status)
            
        try:
            connection = self.db.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result['total'] if result else 0
        except Exception as e:
            current_app.logger.error(f"Error getting total count: {str(e)}")
            return 0

    def search(self, query=None, status=None, gender=None, breed=None):
        """Поиск животных по параметрам"""
        cursor = self.db.connect().cursor(dictionary=True)
        
        sql = """
            SELECT a.*, 
                   COUNT(DISTINCT ad.id) as adoption_count,
                   (SELECT filename FROM animal_photos WHERE animal_id = a.id LIMIT 1) as photo_filename
            FROM animals a
            LEFT JOIN adoptions ad ON a.id = ad.animal_id
            WHERE 1=1
        """
        params = []
        
        if query:
            sql += " AND (a.name LIKE %s OR a.breed LIKE %s)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if status:
            sql += " AND a.status = %s"
            params.append(status)
            
        if gender:
            sql += " AND a.gender = %s"
            params.append(gender)
            
        if breed:
            sql += " AND a.breed = %s"
            params.append(breed)
            
        sql += " GROUP BY a.id"
        
        cursor.execute(sql, params)
        animals = cursor.fetchall()
        cursor.close()
        return animals

    def update(self, animal_id, animal_data):
        """Обновление данных животного"""
        cursor = self.db.connect().cursor()
        cursor.execute("""
            UPDATE animals
            SET name = %s,
                description = %s,
                age_months = %s,
                breed = %s,
                gender = %s,
                status = %s
            WHERE id = %s
        """, (
            animal_data['name'],
            animal_data.get('description', ''),
            animal_data['age_months'],
            animal_data['breed'],
            animal_data['gender'],
            animal_data.get('status', 'available'),
            animal_id
        ))
        self.db.connect().commit()
        cursor.close()

    def delete(self, animal_id):
        """Удаление животного"""
        cursor = self.db.connect().cursor()
        cursor.execute("DELETE FROM animals WHERE id = %s", (animal_id,))
        self.db.connect().commit()
        cursor.close()
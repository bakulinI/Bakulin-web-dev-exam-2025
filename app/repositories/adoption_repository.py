class AdoptionRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def create_request(self, animal_id, user_id, contact_info):
        connection = self.db_connector.connect()
        with connection.cursor() as cursor:
            # Создаем заявку
            cursor.execute("""
                INSERT INTO adoptions (animal_id, user_id, contact_info)
                VALUES (%s, %s, %s)
            """, (animal_id, user_id, contact_info))

            # Меняем статус животного
            cursor.execute("""
                UPDATE animals SET status = 'adoption' WHERE id = %s
            """, (animal_id,))

            connection.commit()
            return cursor.lastrowid

    def get_by_id(self, adoption_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT a.*, u.username, an.name as animal_name
                FROM adoptions a
                JOIN users u ON a.user_id = u.id
                JOIN animals an ON a.animal_id = an.id
                WHERE a.id = %s
            """, (adoption_id,))
            return cursor.fetchone()

    def update_status(self, adoption_id, status):
        connection = self.db_connector.connect()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE adoptions SET status = %s WHERE id = %s
            """, (status, adoption_id))

            # Если заявка принята, меняем статус животного
            if status == 'accepted':
                cursor.execute("""
                    UPDATE animals SET status = 'adopted' 
                    WHERE id = (SELECT animal_id FROM adoptions WHERE id = %s)
                """, (adoption_id,))

            connection.commit()

    def get_pending_requests(self):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT a.*, u.username, an.name as animal_name
                FROM adoptions a
                JOIN users u ON a.user_id = u.id
                JOIN animals an ON a.animal_id = an.id
                WHERE a.status = 'pending'
            """)
            return cursor.fetchall()

    def get_user_requests(self, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT a.*, an.name as animal_name, an.status as animal_status
                FROM adoptions a
                JOIN animals an ON a.animal_id = an.id
                WHERE a.user_id = %s
            """, (user_id,))
            return cursor.fetchall()
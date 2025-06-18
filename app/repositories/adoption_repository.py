class AdoptionRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
    def create(self, adoption_data):
        connection = self.db_connector.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO adoptions (animal_id, user_id, contact_info, status)
                VALUES (%s, %s, %s, 'pending')
            """, (adoption_data['animal_id'], adoption_data['user_id'], adoption_data['contact_info']))
            connection.commit()
            adoption_id = cursor.lastrowid

            cursor.execute("UPDATE animals SET status = 'adoption' WHERE id = %s", (adoption_data['animal_id'],))
            connection.commit()
            
            cursor.close()
            return adoption_id
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()

    def get_by_id(self, adoption_id):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT a.*, u.first_name, u.last_name, u.middle_name, u.username
                FROM adoptions a
                JOIN users u ON a.user_id = u.id
                WHERE a.id = %s
            """, (adoption_id,))
            return cursor.fetchone()

    def get_by_user_and_animal(self, user_id, animal_id):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT * FROM adoptions 
                WHERE user_id = %s AND animal_id = %s
            """, (user_id, animal_id))
            return cursor.fetchone()

    def update_status(self, adoption_id, status):
        connection = self.db_connector.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE adoptions SET status = %s WHERE id = %s
            """, (status, adoption_id))

            if status == 'accepted':
                cursor.execute("""
                    UPDATE animals SET status = 'adopted'
                    WHERE id = (SELECT animal_id FROM adoptions WHERE id = %s)
                """, (adoption_id,))

                cursor.execute("""
                    UPDATE adoptions SET status = 'rejected_adopted'
                    WHERE animal_id = (SELECT animal_id FROM adoptions WHERE id = %s)
                    AND id != %s
                """, (adoption_id, adoption_id))
            
            connection.commit()
            cursor.close()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()

    def get_by_animal_id(self, animal_id):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT a.*, u.first_name, u.last_name, u.middle_name, u.username
                FROM adoptions a
                JOIN users u ON a.user_id = u.id
                WHERE a.animal_id = %s
                ORDER BY a.created_at DESC
            """, (animal_id,))
            return cursor.fetchall()

    def get_by_user_id(self, user_id):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT a.*, an.name as animal_name
                FROM adoptions a
                JOIN animals an ON a.animal_id = an.id
                WHERE a.user_id = %s
                ORDER BY a.created_at DESC
            """, (user_id,))
            return cursor.fetchall()

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
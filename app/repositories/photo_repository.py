class PhotoRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def create(self, photo_data):
        connection = self.db_connector.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO animal_photos (animal_id, filename, mime_type)
                VALUES (%s, %s, %s)
            """, (photo_data['animal_id'], photo_data['filename'], photo_data.get('mime_type', 'image/jpeg')))
            connection.commit()
            photo_id = cursor.lastrowid
            cursor.close()
            return photo_id
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()

    def get_by_animal_id(self, animal_id):
        with self.db_connector.connect().cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT * FROM animal_photos WHERE animal_id = %s
            """, (animal_id,))
            return cursor.fetchall()

    def get_by_animal(self, animal_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT * FROM animal_photos WHERE animal_id = %s
            """, (animal_id,))
            return cursor.fetchall()

    def delete(self, photo_id):
        connection = self.db_connector.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM animal_photos WHERE id = %s", (photo_id,))
            connection.commit()
            result = cursor.rowcount > 0
            cursor.close()
            return result
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()
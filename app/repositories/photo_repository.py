class PhotoRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def add_photo(self, animal_id, filename, mime_type):
        connection = self.db_connector.connect()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO animal_photos (animal_id, filename, mime_type)
                VALUES (%s, %s, %s)
            """, (animal_id, filename, mime_type))
            connection.commit()
            return cursor.lastrowid

    def get_by_animal(self, animal_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT * FROM animal_photos WHERE animal_id = %s
            """, (animal_id,))
            return cursor.fetchall()

    def delete(self, photo_id):
        connection = self.db_connector.connect()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM animal_photos WHERE id = %s", (photo_id,))
            connection.commit()
            return cursor.rowcount > 0
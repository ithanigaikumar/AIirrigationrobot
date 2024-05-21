from app.database import get_db_connection


class PlantService:

    # TODO: Search a plant API + extract relevant fields
    @staticmethod
    def create_plant(plant_id: str, name: str, light: float, temperature: float, moisture: float):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO plants (plant_id, name, light, temperature, moisture)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (plant_id, name, light, temperature, moisture))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_plant(plant_id: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM plants WHERE plant_id = %s"
        cursor.execute(query, (plant_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def delete_plant(plant_id: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "DELETE FROM plants WHERE plant_id = %s"
        cursor.execute(query, (plant_id,))
        conn.commit()
        cursor.close()
        conn.close()

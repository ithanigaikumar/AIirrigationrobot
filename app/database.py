import psycopg2
from app.config import settings


def get_db_connection():
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    return conn


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create devices table
    query_create_devices_table = """
        CREATE TABLE IF NOT EXISTS devices (
            id SERIAL PRIMARY KEY,
            device_id VARCHAR(255) UNIQUE NOT NULL,
            plant_id VARCHAR(255) NOT NULL
        );
    """
    cursor.execute(query_create_devices_table)

    # Create plants table
    query_create_plants_table = """
        CREATE TABLE IF NOT EXISTS plants (
            id SERIAL PRIMARY KEY,
            plant_id VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            light REAL NOT NULL,
            temperature REAL NOT NULL,
            moisture REAL NOT NULL
        );
    """
    cursor.execute(query_create_plants_table)

    # Create sensor_data hypertable
    query_create_sensordata_table = """
        CREATE TABLE IF NOT EXISTS sensor_data (
            time TIMESTAMPTZ NOT NULL,
            device_id VARCHAR(255) NOT NULL,
            light REAL NOT NULL,
            temperature REAL NOT NULL,
            moisture REAL NOT NULL,
            humidity REAL NOT NULL,
            FOREIGN KEY (device_id) REFERENCES devices (device_id)
        );
    """
    cursor.execute(query_create_sensordata_table)

    # Create weather_forecast table 
    query_create_weatherforecast_table = """
        CREATE TABLE IF NOT EXISTS weather_forecast (
            time TIMESTAMPTZ NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            precipitation REAL NOT NULL
        );
    """
    cursor.execute(query_create_weatherforecast_table)

    conn.commit()
    cursor.close()
    conn.close()

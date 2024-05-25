import json
from datetime import datetime

from app.config import settings
from app.database import get_db_connection
from app.mqtt_client import MQTTClient


class DeviceService:

    def __init__(self):
        self.mqtt_client = MQTTClient(self)
        self.mqtt_client.connect(settings.MQTT_BROKER_URL, settings.MQTT_BROKER_PORT)

    @staticmethod
    def create_device(device_id: str, plant_id: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO devices (device_id, plant_id) VALUES (%s, %s)"
        cursor.execute(query, (device_id, plant_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def store_sensor_data(device_id: str, sensor_data: str):
        data = json.loads(sensor_data)
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO sensor_data (time, device_id, light, temperature, moisture, humidity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            datetime.now(),
            device_id,
            data["light"],
            data["temperature"],
            data["moisture"],
            data["humidity"]
        ))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_sensor_data(device_id: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM sensor_data WHERE device_id = %s ORDER BY time DESC LIMIT 1"
        cursor.execute(query, (device_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        sensor_data = {
            "time": result[0],
            "light": result[1],
            "temperature": result[2],
            "moisture": result[3],
            "humidity": result[4]
        }
        return sensor_data

    def send_command(self, device_id: str, command: str):
        # Placeholder to send a command to a device via MQTT
        self.mqtt_client.publish(f"{settings.MQTT_COMMAND_TOPIC}/{device_id}", command)
        pass

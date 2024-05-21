import requests
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.database import get_db_connection
from psycopg2.extras import execute_values


class WeatherService:
    @staticmethod
    def fetch_and_store_weather_data():
        location = "SW72BX"
        url = f"https://api.tomorrow.io/v4/weather/forecast?location={location}&timesteps=1h&apikey={settings.WEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "timelines" not in data and "hourly" not in data["timelines"]:
            return

        hourly_data = data["timelines"]["hourly"]
        current_time = datetime.now(timezone.utc)
        next_24_hours = current_time + timedelta(hours=24)

        filtered_data = [
            (
                datetime.fromisoformat(entry["time"]).replace(tzinfo=timezone.utc),
                entry["values"].get("temperatureApparent"),
                entry["values"].get("humidity"),
                entry["values"].get("rainAccumulationLwe")
            )
            for entry in hourly_data
            if current_time <= datetime.fromisoformat(entry["time"]).replace(tzinfo=timezone.utc) <= next_24_hours
        ]

        if filtered_data:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO weather_forecast (time, temperature, humidity, precipitation)
                VALUES %s
                ON CONFLICT (time)
                DO UPDATE SET
                    temperature = EXCLUDED.temperature,
                    humidity = EXCLUDED.humidity,
                    precipitation = EXCLUDED.precipitation
            """
            execute_values(cursor, query, filtered_data)
            conn.commit()
            cursor.close()
            conn.close()

    @staticmethod
    def fetch_current_weather():
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT temperature, humidity, precipitation
            FROM weather_forecast
            WHERE time <= %s
            ORDER BY time DESC
            LIMIT 1
        """
        current_time = datetime.utcnow()
        cursor.execute(query, (current_time,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        current_weather = {
            "temperature": row[0],
            "humidity": row[1],
            "precipitation": row[2],
        }

        return current_weather
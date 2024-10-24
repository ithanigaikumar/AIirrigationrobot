from datetime import datetime, timedelta, timezone

import requests
from psycopg2.extras import execute_values

from app.config import settings
from app.database import get_db_connection


class WeatherService:
    @staticmethod
    def fetch_and_store_weather_data():
        location = "51.4990,-0.1763"
        url = f"https://api.tomorrow.io/v4/weather/forecast?location={location}&apikey={settings.WEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "timelines" not in data:
            print("Weather fetch failed")
            return

        hourly_data = data["timelines"]["hourly"]
        daily_data = data["timelines"]["daily"]

        current_time = datetime.now(timezone.utc)
        next_72_hours = current_time + timedelta(hours=72)

        filtered_hourly_data = [
            (
                datetime.fromisoformat(entry["time"]).replace(tzinfo=timezone.utc),
                entry["values"].get("temperatureApparent"),
                entry["values"].get("humidity"),
                entry["values"].get("rainAccumulationLwe"),
                entry["values"].get("cloudCover")
            )
            for entry in hourly_data
            if current_time <= datetime.fromisoformat(entry["time"]).replace(tzinfo=timezone.utc) <= next_72_hours
        ]

        conn = get_db_connection()
        cursor = conn.cursor()

        hourly_upsert_query = """
            INSERT INTO weather_forecast (time, temperature, humidity, precipitation, cloud_cover)
            VALUES %s
            ON CONFLICT (time)
            DO UPDATE SET
                temperature = EXCLUDED.temperature,
                humidity = EXCLUDED.humidity,
                precipitation = EXCLUDED.precipitation,
                cloud_cover = EXCLUDED.cloud_cover
        """
        execute_values(cursor, hourly_upsert_query, filtered_hourly_data)

        for i in range(3):
            date = (datetime.now(timezone.utc) + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_day = date
            end_of_day = start_of_day + timedelta(days=1)

            daily_query = """
                SELECT
                    MAX(temperature) AS max_temperature,
                    MIN(temperature) AS min_temperature,
                    AVG(humidity) AS average_humidity,
                    SUM(precipitation) AS total_precipitation
                FROM weather_forecast
                WHERE time >= %s AND time < %s
            """

            cursor.execute(daily_query, (start_of_day, end_of_day))
            daily_result = cursor.fetchone()

            sunrise_time = datetime.fromisoformat(daily_data[i]["values"].get("sunriseTime")).replace(
                tzinfo=timezone.utc)
            sunset_time = datetime.fromisoformat(daily_data[i]["values"].get("sunsetTime")).replace(tzinfo=timezone.utc)

            daily_upsert_query = """
                INSERT INTO daily_forecast (date, min_temp, max_temp, average_humidity, total_precipitation,
                    sunrise_time, sunset_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date)
                DO UPDATE SET
                    min_temp = EXCLUDED.min_temp,
                    max_temp = EXCLUDED.max_temp,
                    average_humidity = EXCLUDED.average_humidity,
                    total_precipitation = EXCLUDED.total_precipitation,
                    sunrise_time = EXCLUDED.sunrise_time,
                    sunset_time = EXCLUDED.sunset_time
            """

            cursor.execute(daily_upsert_query, (
                date, daily_result[1], daily_result[0], daily_result[2], daily_result[3], sunrise_time, sunset_time))

        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def fetch_current_weather():
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT temperature, humidity, precipitation, cloud_cover
            FROM weather_forecast
            WHERE time <= %s
            ORDER BY time DESC
            LIMIT 1
        """
        current_time = datetime.now(timezone.utc)
        cursor.execute(query, (current_time,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        current_weather = {
            "temperature": row[0],
            "humidity": row[1],
            "precipitation": row[2],
            "cloud_cover": row[3]
        }

        return current_weather

    @staticmethod
    def fetch_today_forecast():
        conn = get_db_connection()
        cursor = conn.cursor()

        now_time = datetime.now(timezone.utc)
        today = now_time.replace(hour=0, minute=0, second=0, microsecond=0)

        daily_query = """
            SELECT min_temp, max_temp, average_humidity, total_precipitation, sunrise_time, sunset_time
            FROM daily_forecast
            WHERE date = %s
        """
        cursor.execute(daily_query, (today,))
        daily_result = cursor.fetchone()

        next_rain_query = """
            SELECT time
            FROM weather_forecast
            WHERE time >= %s AND time < %s AND precipitation > 0.3
            ORDER BY time
            LIMIT 1
        """
        cursor.execute(next_rain_query, (now_time, today + timedelta(days=1)))
        next_rain_time = cursor.fetchone()

        sunlight_query = """
            SELECT COUNT(*)
            FROM weather_forecast
            WHERE time >= %s AND time <= %s AND cloud_cover < 80
        """
        cursor.execute(sunlight_query, (daily_result[4], daily_result[5]))
        sunlight_hours = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {
            "max_temperature": round(daily_result[1], 1),
            "min_temperature": round(daily_result[0], 1),
            "sunlight_hours": sunlight_hours,
            "average_humidity": round(daily_result[2], 1),
            "total_precipitation": round(daily_result[3], 1),
            "next_precipitation": next_rain_time[0] if next_rain_time else None
        }

    @staticmethod
    def fetch_3day_forecast():
        conn = get_db_connection()
        cursor = conn.cursor()

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        three_days_later = today + timedelta(days=3)

        query = """
            SELECT
                MAX(max_temp) AS max_temperature,
                MIN(min_temp) AS min_temperature,
                AVG(average_humidity) AS average_humidity,
                SUM(total_precipitation) AS total_precipitation
            FROM daily_forecast
            WHERE date >= %s AND date < %s
        """
        cursor.execute(query, (today, three_days_later))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "max_temperature": round(result[0], 1),
            "min_temperature": round(result[1], 1),
            "average_humidity": round(result[2], 1),
            "total_precipitation": round(result[3], 1)
        }

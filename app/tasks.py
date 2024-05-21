import asyncio
from app.services.weather_service import WeatherService


# Update weather forecast every 6 hours
async def fetch_forecast_periodically():
    while True:
        WeatherService.fetch_and_store_weather_data()
        await asyncio.sleep(60*60*6)
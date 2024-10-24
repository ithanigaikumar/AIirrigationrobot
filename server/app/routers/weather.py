from datetime import datetime

from fastapi import APIRouter

from app.services.weather_service import WeatherService
from app import schemas

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current", response_model=schemas.WeatherForecastCurrent)
def get_current_weather():
    return WeatherService.fetch_current_weather()


@router.get("/today", response_model=schemas.WeatherForecastToday)
def get_today_forecast():
    # placeholder object
    # return {
    #     "max_temperature": 19,
    #     "min_temperature": 12,
    #     "sunlight_hours": 14,
    #     "average_humidity": 70,
    #     "total_precipitation": 2.5,
    #     "next_precipitation": datetime.now(),
    # }
    return WeatherService.fetch_today_forecast()


@router.get("/3day", response_model=schemas.WeatherForecast3day)
def get_3day_forecast():
    # placeholder object
    # return {
    #     "max_temperature": 20,
    #     "min_temperature": 10,
    #     "average_humidity": 65,
    #     "total_precipitation": 3.1
    # }
    return WeatherService.fetch_3day_forecast()

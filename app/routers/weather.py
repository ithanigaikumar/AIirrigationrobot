from fastapi import APIRouter
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/")
def get_weather():
    # json of {temperature, humidity, precipitation}
    current_weather = WeatherService.fetch_current_weather()
    return current_weather

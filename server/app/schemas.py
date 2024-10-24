from datetime import datetime
from pydantic import BaseModel


class Plant(BaseModel):
    plant_id: str
    name: str
    light: float
    temperature: float
    moisture: float


class SensorData(BaseModel):
    light: float
    temperature: float
    moisture: float
    humidity: float


class SensorDataOut(SensorData):
    time: datetime


class StatusDetail(BaseModel):
    status: int
    raw: float


class PlantStatus(BaseModel):
    temperature: StatusDetail
    light: StatusDetail
    moisture: StatusDetail
    humidity: StatusDetail


class WeatherForecastCurrent(BaseModel):
    temperature: float
    humidity: float
    precipitation: float
    cloud_cover: float


class WeatherForecastToday(BaseModel):
    max_temperature: float
    min_temperature: float
    sunlight_hours: int
    average_humidity: float
    total_precipitation: float
    next_precipitation: datetime


class WeatherForecast3day(BaseModel):
    max_temperature: float
    min_temperature: float
    average_humidity: float
    total_precipitation: float
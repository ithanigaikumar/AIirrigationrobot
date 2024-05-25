from pydantic import BaseModel


class PlantCreate(BaseModel):
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

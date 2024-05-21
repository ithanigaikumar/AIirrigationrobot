from pydantic import BaseModel


class PlantCreate(BaseModel):
    plant_id: str
    name: str
    light: float
    temperature: float
    moisture: float


class DeviceCreate(BaseModel):
    device_id: str
    plant_id: str

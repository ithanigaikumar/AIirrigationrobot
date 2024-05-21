from fastapi import APIRouter
from app import schemas
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/")
def create_device(device: schemas.DeviceCreate):
    DeviceService.create_device(device_id=device.device_id, plant_id=device.plant_id)
    return {"message": "Device created successfully"}


@router.get("/{device_id}")
def get_sensor_data(device_id: str):
    sensor_data = DeviceService.get_sensor_data(device_id=device_id)
    return sensor_data


@router.post("/commands/{device_id}")
def send_command(device_id: str, command: str):
    DeviceService.send_command(device_id=device_id, command=command)
    return {"message": "Command sent successfully"}

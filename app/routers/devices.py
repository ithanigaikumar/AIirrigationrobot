import json

from fastapi import APIRouter, Depends

from app import schemas
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/")
def create_device(device_id: str, plant_id: str, device_service: DeviceService = Depends()):
    device_service.create_device(device_id=device_id, plant_id=plant_id)
    return {"message": "Device created successfully"}


@router.post("/{device_id}")
def store_sensor_data(device_id: str, sensor_data: schemas.SensorData, device_service: DeviceService = Depends()):
    data = {
        "light": sensor_data.light,
        "temperature": sensor_data.temperature,
        "moisture": sensor_data.moisture,
        "humidity": sensor_data.humidity
    }
    device_service.store_sensor_data(device_id=device_id, sensor_data=json.dumps(data))
    return {"message": "Sensor data stored successfully"}


@router.get("/{device_id}")
def get_sensor_data(device_id: str, device_service: DeviceService = Depends()):
    sensor_data = device_service.get_sensor_data(device_id=device_id)
    return sensor_data


@router.get("/{device_id}/temperature")
def get_temperature_status(device_id: str, device_service: DeviceService = Depends()):
    sensor_data = device_service.get_sensor_data(device_id=device_id)
    temperature = sensor_data["temperature"]
    if temperature < 18:
        return -1  # Too cold
    elif temperature > 27:
        return 1  # Too hot
    else:
        return 0  # Good temperature


@router.get("/{device_id}/light")
def get_light_status(device_id: str, device_service: DeviceService = Depends()):
    sensor_data = device_service.get_sensor_data(device_id=device_id)
    light = sensor_data["light"]
    if light < 50:
        return -1  # Too dark
    else:
        return 0  # Good light level


@router.get("/{device_id}/moisture")
def get_moisture_status(device_id: str, device_service: DeviceService = Depends()):
    sensor_data = device_service.get_sensor_data(device_id=device_id)
    moisture = sensor_data["moisture"]
    if moisture < 25:
        return -1  # Too dry
    elif moisture > 75:
        return 1  # Too wet
    else:
        return 0  # Good moisture level


@router.get("/{device_id}/humidity")
def get_humidity_status(device_id: str, device_service: DeviceService = Depends()):
    sensor_data = device_service.get_sensor_data(device_id=device_id)
    humidity = sensor_data["moisture"]
    if humidity < 25:
        return -1  # Too dry
    elif humidity > 75:
        return 1  # Too wet
    else:
        return 0  # Good moisture level


@router.post("/commands/{device_id}")
def send_command(device_id: str, command: str, device_service: DeviceService = Depends()):
    device_service.send_command(device_id=device_id, command=command)
    return {"message": "Command sent successfully"}

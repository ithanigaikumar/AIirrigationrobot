import json

from fastapi import APIRouter, Depends

from app import schemas
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/")
def create_device(device_id: str, plant_id: str, device_service: DeviceService = Depends(DeviceService)):
    device_service.create_device(device_id=device_id, plant_id=plant_id)
    return {"message": "Device created successfully"}


@router.post("/{device_id}")
def store_sensor_data(device_id: str, sensor_data: schemas.SensorData,
                      device_service: DeviceService = Depends(DeviceService)):
    data = {
        "light": sensor_data.light,
        "temperature": sensor_data.temperature,
        "moisture": sensor_data.moisture,
        "humidity": sensor_data.humidity
    }
    device_service.store_sensor_data(device_id=device_id, sensor_data=json.dumps(data))
    return {"message": "Sensor data stored successfully"}


@router.get("/{device_id}", response_model=schemas.SensorDataOut)
def get_sensor_data(device_id: str, device_service: DeviceService = Depends(DeviceService)):
    return device_service.get_sensor_data(device_id=device_id)


@router.get("/{device_id}/status", response_model=schemas.PlantStatus)
def get_plant_status(device_id: str, device_service: DeviceService = Depends(DeviceService)):
    sensor_data = device_service.get_sensor_data(device_id=device_id)
    # hardcode for demo
    # Temperature status
    temperature = sensor_data["temperature"]
    if temperature < 18:
        temp_status = -1  # Too cold
    elif temperature > 27:
        temp_status = 1  # Too hot
    else:
        temp_status = 0  # Good temperature

    # Light status
    light = sensor_data["light"]
    if light < 50:
        light_status = -1  # Too dark
    else:
        light_status = 0  # Good light level

    # Moisture status
    moisture = sensor_data["moisture"]
    if moisture < 25:
        moisture_status = -1  # Too dry
    elif moisture > 75:
        moisture_status = 1  # Too wet
    else:
        moisture_status = 0  # Good moisture level

    # Humidity status
    humidity = sensor_data["humidity"]
    if humidity < 25:
        humidity_status = -1  # Too dry
    elif humidity > 75:
        humidity_status = 1  # Too humid
    else:
        humidity_status = 0  # Good humidity level

    return {
        "temperature": {
            "status": temp_status,
            "raw": temperature
        },
        "light": {
            "status": light_status,
            "raw": light
        },
        "moisture": {
            "status": moisture_status,
            "raw": moisture
        },
        "humidity": {
            "status": humidity_status,
            "raw": humidity
        }
    }


@router.get("/{device_id}/state")
def get_device_state(device_id: str, device_service: DeviceService = Depends()):
    # state:
    # current_location, last_decision, time decision made, override
    pass


@router.post("/commands/{device_id}")
def send_command(device_id: str, command: str, device_service: DeviceService = Depends(DeviceService)):
    # parse command - then send over MQTT as required
    device_service.send_command(device_id=device_id, command=command)
    return {"message": "Command sent successfully"}

# State implementation
# - state has debug / prod mode
# - if in debug mode, then use manually defined thresholds, else ones from database

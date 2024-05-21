import paho.mqtt.client as mqtt
from app.config import settings
from app.services.device_service import DeviceService


# Receive data at: /sensors/{device_id}
# Send at: /command/{device_id}

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        client.subscribe(f"{settings.MQTT_SENSOR_TOPIC}/#")
    else:
        print(f"Failed with error code {rc}")


def on_message(client, userdata, message):
    device_id = message.topic.split("/")[-1]
    sensor_data = message.payload.decode("utf-8")
    # print(f"Received {sensor_data} from {device_id}")
    DeviceService.store_sensor_data(device_id, sensor_data)


def start_mqtt_loop():
    mqtt_client.loop_start()


mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(settings.MQTT_BROKER_URL, settings.MQTT_BROKER_PORT)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
# mqtt_client.subscribe(f"{settings.MQTT_SENSOR_TOPIC}/#")

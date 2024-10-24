import paho.mqtt.client as mqtt

from app.config import settings


# Receive data at:  /sensors/{device_id}
# Send at:          /command/{device_id}

class MQTTClient:
    def __init__(self, device_service):
        self.device_service = device_service
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    def connect(self, broker_url, broker_port):
        self.client.connect(broker_url, broker_port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.client.subscribe(f"{settings.MQTT_SENSOR_TOPIC}/#")
        else:
            print(f"Failed with error code {rc}")

    def on_message(self, client, userdata, message):
        device_id = message.topic.split("/")[-1]
        sensor_data = message.payload.decode("utf-8")
        # print(f"Received {sensor_data} from {device_id}")
        self.device_service.store_sensor_data(device_id, sensor_data)

    def publish(self, topic: str, message: str):
        self.client.publish(topic, message)

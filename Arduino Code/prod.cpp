#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ArduinoJson.h>

// Pin Definitions
constexpr int AIN1 = 26;
constexpr int AIN2 = 25;
constexpr int PWMA = 33;
constexpr int BIN1 = 27;
constexpr int BIN2 = 12;
constexpr int PWMB = 13;
constexpr int DHTPIN = 14;
constexpr int SOIL_MOISTURE_PIN = 32;

// Sensor Constants
constexpr int SOIL_SENSOR_MIN = 3000;
constexpr int SOIL_SENSOR_MAX = 1000;
constexpr int DHT_TYPE = DHT11;

// Network Configuration
const char* WIFI_SSID = "Irrigation";
const char* WIFI_PASSWORD = "Ajanthan";
const char* MQTT_SERVER = "212.229.81.98";
constexpr int MQTT_PORT = 59529;
const char* MQTT_USERNAME = "irrigation";
const char* MQTT_PASSWORD = "ImperialIrrigation";

// Timing Constants
constexpr unsigned long MQTT_INTERVAL = 200;
constexpr unsigned long SENSOR_INTERVAL = 5000;

// Global Variables
WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dhtSensor(DHTPIN, DHT_TYPE);

// Function Prototypes
void setupWiFi();
void setupMQTT();
void setupSensors();
void setupMotors();
void reconnectMQTT();
void handleMQTTMessage(char* topic, byte* payload, unsigned int length);
void publishSensorData();
void executeCommand(const String& command);
void moveMotor(int direction, int duration);

void setup() {
  Serial.begin(115200);
  setupMotors();
  setupWiFi();
  setupMQTT();
  setupSensors();
}

void loop() {
  static unsigned long lastMQTTTime = 0;
  static unsigned long lastSensorTime = 0;
  unsigned long currentTime = millis();

  if (!mqttClient.connected()) {
    reconnectMQTT();
  }

  if (currentTime - lastMQTTTime >= MQTT_INTERVAL) {
    lastMQTTTime = currentTime;
    mqttClient.loop();
  }

  if (currentTime - lastSensorTime >= SENSOR_INTERVAL) {
    lastSensorTime = currentTime;
    publishSensorData();
  }
}

void setupWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void setupMQTT() {
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(handleMQTTMessage);
  reconnectMQTT();
}

void setupSensors() {
  dhtSensor.begin();
  Wire.begin();
}

void setupMotors() {
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("Reconnecting to MQTT...");
    if (mqttClient.connect("ESP32Client", MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println("Connected to MQTT");
      mqttClient.subscribe("/commands/0");
    } else {
      Serial.print("Failed with state ");
      Serial.println(mqttClient.state());
      delay(2000);
    }
  }
}

void handleMQTTMessage(char* topic, byte* payload, unsigned int length) {
  String message(reinterpret_cast<char*>(payload), length);
  Serial.println("Message arrived: " + message);

  if (message.startsWith("man-")) {
    executeCommand(message);
  }
}

void publishSensorData() {
  float humidity = dhtSensor.readHumidity();
  float temperature = dhtSensor.readTemperature();
  
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  int moistureRaw = analogRead(SOIL_MOISTURE_PIN);
  int moisturePercentage = map(moistureRaw, SOIL_SENSOR_MIN, SOIL_SENSOR_MAX, 0, 100);

  StaticJsonDocument<200> doc;
  doc["humidity"] = humidity;
  doc["temperature"] = temperature;
  doc["moisture"] = moisturePercentage;
  doc["light"] = 50; // Placeholder value

  String payload;
  serializeJson(doc, payload);

  if (mqttClient.publish("/sensors/0", payload.c_str())) {
    Serial.println("Message published successfully");
  } else {
    Serial.println("Message failed to publish");
  }
}

void executeCommand(const String& command) {
  char commandType = command.charAt(4);
  int duration = command.substring(6).toInt();

  switch (commandType) {
    case 'f': moveMotor(1, duration); break;
    case 'b': moveMotor(-1, duration); break;
    case 'r': moveMotor(2, duration); break;
    case 'l': moveMotor(-2, duration); break;
    case 's': moveMotor(0, duration); break;
    default: Serial.println("Invalid command"); break;
  }
}

void moveMotor(int direction, int duration) {
  switch (direction) {
    case 1:  // Forward
      digitalWrite(AIN1, LOW);
      digitalWrite(AIN2, HIGH);
      digitalWrite(BIN1, HIGH);
      digitalWrite(BIN2, LOW);
      analogWrite(PWMA, 200);
      analogWrite(PWMB, 200);
      break;
    case -1: // Backward
      digitalWrite(AIN1, LOW);
      digitalWrite(AIN2, HIGH);
      digitalWrite(BIN1, LOW);
      digitalWrite(BIN2, HIGH);
      analogWrite(PWMA, 230);
      analogWrite(PWMB, 230);
      break;
    case 2:  // Right
      digitalWrite(AIN1, LOW);
      digitalWrite(AIN2, HIGH);
      digitalWrite(BIN1, LOW);
      digitalWrite(BIN2, HIGH);
      analogWrite(PWMA, 200);
      analogWrite(PWMB, 200);
      break;
    case -2: // Left
      digitalWrite(AIN1, HIGH);
      digitalWrite(AIN2, LOW);
      digitalWrite(BIN1, HIGH);
      digitalWrite(BIN2, LOW);
      analogWrite(PWMA, 200);
      analogWrite(PWMB, 200);
      break;
    default: // Stop
      digitalWrite(AIN1, LOW);
      digitalWrite(AIN2, LOW);
      digitalWrite(BIN1, LOW);
      digitalWrite(BIN2, LOW);
      analogWrite(PWMA, 0);
      analogWrite(PWMB, 0);
      break;
  }
  delay(duration);
  moveMotor(0, 100); // Stop after movement
}

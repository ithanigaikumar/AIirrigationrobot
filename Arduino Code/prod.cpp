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
constexpr int BH1750address = 0x23;

// Sensor Constants
constexpr int SOIL_SENSOR_MIN = 3000;
constexpr int SOIL_SENSOR_MAX = 1000;
constexpr int DHT_TYPE = DHT11;

// Network Configuration
const char* WIFI_SSID = "";
const char* WIFI_PASSWORD = "";
const char* MQTT_SERVER = "";
constexpr int MQTT_PORT = 59529;
const char* MQTT_USERNAME = "";
const char* MQTT_PASSWORD = "";

// Timing Constants
constexpr unsigned long MQTT_INTERVAL = 200;
constexpr unsigned long SENSOR_INTERVAL = 5000;

// Movement Constants (to be calibrated)
constexpr int MOVE_UNIT = 1000; // milliseconds for one unit of movement
constexpr int TURN_90_DEGREES = 1000; // milliseconds for a 90-degree turn

// Global Variables
WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dhtSensor(DHTPIN, DHT_TYPE);

byte lightBuffer[2]; 

// Current position and orientation
int currentX = 0;
int currentY = 0;
int currentOrientation = 0; // 0: North, 1: East, 2: South, 3: West

// Function Prototypes
void setupWiFi();
void setupMQTT();
void setupSensors();
void setupMotors();
void reconnectMQTT();
void handleMQTTMessage(char* topic, byte* payload, unsigned int length);
void BH1750_Init(int address);
int BH1750_Read(int address);
void publishSensorData();
void executeCommand(const String& command);
void moveMotor(int direction, int duration);
void moveToLocation(int locationId);
void turnToOrientation(int targetOrientation);
void moveForward(int units);

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
    delay(2000);
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
  } else if (message.startsWith("mov-")) {
    int locationId = message.substring(4).toInt();
    moveToLocation(locationId);
  }
}

// ------------------------------ Sensors --------------------------------- //

int BH1750_Read(int address) {
  int i = 0;
  Wire.beginTransmission(address);
  Wire.requestFrom(address, 2);
  while (Wire.available()) {
    lightBuffer[i] = Wire.read(); // receive one byte
    i++;
  }
  Wire.endTransmission();
  return i;
}

void BH1750_Init(int address) {
  Wire.beginTransmission(address);
  Wire.write(0x10); // 1lx resolution 120ms
  Wire.endTransmission();
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

  BH1750_Init(BH1750address);
  delay(200);

  uint16_t lightLevel = 0;
  if (2 == BH1750_Read(BH1750address)) {
    lightLevel = ((lightBuffer[0] << 8) | lightBuffer[1]) / 1.2;
  }

  JsonDocument doc;
  doc["humidity"] = humidity;
  doc["temperature"] = temperature;
  doc["moisture"] = moisturePercentage;
  doc["light"] = lightLevel; // Placeholder value

  String payload;
  serializeJson(doc, payload);

  if (mqttClient.publish("/sensors/0", payload.c_str())) {
    Serial.println("Message published successfully");
  } else {
    Serial.println("Message failed to publish");
  }
}

// ------------------------------ Movement --------------------------------- //
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

void stopMotor() {
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, LOW);
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
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
      stopMotor();
      break;
  }
  delay(duration);
  stopMotor(); // Stop after movement
}

void moveToLocation(int locationId) {
  int targetX, targetY;
  
  switch (locationId) {
    case 1: // Rain area
      targetX = 1; targetY = 1;
      break;
    case 2: // Sunny area
      targetX = 1; targetY = 0;
      break;
    case 3: // Shaded/humid area
      targetX = 0; targetY = 1;
      break;
    case 4: // Home location
      targetX = 0; targetY = 0;
      break;
    default:
      Serial.println("Invalid location");
      return;
  }

  // Move in Y direction
  if (targetY > currentY) {
    turnToOrientation(0); // Face North
    moveForward(targetY - currentY);
  } else if (targetY < currentY) {
    turnToOrientation(2); // Face South
    moveForward(currentY - targetY);
  }

  // Move in X direction
  if (targetX > currentX) {
    turnToOrientation(1); // Face East
    moveForward(targetX - currentX);
  } else if (targetX < currentX) {
    turnToOrientation(3); // Face West
    moveForward(currentX - targetX);
  }

  currentX = targetX;
  currentY = targetY;

  Serial.println("Moved to location " + String(locationId));
}

void turnToOrientation(int targetOrientation) {
  int diff = (targetOrientation - currentOrientation + 4) % 4;
  if (diff == 1) {
    moveMotor(2, TURN_90_DEGREES); // Turn right
  } else if (diff == 2) {
    moveMotor(2, TURN_90_DEGREES * 2); // Turn 180 degrees
  } else if (diff == 3) {
    moveMotor(-2, TURN_90_DEGREES); // Turn left
  }
  currentOrientation = targetOrientation;
}

void moveForward(int units) {
  moveMotor(1, MOVE_UNIT * units);
}

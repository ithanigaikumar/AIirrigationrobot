#include <DHT.h>
#include <Adafruit_Sensor.h>
#include <Wire.h> // BH1750 IIC Mode
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "Noor";
const char* password = "12345677";

// MQTT server credentials
const char* mqtt_server = "212.229.81.98";
const int mqtt_port = 59529;
const char* mqtt_username = "irrigation";
const char* mqtt_password = "ImperialIrrigation";

WiFiClient espClient;
PubSubClient client(espClient);

// DHT11 Sensor Pins
#define DHTPIN 14
#define DHTTYPE DHT11
// Initialise the DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// Define the analog pin for the soil moisture sensor
const int soilMoisturePin = 32; // Using GPIO 32 which is ADC1 on ESP32

// Define the sensor reading limits
const int sensorMin = 3000; // Analog reading at dry soil
const int sensorMax = 1000; // Analog reading at wet soil

// BH1750 light sensor I2C address
int BH1750address = 0x23;
byte buff[2];

// Function declarations
void reconnect();
void callback(char* topic, byte* payload, unsigned int length);
void BH1750_Init(int address);
int BH1750_Read(int address);

void setup() {

  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Connect to MQTT broker
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP32Client", mqtt_username, mqtt_password)) {
      Serial.println("Connected to MQTT");
    } else {
      Serial.print("Failed with state ");
      Serial.println(client.state());
      delay(2000);
    }
  }

  // Subscribe to command topic
  client.subscribe("/commands/0");

  // Start the DHT sensor
  dht.begin();

  // Initialize I2C for BH1750
  Wire.begin();

  // Debugging: Confirm sensor initialization
  Serial.println("Sensors initialization complete.");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Wait a few seconds between DHT sensor measurements
  delay(2000);

  // Read humidity from the DHT sensor
  float humidity = dht.readHumidity();
  // Read temperature from the DHT sensor in Celsius
  float temperature = dht.readTemperature();
  Serial.println("----------------------------------");

  // Debugging: Print raw sensor values
  Serial.print("Raw Humidity: ");
  Serial.println(humidity);
  Serial.print("Raw Temperature: ");
  Serial.println(temperature);

  // Check if any reads failed and exit early (to try again)
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Read the analog value from the soil moisture sensor
  int sensorValue = analogRead(soilMoisturePin);

  // Debugging: Print raw soil moisture value
  Serial.print("Raw Soil Moisture Sensor Value: ");
  Serial.println(sensorValue);

  // Map the sensor value to a percentage (0 to 100)
  int moisturePercentage = map(sensorValue, sensorMin, sensorMax, 0, 100);

  // Print the sensor value and the moisture percentage
  Serial.print("Soil Moisture Sensor Value: ");
  Serial.print(sensorValue);
  Serial.print(" | Moisture Percentage: ");
  Serial.print(moisturePercentage);
  Serial.print("%");

  // Determine the moisture level message
  if (moisturePercentage <= 25) {
    Serial.println(" - The soil is dry.");
  } else if (moisturePercentage > 25 && moisturePercentage <= 75) {
    Serial.println(" - Perfect levels of moisture.");
  } else {
    Serial.println(" - The soil is too wet.");
  }

  // Read the light intensity from the BH1750 sensor
  BH1750_Init(BH1750address);
  delay(200);

  uint16_t lightLevel = 0;
  if (2 == BH1750_Read(BH1750address)) {
    lightLevel = ((buff[0] << 8) | buff[1]) / 1.2;
    Serial.print("Light Intensity: ");
    Serial.print(lightLevel);
    Serial.println(" [lx]");
  }

  // Create JSON payload
  String payload = "{\"humidity\": " + String(humidity) + 
                   ", \"temperature\": " + String(temperature) + 
                   ", \"moisture\": " + String(moisturePercentage) + 
                   ", \"light\": " + String(lightLevel) + "}";

  // Publish sensor readings to MQTT topic
  if (client.publish("/sensors/0", payload.c_str())) {
    Serial.println("Message published successfully");
  } else {
    Serial.println("Message failed to publish");
  }

  // Wait for a second before taking another reading
  delay(1000);
}

int BH1750_Read(int address) {
  int i = 0;
  Wire.beginTransmission(address);
  Wire.requestFrom(address, 2);
  while (Wire.available()) {
    buff[i] = Wire.read(); // receive one byte
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

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  if (message == "m-water") {
    // Perform watering action
    Serial.println("Watering the plant");
  } else if (message == "m-heat") {
    // Perform heating action
    Serial.println("Heating the plant");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Reconnecting to MQTT...");
    if (client.connect("ESP32Client", mqtt_username, mqtt_password)) {
      Serial.println("Connected to MQTT");
      client.subscribe("/commands/0");
    } else {
      Serial.print("Failed with state ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

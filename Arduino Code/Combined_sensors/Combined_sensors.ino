#include "DHT.h"

// Define the pin where the DHT11 data pin is connected
#define DHTPIN 2

// Define the type of sensor (DHT11)
#define DHTTYPE DHT11

// Initialize the DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// Define the analog pin for the soil moisture sensor
const int soilMoisturePin = A0;

// Define the sensor reading limits
const int sensorMin = 0;    // Analog reading at dry soil
const int sensorMax = 1023; // Analog reading at wet soil

void setup() {
  // Initialize the serial communication
  Serial.begin(9600);
  
  // Start the DHT sensor
  dht.begin();
}

void loop() {
  // Wait a few seconds between DHT sensor measurements
  delay(2000);
  
  // Read humidity from the DHT sensor
  float humidity = dht.readHumidity();
  // Read temperature from the DHT sensor in Celsius
  float temperature = dht.readTemperature();

  // Check if any reads failed and exit early (to try again)
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  
  // Print the humidity
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print(" %\t");

  // Print the temperature and additional message based on the temperature
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" *C\t");

  // Determine the temperature level message
  if (temperature < 18) {
    Serial.println("It is cold, Jeff can do with more heat.");
  } else if (temperature >= 18 && temperature <= 27) {
    Serial.println("Jeff is getting a nice tan whilst the temp is nice.");
  } else {
    Serial.println("The temp is too hot to handle, Jeff is gonna get smoked.");
  }

  // Determine the humidity level message
  if (humidity < 25) {
    Serial.println("Maannnn its like the desert out here.");
  } else if (humidity > 75) {
    Serial.println("Its like the Amazon rainforest - super humid.");
  } else {
    Serial.println("Just rightttt.");
  }

  // Read the analog value from the soil moisture sensor
  int sensorValue = analogRead(soilMoisturePin);

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

  // Wait for a second before taking another reading
  delay(1000);
}

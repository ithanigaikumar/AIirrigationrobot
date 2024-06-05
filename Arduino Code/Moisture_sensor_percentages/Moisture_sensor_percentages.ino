// Define the analog pin
const int sensorPin = A0;

// Define the sensor reading limits
const int sensorMin = 0;    // Analog reading at dry soil
const int sensorMax = 1023; // Analog reading at wet soil

void setup() {
  // Initialize the serial communication
  Serial.begin(9600);
}

void loop() {
  // Read the analog value from the sensor
  int sensorValue = analogRead(sensorPin);

  // Map the sensor value to a percentage (0 to 100)
  int moisturePercentage = map(sensorValue, sensorMin, sensorMax, 0, 100);

  // Print the sensor value and the moisture percentage
  Serial.print("Sensor Value: ");
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

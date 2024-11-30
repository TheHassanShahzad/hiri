#include <WiFi.h>
#include <HTTPClient.h>

// Wi-Fi credentials
const char* ssid = "BT-6FCKZP";
const char* password = "Yt4Gk6UePKDypC";

// Flask server details
const char* serverIP = "192.168.1.78"; // Replace with your Raspberry Pi's IP address
const int serverPort = 5000;

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Send data to Flask server
  HTTPClient http;
  http.begin(String("http://") + serverIP + ":" + serverPort + "/store");
  http.addHeader("Content-Type", "application/json");

  String jsonPayload = "{\"value\":\"Hello from ESP32!\"}";
  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    Serial.println("Data sent to server!");
    String response = http.getString();
    Serial.println(response);
  } else {
    Serial.print("Error sending data: ");
    Serial.println(httpResponseCode);
  }
  http.end();
}

void loop() {
  // Add periodic updates here
}

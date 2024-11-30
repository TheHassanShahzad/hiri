#include <WiFi.h>
#include <ESPmDNS.h>

// Replace with your Wi-Fi credentials
const char* ssid = "BT-6FCKZP";
const char* password = "Yt4Gk6UePKDypC";

void setup() {
  Serial.begin(115200);
  Serial.println();

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Get MAC address, format it, and set as the hostname
  String macAddress = WiFi.macAddress(); // Example: "AA:BB:CC:DD:EE:FF"
  macAddress.replace(":", "");           // Remove colons
  macAddress.toLowerCase();              // Convert to lowercase

  // Start mDNS service
  if (MDNS.begin(macAddress.c_str())) {
    Serial.println("mDNS responder started");
    Serial.print("Hostname: ");
    Serial.println(macAddress + ".local");
  } else {
    Serial.println("Error starting mDNS responder");
  }
}

void loop() {
  // No need to call MDNS.update() for ESP32
}

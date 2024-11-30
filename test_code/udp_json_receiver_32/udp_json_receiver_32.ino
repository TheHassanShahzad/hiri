#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>  // Include the ArduinoJson library

// Replace with your Wi-Fi credentials
const char* ssid = "BT-6FCKZP";
const char* password = "Yt4Gk6UePKDypC";

WiFiUDP udp;              // UDP instance
const unsigned int localUdpPort = 12345;  // Port to listen on
char incomingPacket[512];                 // Buffer for incoming data
String macAddress;

void setup() {
  Serial.begin(115200);

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
  macAddress = WiFi.macAddress();
  macAddress.replace(":", "");
  macAddress.toLowerCase();

  if (MDNS.begin(macAddress.c_str())) {
    Serial.println("mDNS responder started");
    Serial.printf("Hostname: %s.local\n", macAddress.c_str());
  } else {
    Serial.println("Error starting mDNS responder");
  }

  // Start UDP
  udp.begin(localUdpPort);
  Serial.printf("UDP server started at port %d\n", localUdpPort);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    Serial.printf("Received %d bytes from %s, port %d\n",
                  packetSize, udp.remoteIP().toString().c_str(), udp.remotePort());

    int len = udp.read(incomingPacket, 512);
    if (len > 0) {
      incomingPacket[len] = 0;  // Null-terminate the string
    }

    Serial.printf("UDP packet content: %s\n", incomingPacket);

    // Parse the JSON data
    StaticJsonDocument<256> doc;  // Allocate a JSON document
    DeserializationError error = deserializeJson(doc, incomingPacket);

    if (error) {
      Serial.print("JSON parse error: ");
      Serial.println(error.c_str());
    } else {
      // Extract values
      const char* command = doc["command"];
      int pin = doc["pin"];
      int duration = doc["duration"];

      Serial.printf("Parsed Command: %s\n", command);
      Serial.printf("Pin: %d\n", pin);
      Serial.printf("Duration: %dms\n", duration);

      // Example: Blink an LED if the command is "LED_ON"
      if (strcmp(command, "LED_ON") == 0) {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, HIGH);
        delay(duration);
        digitalWrite(pin, LOW);
      }
    }

    // Send a response
    udp.beginPacket(udp.remoteIP(), udp.remotePort());
    udp.printf("JSON received and parsed by ESP32 at %s.local", macAddress.c_str());
    udp.endPacket();
  }
}

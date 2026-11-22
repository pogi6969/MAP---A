// WiFi_Test - only starts the Wi-Fi network, nothing else (no pins used)
// If "ViperTest" appears on your phone, the board and Wi-Fi are fine.
#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("WiFi_Test starting...");
  WiFi.mode(WIFI_AP);
  bool ok = WiFi.softAP("ViperTest", "12345678", 1);   // channel 1, 2.4 GHz
  Serial.println(ok ? "Wi-Fi ViperTest is ON" : "Wi-Fi FAILED to start");
  Serial.print("IP: "); Serial.println(WiFi.softAPIP());
}

void loop() {
  Serial.print("running, phones connected: ");
  Serial.println(WiFi.softAPgetStationNum());
  delay(2000);
}

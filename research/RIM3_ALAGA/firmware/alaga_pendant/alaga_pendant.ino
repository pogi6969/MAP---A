// ALAGA pendant: fall detection and SOS button worn by the older adult (ESP32-C3 SuperMini + MPU6050).
// Fall rule (threshold method): free fall (< 0.5 g) followed within 1 s by an impact (> 2.5 g), then
// 2 s of lying still. The buzzer then sounds for 10 s; pressing the button cancels a false alarm.
// Holding the button for 2 s sends SOS. Messages go to the robot by ESP-NOW broadcast.

#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <Wire.h>

const int WIFI_CHANNEL = 6;      // must match the channel the robot prints on its Serial Monitor
const int PIN_SDA = 6, PIN_SCL = 7, PIN_BUTTON = 3, PIN_BUZZER = 4;
const float FREE_FALL_G = 0.5, IMPACT_G = 2.5, STILL_RANGE_G = 0.3;
const uint8_t MPU = 0x68;

enum PendantEvent { EV_FALL = 1, EV_SOS = 2, EV_BEAT = 3, EV_CANCEL = 4 };
struct PendantMsg { char tag[6]; uint8_t type; float peakG; };
uint8_t broadcast[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
unsigned long lastBeat = 0;

void send(uint8_t type, float peak = 0) {
  PendantMsg m = {"ALAGA", type, peak};
  for (int i = 0; i < 3; i++) { esp_now_send(broadcast, (uint8_t *)&m, sizeof m); delay(50); }
}

float readG() {
  Wire.beginTransmission(MPU); Wire.write(0x3B); Wire.endTransmission(false);
  Wire.requestFrom(MPU, (uint8_t)6);
  int16_t ax = Wire.read() << 8 | Wire.read();
  int16_t ay = Wire.read() << 8 | Wire.read();
  int16_t az = Wire.read() << 8 | Wire.read();
  const float lsb = 4096.0;  // +-8 g range
  return sqrt(sq(ax / lsb) + sq(ay / lsb) + sq(az / lsb));
}

bool held(unsigned long ms) {
  unsigned long t = millis();
  while (digitalRead(PIN_BUTTON) == LOW) { if (millis() - t > ms) return true; delay(10); }
  return false;
}

// After a possible fall: beep for 10 s. A press means "I am OK".
bool confirmFall() {
  for (int i = 0; i < 50; i++) {
    digitalWrite(PIN_BUZZER, i % 2); delay(200);
    if (digitalRead(PIN_BUTTON) == LOW) { digitalWrite(PIN_BUZZER, LOW); send(EV_CANCEL); return false; }
  }
  digitalWrite(PIN_BUZZER, LOW);
  return true;
}

void setup() {
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_BUZZER, OUTPUT);
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.beginTransmission(MPU); Wire.write(0x6B); Wire.write(0); Wire.endTransmission();     // wake up
  Wire.beginTransmission(MPU); Wire.write(0x1C); Wire.write(0x10); Wire.endTransmission();  // +-8 g
  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
  esp_now_init();
  esp_now_peer_info_t peer = {};
  memcpy(peer.peer_addr, broadcast, 6);
  peer.channel = WIFI_CHANNEL;
  esp_now_add_peer(&peer);
}

void loop() {
  if (digitalRead(PIN_BUTTON) == LOW && held(2000)) {  // SOS
    send(EV_SOS);
    for (int i = 0; i < 6; i++) { digitalWrite(PIN_BUZZER, i % 2); delay(150); }
    while (digitalRead(PIN_BUTTON) == LOW) delay(10);
  }
  if (readG() < FREE_FALL_G) {
    float peak = 0;
    for (int i = 0; i < 50; i++) { peak = max(peak, readG()); delay(20); }  // next 1 s at 50 Hz
    if (peak > IMPACT_G) {
      delay(1000);
      float lo = 9, hi = 0;
      for (int i = 0; i < 100; i++) { float g = readG(); lo = min(lo, g); hi = max(hi, g); delay(20); }
      if (hi - lo < STILL_RANGE_G && confirmFall()) send(EV_FALL, peak);
    }
  }
  if (millis() - lastBeat > 60000) { send(EV_BEAT); lastBeat = millis(); }
  delay(20);
}

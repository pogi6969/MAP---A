// KALINGA: low-cost wearable health pendant (ESP32-C3 SuperMini)
// Spot checks of forehead temperature, pulse rate, and SpO2; fall, SOS, and inactivity alerts; a 4-slot pill
// carousel that presents each scheduled dose; and live sync with the KALINGA Monitor app through Firebase.
// KALINGA reminds, presents doses, checks, and alerts; it does not diagnose or treat.
// Libraries: Adafruit MLX90614, Adafruit SSD1306 + GFX, SparkFun MAX3010x, ESP32Servo, ArduinoJson (v7).
// Board: ESP32C3 Dev Module, USB CDC On Boot: Enabled.

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <Wire.h>
#include <time.h>
#include <Adafruit_MLX90614.h>
#include <Adafruit_SSD1306.h>
#include <ESP32Servo.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

// ---------- Settings: edit before uploading ----------
const char *WIFI_SSID = "YOUR_WIFI_NAME";
const char *WIFI_PASS = "YOUR_WIFI_PASSWORD";
const char *API_KEY = "YOUR_FIREBASE_WEB_API_KEY";
const char *DB_URL = "https://YOUR-PROJECT-default-rtdb.asia-southeast1.firebasedatabase.app";
const char *DEVICE_EMAIL = "pendant@your-family.ph";  // Firebase Authentication user for the pendant
const char *DEVICE_PASS = "a-long-device-password";
const char *PATIENT = "lola1";                         // must match the patient id in the app

// ---------- Pins ----------
const int PIN_SDA = 6, PIN_SCL = 7;
const int PIN_SERVO = 5, PIN_SERVO_PWR = 10;  // AO3400 cuts the servo ground when idle
const int PIN_SOS = 1, PIN_OK = 2;            // buttons to GND
const int PIN_BUZZER = 3, PIN_VIBE = 21;      // active buzzer; coin motor through S8050
const int PIN_BATT = 4;                       // 100k/100k divider from the battery

// ---------- Limits ----------
const float TEMP_FEVER = 37.5, TEMP_HIGH = 39.0;
const int SPO2_LOW = 95, SPO2_URGENT = 92, PR_LOW = 60, PR_HIGH = 100, PR_URG_LOW = 40, PR_URG_HIGH = 130;
float TEMP_A = 1.00, TEMP_B = 2.30;  // body = a * skin + b, from the calibration set
int SPO2_OFFSET = 0, PR_OFFSET = 0;
const float FREE_FALL_G = 0.5, IMPACT_G = 2.5, STILL_RANGE_G = 0.3;
const int SLOT_ANGLE[5] = {0, 45, 90, 135, 180};  // 0 = closed, 1-4 = dose slots under the window
const unsigned long DOSE_WINDOW_MS = 30UL * 60 * 1000, REMIND_EVERY_MS = 2UL * 60 * 1000;

Adafruit_MLX90614 mlx;
Adafruit_SSD1306 oled(128, 32, &Wire, -1);
MAX30105 pox;
Servo carousel;
Preferences prefs;

struct Slot { char time[6]; char label[32]; bool enabled; };
Slot slots[4];
int checkHour[2] = {8, 18};
int inactivityHours = 3;
String idToken, refreshToken;
unsigned long tokenAt = 0, lastSync = 0, lastBeat = 0, lastMove = 0;
int doneDay[4] = {-1, -1, -1, -1}, checkDay[2] = {-1, -1};
bool inactivitySent = false;

// ---------- Output helpers ----------
void show(const String &a, const String &b = "") {
  oled.clearDisplay(); oled.setTextColor(SSD1306_WHITE);
  oled.setTextSize(1); oled.setCursor(0, 0); oled.println(a);
  oled.setCursor(0, 16); oled.println(b);
  oled.display();
}

void alertPulse(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(PIN_VIBE, HIGH); digitalWrite(PIN_BUZZER, HIGH); delay(250);
    digitalWrite(PIN_VIBE, LOW); digitalWrite(PIN_BUZZER, LOW); delay(200);
  }
}

bool pressed(int pin) {
  if (digitalRead(pin) == LOW) { delay(30); while (digitalRead(pin) == LOW) delay(5); return true; }
  return false;
}

int batteryPct() {
  float v = analogReadMilliVolts(PIN_BATT) * 2 / 1000.0;
  return constrain((int)((v - 3.4) / (4.2 - 3.4) * 100), 0, 100);
}

uint64_t nowMs() { return (uint64_t)time(nullptr) * 1000ULL; }

// ---------- Firebase (REST) ----------
bool postJson(const String &url, const String &body, String &out, const char *type = "application/json") {
  WiFiClientSecure tls;
  tls.setInsecure();  // prototype only: add Google's root certificate before real use
  HTTPClient http;
  if (!http.begin(tls, url)) return false;
  http.addHeader("Content-Type", type);
  int code = http.POST(body);
  out = http.getString();
  http.end();
  return code == 200;
}

bool signIn() {
  String out;
  bool ok;
  if (refreshToken.length()) {
    ok = postJson(String("https://securetoken.googleapis.com/v1/token?key=") + API_KEY,
                  "grant_type=refresh_token&refresh_token=" + refreshToken, out, "application/x-www-form-urlencoded");
  } else {
    JsonDocument req;
    req["email"] = DEVICE_EMAIL; req["password"] = DEVICE_PASS; req["returnSecureToken"] = true;
    String body; serializeJson(req, body);
    ok = postJson(String("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=") + API_KEY,
                  body, out);
  }
  if (!ok) { refreshToken = ""; return false; }
  JsonDocument res;
  deserializeJson(res, out);
  idToken = res["idToken"] | "";
  if (!idToken.length()) idToken = res["id_token"] | "";
  refreshToken = res["refreshToken"] | "";
  if (!refreshToken.length()) refreshToken = res["refresh_token"] | "";
  tokenAt = millis();
  return idToken.length() > 0;
}

// method: "PUT", "PATCH", "POST" (push), "GET", "DELETE"
bool db(const char *method, const String &path, const String &body, String *reply = nullptr) {
  if (WiFi.status() != WL_CONNECTED) return false;
  if (!idToken.length() || millis() - tokenAt > 50UL * 60 * 1000) if (!signIn()) return false;
  WiFiClientSecure tls;
  tls.setInsecure();
  HTTPClient http;
  String url = String(DB_URL) + "/patients/" + PATIENT + path + ".json?auth=" + idToken;
  if (!http.begin(tls, url)) return false;
  http.addHeader("Content-Type", "application/json");
  int code = http.sendRequest(method, body);
  if (reply) *reply = http.getString();
  http.end();
  return code == 200;
}

// Alerts and records that fail to send wait here and are retried on the next sync.
String queuePath[12], queueBody[12];
int queued = 0;
void send(const String &path, const String &body) {
  if (db("POST", path, body)) return;
  if (queued < 12) { queuePath[queued] = path; queueBody[queued] = body; queued++; }
}
void flushQueue() {
  int kept = 0;
  for (int i = 0; i < queued; i++)
    if (!db("POST", queuePath[i], queueBody[i])) { queuePath[kept] = queuePath[i]; queueBody[kept++] = queueBody[i]; }
  queued = kept;
}

void sendAlert(const char *type, const String &msg) {
  JsonDocument d;
  d["ts"] = nowMs(); d["type"] = type; d["msg"] = msg; d["ack"] = false;
  String b; serializeJson(d, b);
  send("/alerts", b);
}

// ---------- Schedule ----------
void loadSchedule() {
  prefs.begin("kalinga", true);
  for (int i = 0; i < 4; i++) {
    String t = prefs.getString(("t" + String(i)).c_str(), "");
    String l = prefs.getString(("l" + String(i)).c_str(), "");
    strlcpy(slots[i].time, t.c_str(), 6); strlcpy(slots[i].label, l.c_str(), 32);
    slots[i].enabled = t.length() == 5;
  }
  prefs.end();
}

void syncFromApp() {
  String r;
  if (db("GET", "/schedule", "", &r)) {
    JsonDocument d;
    if (!deserializeJson(d, r)) {
      prefs.begin("kalinga", false);
      for (int i = 0; i < 4; i++) {
        JsonVariant s = d[String(i + 1)];
        bool en = s["enabled"] | false;
        String t = en ? String((const char *)(s["time"] | "")) : "";
        prefs.putString(("t" + String(i)).c_str(), t);
        prefs.putString(("l" + String(i)).c_str(), String((const char *)(s["label"] | "Gamot")));
      }
      prefs.end();
      loadSchedule();
    }
  }
  if (db("GET", "/settings", "", &r)) {
    JsonDocument d;
    if (!deserializeJson(d, r)) {
      checkHour[0] = d["checkHours"][0] | 8; checkHour[1] = d["checkHours"][1] | 18;
      inactivityHours = d["inactivityHours"] | 3;
    }
  }
  if (db("GET", "/commands", "", &r)) {
    JsonDocument d;
    if (!deserializeJson(d, r) && !d.isNull()) {
      db("DELETE", "/commands", "");
      if (!d["ring"].isNull()) { show("Nandito ako!", "I am here"); alertPulse(8); }
      if (!d["check"].isNull()) vitalsCheck("app");
    }
  }
  JsonDocument s;
  s["ts"] = nowMs(); s["battery"] = batteryPct(); s["rssi"] = WiFi.RSSI(); s["queued"] = queued;
  String b; serializeJson(s, b);
  db("PUT", "/status", b);
  flushQueue();
}

// ---------- Motion ----------
float accel(float *z = nullptr) {
  Wire.beginTransmission(0x68); Wire.write(0x3B); Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)0x68, (uint8_t)6);
  int16_t ax = Wire.read() << 8 | Wire.read(), ay = Wire.read() << 8 | Wire.read(), az = Wire.read() << 8 | Wire.read();
  if (z) *z = az / 4096.0;
  return sqrt(sq(ax / 4096.0) + sq(ay / 4096.0) + sq(az / 4096.0));
}

void checkFall() {
  float g = accel();
  if (fabs(g - 1.0) > 0.15) lastMove = millis(), inactivitySent = false;
  if (g >= FREE_FALL_G) return;
  float peak = 0;
  for (int i = 0; i < 50; i++) { peak = max(peak, accel()); delay(20); }
  if (peak < IMPACT_G) return;
  delay(1000);
  float lo = 9, hi = 0;
  for (int i = 0; i < 100; i++) { float a = accel(); lo = min(lo, a); hi = max(hi, a); delay(20); }
  if (hi - lo > STILL_RANGE_G) return;
  show("Nahulog ka ba?", "OK = I am fine");
  for (int i = 0; i < 40; i++) {  // 10-second cancel window
    digitalWrite(PIN_BUZZER, i % 2); digitalWrite(PIN_VIBE, i % 2); delay(250);
    if (pressed(PIN_OK)) { digitalWrite(PIN_BUZZER, LOW); digitalWrite(PIN_VIBE, LOW); show("OK", "Cancelled"); return; }
  }
  digitalWrite(PIN_BUZZER, LOW); digitalWrite(PIN_VIBE, LOW);
  show("FALL ALERT", "Family notified");
  sendAlert("FALL", "Possible fall, peak " + String(peak, 1) + " g, no answer in 10 s.");
}

// ---------- Vital-sign check ----------
void vitalsCheck(const char *source) {
  unsigned long t0 = millis();
  float tempC = NAN; int pr = -1, spo2 = -1;
  show("Ilapit sa noo", "Bring to forehead"); alertPulse(1);
  unsigned long t = millis();
  while (isnan(tempC) && millis() - t < 60000) {
    if (mlx.readObjectTempC() > 32.0) {  // a forehead 3-5 cm away fills the sensor's view
      delay(300);
      float sum = 0;
      for (int i = 0; i < 5; i++) { sum += mlx.readObjectTempC(); delay(100); }
      tempC = TEMP_A * sum / 5 + TEMP_B;
    }
    delay(50);
  }
  show("Daliri sa pad", "Finger on the pad"); alertPulse(1);
  const int N = 100;
  static uint32_t ir[N], red[N];
  t = millis();
  while (spo2 < 0 && millis() - t < 60000) {
    pox.check();
    if (pox.getIR() < 50000) { delay(50); continue; }
    show("Huwag gumalaw", "Hold still");
    for (int i = 0; i < N; i++) { while (!pox.available()) pox.check(); red[i] = pox.getRed(); ir[i] = pox.getIR(); pox.nextSample(); }
    int32_t s, hr; int8_t sOk, hrOk;
    maxim_heart_rate_and_oxygen_saturation(ir, N, red, &s, &sOk, &hr, &hrOk);
    if (sOk && hrOk && hr > 30 && hr < 220 && s > 70) { spo2 = min(100, (int)s + SPO2_OFFSET); pr = hr + PR_OFFSET; }
  }
  bool red_ = tempC >= TEMP_HIGH || (spo2 > 0 && spo2 < SPO2_URGENT) || (pr > 0 && (pr < PR_URG_LOW || pr > PR_URG_HIGH));
  bool yel = tempC >= TEMP_FEVER || (spo2 > 0 && spo2 < SPO2_LOW) || (pr > 0 && (pr < PR_LOW || pr > PR_HIGH));
  const char *level = red_ ? "RED" : yel ? "YELLOW" : "GREEN";
  show(String(tempC, 1) + "C " + pr + "bpm " + spo2 + "%", level);
  JsonDocument d;
  d["ts"] = nowMs(); d["temp"] = isnan(tempC) ? 0 : round(tempC * 10) / 10.0; d["hr"] = pr; d["spo2"] = spo2;
  d["level"] = level; d["source"] = source; d["secs"] = (millis() - t0) / 1000;
  String b; serializeJson(d, b);
  db("PUT", "/latest", b);
  send("/vitals", b);
  if (red_) sendAlert("VITALS_RED", String("Check: ") + String(tempC, 1) + " C, PR " + pr + ", SpO2 " + spo2 + "%.");
  delay(5000);
}

// ---------- Dose presentation ----------
void moveCarousel(int slot) {
  digitalWrite(PIN_SERVO_PWR, HIGH);
  carousel.attach(PIN_SERVO, 500, 2400);
  carousel.write(SLOT_ANGLE[slot]);
  delay(700);
  carousel.detach();
  digitalWrite(PIN_SERVO_PWR, LOW);
}

void presentDose(int i, const String &due) {
  moveCarousel(i + 1);
  unsigned long t = millis(), lastRemind = 0;
  bool tilted = false, taken = false;
  while (millis() - t < DOSE_WINDOW_MS && !taken) {
    if (millis() - lastRemind > REMIND_EVERY_MS) { show("Gamot: " + String(slots[i].label), "Tilt out, press OK"); alertPulse(3); lastRemind = millis(); }
    float z; accel(&z);
    if (z < -0.5) tilted = true;  // window turned toward the palm
    if (pressed(PIN_OK)) taken = true;
    if (pressed(PIN_SOS)) break;
    delay(50);
  }
  moveCarousel(0);
  bool late = taken && millis() - t > 10UL * 60 * 1000;
  JsonDocument d;
  d["ts"] = nowMs(); d["slot"] = i + 1; d["label"] = slots[i].label; d["due"] = due;
  d["status"] = taken ? (late ? "late" : "taken") : "missed"; d["tilted"] = tilted;
  String b; serializeJson(d, b);
  send("/doses", b);
  show(taken ? "Salamat!" : "Hindi nainom", taken ? "Dose recorded" : "Family notified");
  if (!taken) sendAlert("MISSED_DOSE", String("Missed ") + slots[i].label + " due " + due + ".");
}

void checkClock() {
  struct tm tm;
  if (!getLocalTime(&tm, 10)) return;
  char hm[6]; strftime(hm, sizeof hm, "%H:%M", &tm);
  for (int i = 0; i < 4; i++)
    if (slots[i].enabled && !strcmp(hm, slots[i].time) && doneDay[i] != tm.tm_yday) { doneDay[i] = tm.tm_yday; presentDose(i, hm); }
  for (int k = 0; k < 2; k++)
    if (tm.tm_hour == checkHour[k] && tm.tm_min == 0 && checkDay[k] != tm.tm_yday) { checkDay[k] = tm.tm_yday; vitalsCheck("schedule"); }
  bool daytime = tm.tm_hour >= 7 && tm.tm_hour < 21;
  if (daytime && !inactivitySent && millis() - lastMove > (unsigned long)inactivityHours * 3600000UL) {
    inactivitySent = true;
    sendAlert("INACTIVE", String("No movement for ") + inactivityHours + " hours.");
  }
  static int lastMin = -1;
  if (tm.tm_min != lastMin) {
    lastMin = tm.tm_min;
    String next = "";
    for (int i = 0; i < 4; i++) if (slots[i].enabled && strcmp(slots[i].time, hm) > 0) { next = slots[i].time; break; }
    show(String(hm) + "  " + batteryPct() + "%", next.length() ? "Next dose " + next : "KALINGA");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_SOS, INPUT_PULLUP); pinMode(PIN_OK, INPUT_PULLUP);
  pinMode(PIN_BUZZER, OUTPUT); pinMode(PIN_VIBE, OUTPUT); pinMode(PIN_SERVO_PWR, OUTPUT);
  Wire.begin(PIN_SDA, PIN_SCL, 100000);
  Wire.beginTransmission(0x68); Wire.write(0x6B); Wire.write(0); Wire.endTransmission();     // MPU6050 on
  Wire.beginTransmission(0x68); Wire.write(0x1C); Wire.write(0x10); Wire.endTransmission();  // +-8 g
  mlx.begin();
  oled.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  pox.begin(Wire, I2C_SPEED_STANDARD);
  pox.setup(60, 4, 2, 100, 411, 4096);
  ESP32PWM::allocateTimer(0);
  moveCarousel(0);
  loadSchedule();
  show("KALINGA", "Connecting...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) delay(500);
  configTime(8 * 3600, 0, "pool.ntp.org", "time.google.com");  // Philippine time
  lastMove = millis();
  syncFromApp();
}

void loop() {
  checkFall();
  if (digitalRead(PIN_SOS) == LOW) {
    unsigned long t = millis();
    while (digitalRead(PIN_SOS) == LOW && millis() - t < 2000) delay(10);
    if (millis() - t >= 2000) { show("SOS", "Family notified"); alertPulse(2); sendAlert("SOS", "SOS button held."); }
  }
  if (pressed(PIN_OK)) vitalsCheck("button");
  checkClock();
  if (millis() - lastSync > 60000) { lastSync = millis(); syncFromApp(); }
  if (WiFi.status() != WL_CONNECTED && millis() % 30000 < 25) WiFi.reconnect();
  delay(20);
}

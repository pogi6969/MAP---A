// ALAGA: low-cost wheeled soft inflatable home companion robot for older adults (ESP32 DevKit V1)
// While the family is at work, ALAGA follows a floor-tape route between home stations, reminds the
// older adult about medicine and water, checks temperature, pulse rate, SpO2, and pain, keeps company
// with music and prayers, and sends reports and alerts to the family through Telegram. It also receives
// fall and SOS alerts from the ALAGA pendant (alaga_pendant.ino) by ESP-NOW.
// ALAGA reminds, checks, and alerts; it does not diagnose, treat, or give medicine.
// Libraries: Adafruit MLX90614, SparkFun MAX3010x, Adafruit SSD1306 + GFX, DFRobotDFPlayerMini,
// UniversalTelegramBot, ArduinoJson. Board: ESP32 Dev Module (Arduino-ESP32 core 2.x or 3.x).

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <esp_now.h>
#include <Wire.h>
#include <LittleFS.h>
#include <time.h>
#include <UniversalTelegramBot.h>
#include <Adafruit_MLX90614.h>
#include <Adafruit_SSD1306.h>
#include <DFRobotDFPlayerMini.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

// ---------- Family settings: edit before uploading ----------
const char *WIFI_SSID = "YOUR_WIFI_NAME";
const char *WIFI_PASS = "YOUR_WIFI_PASSWORD";
const char *BOT_TOKEN = "YOUR_BOT_TOKEN";   // from @BotFather in Telegram
const char *FAMILY_CHAT = "YOUR_CHAT_ID";   // family group chat id
const char *ELDER = "Lola";                 // name used in messages

enum TaskType { MEDS, VITALS, CHECKIN, WATER };
struct Task { uint8_t hour, minute; TaskType type; };
Task schedule[] = {{7, 0, VITALS}, {7, 30, MEDS}, {10, 0, WATER}, {12, 30, MEDS},
                   {15, 0, CHECKIN}, {18, 0, VITALS}, {18, 30, MEDS}};
const int NUM_TASKS = sizeof(schedule) / sizeof(schedule[0]);

// Route: stations are tape markers counted in travel order around one closed loop. 0 = dock.
const int ST_DOCK = 0, ST_CHAIR = 1, MARKERS = 4;  // dock, chair, bed, kitchen
const char *STATION[] = {"dock", "chair", "bed", "kitchen"};

// ---------- Pins (see the wiring table in the build guide) ----------
const int PIN_FAN = 25;      // D4184 MOSFET module, 12 V blower fan
const int PIN_BUTTON = 27;   // red chest button to GND
const int PIN_SOUND = 26;    // KY-037 digital out (a loud call such as "ALAGA!" or "Tulong!")
const int PIN_BUMP = 2;      // front bumper microswitches to GND
const int PIN_TRIG = 32, PIN_ECHO = 33;  // HC-SR04 at the front of the base; ECHO through 1k/2k divider
const int PIN_DIAL = 34;     // dial potentiometer wiper
const int PIN_DF_RX = 16, PIN_DF_TX = 17;
const int LINE[5] = {35, 36, 39, 4, 13};  // 5-channel line sensor, left to right
const int LINE_ON_TAPE = HIGH;            // output over black tape; use LOW for white tape on a dark floor
const int ENA = 14, IN1 = 18, IN2 = 19;   // L298N left motor
const int ENB = 23, IN3 = 5, IN4 = 15;    // L298N right motor
const int SPEED = 120, KP = 40;           // PWM 0-255 (about 0.2 m/s) and steering gain
const int STOP_CM = 25;                   // stop when something is this close

// ---------- Screening limits and calibration ----------
const float TEMP_FEVER = 37.5, TEMP_HIGH = 39.0;
const int SPO2_LOW = 95, SPO2_URGENT = 92;
const int PR_LOW = 60, PR_HIGH = 100, PR_URG_LOW = 40, PR_URG_HIGH = 130;
const int PAIN_REFER = 4, PAIN_URGENT = 7;
float TEMP_A = 1.00, TEMP_B = 2.30;  // body = a * skin + b, from the calibration set
int SPO2_OFFSET = 0, PR_OFFSET = 0;

// Audio on the microSD card: /mp3/0001.mp3 ... and music or prayers in /02/001.mp3 ... /02/005.mp3
enum Track { T_HELLO = 1, T_PAIN, T_TEMP, T_FINGER, T_GREEN, T_YELLOW, T_RED, T_BYE, T_CLOSER, T_RETRY,
             T_MEDS, T_MEDS_AGAIN, T_MEDS_OK, T_CHECKIN, T_WATER, T_EXCUSE, T_ALERT, T_CALLED, T_MENU,
             T_HOME };

// ---------- Pendant messages (ESP-NOW) ----------
enum PendantEvent { EV_NONE = 0, EV_FALL = 1, EV_SOS = 2, EV_BEAT = 3, EV_CANCEL = 4 };
struct PendantMsg { char tag[6]; uint8_t type; float peakG; };
volatile uint8_t pendantEvent = EV_NONE;
volatile unsigned long lastBeat = 0;
volatile bool soundHeard = false;
bool beatWarned = false;

Adafruit_MLX90614 mlx;
MAX30105 pox;
Adafruit_SSD1306 oled(128, 64, &Wire, -1);
DFRobotDFPlayerMini player;
WiFiClientSecure tls;
UniversalTelegramBot bot(BOT_TOKEN, tls);

int pos = ST_DOCK;
int lastRunDay[NUM_TASKS];
int pain = -1, pulseRate = -1, spo2 = -1;
float tempC = NAN;
char level = 'G';
String lastVitals = "none yet", lastMeds = "none yet";
unsigned long lastPoll = 0;

// ---------- Small helpers ----------
void say(Track t) { player.playMp3Folder(t); }

void show(const char *l1, const char *l2 = "") {
  oled.clearDisplay();
  oled.setTextColor(SSD1306_WHITE);
  oled.setTextSize(2); oled.setCursor(0, 0); oled.println(l1);
  oled.setTextSize(1); oled.setCursor(0, 40); oled.println(l2);
  oled.display();
}

String nowText() {
  struct tm t;
  if (!getLocalTime(&t, 50)) return "--:--";
  char b[8]; strftime(b, sizeof b, "%H:%M", &t);
  return String(b);
}

void logLine(const String &s) {
  File f = LittleFS.open("/log.csv", FILE_APPEND);
  if (f) { f.println(nowText() + "," + s); f.close(); }
  Serial.println("LOG," + nowText() + "," + s);
}

bool notify(const String &msg) {
  if (WiFi.status() != WL_CONNECTED) { WiFi.reconnect(); delay(3000); }
  for (int i = 0; i < 3; i++) {
    if (bot.sendMessage(FAMILY_CHAT, msg, "")) { logLine("SENT," + msg); return true; }
    delay(1000);
  }
  logLine("NOT SENT," + msg);
  return false;
}

void motors(int l, int r) {
  digitalWrite(IN1, l >= 0); digitalWrite(IN2, l < 0);
  digitalWrite(IN3, r >= 0); digitalWrite(IN4, r < 0);
  analogWrite(ENA, constrain(abs(l), 0, 255));
  analogWrite(ENB, constrain(abs(r), 0, 255));
}
void stopMotors() { motors(0, 0); }

float distanceCm() {
  static unsigned long last = 0;
  static float d = 999;
  if (millis() - last < 60) return d;
  last = millis();
  digitalWrite(PIN_TRIG, LOW); delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  unsigned long us = pulseIn(PIN_ECHO, HIGH, 25000);
  d = us ? us / 58.0 : 999;
  return d;
}

// Handles pendant alerts at any time, even during a trip or a task.
void service() {
  uint8_t e = pendantEvent;
  if (e == EV_FALL || e == EV_SOS) {
    pendantEvent = EV_NONE;
    stopMotors();
    say(T_ALERT);
    show(e == EV_FALL ? "FALL!" : "SOS!", "Alerting family");
    notify(String(e == EV_FALL ? "🚨 FALL detected" : "🚨 SOS pressed") + " on " + ELDER + "'s pendant at " +
           nowText() + ". Please call " + ELDER + " or ask a neighbor to check now.");
  }
  if (lastBeat && !beatWarned && millis() - lastBeat > 10UL * 60 * 1000) {
    beatWarned = true;
    notify(String("⚠️ No signal from ") + ELDER + "'s pendant for 10 minutes. Is it charged and worn?");
  }
}

void wait(unsigned long ms) {
  unsigned long t = millis();
  while (millis() - t < ms) { service(); delay(20); }
}

// Waits for the chest button; returns true if pressed within ms.
bool waitButton(unsigned long ms) {
  unsigned long t = millis();
  while (millis() - t < ms) {
    service();
    if (digitalRead(PIN_BUTTON) == LOW) {
      delay(30); while (digitalRead(PIN_BUTTON) == LOW) delay(5);
      return true;
    }
    delay(20);
  }
  return false;
}

int readDial(int maxValue) { return constrain(map(analogRead(PIN_DIAL), 0, 4095, 0, maxValue + 1), 0, maxValue); }

// ---------- Moving ----------
void inflate() { digitalWrite(PIN_FAN, HIGH); show("ALAGA", "Inflating..."); wait(30000); }
void deflate() { digitalWrite(PIN_FAN, LOW); show("ALAGA", nowText().c_str()); }

// Follows the tape and counts station markers until it reaches the target station.
bool goTo(int target) {
  unsigned long lost = 0, lastExcuse = 0;
  bool onMarker = true;
  show("Going to", STATION[target]);
  while (pos != target) {
    service();
    bool bump = digitalRead(PIN_BUMP) == LOW;
    if (bump || distanceCm() < STOP_CM) {
      stopMotors();
      if (millis() - lastExcuse > 10000) { say(T_EXCUSE); lastExcuse = millis(); }
      if (bump) { motors(-SPEED, -SPEED); delay(300); stopMotors(); }
      delay(200);
      continue;
    }
    int n = 0, sum = 0;
    for (int i = 0; i < 5; i++)
      if (digitalRead(LINE[i]) == LINE_ON_TAPE) { n++; sum += i - 2; }
    if (n == 5) {  // a station marker crosses the route
      if (!onMarker) { onMarker = true; pos = (pos + 1) % MARKERS; }
      motors(SPEED, SPEED);
    } else if (n == 0) {  // line lost: keep the last command for a moment
      if (!lost) lost = millis();
      if (millis() - lost > 3000) {
        stopMotors();
        notify(String("⚠️ ALAGA lost its route after the ") + STATION[pos] +
               ". Please put it back on the dock and hold its chest button for 5 s.");
        return false;
      }
    } else {
      onMarker = false; lost = 0;
      int corr = KP * sum / n;
      motors(SPEED + corr, SPEED - corr);
    }
    delay(5);
  }
  stopMotors();
  return true;
}

// ---------- Health check ----------
bool readPulse() {
  const int N = 100;
  static uint32_t ir[N], red[N];
  int32_t s, hr; int8_t sOk, hrOk;
  for (int tries = 0; tries < 3; tries++) {
    for (int i = 0; i < N; i++) {
      while (!pox.available()) pox.check();
      red[i] = pox.getRed(); ir[i] = pox.getIR(); pox.nextSample();
    }
    maxim_heart_rate_and_oxygen_saturation(ir, N, red, &s, &sOk, &hr, &hrOk);
    if (sOk && hrOk && hr > 30 && hr < 220 && s > 70) {
      spo2 = min(100, (int)s + SPO2_OFFSET); pulseRate = hr + PR_OFFSET;
      return true;
    }
    say(T_RETRY);
  }
  return false;
}

char triage() {
  bool red = tempC >= TEMP_HIGH || spo2 < SPO2_URGENT || pulseRate < PR_URG_LOW ||
             pulseRate > PR_URG_HIGH || pain >= PAIN_URGENT;
  bool yellow = tempC >= TEMP_FEVER || spo2 < SPO2_LOW || pulseRate < PR_LOW ||
                pulseRate > PR_HIGH || pain >= PAIN_REFER;
  return red ? 'R' : (yellow ? 'Y' : 'G');
}

void doVitals() {
  unsigned long t0 = millis();
  pain = -1; pulseRate = spo2 = -1; tempC = NAN;
  say(T_PAIN);
  unsigned long t = millis();
  while (millis() - t < 60000) {
    service();
    pain = readDial(10);
    char b[24]; snprintf(b, sizeof b, "Pain: %d / 10", pain);
    show(b, "Turn dial, press button");
    if (waitButton(200)) break;
  }
  say(T_TEMP);
  t = millis();
  unsigned long lastPrompt = millis();
  while (isnan(tempC) && millis() - t < 60000) {
    service();
    // A forehead 3-5 cm away fills the sensor's view, so the object reading jumps above 32 C.
    if (mlx.readObjectTempC() > 32.0) {
      delay(300);
      float sum = 0;
      for (int i = 0; i < 5; i++) { sum += mlx.readObjectTempC(); delay(100); }
      tempC = TEMP_A * (sum / 5) + TEMP_B;
    } else if (millis() - lastPrompt > 8000) {
      say(T_CLOSER); lastPrompt = millis();
    }
    delay(50);
  }
  say(T_FINGER);
  show("Finger", "Place finger in slot");
  t = millis();
  while (spo2 < 0 && millis() - t < 60000) {
    service();
    pox.check();
    if (pox.getIR() > 50000) { show("Hold still", "Measuring..."); if (!readPulse()) break; }
    delay(50);
  }
  level = triage();
  char b[64];
  snprintf(b, sizeof b, "%.1f C, PR %d, SpO2 %d%%, pain %d", tempC, pulseRate, spo2, pain);
  show(level == 'G' ? "GREEN" : level == 'Y' ? "YELLOW" : "RED", b);
  say(level == 'G' ? T_GREEN : level == 'Y' ? T_YELLOW : T_RED);
  lastVitals = nowText() + " " + b;
  logLine(String("VITALS,") + b + "," + level + "," + (millis() - t0) / 1000 + "s");
  const char *icon = level == 'G' ? "🟢" : level == 'Y' ? "🟡" : "🔴";
  notify(String(icon) + " " + ELDER + "'s check at " + nowText() + ": " + b +
         (level == 'R' ? ". Please call now." : level == 'Y' ? ". Please call to ask how she feels." : "."));
  wait(8000);
}

// ---------- Tasks ----------
void runTask(TaskType type) {
  String when = nowText();
  if (type == MEDS) {
    bool ok = false;
    for (int i = 0; i < 5 && !ok; i++) {  // remind every 2 minutes for 10 minutes
      say(i ? T_MEDS_AGAIN : T_MEDS);
      show("Medicine", "Press after taking");
      ok = waitButton(120000);
    }
    if (ok) {
      say(T_MEDS_OK);
      lastMeds = when + " confirmed at " + nowText();
      notify(String("✅ ") + ELDER + " confirmed the " + when + " medicine at " + nowText() + ".");
    } else {
      lastMeds = when + " NOT confirmed";
      notify(String("❗ ") + ELDER + " did not confirm the " + when + " medicine. Please call.");
    }
    logLine(String("MEDS,") + when + "," + (ok ? "confirmed" : "missed"));
  } else if (type == VITALS) {
    doVitals();
  } else if (type == CHECKIN) {
    say(T_CHECKIN);
    show("Kumusta po?", "Press if OK");
    bool ok = waitButton(5UL * 60 * 1000);
    notify(ok ? String("🙂 ") + ELDER + " answered the " + when + " check-in: OK."
              : String("❗ No answer to the ") + when + " check-in. Please call " + ELDER + ".");
    logLine(String("CHECKIN,") + when + "," + (ok ? "ok" : "no answer"));
  } else {
    say(T_WATER);
    wait(8000);
  }
}

void mission(TaskType type) {
  inflate();
  if (goTo(ST_CHAIR)) {
    say(T_HELLO); wait(4000);
    runTask(type);
    say(T_HOME); wait(3000);
    goTo(ST_DOCK);
  }
  deflate();
}

// Called by a loud voice: go to the chair, ask if all is well, then keep company.
void called() {
  inflate();
  if (!goTo(ST_CHAIR)) { deflate(); return; }
  say(T_CALLED);
  show("Tinawag mo ako?", "Press if OK");
  if (!waitButton(60000)) {
    notify(String("❗ ALAGA heard a loud call at ") + nowText() + " and got no answer at the chair. Please call " +
           ELDER + ".");
  } else {
    say(T_MENU);
    unsigned long idle = millis();
    while (millis() - idle < 10UL * 60 * 1000) {
      int choice = readDial(5);
      char b[24]; snprintf(b, sizeof b, choice ? "Song %d" : "Check me", choice);
      show(b, "Turn dial, press button");
      if (waitButton(200)) {
        idle = millis();
        if (choice == 0) doVitals();
        else { player.playFolder(2, choice); waitButton(10UL * 60 * 1000); player.stop(); }
      }
    }
  }
  say(T_HOME); wait(3000);
  goTo(ST_DOCK);
  deflate();
}

String statusText() {
  return String("ALAGA status ") + nowText() + "\nPlace: " + STATION[pos] + "\nLast check: " + lastVitals +
         "\nLast medicine: " + lastMeds + "\nPendant: " +
         (lastBeat ? String((millis() - lastBeat) / 60000) + " min since last signal" : "not seen yet");
}

void pollTelegram() {
  if (millis() - lastPoll < 5000 || WiFi.status() != WL_CONNECTED) return;
  lastPoll = millis();
  int n = bot.getUpdates(bot.last_message_received + 1);
  for (int i = 0; i < n; i++) {
    String text = bot.messages[i].text;
    if (bot.messages[i].chat_id != FAMILY_CHAT) continue;
    if (text.startsWith("/status")) bot.sendMessage(FAMILY_CHAT, statusText(), "");
    else if (text.startsWith("/check")) mission(CHECKIN);
    else if (text.startsWith("/vitals")) mission(VITALS);
    else if (text.startsWith("/water")) mission(WATER);
    else bot.sendMessage(FAMILY_CHAT, "Commands: /status /check /vitals /water", "");
  }
}

void checkSchedule() {
  struct tm t;
  if (!getLocalTime(&t, 10)) return;
  for (int i = 0; i < NUM_TASKS; i++) {
    if (schedule[i].hour == t.tm_hour && schedule[i].minute == t.tm_min && lastRunDay[i] != t.tm_yday) {
      lastRunDay[i] = t.tm_yday;
      mission(schedule[i].type);
    }
  }
}

#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
void onPendant(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
#else
void onPendant(const uint8_t *mac, const uint8_t *data, int len) {
#endif
  if (len != sizeof(PendantMsg)) return;
  PendantMsg m;
  memcpy(&m, data, sizeof m);
  if (strncmp(m.tag, "ALAGA", 5) != 0) return;
  lastBeat = millis();
  beatWarned = false;
  if (m.type == EV_FALL || m.type == EV_SOS) pendantEvent = m.type;
}

void IRAM_ATTR onSound() { soundHeard = true; }

void setup() {
  Serial.begin(115200);
  pinMode(PIN_FAN, OUTPUT); digitalWrite(PIN_FAN, LOW);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_BUMP, INPUT_PULLUP);
  pinMode(PIN_SOUND, INPUT);
  pinMode(PIN_TRIG, OUTPUT); pinMode(PIN_ECHO, INPUT);
  for (int p : LINE) pinMode(p, INPUT);
  for (int p : {ENA, IN1, IN2, ENB, IN3, IN4}) pinMode(p, OUTPUT);
  stopMotors();
  for (int i = 0; i < NUM_TASKS; i++) lastRunDay[i] = -1;

  Wire.begin(21, 22, 100000);  // MLX90614 needs 100 kHz
  mlx.begin();
  oled.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  pox.begin(Wire, I2C_SPEED_STANDARD);
  pox.setup(60, 4, 2, 100, 411, 4096);
  Serial2.begin(9600, SERIAL_8N1, PIN_DF_RX, PIN_DF_TX);
  player.begin(Serial2); player.volume(28);
  LittleFS.begin(true);
  show("ALAGA", "Connecting WiFi");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) delay(500);
  Serial.printf("WiFi %s, channel %d (set this channel in the pendant)\n",
                WiFi.status() == WL_CONNECTED ? "connected" : "NOT connected", WiFi.channel());
  configTime(8 * 3600, 0, "pool.ntp.org", "time.google.com");  // Philippine time, UTC+8
  tls.setCACert(TELEGRAM_CERTIFICATE_ROOT);
  if (esp_now_init() == ESP_OK) esp_now_register_recv_cb(onPendant);
  attachInterrupt(digitalPinToInterrupt(PIN_SOUND), onSound, RISING);
  notify(String("👋 ALAGA is on duty for ") + ELDER + ". Send /status any time.");
  deflate();
}

void loop() {
  service();
  pollTelegram();
  checkSchedule();
  if (digitalRead(PIN_BUTTON) == LOW) {  // hold 5 s = "I am on the dock"
    unsigned long t = millis();
    while (digitalRead(PIN_BUTTON) == LOW) delay(10);
    if (millis() - t > 5000) { pos = ST_DOCK; say(T_BYE); }
    else called();
  }
  if (soundHeard) { soundHeard = false; called(); soundHeard = false; }
  delay(20);
}

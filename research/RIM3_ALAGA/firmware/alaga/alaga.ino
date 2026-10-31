// ALAGA: low-cost soft inflatable healthcare companion robot (ESP32)
// Screening order: pain dial -> forehead temperature -> pulse rate and SpO2 -> triage -> spoken result.
// Libraries: Adafruit MLX90614, SparkFun MAX3010x (with spo2_algorithm), Adafruit SSD1306 + GFX,
// DFRobotDFPlayerMini. Board: ESP32 Dev Module. ALAGA screens and refers; it does not diagnose.

#include <Wire.h>
#include <LittleFS.h>
#include <Adafruit_MLX90614.h>
#include <Adafruit_SSD1306.h>
#include <DFRobotDFPlayerMini.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

// Pins (see the wiring table in Appendix G)
const int PIN_FAN = 25;      // IRF520 MOSFET gate, 12 V blower fan
const int PIN_BUTTON = 27;   // chest button to GND
const int PIN_SOUND = 26;    // KY-037 digital out ("aray!" or a loud voice)
const int PIN_TRIG = 32;     // HC-SR04 trigger
const int PIN_ECHO = 33;     // HC-SR04 echo through a 1k/2k divider
const int PIN_DIAL = 34;     // pain dial potentiometer wiper
const int PIN_DF_RX = 16, PIN_DF_TX = 17;

// Screening limits agreed with the school nurse
const float TEMP_FEVER = 37.5, TEMP_HIGH = 39.0;
const int SPO2_LOW = 95, SPO2_URGENT = 92;
const int PR_LOW = 60, PR_HIGH = 100, PR_URG_LOW = 40, PR_URG_HIGH = 130;
const int PAIN_REFER = 4, PAIN_URGENT = 7;

// Calibration from the calibration set (Step 6): body = a * skin + b
float TEMP_A = 1.00, TEMP_B = 2.30;
int SPO2_OFFSET = 0, PR_OFFSET = 0;

// Audio files on the microSD card: /mp3/0001.mp3 ...
enum Track { T_HELLO = 1, T_PAIN, T_TEMP, T_FINGER, T_GREEN, T_YELLOW, T_RED, T_BYE, T_CLOSER, T_RETRY };

enum State { SLEEP, WAKE, PAIN, TEMP, PULSE, TRIAGE, RESULT, BYE };
State state = SLEEP;

Adafruit_MLX90614 mlx;
MAX30105 pox;
Adafruit_SSD1306 oled(128, 64, &Wire, -1);
DFRobotDFPlayerMini player;

int pain = -1, pulseRate = -1, spo2 = -1;
float tempC = NAN;
char level = 'G';
unsigned long tStart = 0, tState = 0, tPrompt = 0;
bool spoke = false;

void say(Track t) { player.playMp3Folder(t); }

void show(const char *l1, const char *l2 = "") {
  oled.clearDisplay();
  oled.setTextColor(SSD1306_WHITE);
  oled.setTextSize(2); oled.setCursor(0, 0); oled.println(l1);
  oled.setTextSize(1); oled.setCursor(0, 40); oled.println(l2);
  oled.display();
}

void go(State s) { state = s; tState = millis(); spoke = false; }

bool pressed() {
  if (digitalRead(PIN_BUTTON) == LOW) { delay(30); while (digitalRead(PIN_BUTTON) == LOW) delay(5); return true; }
  return false;
}

float distanceCm() {
  digitalWrite(PIN_TRIG, LOW); delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  unsigned long us = pulseIn(PIN_ECHO, HIGH, 30000);
  return us ? us / 58.0 : 999;
}

int readPain() { return constrain(map(analogRead(PIN_DIAL), 0, 4095, 0, 11), 0, 10); }

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
      spo2 = min(100, (int)s + SPO2_OFFSET); pulseRate = hr + PR_OFFSET; return true;
    }
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

void logResult() {
  File f = LittleFS.open("/log.csv", FILE_APPEND);
  if (!f) return;
  f.printf("%lu,%d,%.1f,%d,%d,%c,%lu\n", millis() / 1000, pain, tempC, pulseRate, spo2, level,
           (millis() - tStart) / 1000);
  f.close();
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_FAN, OUTPUT); digitalWrite(PIN_FAN, LOW);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_SOUND, INPUT);
  pinMode(PIN_TRIG, OUTPUT); pinMode(PIN_ECHO, INPUT);
  Wire.begin(21, 22, 100000);  // MLX90614 needs 100 kHz
  mlx.begin();
  oled.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  pox.begin(Wire, I2C_SPEED_STANDARD);
  pox.setup(60, 4, 2, 100, 411, 4096);  // red + IR, 25 samples/s after averaging
  Serial2.begin(9600, SERIAL_8N1, PIN_DF_RX, PIN_DF_TX);
  player.begin(Serial2); player.volume(25);
  LittleFS.begin(true);
  show("ALAGA", "Press my chest");
}

void loop() {
  switch (state) {
    case SLEEP:
      if (pressed() || digitalRead(PIN_SOUND) == HIGH) {
        digitalWrite(PIN_FAN, HIGH); tStart = millis();
        pain = pulseRate = spo2 = -1; tempC = NAN;
        show("Hello!", "Inflating..."); go(WAKE);
      }
      break;
    case WAKE:
      if (millis() - tState > 20000) { say(T_HELLO); delay(4000); say(T_PAIN); go(PAIN); }
      break;
    case PAIN: {
      pain = readPain();
      char b[24]; snprintf(b, sizeof b, "Pain: %d / 10", pain);
      show(b, "Turn dial, press chest");
      if (pressed()) { say(T_TEMP); go(TEMP); }
      if (millis() - tState > 60000) go(BYE);
      break;
    }
    case TEMP: {
      float d = distanceCm();
      if (d >= 3 && d <= 5) {
        float sum = 0;
        for (int i = 0; i < 5; i++) { sum += mlx.readObjectTempC(); delay(100); }
        tempC = TEMP_A * (sum / 5) + TEMP_B;
        say(T_FINGER); show("Finger", "Place finger on cradle"); go(PULSE);
      } else if (millis() - tState > 20000) {
        go(BYE);
      } else if (d < 60 && millis() - tPrompt > 5000) {
        say(T_CLOSER); tPrompt = millis();
      }
      break;
    }
    case PULSE:
      pox.check();
      if (pox.getIR() > 50000) {
        show("Hold still", "Measuring...");
        if (readPulse()) go(TRIAGE); else { say(T_RETRY); tState = millis(); }
      } else if (millis() - tState > 20000) {
        go(BYE);
      }
      break;
    case TRIAGE:
      level = triage(); logResult(); go(RESULT);
      break;
    case RESULT: {
      char b[48];
      snprintf(b, sizeof b, "%.1fC PR%d SpO2 %d%% P%d", tempC, pulseRate, spo2, pain);
      show(level == 'G' ? "GREEN" : level == 'Y' ? "YELLOW" : "RED", b);
      say(level == 'G' ? T_GREEN : level == 'Y' ? T_YELLOW : T_RED);
      Serial.printf("RESULT,%s,%lu s\n", b, (millis() - tStart) / 1000);
      delay(8000); go(BYE);
      break;
    }
    case BYE:
      if (!spoke) { say(T_BYE); spoke = true; }
      if (millis() - tState > 30000 || pressed()) {
        digitalWrite(PIN_FAN, LOW); show("ALAGA", "Press my chest"); go(SLEEP);
      }
      break;
  }
}

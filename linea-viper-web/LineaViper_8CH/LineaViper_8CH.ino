// =====================================================================
//  LINEA VIPER 8CH - ESP32-S3 Wi-Fi control (no extra library needed)
//  Phone -> join Wi-Fi "LineaViper8" (password 12345678) -> open 192.168.4.1
//  Calibration tab : live 16 sensor bars, Capture WHITE / BLACK, Reset, Save to ESP32
//  LineaTrack tab  : Speed / Kp / Kd / Duration sliders, Run / Stop, copy LineaTrack(...) code
//  RC Drive tab    : joystick / arrow buttons drive the robot by hand (stops if Wi-Fi drops)
//  Board: "ESP32S3 Dev Module" in Arduino IDE (esp32 core 2.0.x or 3.x)
// =====================================================================
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>

// ---------------- SENSOR BOARD ----------------
#define NUM_SENSORS 8                  // 4, 8 or 16
#define USE_MUX 0                      // 1 = 16CH board through the CD74HC4067 mux, 0 = sensors wired straight to ADC pins
// ---------------- PINS (CHECK THESE AGAINST YOUR BOARD) ----------------
const int MUX_S[4] = {14, 13, 12, 11};   // mux S1, S2, S3, S4 -> GPIO (16CH only)
const int MUX_SIG  = 1;                  // mux SIG -> ADC GPIO 1..10 (16CH only)
const int DIRECT_PINS[8] = {1, 2, 3, 8, 9, 10, 4, 5};   // 4CH / 8CH: sensor outputs, left to right (ADC GPIO 1..10 only)
// TB6612 motor driver
const int PWMA = 4,  AIN1 = 5,  AIN2 = 6;   // left motor
const int PWMB = 7,  BIN1 = 15, BIN2 = 16;  // right motor
const int STBY = 17;                        // set to -1 if STBY is tied high
const int OK_BTN = 0;                       // OK button (active LOW), -1 = none

// ---------------- SETTINGS ----------------
const char* AP_SSID = "LineaViper8";
const char* AP_PASS = "12345678";
const int N = NUM_SENSORS;
const bool BLACK_LINE = true;     // true = black line on white, false = white line on black

WebServer server(80);
Preferences prefs;
int raw[N], cal[N], whiteV[N], blackV[N];
const long CENTER = (N - 1) * 500L;   // middle of the array (7500 for 16CH)
long linePos = CENTER;
int lastErr = 0;
bool running = false;
bool rcMode = false; unsigned long rcLast = 0;   // RC drive from the phone
unsigned long runEnd = 0;
int runSpeed = 79; float runKp = 0.035, runKd = 0.10;

// ---------------- SENSORS ----------------
int readChannel(int ch) {
#if !USE_MUX
  return analogRead(DIRECT_PINS[ch]);
#endif
  for (int b = 0; b < 4; b++) digitalWrite(MUX_S[b], (ch >> b) & 1);
  delayMicroseconds(5);                         // mux settle
  return analogRead(MUX_SIG);
}

void readSensors() {
  long sum = 0, wsum = 0;
  for (int i = 0; i < N; i++) {
    raw[i] = readChannel(i);
    int lo = whiteV[i], hi = blackV[i];
    if (!BLACK_LINE) { lo = blackV[i]; hi = whiteV[i]; }
    long v = (hi == lo) ? 0 : (long)(raw[i] - lo) * 1000 / (hi - lo);   // 0 = background, 1000 = line
    v = constrain(v, 0, 1000);
    cal[i] = v;
    if (v > 100) { sum += v; wsum += v * (long)i * 1000; }              // ignore noise below 10 %
  }
  if (sum > 0) linePos = wsum / sum;                                   // 0 .. (N-1)*1000
  else linePos = (lastErr > 0) ? (N - 1) * 1000L : 0;                           // line lost: keep last side
}

// ---------------- MOTORS ----------------
void motor(int pwm, int in1, int in2, int sp) {
  sp = constrain(sp, -255, 255);
  digitalWrite(in1, sp > 0); digitalWrite(in2, sp < 0);
  analogWrite(pwm, abs(sp));
}
void Motor(int l, int r) { motor(PWMA, AIN1, AIN2, l); motor(PWMB, BIN1, BIN2, r); }
void Stop() { Motor(0, 0); running = false; }

// ---------------- PID (same idea as LineaTrack) ----------------
void pidStep(int speed, float kp, float kd) {
  readSensors();
  int err = (linePos - CENTER) * 15 / (N - 1);   // scaled so Kp/Kd feel the same on 4/8/16CH
  int corr = kp * err + kd * (err - lastErr);
  lastErr = err;
  corr = constrain(corr, -255, 255);
  Motor(speed + corr, speed - corr);
}

// call from your own code: LineaTrack(speed, kp, kd, milliseconds)
void LineaTrack(int speed, float kp, float kd, int totalTime) {
  unsigned long end = millis() + totalTime;
  while (millis() < end) { pidStep(speed, kp, kd); server.handleClient(); delay(2); }
  Stop();
}

// ---------------- CALIBRATION STORAGE ----------------
void loadCal() {
  prefs.begin("viper", true);
  for (int i = 0; i < N; i++) {
    whiteV[i] = prefs.getInt(("w" + String(i)).c_str(), 300);
    blackV[i] = prefs.getInt(("b" + String(i)).c_str(), 3000);
  }
  prefs.end();
}
void saveCal() {
  prefs.begin("viper", false);
  for (int i = 0; i < N; i++) { prefs.putInt(("w" + String(i)).c_str(), whiteV[i]); prefs.putInt(("b" + String(i)).c_str(), blackV[i]); }
  prefs.end();
}
void capture(int* dst) {                       // average 20 readings per sensor
  long acc[N] = {0};
  for (int k = 0; k < 20; k++) { for (int i = 0; i < N; i++) acc[i] += readChannel(i); delay(5); }
  for (int i = 0; i < N; i++) dst[i] = acc[i] / 20;
}

// ---------------- WEB PAGE ----------------
const char PAGE[] PROGMEM = R"HTML(
<title>Linea Viper Control</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* layout: phone-first control panel, two tabs (Calibration / LineaTrack) */
:root{--bg:#0b1220;--panel:#121b2e;--line:#22304d;--fg:#e6edf7;--muted:#8a9bb8;--accent:#22c3ee;--accent-fg:#06202a;--stop:#f2643c;--bar:#1da1d6;--white:#e6edf7;color-scheme:dark;
--body:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--mono:ui-monospace,Menlo,Consolas,monospace}
body{background:var(--bg);color:var(--fg);font:15px/1.45 var(--body);margin:0;padding-left:max(14px,env(safe-area-inset-left,0px));padding-right:max(14px,env(safe-area-inset-right,0px));padding-block:14px 30px}
.wrap{max-width:560px;margin:0 auto;display:grid;gap:12px}
h1{font-size:20px;margin:0;letter-spacing:.06em}h1 b{color:var(--accent)}
.st{font-size:12px;color:var(--muted)}
.tabs{display:flex;gap:18px;border-bottom:1px solid var(--line)}
.tab{background:none;border:0;color:var(--muted);font:600 15px var(--body);padding:8px 2px;cursor:pointer;border-bottom:2px solid transparent}
.tab[aria-selected="true"]{color:var(--accent);border-color:var(--accent)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;display:grid;gap:12px;min-width:0}
.row{display:flex;gap:8px;flex-wrap:wrap}
.btn{font:600 14px var(--body);border:0;border-radius:8px;padding:9px 14px;background:var(--accent);color:var(--accent-fg);cursor:pointer}
.btn.dark{background:#1c2740;color:var(--fg)}.btn.stop{background:var(--stop);color:#fff}
.btn:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.bars{display:grid;grid-template-columns:repeat(var(--n,16),1fr);gap:3px;height:150px;align-items:end;background:#0a1120;border:1px solid var(--line);border-radius:8px;padding:6px}
.bars div{background:var(--bar);border-radius:2px;min-height:2px;transition:height .08s}
.lbl{display:grid;grid-template-columns:repeat(var(--n,16),1fr);gap:3px;font:10px var(--mono);color:var(--muted);text-align:center;padding:0 6px}
.pos{position:relative;height:8px;background:#0a1120;border-radius:4px;border:1px solid var(--line)}.pos i{position:absolute;top:-3px;width:12px;height:12px;border-radius:50%;background:var(--accent);margin-left:-6px}
table{width:100%;border-collapse:collapse;font:12px var(--mono)}th,td{padding:3px 6px;border-bottom:1px solid var(--line);text-align:right}th:first-child,td:first-child{text-align:left;color:var(--muted)}
.tw{overflow-x:auto}
.sl{display:grid;grid-template-columns:70px 1fr 64px;gap:10px;align-items:center}
.sl input[type=range]{width:100%;accent-color:var(--accent)}
.sl output{font:600 14px var(--mono);text-align:right}
input[type=number]{background:#0a1120;color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 8px;font:14px var(--mono);width:110px}
.pad{position:relative;width:min(80vw,280px);aspect-ratio:1;margin:0 auto;border-radius:50%;background:#0a1120;border:2px solid var(--line);touch-action:none}.pad i{position:absolute;left:50%;top:50%;width:70px;height:70px;margin:-35px;border-radius:50%;background:var(--accent);box-shadow:0 0 20px #22c3ee66}
.dp{display:grid;grid-template-columns:repeat(3,64px);gap:6px;justify-content:center}.dp .btn{height:56px;font-size:20px}
pre{margin:0;background:#0a1120;border:1px solid var(--line);border-radius:8px;padding:10px;font:13px var(--mono);overflow-x:auto}
.note{font-size:13px;color:var(--muted);margin:0}
</style>
<div class="wrap">
<header><h1>LINEA <b>VIPER</b> <span id="nch">X16</span></h1><div class="st" id="st">connecting…</div></header>
<nav class="tabs"><button class="tab" id="t1" aria-selected="true">Calibration</button><button class="tab" id="t2" aria-selected="false">LineaTrack</button><button class="tab" id="t3" aria-selected="false">RC Drive</button></nav>

<section class="card" id="v1">
<div class="row"><button class="btn" data-a="capture?c=white">Capture WHITE</button><button class="btn" data-a="capture?c=black">Capture BLACK</button><button class="btn dark" data-a="reset">Reset</button><button class="btn dark" data-a="save">Save to ESP32</button></div>
<p class="note">Live line values below. Move the robot over white and black surfaces, then capture.</p>
<div class="bars" id="bars"></div><div class="lbl" id="lbl"></div>
<div class="pos" aria-label="line position"><i id="pi" style="left:50%"></i></div>
<div class="tw"><table><thead><tr><th>Sensor</th><th>Raw</th><th>White</th><th>Black</th></tr></thead><tbody id="tb"></tbody></table></div>
</section>

<section class="card" id="v2" hidden>
<div class="row"><button class="btn" id="run">Run</button><button class="btn stop" data-a="stop">Stop</button></div>
<div class="sl"><span>Speed</span><input id="sp" type="range" min="0" max="255" value="79"><output id="osp"></output></div>
<div class="sl"><span>Kp</span><input id="kp" type="range" min="0" max="0.2" step="0.001" value="0.035"><output id="okp"></output></div>
<div class="sl"><span>Kd</span><input id="kd" type="range" min="0" max="2" step="0.01" value="0.10"><output id="okd"></output></div>
<div class="row" style="align-items:center"><span style="width:70px">Duration</span><input id="du" type="number" value="10000" min="500" step="500"> ms</div>
<div class="row"><button class="btn dark" data-t="5000">5s</button><button class="btn dark" data-t="10000">10s</button><button class="btn dark" data-t="20000">20s</button><button class="btn dark" data-t="60000">60s</button></div>
<p class="note">Generated sequence (paste into the Arduino sketch's Program1):</p>
<pre id="code"></pre><div class="row"><button class="btn dark" id="copy">Copy code</button></div>
</section>
<section class="card" id="v3" hidden>
<p class="note">Drag the joystick (or hold the arrows). Let go = stop. The robot also stops by itself if the connection drops.</p>
<div class="pad" id="pad"><i id="knob"></i></div>
<div class="dp"><span></span><button class="btn dark" data-d="1,0">▲</button><span></span><button class="btn dark" data-d="0,-1">◀</button><button class="btn stop" data-d="0,0">■</button><button class="btn dark" data-d="0,1">▶</button><span></span><button class="btn dark" data-d="-1,0">▼</button><span></span></div>
<div class="sl"><span>Max speed</span><input id="rcmax" type="range" min="40" max="255" value="180"><output id="orc">180</output></div>
<p class="note" id="rcst">L 0 · R 0</p>
</section>
</div>
<script>
const $=id=>document.getElementById(id);let demo=false,t=0;
let N=0;function build(n){N=n;document.documentElement.style.setProperty("--n",n);$("nch").textContent="X"+n;$("bars").innerHTML=$("lbl").innerHTML=$("tb").innerHTML="";
for(let i=0;i<n;i++){$("bars").insertAdjacentHTML("beforeend","<div></div>");$("lbl").insertAdjacentHTML("beforeend",`<span>${i}</span>`);$("tb").insertAdjacentHTML("beforeend",`<tr><td>S${i}</td><td></td><td></td><td></td></tr>`);}}
const TB=[["t1","v1"],["t2","v2"],["t3","v3"]];TB.forEach(([b,v])=>$(b).onclick=()=>{TB.forEach(([x,w])=>{$(x).setAttribute("aria-selected",x===b);$(w).hidden=w!==v;});if(v!=="v3")drive(0,0);});
function api(p){if(demo){$("st").textContent="demo: "+p;return Promise.resolve();}return fetch("/"+p).then(r=>r.text()).then(m=>$("st").textContent=m).catch(()=>$("st").textContent="no connection");}
document.querySelectorAll("[data-a]").forEach(b=>b.onclick=()=>api(b.dataset.a));
document.querySelectorAll("[data-t]").forEach(b=>b.onclick=()=>{$("du").value=b.dataset.t;upd();});
function upd(){const s=$("sp").value,kp=(+$("kp").value).toFixed(3),kd=(+$("kd").value).toFixed(2),d=$("du").value;$("osp").value=s;$("okp").value=kp;$("okd").value=kd;$("code").textContent=`LineaTrack(${s}, ${kp}, ${kd}, ${d});`;return{s,kp,kd,d};}
["sp","kp","kd","du"].forEach(i=>$(i).oninput=upd);upd();
$("run").onclick=()=>{const v=upd();api(`run?s=${v.s}&kp=${v.kp}&kd=${v.kd}&t=${v.d}`);};
$("copy").onclick=()=>{const txt=$("code").textContent;navigator.clipboard?navigator.clipboard.writeText(txt).then(()=>$("copy").textContent="Copied",()=>{}):0;};
function show(d){if(d.raw.length!==N)build(d.raw.length);const bars=$("bars").children,rows=$("tb").children;for(let i=0;i<N;i++){bars[i].style.height=(d.cal[i]/10)+"%";const c=rows[i].children;c[1].textContent=d.raw[i];c[2].textContent=d.wh[i];c[3].textContent=d.bk[i];}
 $("pi").style.left=(d.pos/((N-1)*10))+"%";if(!demo)$("st").textContent=(d.run?"RUNNING":"idle")+" · 192.168.4.1";}
function fake(){t+=.12;const n=16,c=7500+5500*Math.sin(t),raw=[],cal=[];for(let i=0;i<n;i++){const v=Math.max(0,1000-Math.abs(i*1000-c)/1.2);cal.push(Math.round(v));raw.push(Math.round(300+v*2.8));}
 return{raw,cal,wh:Array(16).fill(300),bk:Array(16).fill(3100),pos:c,run:false};}
function poll(){if(demo){show(fake());return setTimeout(poll,120);}fetch("/data").then(r=>r.json()).then(d=>{show(d);setTimeout(poll,150);}).catch(()=>{demo=true;$("st").textContent="demo mode (not connected to the robot)";poll();});}
/* RC */
let rcL=0,rcR=0,last="";function drive(f,t){const m=+$("rcmax").value;rcL=Math.round(Math.max(-1,Math.min(1,f+t))*m);rcR=Math.round(Math.max(-1,Math.min(1,f-t))*m);$("rcst").textContent=`L ${rcL} · R ${rcR}`;}
setInterval(()=>{if($("v3").hidden)return;const k=rcL+","+rcR;if(k==="0,0"&&last==="0,0")return;last=k;if(!demo)fetch(`/rc?l=${rcL}&r=${rcR}`).catch(()=>{});},100);
$("rcmax").oninput=()=>$("orc").value=$("rcmax").value;
const pad=$("pad"),knob=$("knob");function mv(e){const b=pad.getBoundingClientRect(),R=b.width/2;let x=(e.clientX-b.left-R)/R,y=(e.clientY-b.top-R)/R;const d=Math.hypot(x,y);if(d>1){x/=d;y/=d;}knob.style.left=50+x*40+"%";knob.style.top=50+y*40+"%";drive(-y,x);}
pad.onpointerdown=e=>{pad.setPointerCapture(e.pointerId);mv(e);};pad.onpointermove=e=>{if(e.buttons)mv(e);};pad.onpointerup=pad.onpointercancel=()=>{knob.style.left=knob.style.top="50%";drive(0,0);};
document.querySelectorAll("[data-d]").forEach(b=>{const[f,t]=b.dataset.d.split(",").map(Number);b.onpointerdown=()=>drive(f,t);b.onpointerup=b.onpointerleave=()=>drive(0,0);});
poll();
</script>

)HTML";

String arr(int* a) { String s = "["; for (int i = 0; i < N; i++) { s += a[i]; if (i < N - 1) s += ","; } return s + "]"; }

void setupWeb() {
  server.on("/", [] { server.send_P(200, "text/html", PAGE); });
  server.on("/data", [] {
    if (!running) readSensors();
    server.send(200, "application/json", "{\"raw\":" + arr(raw) + ",\"cal\":" + arr(cal) + ",\"wh\":" + arr(whiteV) +
                ",\"bk\":" + arr(blackV) + ",\"pos\":" + String(linePos) + ",\"run\":" + (running ? "true" : "false") + "}");
  });
  server.on("/capture", [] {
    bool w = server.arg("c") == "white";
    capture(w ? whiteV : blackV);
    server.send(200, "text/plain", w ? "WHITE captured" : "BLACK captured");
  });
  server.on("/reset", [] { for (int i = 0; i < N; i++) { whiteV[i] = 300; blackV[i] = 3000; } server.send(200, "text/plain", "calibration reset"); });
  server.on("/save", [] { saveCal(); server.send(200, "text/plain", "saved to ESP32"); });
  server.on("/run", [] {
    runSpeed = server.arg("s").toInt(); runKp = server.arg("kp").toFloat(); runKd = server.arg("kd").toFloat();
    runEnd = millis() + server.arg("t").toInt(); lastErr = 0; running = true;
    server.send(200, "text/plain", "RUNNING");
  });
  server.on("/stop", [] { Stop(); rcMode = false; server.send(200, "text/plain", "stopped"); });
  server.on("/rc", [] {                       // RC: left / right motor -255..255
    running = false; rcMode = true; rcLast = millis();
    Motor(server.arg("l").toInt(), server.arg("r").toInt());
    server.send(200, "text/plain", "RC");
  });
  server.begin();
}

void setup() {
  Serial.begin(115200);
  for (int b = 0; b < 4; b++) pinMode(MUX_S[b], OUTPUT);
  pinMode(MUX_SIG, INPUT);
  if (!USE_MUX) for (int i = 0; i < N; i++) pinMode(DIRECT_PINS[i], INPUT);
  int outs[] = {PWMA, AIN1, AIN2, PWMB, BIN1, BIN2};
  for (int p : outs) pinMode(p, OUTPUT);
  if (STBY >= 0) { pinMode(STBY, OUTPUT); digitalWrite(STBY, HIGH); }
  if (OK_BTN >= 0) pinMode(OK_BTN, INPUT_PULLUP);
  analogReadResolution(12);
  loadCal();
  Stop();
  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.print("Open http://"); Serial.println(WiFi.softAPIP());   // 192.168.4.1
  setupWeb();
}

void loop() {
  server.handleClient();
  if (rcMode && millis() - rcLast > 400) { Motor(0, 0); rcMode = false; }   // RC failsafe: no command = stop
  if (running) {
    if (millis() >= runEnd) Stop();
    else pidStep(runSpeed, runKp, runKd);
  }
  if (OK_BTN >= 0 && digitalRead(OK_BTN) == LOW && !running) {   // OK button = run with the last web settings
    delay(300); runEnd = millis() + 10000; lastErr = 0; running = true;
  }
  delay(2);
}

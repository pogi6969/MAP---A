// =====================================================================
//  LINEA VIPER - ESP32-S3 Wi-Fi line follower app (4 / 8 / 16 sensors, set from the phone)
//  Phone -> Wi-Fi "LineaViper" (password 12345678) -> open 192.168.4.1
//  Calibration : live sensor bars, Capture WHITE / BLACK, Reset, Save
//  LineaTrack  : Speed / Kp / Kd / Duration, Run / Stop, copy LineaTrack(...) code
//  Settings    : number of sensors, mux or direct wiring, every pin, line colour - saved, no re-upload
//  Arduino IDE board: "ESP32S3 Dev Module". No extra library needed.
// =====================================================================
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>

const char* AP_SSID = "LineaViper";
const char* AP_PASS = "12345678";

// ---------------- CONFIG (defaults - change them in the Settings tab) ----------------
int N = 16;                 // 4, 8 or 16 sensors
int useMux = 1;             // 1 = CD74HC4067 mux, 0 = sensors wired straight to ADC pins
int blackLine = 1;          // 1 = black line on white
int muxS[4] = {14, 13, 12, 11}, muxSig = 1;
int direct[16] = {1, 2, 3, 8, 9, 10, 4, 5};
int mA[3] = {4, 5, 6}, mB[3] = {7, 15, 16};   // PWM, IN1, IN2
int stby = 17, okBtn = 0, swapLR = 0;

WebServer server(80);
Preferences prefs;
int raw[16], cal[16], whiteV[16], blackV[16];
long linePos = 0, center = 7500;
int lastErr = 0;
bool running = false;
unsigned long runEnd = 0;
int runSpeed = 79; float runKp = 0.035, runKd = 0.10;

int parseList(String s, int* out, int maxN) {          // "14,13,12,11" -> array
  int n = 0;
  while (s.length() && n < maxN) { int c = s.indexOf(','); out[n++] = (c < 0 ? s : s.substring(0, c)).toInt(); if (c < 0) break; s = s.substring(c + 1); }
  return n;
}
String list(int* a, int n) { String s; for (int i = 0; i < n; i++) { s += a[i]; if (i < n - 1) s += ","; } return s; }

// ---------------- SENSORS ----------------
int readChannel(int ch) {
  if (!useMux) return analogRead(direct[ch]);
  for (int b = 0; b < 4; b++) digitalWrite(muxS[b], (ch >> b) & 1);
  delayMicroseconds(5);
  return analogRead(muxSig);
}
void readSensors() {
  long sum = 0, wsum = 0;
  for (int i = 0; i < N; i++) {
    raw[i] = readChannel(i);
    int lo = blackLine ? whiteV[i] : blackV[i], hi = blackLine ? blackV[i] : whiteV[i];
    long v = (hi == lo) ? 0 : (long)(raw[i] - lo) * 1000 / (hi - lo);
    cal[i] = v = constrain(v, 0, 1000);                     // 0 = background, 1000 = line
    if (v > 100) { sum += v; wsum += v * (long)i * 1000; }
  }
  if (sum > 0) linePos = wsum / sum;                        // weighted average position
  else linePos = (lastErr > 0) ? (N - 1) * 1000L : 0;       // lost: keep turning to the last side
}

// ---------------- MOTORS ----------------
void motor(int* m, int sp) { sp = constrain(sp, -255, 255); digitalWrite(m[1], sp > 0); digitalWrite(m[2], sp < 0); analogWrite(m[0], abs(sp)); }
void Motor(int l, int r) { if (swapLR) { int t = l; l = r; r = t; } motor(mA, l); motor(mB, r); }
void Stop() { Motor(0, 0); running = false; }

void pidStep(int speed, float kp, float kd) {
  readSensors();
  int err = (linePos - center) * 15 / (N - 1);              // same scale as 16CH, so Kp/Kd carry over
  int corr = constrain((int)(kp * err + kd * (err - lastErr)), -255, 255);
  lastErr = err;
  Motor(speed + corr, speed - corr);
}
void LineaTrack(int speed, float kp, float kd, int totalTime) {   // same call as the Reybot library
  unsigned long end = millis() + totalTime;
  while (millis() < end) { pidStep(speed, kp, kd); server.handleClient(); delay(2); }
  Stop();
}

// ---------------- SAVE / LOAD ----------------
void loadAll() {
  prefs.begin("viper", true);
  N = prefs.getInt("N", N); useMux = prefs.getInt("mux", useMux); blackLine = prefs.getInt("blk", blackLine);
  parseList(prefs.getString("S", list(muxS, 4)), muxS, 4); muxSig = prefs.getInt("G", muxSig);
  parseList(prefs.getString("D", list(direct, 8)), direct, 16);
  parseList(prefs.getString("A", list(mA, 3)), mA, 3); parseList(prefs.getString("B", list(mB, 3)), mB, 3);
  stby = prefs.getInt("stby", stby); okBtn = prefs.getInt("ok", okBtn); swapLR = prefs.getInt("sw", swapLR);
  for (int i = 0; i < 16; i++) { whiteV[i] = prefs.getInt(("w" + String(i)).c_str(), 300); blackV[i] = prefs.getInt(("b" + String(i)).c_str(), 3000); }
  prefs.end();
  N = (N == 4 || N == 8) ? N : 16;
  center = (N - 1) * 500L;
}
void saveCal() {
  prefs.begin("viper", false);
  for (int i = 0; i < 16; i++) { prefs.putInt(("w" + String(i)).c_str(), whiteV[i]); prefs.putInt(("b" + String(i)).c_str(), blackV[i]); }
  prefs.end();
}
void capture(int* dst) {
  long acc[16] = {0};
  for (int k = 0; k < 20; k++) { for (int i = 0; i < N; i++) acc[i] += readChannel(i); delay(5); }
  for (int i = 0; i < N; i++) dst[i] = acc[i] / 20;
}

// ---------------- WEB ----------------
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
input[type=number],select,label input,select{background:#0a1120;color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 8px;font:14px var(--mono);width:110px}
.pad{position:relative;width:min(80vw,280px);aspect-ratio:1;margin:0 auto;border-radius:50%;background:#0a1120;border:2px solid var(--line);touch-action:none}.pad i{position:absolute;left:50%;top:50%;width:70px;height:70px;margin:-35px;border-radius:50%;background:var(--accent);box-shadow:0 0 20px #22c3ee66}
.dp{display:grid;grid-template-columns:repeat(3,64px);gap:6px;justify-content:center}.dp .btn{height:56px;font-size:20px}
pre{margin:0;background:#0a1120;border:1px solid var(--line);border-radius:8px;padding:10px;font:13px var(--mono);overflow-x:auto}
.note{font-size:13px;color:var(--muted);margin:0}
</style>
<div class="wrap">
<header><h1>LINEA <b>VIPER</b> <span id="nch">X16</span></h1><div class="st" id="st">connecting…</div></header>
<nav class="tabs"><button class="tab" id="t1" aria-selected="true">Calibration</button><button class="tab" id="t2" aria-selected="false">LineaTrack</button><button class="tab" id="t3" aria-selected="false">Settings</button></nav>

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
<p class="note">Change the board setup here, press Save &amp; restart. No re-upload needed.</p>
<div class="sl"><span>Sensors</span><select id="cN"><option>4</option><option>8</option><option selected>16</option></select><span></span></div>
<div class="sl"><span>Wiring</span><select id="cM"><option value="1">16CH mux (S1-S4 + SIG)</option><option value="0">direct to ADC pins</option></select><span></span></div>
<div class="sl"><span>Line</span><select id="cB"><option value="1">black line on white</option><option value="0">white line on black</option></select><span></span></div>
<label class="note">Mux S1,S2,S3,S4 <input id="cS" value="14,13,12,11"></label>
<label class="note">Mux SIG <input id="cG" value="1"></label>
<label class="note">Direct sensor pins, left to right (GPIO 1-10) <input id="cD" value="1,2,3,8,9,10,4,5"></label>
<label class="note">Left motor PWMA,AIN1,AIN2 <input id="cA" value="4,5,6"></label>
<label class="note">Right motor PWMB,BIN1,BIN2 <input id="cBm" value="7,15,16"></label>
<label class="note">STBY, OK button (-1 = none) <input id="cO" value="17,0"></label>
<label class="note">Swap left/right motors <select id="cW"><option value="0">no</option><option value="1">yes</option></select></label>
<div class="row"><button class="btn" id="csave">Save &amp; restart</button></div>
</section>
</div>
<script>
const $=id=>document.getElementById(id);let demo=false,t=0;
let N=0;function build(n){N=n;document.documentElement.style.setProperty("--n",n);$("nch").textContent="X"+n;$("bars").innerHTML=$("lbl").innerHTML=$("tb").innerHTML="";
for(let i=0;i<n;i++){$("bars").insertAdjacentHTML("beforeend","<div></div>");$("lbl").insertAdjacentHTML("beforeend",`<span>${i}</span>`);$("tb").insertAdjacentHTML("beforeend",`<tr><td>S${i}</td><td></td><td></td><td></td></tr>`);}}
const TB=[["t1","v1"],["t2","v2"],["t3","v3"]];TB.forEach(([b,v])=>$(b).onclick=()=>{TB.forEach(([x,w])=>{$(x).setAttribute("aria-selected",x===b);$(w).hidden=w!==v;});});
function api(p){if(demo){$("st").textContent="demo: "+p;return Promise.resolve();}return fetch("/"+p).then(r=>r.text()).then(m=>$("st").textContent=m).catch(()=>$("st").textContent="no connection");}
document.querySelectorAll("[data-a]").forEach(b=>b.onclick=()=>api(b.dataset.a));
document.querySelectorAll("[data-t]").forEach(b=>b.onclick=()=>{$("du").value=b.dataset.t;upd();});
function upd(){const s=$("sp").value,kp=(+$("kp").value).toFixed(3),kd=(+$("kd").value).toFixed(2),d=$("du").value;$("osp").value=s;$("okp").value=kp;$("okd").value=kd;$("code").textContent=`LineaTrack(${s}, ${kp}, ${kd}, ${d});`;return{s,kp,kd,d};}
["sp","kp","kd","du"].forEach(i=>$(i).oninput=upd);upd();
$("run").onclick=()=>{const v=upd();api(`run?s=${v.s}&kp=${v.kp}&kd=${v.kd}&t=${v.d}`);};
$("copy").onclick=()=>{const txt=$("code").textContent;navigator.clipboard?navigator.clipboard.writeText(txt).then(()=>$("copy").textContent="Copied",()=>{}):0;};
function show(d){if(d.raw.length!==N)build(d.raw.length);const bars=$("bars").children,rows=$("tb").children;for(let i=0;i<N;i++){bars[i].style.height=(d.cal[i]/10)+"%";const c=rows[i].children;c[1].textContent=d.raw[i];c[2].textContent=d.wh[i];c[3].textContent=d.bk[i];}
 $("pi").style.left=(d.pos/150)+"%";if(!demo)$("st").textContent=(d.run?"RUNNING":"idle")+" · 192.168.4.1";}
function fake(){t+=.12;const n=16,c=7500+5500*Math.sin(t),raw=[],cal=[];for(let i=0;i<n;i++){const v=Math.max(0,1000-Math.abs(i*1000-c)/1.2);cal.push(Math.round(v));raw.push(Math.round(300+v*2.8));}
 return{raw,cal,wh:Array(16).fill(300),bk:Array(16).fill(3100),pos:c,run:false};}
function poll(){if(demo){show(fake());return setTimeout(poll,120);}fetch("/data").then(r=>r.json()).then(d=>{show(d);setTimeout(poll,150);}).catch(()=>{demo=true;$("st").textContent="demo mode (not connected to the robot)";poll();});}
/* settings */
const CF=["cN","cM","cB","cS","cG","cD","cA","cBm","cO","cW"];
fetch("/cfg").then(r=>r.json()).then(c=>CF.forEach(k=>{if(c[k]!==undefined)$(k).value=c[k];})).catch(()=>{});
$("csave").onclick=()=>{const q=CF.map(k=>k+"="+encodeURIComponent($(k).value.replace(/\s/g,""))).join("&");api("setcfg?"+q).then(()=>$("st").textContent="saved - restarting, reconnect in 5 s");};
poll();
</script>

)HTML";

String arr(int* a) { return "[" + list(a, N) + "]"; }
String q(const char* k) { return server.arg(k); }

void setupWeb() {
  server.on("/", [] { server.send_P(200, "text/html", PAGE); });
  server.on("/data", [] {
    if (!running) readSensors();
    server.send(200, "application/json", "{\"raw\":" + arr(raw) + ",\"cal\":" + arr(cal) + ",\"wh\":" + arr(whiteV) + ",\"bk\":" + arr(blackV) +
                ",\"pos\":" + String(linePos * 15 / (N - 1)) + ",\"run\":" + (running ? "true" : "false") + "}");
  });
  server.on("/capture", [] { bool w = q("c") == "white"; capture(w ? whiteV : blackV); server.send(200, "text/plain", w ? "WHITE captured" : "BLACK captured"); });
  server.on("/reset", [] { for (int i = 0; i < 16; i++) { whiteV[i] = 300; blackV[i] = 3000; } server.send(200, "text/plain", "calibration reset"); });
  server.on("/save", [] { saveCal(); server.send(200, "text/plain", "saved to ESP32"); });
  server.on("/run", [] { runSpeed = q("s").toInt(); runKp = q("kp").toFloat(); runKd = q("kd").toFloat(); runEnd = millis() + q("t").toInt(); lastErr = 0; running = true; server.send(200, "text/plain", "RUNNING"); });
  server.on("/stop", [] { Stop(); server.send(200, "text/plain", "stopped"); });
  server.on("/cfg", [] {
    server.send(200, "application/json", "{\"cN\":\"" + String(N) + "\",\"cM\":\"" + String(useMux) + "\",\"cB\":\"" + String(blackLine) + "\",\"cS\":\"" + list(muxS, 4) +
                "\",\"cG\":\"" + String(muxSig) + "\",\"cD\":\"" + list(direct, N == 16 ? 8 : N) + "\",\"cA\":\"" + list(mA, 3) + "\",\"cBm\":\"" + list(mB, 3) +
                "\",\"cO\":\"" + String(stby) + "," + String(okBtn) + "\",\"cW\":\"" + String(swapLR) + "\"}");
  });
  server.on("/setcfg", [] {
    int o[2] = {stby, okBtn};
    prefs.begin("viper", false);
    prefs.putInt("N", q("cN").toInt()); prefs.putInt("mux", q("cM").toInt()); prefs.putInt("blk", q("cB").toInt());
    prefs.putString("S", q("cS")); prefs.putInt("G", q("cG").toInt()); prefs.putString("D", q("cD"));
    prefs.putString("A", q("cA")); prefs.putString("B", q("cBm")); parseList(q("cO"), o, 2);
    prefs.putInt("stby", o[0]); prefs.putInt("ok", o[1]); prefs.putInt("sw", q("cW").toInt());
    prefs.end();
    server.send(200, "text/plain", "saved - restarting");
    delay(500); ESP.restart();
  });
  server.begin();
}

void setup() {
  Serial.begin(115200);
  loadAll();
  if (useMux) { for (int b = 0; b < 4; b++) pinMode(muxS[b], OUTPUT); pinMode(muxSig, INPUT); }
  else for (int i = 0; i < N; i++) pinMode(direct[i], INPUT);
  for (int i = 0; i < 3; i++) { pinMode(mA[i], OUTPUT); pinMode(mB[i], OUTPUT); }
  if (stby >= 0) { pinMode(stby, OUTPUT); digitalWrite(stby, HIGH); }
  if (okBtn >= 0) pinMode(okBtn, INPUT_PULLUP);
  analogReadResolution(12);
  Stop();
  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.printf("%d sensors, %s - open http://", N, useMux ? "mux" : "direct"); Serial.println(WiFi.softAPIP());
  setupWeb();
}

void loop() {
  server.handleClient();
  if (running) { if (millis() >= runEnd) Stop(); else pidStep(runSpeed, runKp, runKd); }
  if (okBtn >= 0 && !running && digitalRead(okBtn) == LOW) { delay(300); runEnd = millis() + 10000; lastErr = 0; running = true; }
  delay(2);
}

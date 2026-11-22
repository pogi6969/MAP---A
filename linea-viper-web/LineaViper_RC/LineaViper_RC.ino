// =====================================================================
//  LINEA VIPER RC - ESP32-S3 remote control over Wi-Fi
//  Phone -> Wi-Fi "LineaViperRC" (password 12345678) -> open 192.168.4.1
//  Joystick or arrow buttons drive the robot. Stops by itself if the phone stops sending (0.4 s).
//  Arduino IDE board: "ESP32S3 Dev Module". No extra library needed.
// =====================================================================
#include <WiFi.h>
#include <WebServer.h>

const char* AP_SSID = "LineaViperRC";
const char* AP_PASS = "12345678";

// ---------------- MOTOR PINS (TB6612) - check against your board ----------------
int mA[3] = {4, 5, 6};      // left  motor PWMA, AIN1, AIN2
int mB[3] = {7, 15, 16};    // right motor PWMB, BIN1, BIN2
const int STBY = 17;        // -1 if not used
const bool SWAP_LR = false; // true if left and right are swapped

WebServer server(80);
unsigned long lastCmd = 0;

void motor(int* m, int sp) { sp = constrain(sp, -255, 255); digitalWrite(m[1], sp > 0); digitalWrite(m[2], sp < 0); analogWrite(m[0], abs(sp)); }
void Motor(int l, int r) { if (SWAP_LR) { int t = l; l = r; r = t; } motor(mA, l); motor(mB, r); }

const char PAGE[] PROGMEM = R"HTML(
<title>Linea Viper RC</title>
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
<div class="wrap"><header><h1>LINEA <b>VIPER</b> RC</h1><div class="st" id="st">connecting…</div></header>
<section class="card" id="v3">
<p class="note">Drag the joystick (or hold the arrows). Let go = stop. The robot also stops by itself if the connection drops.</p>
<div class="pad" id="pad"><i id="knob"></i></div>
<div class="dp"><span></span><button class="btn dark" data-d="1,0">▲</button><span></span><button class="btn dark" data-d="0,-1">◀</button><button class="btn stop" data-d="0,0">■</button><button class="btn dark" data-d="0,1">▶</button><span></span><button class="btn dark" data-d="-1,0">▼</button><span></span></div>
<div class="sl"><span>Max speed</span><input id="rcmax" type="range" min="40" max="255" value="180"><output id="orc">180</output></div>
<p class="note" id="rcst">L 0 · R 0</p>
</section></div>
<script>
const $=id=>document.getElementById(id);let demo=false;
/* RC */
let rcL=0,rcR=0,last="";function drive(f,t){const m=+$("rcmax").value;rcL=Math.round(Math.max(-1,Math.min(1,f+t))*m);rcR=Math.round(Math.max(-1,Math.min(1,f-t))*m);$("rcst").textContent=`L ${rcL} · R ${rcR}`;}
setInterval(()=>{const k=rcL+","+rcR;if(k==="0,0"&&last==="0,0")return;last=k;if(!demo)fetch(`/rc?l=${rcL}&r=${rcR}`).catch(()=>{});},100);
$("rcmax").oninput=()=>$("orc").value=$("rcmax").value;
const pad=$("pad"),knob=$("knob");function mv(e){const b=pad.getBoundingClientRect(),R=b.width/2;let x=(e.clientX-b.left-R)/R,y=(e.clientY-b.top-R)/R;const d=Math.hypot(x,y);if(d>1){x/=d;y/=d;}knob.style.left=50+x*40+"%";knob.style.top=50+y*40+"%";drive(-y,x);}
pad.onpointerdown=e=>{pad.setPointerCapture(e.pointerId);mv(e);};pad.onpointermove=e=>{if(e.buttons)mv(e);};pad.onpointerup=pad.onpointercancel=()=>{knob.style.left=knob.style.top="50%";drive(0,0);};
document.querySelectorAll("[data-d]").forEach(b=>{const[f,t]=b.dataset.d.split(",").map(Number);b.onpointerdown=()=>drive(f,t);b.onpointerup=b.onpointerleave=()=>drive(0,0);});
fetch("/ping").then(()=>$("st").textContent="connected · 192.168.4.1").catch(()=>{demo=true;$("st").textContent="demo mode (not connected to the robot)";});
</script>

)HTML";

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 3; i++) { pinMode(mA[i], OUTPUT); pinMode(mB[i], OUTPUT); }
  if (STBY >= 0) { pinMode(STBY, OUTPUT); digitalWrite(STBY, HIGH); }
  Motor(0, 0);
  WiFi.softAP(AP_SSID, AP_PASS);
  server.on("/", [] { server.send_P(200, "text/html", PAGE); });
  server.on("/ping", [] { server.send(200, "text/plain", "ok"); });
  server.on("/rc", [] { Motor(server.arg("l").toInt(), server.arg("r").toInt()); lastCmd = millis(); server.send(200, "text/plain", "RC"); });
  server.begin();
  Serial.print("Open http://"); Serial.println(WiFi.softAPIP());
}

void loop() {
  server.handleClient();
  if (millis() - lastCmd > 400) Motor(0, 0);     // failsafe
  delay(2);
}

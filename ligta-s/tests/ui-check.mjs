// Clicks through the LIGTA-S website and app in headless Chromium and fails on any console error.
//   node ligta-s/tests/ui-check.mjs [screenshot folder]
// Serves the repository root on a local port (so ../research links and the service worker behave as on
// GitHub Pages), opens both pages at 1440 x 900 and 390 x 844, in light and dark mode, and saves
// screenshots (default: a temporary folder; they are not part of the site).
// Needs Playwright with a Chromium build: set PLAYWRIGHT_MODULE and CHROMIUM_PATH if they are elsewhere.
import http from "node:http";
import { readFileSync, existsSync, mkdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, extname, normalize } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { tmpdir } from "node:os";

const HERE = dirname(fileURLToPath(import.meta.url));
const SITE = join(HERE, "..");
const REPO = join(SITE, "..");
const OUT = process.argv[2] || join(tmpdir(), "ligta-s-shots");
mkdirSync(OUT, { recursive: true });

let pw;
try { pw = await import("playwright"); } catch (e) {
  pw = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE || "/opt/node-tools/node_modules/playwright/index.js").href);
}
const chromium = pw.chromium || pw.default.chromium;
const exe = process.env.CHROMIUM_PATH || (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);

/* static server for the repository root */
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".webmanifest": "application/manifest+json", ".png": "image/png", ".webp": "image/webp",
  ".ico": "image/x-icon", ".svg": "image/svg+xml", ".pdf": "application/pdf" };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  let f = normalize(join(REPO, p));
  if (!f.startsWith(REPO)) { res.writeHead(403); return res.end(); }
  if (existsSync(f) && statSync(f).isDirectory()) f = join(f, "index.html");
  if (!existsSync(f)) { res.writeHead(404); return res.end("not found"); }
  res.writeHead(200, { "content-type": TYPES[extname(f)] || "application/octet-stream" });
  res.end(readFileSync(f));
});
await new Promise((ok) => server.listen(0, "127.0.0.1", ok));
const BASE = `http://127.0.0.1:${server.address().port}/ligta-s/`;

const browser = await chromium.launch({ executablePath: exe });
const problems = [];
let shots = 0, steps = 0;
function expect(cond, what) { steps++; if (!cond) problems.push(what); }

async function newPage(w, h, scheme) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme, acceptDownloads: true });
  const page = await ctx.newPage();
  const errs = [];
  page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  page.on("pageerror", (e) => errs.push("page error: " + e.message));
  page.on("requestfailed", (r) => { if (!/fonts\.(googleapis|gstatic)\.com/.test(r.url())) errs.push("request failed: " + r.url()); });
  page.on("response", (r) => { if (r.status() >= 400 && r.url().startsWith(BASE)) errs.push(`HTTP ${r.status()}: ${r.url()}`); });
  return { ctx, page, errs };
}
async function shot(page, name, full) {
  await page.screenshot({ path: join(OUT, name + ".png"), fullPage: !!full });
  shots++;
}
async function noHScroll(page, label) {
  const sw = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(sw <= 1, `${label}: page scrolls sideways by ${sw}px`);
}

/* ---------------------------------------------------------------- website */
for (const [w, h, tag] of [[1440, 900, "desktop"], [390, 844, "phone"]]) {
  for (const scheme of ["light", "dark"]) {
    const { ctx, page, errs } = await newPage(w, h, scheme);
    await page.goto(BASE, { waitUntil: "networkidle" });
    // scroll through so lazy images load
    await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 40)); } window.scrollTo(0, 0); });
    await page.waitForTimeout(600);
    await noHScroll(page, `website ${tag} ${scheme}`);
    const imgs = await page.evaluate(() => Array.from(document.images).filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.src));
    expect(imgs.length === 0, `website ${tag}: images not loaded ${imgs.join(", ")}`);
    const eqs = await page.locator(".eq svg").count();
    expect(eqs >= 15, `website: only ${eqs} typeset equations`);
    const pdf = await page.locator('a[href="../research/safe-shelter-open-schools/paper/Safe-Shelter-Open-Schools_MCS-T.pdf"]').count();
    expect(pdf >= 1, "website: paper link missing");
    expect(await page.locator(".lead-row").innerText().then((t) => t.includes("De Asis, Dave Justin Ll.")), "website: lead researcher missing");
    if (scheme === "light") {
      await shot(page, `site-${tag}-full`, true);
      // demo: every scenario, rule and closure
      const demo = page.locator("#demo");
      await demo.scrollIntoViewIfNeeded();
      const out = page.locator("#demo-out");
      await page.waitForFunction(() => /classrooms closed/.test(document.getElementById("demo-out").textContent));
      let txt = await out.innerText();
      expect(/14\s*classrooms closed/.test(txt) && /532/.test(txt) && /53/.test(txt), "demo AL3 school-preserving: expected 14 classrooms, 532 learners, 53 min");
      await page.click('#d-rule [data-v="time"]'); await page.waitForTimeout(150);
      txt = await out.innerText();
      expect(/40\s*classrooms closed/.test(txt) && /1,702/.test(txt), "demo AL3 time-only: expected 40 classrooms, 1,702 learners");
      await page.click('#d-rule [data-v="near"]'); await page.waitForTimeout(150);
      txt = await out.innerText();
      expect(/298/.test(txt), "demo AL3 nearest site: expected 298 at full shelters");
      await page.click('#d-rule [data-v="lex"]');
      await page.click('#d-scen [data-v="AL4"]'); await page.waitForTimeout(200);
      txt = await out.innerText();
      expect(/60\s*classrooms closed/.test(txt), "demo AL4: expected 60 classrooms");
      await page.click('#d-ch [data-v="A"]'); await page.waitForTimeout(300);
      txt = await out.innerText();
      expect(/95/.test(txt), "demo AL4 channel A cut: expected clearance 95 min");
      await page.click('#d-scen [data-v="AL4+L"]'); await page.waitForTimeout(300);
      txt = await out.innerText();
      expect(/450 residents are cut off/.test(txt), "demo AL4+L: expected 450 cut off");
      await demo.screenshot({ path: join(OUT, `site-${tag}-demo.png`) }); shots++;
      // install button without a prompt shows the steps
      await page.click("#install-btn");
      await page.waitForTimeout(200);
      expect((await page.locator("#install-status").innerText()).length > 10, "install: no guidance shown");
      // theme switch
      await page.click("#theme-btn"); await page.click("#theme-btn");
      expect(await page.evaluate(() => document.documentElement.getAttribute("data-theme")) === "dark", "theme switch did not reach dark");
      await page.click("#theme-btn");
    } else {
      await page.locator("#demo").scrollIntoViewIfNeeded();
      await shot(page, `site-${tag}-dark-demo`);
      await page.locator("#mcs").scrollIntoViewIfNeeded();
      await shot(page, `site-${tag}-dark-mcs`);
      await page.evaluate(() => window.scrollTo(0, 0));
      await shot(page, `site-${tag}-dark-top`);
    }
    expect(errs.length === 0, `website ${tag} ${scheme} console: ${errs.join(" | ")}`);
    await ctx.close();
  }
}

/* ---------------------------------------------------------------- app */
for (const [w, h, tag] of [[1440, 900, "desktop"], [390, 844, "phone"]]) {
  const { ctx, page, errs } = await newPage(w, h, "light");
  await page.goto(BASE + "app/#plan", { waitUntil: "networkidle" });
  await page.waitForFunction(() => /classrooms closed/.test(document.getElementById("plan-result").textContent));
  let t = await page.locator("#plan-result").innerText();
  expect(/14\s*classrooms closed/.test(t) && /532\s*learners displaced/.test(t), "app planner AL3: 14 classrooms, 532 learners");
  expect(/31\.18 min/.test(t) && /53 min/.test(t), "app planner AL3: mean trip 31.18, clearance 53");
  await noHScroll(page, `app ${tag} planner`);
  await shot(page, `app-${tag}-plan`, tag === "desktop");
  await page.click('[data-rule="time"]'); await page.waitForTimeout(500);
  t = await page.locator("#plan-result").innerText();
  expect(/40\s*classrooms closed/.test(t) && /1,702/.test(t) && /29\.48/.test(t), "app time-only AL3: 40 classrooms, 1,702 learners, 29.48 min");
  await page.click('[data-rule="near"]'); await page.waitForTimeout(500);
  t = await page.locator("#plan-result").innerText();
  expect(/298/.test(t), "app nearest AL3: 298 arrive at full shelters");
  await page.click('[data-rule="lex"]'); await page.waitForTimeout(400);
  // "Who goes where" at Alert Level 3 is the paper's Table 13 (persons by origin, shelter and space)
  const who = await page.$$eval("#plan-detail tbody tr", (rows) => rows.map((r) => Array.from(r.cells).map((c) => c.innerText.trim())));
  const t13 = {};
  who.forEach((c) => { const k = `${c[0]}|${c[2].split(/\s+/)[0]}|${c[3]}`; t13[k] = (t13[k] || 0) + Number(c[4].replace(/,/g, "")); });
  const want13 = { "O1|EC3|Non-school space": 280, "O1|SCH3|Classroom": 240, "O2|EC1|Non-school space": 400, "O2|EC2|Non-school space": 30,
    "O3|EC2|Non-school space": 170, "O3|EC3|Non-school space": 20, "O3|SCH1|School open space": 180, "O3|SCH2|School open space": 240 };
  expect(JSON.stringify(Object.entries(t13).sort()) === JSON.stringify(Object.entries(want13).sort()), `app "Who goes where" AL3 should be the paper's Table 13, got ${JSON.stringify(t13)}`);
  const cmp = await page.locator("#compare").innerText();
  expect(/40/.test(cmp) && /14/.test(cmp) && /298 over/.test(cmp), "app comparison table");
  // stay length changes classroom-days
  await page.fill("#days", "10"); await page.locator("#days").dispatchEvent("change"); await page.waitForTimeout(500);
  expect(/140\s*classroom-days/.test(await page.locator("#plan-result").innerText()), "app: 14 classrooms x 10 days = 140 classroom-days");
  // edit a table cell, then undo by resetting
  await page.locator('[data-t="origins"][data-i="0"][data-f="pop"]').fill("530");
  await page.locator('[data-t="origins"][data-i="0"][data-f="pop"]').dispatchEvent("change");
  await page.waitForTimeout(500);
  expect(/Edited copy/.test(await page.locator("#banner-text").innerText()), "app: edit marks the data as edited");
  expect(await page.evaluate(() => { try { return JSON.parse(localStorage.getItem("ligtas.data.v1")).origins[0].pop; } catch (e) { return null; } }) === 530, "app: edit saved in localStorage");

  // clearance and bridges (Alert Level 4)
  await page.click("#tab-data"); await page.waitForTimeout(200);
  page.once("dialog", (d) => d.accept());
  await page.click("#reset-data"); await page.waitForTimeout(400);
  await page.click("#tab-clear"); await page.waitForTimeout(300);
  await page.locator('#view-clear .scen-seg button[data-id="AL4"]').click();
  await page.waitForFunction(() => /clearance time/.test(document.getElementById("clear-result").textContent));
  t = await page.locator("#clear-result").innerText();
  expect(/53/.test(t), "app clearance AL4: 53 min");
  await page.click('[data-close="A"]');
  await page.waitForFunction(() => /same plan/.test(document.getElementById("closure-result").textContent), null, { timeout: 15000 });
  t = await page.locator("#closure-result").innerText();
  expect(/95/.test(t) && /\+42/.test(t), "app: channel A closed gives 95 min, +42");
  await page.click('[data-close="AB"]'); await page.waitForTimeout(1200);
  t = await page.locator("#closure-result").innerText();
  expect(/450/.test(t), "app: both channels closed trap 450");
  await page.click('[data-close="none"]'); await page.waitForTimeout(800);
  if (tag === "desktop") {
    await page.locator('#map-clear [data-bridge="A4"]').click(); await page.waitForTimeout(1200);
    expect(/54/.test(await page.locator("#closure-result").innerText()), "app: bridge A4 alone gives 54 min");
  }
  const study = await page.locator("#study").innerText();
  expect(/\+42/.test(study) && /\+21/.test(study) && /450/.test(study), "app lahar study under AL4: +42, +21, 450 trapped");
  await shot(page, `app-${tag}-clearance`, tag === "desktop");

  // siting
  await page.click("#tab-site"); await page.waitForTimeout(300);
  await page.click("#site-run");
  await page.waitForFunction(() => /Greedy choice/.test(document.getElementById("site-result").textContent), null, { timeout: 15000 });
  t = await page.locator("#site-result").innerText();
  expect(/TS, TNE, TSW/.test(t) && /900/.test(t) && /750/.test(t) && /570/.test(t), "app siting: TS, TNE, TSW with gains 400/750/900, 570 in classrooms at k=2");
  await shot(page, `app-${tag}-siting`, tag === "desktop");

  // resident
  await page.click("#tab-res"); await page.waitForTimeout(300);
  await page.selectOption("#res-origin", "O3");
  await page.waitForTimeout(800);
  await page.check("#res-vul"); await page.waitForTimeout(800);
  t = await page.locator("#res-cards").innerText();
  expect(/Alert Level 3/.test(t) && /min/.test(t) && /accessible/.test(t), "app resident: O3 assignments with trip time and accessibility");
  await shot(page, `app-${tag}-resident`, tag === "desktop");

  // capacity calculator
  await page.click("#tab-cap"); await page.waitForTimeout(200);
  await page.fill("#cap-area", "1400");
  expect((await page.locator("#cap-area-out").innerText()) === "400", "capacity: 1,400 m2 holds 400");
  await page.fill("#cap-ev", "240"); await page.fill("#cap-lpr", "38");
  expect((await page.locator("#cap-ev-out").innerText()) === "14", "capacity: 240 evacuees close 14 classrooms");
  await shot(page, `app-${tag}-capacity`);

  // data export and import
  await page.click("#tab-data"); await page.waitForTimeout(200);
  const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#exp-json")]);
  const exported = join(OUT, `export-${tag}.json`);
  await dl.saveAs(exported);
  const ex = JSON.parse(readFileSync(exported, "utf8"));
  expect(ex.origins.length === 6 && ex.shelters.length === 6, "export JSON has the 6 origins and 6 shelters");
  const [dl2] = await Promise.all([page.waitForEvent("download"), page.click('[data-csv="shelters"]')]);
  const csvPath = join(OUT, `shelters-${tag}.csv`);
  await dl2.saveAs(csvPath);
  const csv = readFileSync(csvPath, "utf8");
  expect(/^id,name,node,kind,areaNonSchool/.test(csv), "export CSV header");
  // import an edited CSV: one more classroom at SCH3
  const edited = csv.replace(/\r?\n(SCH3,[^\r\n]*)/, (m0, row) => "\r\n" + row.replace(/,0,14,38,/, ",0,15,38,"));
  const csvIn = join(OUT, `shelters-in-${tag}.csv`);
  writeFileSync(csvIn, edited);
  await page.setInputFiles("#imp-file", csvIn); await page.waitForTimeout(600);
  expect(await page.evaluate(() => JSON.parse(localStorage.getItem("ligtas.data.v1")).shelters.find((s) => s.id === "SCH3").rooms) === 15, "CSV import changed SCH3 to 15 classrooms");
  await page.setInputFiles("#imp-file", exported); await page.waitForTimeout(600);
  expect(await page.evaluate(() => JSON.parse(localStorage.getItem("ligtas.data.v1")).shelters.find((s) => s.id === "SCH3").rooms) === 14, "JSON import restored SCH3");
  await shot(page, `app-${tag}-data`, tag === "desktop");

  // about dialog and dark theme
  await page.click("#about-btn"); await page.waitForTimeout(200);
  expect(await page.locator("#about").evaluate((d) => d.open), "about dialog opens");
  await shot(page, `app-${tag}-about`);
  await page.click("#about-close");
  await page.click("#theme-btn"); await page.click("#theme-btn");
  await page.click("#tab-plan"); await page.waitForTimeout(800);
  await shot(page, `app-${tag}-dark-plan`);
  await noHScroll(page, `app ${tag} dark`);
  expect(errs.length === 0, `app ${tag} console: ${errs.join(" | ")}`);
  await ctx.close();
}

/* the narrowest phones: 360 px wide, every view, no sideways scrolling */
{
  const { ctx, page, errs } = await newPage(360, 740, "light");
  await page.goto(BASE, { waitUntil: "networkidle" });
  await noHScroll(page, "website 360px");
  await page.goto(BASE + "app/#plan", { waitUntil: "networkidle" });
  for (const t of ["plan", "clear", "site", "res", "cap", "data"]) {
    await page.click("#tab-" + t); await page.waitForTimeout(t === "clear" ? 1500 : 500);
    if (t === "site") { await page.click("#site-run"); await page.waitForTimeout(1500); }
    await noHScroll(page, "app 360px " + t);
  }
  await shot(page, "app-360-data");
  expect(errs.length === 0, "360px console: " + errs.join(" | "));
  await ctx.close();
}

/* installed copy: the service worker keeps the app and the website for offline use */
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil: "networkidle" });
  const scope = await page.evaluate(async () => (await navigator.serviceWorker.ready).scope);
  expect(/\/ligta-s\/$/.test(scope), "service worker scope is /ligta-s/: " + scope);
  await page.goto(BASE + "app/", { waitUntil: "networkidle" });
  await page.waitForTimeout(500);
  const keys = await page.evaluate(async () => (await caches.keys()).join(","));
  expect(/^ligta-s-v\d+/.test(keys), "offline cache named ligta-s-v*: " + keys);
  await ctx.setOffline(true);
  await page.reload();
  await page.waitForFunction(() => /classrooms closed/.test(document.getElementById("plan-result").textContent));
  expect(/14\s*classrooms closed/.test(await page.locator("#plan-result").innerText()), "app opens and computes offline");
  await page.goto(BASE);
  expect(await page.locator("#hero-h").count() === 1, "website opens offline");
  await ctx.close();
}

/* the downloaded single file works from disk too */
{
  const ctx = await browser.newContext({ viewport: { width: 1024, height: 800 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on("pageerror", (e) => errs.push(e.message));
  page.on("console", (m) => { if (m.type() === "error" && !/manifest|apple-touch|Failed to load resource/i.test(m.text())) errs.push(m.text()); });
  await page.goto(pathToFileURL(join(SITE, "app", "index.html")).href);
  await page.waitForFunction(() => /classrooms closed/.test(document.getElementById("plan-result").textContent));
  expect(/14\s*classrooms closed/.test(await page.locator("#plan-result").innerText()), "app opened from a file computes the plan");
  expect(errs.length === 0, "app from file: " + errs.join(" | "));
  await ctx.close();
}

await browser.close();
server.close();
console.log(`${steps - problems.length} of ${steps} UI checks passed; ${shots} screenshots in ${OUT}`);
if (problems.length) { console.log("PROBLEMS:\n  " + problems.join("\n  ")); process.exit(1); }

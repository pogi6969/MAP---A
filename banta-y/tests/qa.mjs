// Browser check of the BANTA-Y website and app with headless Chromium (Playwright).
//   node tests/qa.mjs [outdir]
// Serves the repository the way GitHub Pages does (under /MAP---A/), opens the website and the app at
// 1440x900 and 390x844, clicks through every screen, checks key numbers of the synthetic test network D1,
// fails on any console error, page error or sideways scrolling, and saves screenshots to outdir
// (default: a folder in the system temp directory).
import http from "node:http";
import { readFileSync, existsSync, statSync, mkdirSync, writeFileSync } from "node:fs";
import { join, dirname, extname } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let pw;
try { pw = require("playwright"); } catch { pw = require("/opt/node-tools/node_modules/playwright"); }

const HERE = dirname(dirname(fileURLToPath(import.meta.url)));       // banta-y/
const REPO = dirname(HERE);
const OUT = process.argv[2] || join(tmpdir(), "banta-y-qa");
mkdirSync(OUT, { recursive: true });

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json",
  ".webmanifest": "application/manifest+json", ".png": "image/png", ".webp": "image/webp", ".ico": "image/x-icon", ".svg": "image/svg+xml",
  ".pdf": "application/pdf", ".css": "text/css", ".py": "text/plain; charset=utf-8", ".md": "text/plain; charset=utf-8" };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (!p.startsWith("/MAP---A/")) { res.writeHead(404); return res.end(); }
  p = join(REPO, p.slice("/MAP---A/".length));
  if (existsSync(p) && statSync(p).isDirectory()) p = join(p, "index.html");
  if (!existsSync(p)) { res.writeHead(404); return res.end("not found"); }
  res.writeHead(200, { "content-type": TYPES[extname(p)] || "application/octet-stream" });
  res.end(readFileSync(p));
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${server.address().port}/MAP---A/banta-y/`;

const browser = await pw.chromium.launch({ executablePath: "/opt/pw-browsers/chromium" }).catch(() => pw.chromium.launch());
const problems = [], shots = [];
let checks = 0;
function check(cond, msg) { checks++; if (!cond) problems.push(msg); }

async function open(url, vp, name, opts) {
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, colorScheme: (opts && opts.scheme) || "light", acceptDownloads: true });
  const page = await ctx.newPage();
  const errs = [];
  page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  page.on("pageerror", (e) => errs.push("pageerror: " + e.message));
  page.on("requestfailed", (r) => { const u = r.url(); if (!/fonts\.(googleapis|gstatic)\.com/.test(u)) errs.push("requestfailed: " + u + " " + (r.failure() || {}).errorText); });
  await page.goto(url, { waitUntil: "load" });
  await page.waitForTimeout(400);
  return { ctx, page, errs, name };
}
async function noOverflow(page, label) {
  const o = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, w: window.innerWidth }));
  check(o.sw <= o.w + 1, `${label}: page scrolls sideways (${o.sw} > ${o.w})`);
}
async function shot(page, file, full) {
  const p = join(OUT, file);
  if (full !== false) {          // scroll through the page so lazy images load, then back to the top
    const height = await page.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < height; y += 500) { await page.evaluate((yy) => window.scrollTo(0, yy), y); await page.waitForTimeout(70); }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForFunction(() => Array.prototype.every.call(document.images, (i) => i.complete && i.naturalWidth > 0), null, { timeout: 8000 }).catch(async () => problems.push(file + ": images not loaded: " + (await page.evaluate(() => Array.prototype.filter.call(document.images, (i) => !(i.complete && i.naturalWidth > 0)).map((i) => i.currentSrc || i.src).join(", ")))));
    await page.waitForTimeout(300);
  }
  await page.screenshot({ path: p, fullPage: full !== false });
  shots.push(p);
}
const text = (page, sel) => page.locator(sel).first().innerText();

/* ------------------------------------------------------------------ the app */
for (const [vp, tag] of [[{ width: 1440, height: 900 }, "1440"], [{ width: 390, height: 844 }, "390"]]) {
  const { ctx, page, errs } = await open(BASE + "app/", vp, "app-" + tag);
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload({ waitUntil: "load" });
  await page.waitForTimeout(300);
  check(await page.locator("#banner").isVisible(), `app ${tag}: synthetic-network banner missing`);
  await shot(page, `app-${tag}-1-network.png`);
  await noOverflow(page, `app ${tag} network`);

  await page.click('.tab[data-tab="spread"]'); await page.waitForTimeout(250);
  const kpis = await text(page, "#kpis");
  check(kpis.includes("1.214"), `app ${tag}: network R0 1.214 not shown`);
  check(kpis.includes("1.204"), `app ${tag}: province-average R0 1.204 not shown`);
  check(kpis.includes("1.759"), `app ${tag}: no-movement R0 1.759 not shown`);
  const ins = await text(page, "#spread-insight");
  check(ins.includes("28.5%") && ins.includes("42.6%"), `app ${tag}: spread insight should say 28.5% and 42.6% (got: ${ins})`);
  await shot(page, `app-${tag}-2-spread.png`);
  await noOverflow(page, `app ${tag} spread`);

  await page.click('.tab[data-tab="control"]');
  await page.waitForSelector("#chart-season svg", { timeout: 15000 });
  const bars = await text(page, "#strat-bars");
  for (const v of ["37.47", "38.88", "29.54", "26.49", "22.60"]) check(bars.includes(v), `app ${tag}: strategy cost ${v} not shown`);
  const cert = await text(page, "#cert-note");
  check(/\[22\.596\d, 22\.596\d\]/.test(cert), `app ${tag}: certified interval not shown (${cert.slice(0, 120)})`);
  const season = await text(page, "#season-wait");
  check(season.includes("1.4 → 44.3") && season.includes("0.6 → 0.0"), `app ${tag}: season curve points wrong (${season})`);
  await shot(page, `app-${tag}-3-control.png`);
  await noOverflow(page, `app ${tag} control`);
  // season slider: 1.2 must give 34.86 team-days
  await page.locator("#season-b").evaluate((el) => { el.value = "1.2"; el.dispatchEvent(new Event("input", { bubbles: true })); });
  await page.waitForTimeout(500);
  check((await text(page, "#strat-bars")).includes("34.86"), `app ${tag}: season 1.2 should cost 34.86 team-days`);
  await page.locator("#season-b").evaluate((el) => { el.value = "1"; el.dispatchEvent(new Event("input", { bubbles: true })); });
  await page.waitForTimeout(400);

  await page.click('.tab[data-tab="places"]'); await page.waitForTimeout(250);
  const pl = await text(page, "#tbl-places");
  for (const v of ["151.0", "55.8", "40.0", "32.5", "15.5", "13.2", "138.8"]) check(pl.includes(v), `app ${tag}: inversion value ${v} not shown`);
  await shot(page, `app-${tag}-4-places.png`);
  await noOverflow(page, `app ${tag} places`);

  await page.click('.tab[data-tab="alarm"]'); await page.waitForTimeout(250);
  const st = await text(page, "#alarm-status");
  check(st.includes("Week 34") && st.includes("Week 32"), `app ${tag}: alarm weeks should be 34 (CUSUM) and 32 (single week)`);
  await shot(page, `app-${tag}-5-alarm.png`);
  await noOverflow(page, `app ${tag} alarm`);

  await page.click('.tab[data-tab="fours"]'); await page.waitForTimeout(200);
  await page.click("#ck-search");
  check(await page.locator("li.check.done").count() === 1, `app ${tag}: 4S tick not kept`);
  await shot(page, `app-${tag}-6-fours.png`);

  if (tag === "1440") {
    // edit a cell, check R0 moves and the edit survives a reload (localStorage)
    await page.click('.tab[data-tab="network"]');
    const cell = page.locator('[data-i="0"][data-f="mhat"]');
    await cell.fill("4");
    await page.waitForTimeout(400);
    await page.click('.tab[data-tab="spread"]'); await page.waitForTimeout(250);
    const r0b = await text(page, "#kpis .kpi-value");
    check(r0b !== "1.214", "app: editing mosquitoes per resident did not change R0");
    // Python (denguemodel.py) for D1 with B1 at 4 mosquitoes per resident: R0 1.15587, least cost 21.2949 team-days
    check(r0b === "1.156", `app: edited D1 should give R0 1.156 as in Python (got ${r0b})`);
    check((await text(page, "#banner-text")).startsWith("Edited from the synthetic test network D1") && (await text(page, "#brand-sub")) === "Edited from test network D1", "app: edited D1 is still labelled as the original test network");
    await page.click('.tab[data-tab="control"]'); await page.waitForSelector("#chart-season svg", { timeout: 15000 });
    check((await text(page, "#cert-note")).includes("[21.2949, 21.2949]"), "app: edited D1 least cost should be 21.2949 as in Python");
    await page.click('.tab[data-tab="spread"]'); await page.waitForTimeout(250);
    await page.reload({ waitUntil: "load" }); await page.waitForTimeout(300);
    check((await page.locator('[data-i="0"][data-f="mhat"]').inputValue()) === "4" || (await text(page, "#kpis .kpi-value")) === r0b, "app: edit not kept after reload");
    // export JSON, load D1, import the export back
    await page.click("#data-btn");
    const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#exp-json")]);
    const jsonPath = join(OUT, "export.json"); await dl.saveAs(jsonPath);
    const [dl2] = await Promise.all([page.waitForEvent("download"), page.click("#exp-csv")]);
    const csvPath = join(OUT, "export.csv"); await dl2.saveAs(csvPath);
    check(readFileSync(csvPath, "utf8").split("\n")[0].startsWith("name,residents,mosquitoes_per_resident"), "app: CSV export header wrong");
    await shot(page, "app-1440-dialog.png", false);
    await page.click("#load-d1"); await page.waitForTimeout(300);
    await page.click('.tab[data-tab="spread"]'); await page.waitForTimeout(250);
    check((await text(page, "#kpis .kpi-value")) === "1.214", "app: Load D1 did not restore R0 1.214");
    await page.click("#data-btn");
    await page.setInputFiles("#imp-file", jsonPath); await page.waitForTimeout(500);
    check((await text(page, "#kpis .kpi-value")) === r0b, "app: JSON import did not restore the edited network");
    // CSV import of the edited network: same R0, now marked as the user's own network
    await page.click("#data-btn");
    await page.setInputFiles("#imp-file", csvPath); await page.waitForTimeout(500);
    check((await text(page, "#kpis .kpi-value")) === r0b, "app: CSV import did not reproduce R0");
    check(!(await page.locator("#banner").isVisible()), "app: imported network still marked synthetic");
    await page.click("#data-btn"); await page.click("#load-d1"); await page.waitForTimeout(300);
    // travel-time table mode gives the same R0 when filled from positions (rounded to 0.1 min)
    await page.click('.tab[data-tab="network"]');
    await page.click('[data-tmode="matrix"]'); await page.waitForTimeout(300);
    check(await page.locator("#tbl-travel input").count() === 30, "app: travel-time table should have 30 inputs");
    await page.click('.tab[data-tab="spread"]'); await page.waitForTimeout(250);
    check((await text(page, "#kpis .kpi-value")) === "1.214", "app: travel table mode changed R0");
    await page.click('.tab[data-tab="network"]'); await page.click('[data-tmode="positions"]');
    // add and remove a barangay
    const rows0 = await page.locator("#tbl-brgy tbody tr").count();
    await page.click("#add-row"); await page.waitForTimeout(200);
    check(await page.locator("#tbl-brgy tbody tr").count() === rows0 + 1, "app: add barangay failed");
    await page.locator("#tbl-brgy tbody tr").last().locator(".del-btn").click(); await page.waitForTimeout(200);
    check(await page.locator("#tbl-brgy tbody tr").count() === rows0, "app: remove barangay failed");
    // edge cases must not break the charts: nobody moves, then no mosquitoes at all
    for (let i = 0; i < 6; i++) await page.locator(`[data-i="${i}"][data-f="away"]`).fill("0");
    await page.waitForTimeout(300);
    check(!(await page.locator("#map").innerHTML()).includes("NaN"), "app: map with nobody moving has NaN");
    await page.click('.tab[data-tab="control"]'); await page.waitForSelector("#chart-season svg", { timeout: 15000 });
    check(((await text(page, "#strat-bars")).match(/out of reach/g) || []).length === 2 && (await text(page, "#strat-bars")).includes("23.14"), "app: with nobody moving, two plans are out of reach and the least cost is 23.14");
    await page.click('.tab[data-tab="network"]');
    for (let i = 0; i < 6; i++) await page.locator(`[data-i="${i}"][data-f="mhat"]`).fill("0");
    await page.click('.tab[data-tab="spread"]'); await page.waitForTimeout(300);
    check((await text(page, "#spread-insight")).includes("no transmission") && !(await page.locator("#chart-shares").innerHTML()).includes("NaN"), "app: zero mosquitoes should say there is no transmission and draw no NaN bars");
    await page.click("#data-btn"); await page.click("#load-d1"); await page.waitForTimeout(300);
    check((await text(page, "#brand-sub")) === "Test network D1 · synthetic", "app: Load D1 should restore the original label");
    // dark theme
    await page.click('.tab[data-tab="network"]');
    await page.click("#theme-btn"); await page.waitForTimeout(300);
    check((await page.evaluate(() => document.documentElement.getAttribute("data-theme"))) === "dark", "app: theme toggle failed");
    await shot(page, "app-1440-network-dark.png");
    await page.click('.tab[data-tab="control"]'); await page.waitForSelector("#chart-season svg", { timeout: 15000 });
    await shot(page, "app-1440-control-dark.png");
  }
  check(errs.length === 0, `app ${tag}: console errors: ${errs.join(" | ")}`);
  await ctx.close();
}

/* ------------------------------------------------------------------ the website */
if (existsSync(join(HERE, "index.html"))) {
  for (const [vp, tag] of [[{ width: 1440, height: 900 }, "1440"], [{ width: 390, height: 844 }, "390"]]) {
    const { ctx, page, errs } = await open(BASE, vp, "site-" + tag);
    await page.waitForTimeout(600);
    await shot(page, `site-${tag}-top.png`, false);
    await shot(page, `site-${tag}-full.png`);
    await noOverflow(page, `site ${tag}`);
    const demo = await text(page, "#demo");
    check(demo.includes("1.214"), `site ${tag}: demo should show R0 1.214`);
    check(demo.includes("22.60"), `site ${tag}: demo should show 22.60 team-days`);
    // move the demo's season slider and check the outputs follow
    await page.locator("#d-season").evaluate((el) => { el.value = "1.4"; el.dispatchEvent(new Event("input", { bubbles: true })); });
    await page.waitForTimeout(500);
    check((await text(page, "#demo")).includes("44.33"), `site ${tag}: demo season 1.4 should cost 44.33 team-days`);
    await page.locator("#d-move").evaluate((el) => { el.value = "0"; el.dispatchEvent(new Event("input", { bubbles: true })); });
    await page.waitForTimeout(500);
    await page.locator("#d-season").evaluate((el) => { el.value = "1"; el.dispatchEvent(new Event("input", { bubbles: true })); });
    await page.waitForTimeout(500);
    check((await text(page, "#demo")).includes("1.759"), `site ${tag}: demo with no movement should show R0 1.759`);
    await page.locator("#demo").screenshot({ path: join(OUT, `site-${tag}-demo-nomove.png`) }); shots.push(join(OUT, `site-${tag}-demo-nomove.png`));
    // links that must exist
    const pdf = await page.locator('a[href="../research/where-people-go-dengue/paper/Where-People-Go-Dengue-Goes_MCS-T.pdf"]').count();
    check(pdf >= 1, `site ${tag}: link to the paper PDF missing`);
    check(await page.locator('a[href="app/index.html"][download]').count() >= 1, `site ${tag}: one-file download link missing`);
    check(await page.locator("#install-btn").count() === 1, `site ${tag}: install button missing`);
    const credits = await text(page, "#credits");
    for (const nm of ["Brimbuela, Peter John A.", "De Asis, Dave Justin Ll.", "Shin, Yeaseong", "Calleja, Dick Anthony M."]) check(credits.includes(nm), `site ${tag}: credits missing ${nm}`);
    if (tag === "390") {
      await page.click('[data-plat="ios"]'); await page.waitForTimeout(150);
      check(await page.locator("#steps-ios").isVisible(), "site 390: iPhone steps not shown");
      await page.locator("#install").screenshot({ path: join(OUT, "site-390-install-ios.png") }); shots.push(join(OUT, "site-390-install-ios.png"));
    }
    if (tag === "1440") {
      await page.click("#theme-btn"); await page.waitForTimeout(300);
      await shot(page, "site-1440-dark-full.png");
      await page.locator("#mcs").screenshot({ path: join(OUT, "site-1440-mcs-dark.png") }); shots.push(join(OUT, "site-1440-mcs-dark.png"));
    }
    check(errs.length === 0, `site ${tag}: console errors: ${errs.join(" | ")}`);
    await ctx.close();
  }
  // the PDF the website links to is served
  const r = await fetch(new URL("../research/where-people-go-dengue/paper/Where-People-Go-Dengue-Goes_MCS-T.pdf", BASE));
  check(r.ok, "paper PDF not found at the linked path");
}

/* ------------------------------------------------------------------ the narrowest phones: 360 px, no sideways scrolling */
{
  const { ctx, page, errs } = await open(BASE + "app/", { width: 360, height: 740 }, "app-360");
  for (const t of ["network", "spread", "control", "places", "alarm", "fours"]) {
    await page.click(`.tab[data-tab="${t}"]`);
    if (t === "control") await page.waitForSelector("#chart-season svg", { timeout: 15000 });
    await page.waitForTimeout(250);
    await noOverflow(page, "app 360 " + t);
  }
  await shot(page, "app-360-fours.png");
  check(errs.length === 0, "app 360: console errors: " + errs.join(" | "));
  await ctx.close();
  if (existsSync(join(HERE, "index.html"))) {
    const o = await open(BASE, { width: 360, height: 740 }, "site-360");
    await o.page.waitForTimeout(400);
    await noOverflow(o.page, "site 360");
    await o.page.click("#menu-btn"); await o.page.waitForTimeout(150);
    check(await o.page.locator("#nav a").first().isVisible(), "site 360: section menu does not open");
    await shot(o.page, "site-360-menu.png", false);
    check(o.errs.length === 0, "site 360: console errors: " + o.errs.join(" | "));
    await o.ctx.close();
  }
}

/* ------------------------------------------------------------------ offline: the service worker keeps both pages */
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil: "load" });
  const scope = await page.evaluate(() => Promise.race([
    navigator.serviceWorker.ready.then((r) => r.scope),
    new Promise((res) => setTimeout(() => res(null), 10000))
  ]));
  check(scope && scope.endsWith("/MAP---A/banta-y/"), "service worker not active with scope banta-y/ (" + scope + ")");
  const cached = await page.evaluate(async () => { const keys = await caches.keys(); const c = await caches.open(keys.find((k) => k.startsWith("banta-y-"))); return (await c.keys()).map((r) => new URL(r.url).pathname); });
  check(cached.some((p) => p.endsWith("/banta-y/app/")) && cached.some((p) => p.endsWith("/banta-y/")), "offline cache lacks the app or the website: " + cached.join(", "));
  await ctx.setOffline(true);
  await page.goto(BASE + "app/", { waitUntil: "load" }).catch(() => {});
  await page.waitForTimeout(400);
  check((await page.locator(".brand-name").count()) === 1 && (await page.locator("#tbl-brgy tbody tr").count()) === 6, "app does not open offline");
  await page.click('.tab[data-tab="control"]').catch(() => {});
  await page.waitForTimeout(600);
  check(((await page.locator("#strat-bars").innerText().catch(() => "")) || "").includes("22.60"), "app does not compute offline");
  await page.goto(BASE, { waitUntil: "load" }).catch(() => {});
  check((await page.locator("#demo").count()) === 1, "website does not open offline");
  await page.screenshot({ path: join(OUT, "offline-site-390.png") }); shots.push(join(OUT, "offline-site-390.png"));
  await ctx.close();
}

await browser.close();
server.close();
writeFileSync(join(OUT, "qa-report.json"), JSON.stringify({ checks, problems, shots }, null, 1));
console.log(`${checks} browser checks, ${problems.length} problems`);
problems.forEach((p) => console.log("  PROBLEM:", p));
console.log("screenshots in", OUT);
process.exit(problems.length ? 1 : 0);

// Takes the app screenshots shown on the BANTA-Y website (assets/shot-*.webp, assets/app-phone.webp).
//   node tools/make-shots.mjs      (after node tools/build.mjs; needs Playwright, Chromium at /opt/pw-browsers, python3 with PIL)
// The app is opened from the built file with the synthetic test network D1, in the light theme.
import { mkdtempSync, rmSync } from "node:fs";
import { join, dirname } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
let pw;
try { pw = require("playwright"); } catch { pw = require("/opt/node-tools/node_modules/playwright"); }

const HERE = dirname(dirname(fileURLToPath(import.meta.url)));
const APP = pathToFileURL(join(HERE, "app", "index.html")).href;
const TMP = mkdtempSync(join(tmpdir(), "banta-y-shots-"));
const browser = await pw.chromium.launch({ executablePath: "/opt/pw-browsers/chromium" }).catch(() => pw.chromium.launch());
const jobs = [];   // [png, webp, max width]

async function app(viewport, scale) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: scale, colorScheme: "light" });
  const page = await ctx.newPage();
  await page.goto(APP);
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(300);
  return { ctx, page };
}
async function tab(page, name) {
  await page.click(`.tab[data-tab="${name}"]`);
  await page.waitForTimeout(300);
  if (name === "control") await page.waitForSelector("#chart-season svg", { timeout: 15000 });
}

/* feature crops at desktop width */
{
  const { ctx, page } = await app({ width: 1440, height: 900 }, 1);
  const crops = [
    ["network", "#scr-network .grid2.wl"],
    ["spread", "#scr-spread .card:has(#chart-shares)"],
    ["control", "#scr-control .card:has(#strat-bars)"],
    ["places", "#scr-places .card:has(#chart-places)"],
    ["alarm", "#scr-alarm .card:has(#chart-alarm)"],
    ["fours", "#checks"]
  ];
  for (const [name, sel] of crops) {
    await tab(page, name);
    if (name === "fours") { await page.click("#ck-search"); await page.click("#ck-self"); await page.waitForTimeout(150); }
    const png = join(TMP, name + ".png");
    await page.locator(sel).first().screenshot({ path: png });
    jobs.push([png, join(HERE, "assets", "shot-" + name + ".webp"), 960]);
  }
  await ctx.close();
}
/* phone screen: the Spread screen at the network R0 */
{
  const { ctx, page } = await app({ width: 390, height: 844 }, 2);
  await tab(page, "spread");
  const y = await page.evaluate(() => document.querySelector("#scr-spread .card").getBoundingClientRect().top + window.scrollY - 14);
  await page.evaluate((yy) => window.scrollTo(0, yy), y);
  await page.waitForTimeout(200);
  const png = join(TMP, "phone.png");
  await page.screenshot({ path: png });
  jobs.push([png, join(HERE, "assets", "app-phone.webp"), 560]);
  await ctx.close();
}
await browser.close();

const py = `
import sys
from PIL import Image
for i in range(1, len(sys.argv), 3):
    src, dst, w = sys.argv[i], sys.argv[i + 1], int(sys.argv[i + 2])
    im = Image.open(src).convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=80, method=6)
    print("wrote", dst, im.size)
`;
console.log(execFileSync("python3", ["-c", py, ...jobs.flat().map(String)]).toString().trim());
rmSync(TMP, { recursive: true, force: true });

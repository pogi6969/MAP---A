// Renders assets/banta-y-logo.svg to the app icons with headless Chromium.
// Run: node tools/make-icons.mjs   (needs the playwright module and Chromium at /opt/pw-browsers)
import { readFileSync, writeFileSync, copyFileSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
let pw;
try { pw = require("playwright"); } catch { pw = require("/opt/node-tools/node_modules/playwright"); }
const HERE = dirname(dirname(fileURLToPath(import.meta.url)));
const svg = readFileSync(join(HERE, "assets/banta-y-logo.svg"), "utf8");
const bare = svg.replace(/<title[^>]*>.*?<\/title>/s, "");
// variants: rounded (any purpose, transparent corners), full-bleed (maskable / apple), mark only scaled for maskable safe zone
const full = bare.replace(/rx="112"/, 'rx="0"');
const maskable = full.replace('<g id="mark">', '<g id="mark" transform="translate(256 256) scale(0.8) translate(-256 -256)">');
// favicon: no rays and no network lines, a bigger pupil, so it reads at 16-48 px
const tiny = bare.replace(/<g id="rays"[\s\S]*?<\/g>/, "").replace(/<g id="net">[\s\S]*?<\/g><\/g>/, "")
  .replace('r="17" fill="#1C0F0E" stroke="#F6D06B" stroke-width="5"', 'r="26" fill="#1C0F0E" stroke="#F6D06B" stroke-width="8"')
  .replace('<g id="mark">', '<g id="mark" transform="translate(256 256) scale(1.12) translate(-256 -262)">');
const jobs = [
  ["icons/icon-192.png", bare, 192], ["icons/icon-512.png", bare, 512],
  ["icons/maskable-192.png", maskable, 192], ["icons/maskable-512.png", maskable, 512],
  ["icons/apple-touch-icon.png", full, 180], ["icons/favicon-32.png", tiny, 32],
  ["icons/favicon-16.png", tiny, 16], ["icons/favicon-48.png", tiny, 48],
  ["assets/banta-y-logo-256.png", bare, 256],
];
const browser = await pw.chromium.launch({ executablePath: "/opt/pw-browsers/chromium" }).catch(() => pw.chromium.launch());
const page = await browser.newPage();
for (const [out, src, size] of jobs) {
  await page.setViewportSize({ width: size, height: size });
  const s = src.replace("<svg ", `<svg width="${size}" height="${size}" `);
  await page.setContent(`<!doctype html><html><body style="margin:0;background:transparent">${s}</body></html>`);
  const buf = await page.screenshot({ omitBackground: true, clip: { x: 0, y: 0, width: size, height: size } });
  writeFileSync(join(HERE, out), buf);
  console.log("wrote", out);
}
await browser.close();
// favicon.ico with 16, 32 and 48 px images (PIL), in icons/ and at the folder root
const ico = join(HERE, "icons/favicon.ico");
execFileSync("python3", ["-c", "import sys\nfrom PIL import Image\nims=[Image.open(p).convert('RGBA') for p in sys.argv[2:]]\nims[-1].save(sys.argv[1], sizes=[im.size for im in ims], append_images=ims[:-1])",
  ico, join(HERE, "icons/favicon-16.png"), join(HERE, "icons/favicon-32.png"), join(HERE, "icons/favicon-48.png")]);
copyFileSync(ico, join(HERE, "favicon.ico"));
for (const f of ["icons/favicon-16.png", "icons/favicon-48.png"]) rmSync(join(HERE, f));
console.log("wrote icons/favicon.ico and favicon.ico");

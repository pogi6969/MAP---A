// Builds the LIGTA-S app (app/index.html) and website (index.html) from src/.
//   node ligta-s/tools/build.mjs
// The app is one self-contained file: styles, the demo data (synthetic test network E1),
// the engine, the map and the interface are inlined, so it also works when downloaded.
// The engine sits in its own <script id="ligtas-engine"> block between the markers
// LIGTAS-ENGINE:BEGIN and LIGTAS-ENGINE:END; tests/verify.mjs runs exactly that block.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC = join(ROOT, "src");
const read = (p) => readFileSync(join(SRC, p), "utf8");

export const APP_VERSION = "1.0.0";

const engine = read("engine.js");
const engineVersion = (engine.match(/version:\s*"([^"]+)"/) || [])[1] || "?";
const mapJs = read("map.js");
const appJs = read("app.js");
const css = read("app.css");
const demo = JSON.parse(read("e1-data.json"));

let logoCount = 0;
function logo(cls) {
  // inline copy of the rounded logo with ids made unique per copy
  const n = ++logoCount;
  return read("logo/logo-rounded.svg")
    .replace(/id="bg"/g, `id="lg-bg-${n}"`).replace(/url\(#bg\)/g, `url(#lg-bg-${n})`)
    .replace(' width="512" height="512"', ` class="${cls || "logo"}" aria-hidden="true" focusable="false"`);
}
const favicon = "data:image/svg+xml," + encodeURIComponent(read("logo/logo-small.svg").replace(' width="512" height="512"', ""));
const safeJSON = (o) => JSON.stringify(o).replace(/</g, "\\u003c").replace(/>/g, "\\u003e").replace(/&/g, "\\u0026");
const noClose = (js) => js.replace(/<\/script/gi, "<\\/script");

function fill(html, map) {
  for (const [k, v] of Object.entries(map)) {
    if (!html.includes(k)) throw new Error("placeholder missing: " + k);
    html = html.split(k).join(typeof v === "function" ? "\u0000" : v);
    if (typeof v === "function") html = html.replace(/\u0000/g, () => v());
  }
  const left = html.match(/@@[A-Z_]+@@|<!--@[A-Z]+-->/);
  if (left) throw new Error("unfilled placeholder " + left[0]);
  return html;
}

const engineBlock = `<script id="ligtas-engine">\n/* LIGTAS-ENGINE:BEGIN */\n${noClose(engine)}\n/* LIGTAS-ENGINE:END */\n</script>`;
const dataBlock = `<script type="application/json" id="ligtas-demo">${safeJSON(demo)}</script>`;

/* ---------------------------------------------------------------- app */
logoCount = 0;
const app = fill(read("app.html"), {
  "@@FAVICON_DATAURI@@": favicon,
  "@@LOGO_SVG@@": () => logo("logo"),
  "@@VERSION@@": APP_VERSION,
  "@@ENGINE_VERSION@@": engineVersion,
  "<!--@CSS-->": `<style>\n${css}\n</style>`,
  "<!--@DATA-->": dataBlock,
  "<!--@ENGINE-->": engineBlock,
  "<!--@MAP-->": `<script id="ligtas-map">\n${noClose(mapJs)}\n</script>`,
  "<!--@APPJS-->": `<script id="ligtas-app">\n${noClose(appJs)}\n</script>`,
});
mkdirSync(join(ROOT, "app"), { recursive: true });
writeFileSync(join(ROOT, "app", "index.html"), app);
console.log("app/index.html", (app.length / 1024).toFixed(1), "KB");

/* ---------------------------------------------------------------- website */
const siteTpl = read("site.html");
const eq = JSON.parse(read("equations.json"));
const siteMap = {
  "@@LOGO_SVG@@": () => logo("logo"),
  "@@VERSION@@": APP_VERSION,
  "<!--@SITECSS-->": `<style>\n${read("site.css")}\n</style>`,
  "<!--@DATA-->": dataBlock,
  "<!--@ENGINE-->": engineBlock,
  "<!--@MAP-->": `<script id="ligtas-map">\n${noClose(mapJs)}\n</script>`,
  "<!--@SITEJS-->": `<script id="ligtas-site">\n${noClose(read("site.js"))}\n</script>`,
};
// the count shown on the website comes from the last run of tests/verify.mjs
let checks = "All";
try {
  const r = JSON.parse(readFileSync(join(ROOT, "tests", "verify-result.json"), "utf8"));
  const n = (x) => x.toLocaleString("en-US");
  checks = `${n(r.passed)} / ${n(r.checks)}`;
} catch (e) { /* tests not run yet */ }
siteMap["@@APPCHECKS@@"] = checks;
// equations, pre-rendered to SVG by src/render_equations.cjs: only the ones the page uses
for (const k of Object.keys(eq)) {
  const ph = `@@EQ_${k.toUpperCase()}@@`;
  // long equations also come broken over two lines; site.css shows that form on phones
  if (siteTpl.includes(ph)) siteMap[ph] = eq[k].svgNarrow
    ? `<span class="eq-w">${eq[k].svg}</span><span class="eq-n">${eq[k].svgNarrow}</span>` : eq[k].svg;
}
logoCount = 10;
const site = fill(siteTpl, siteMap);
writeFileSync(join(ROOT, "index.html"), site);
console.log("index.html", (site.length / 1024).toFixed(1), "KB");

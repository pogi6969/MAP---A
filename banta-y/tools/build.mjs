// Builds the BANTA-Y website and app from their templates.
//   node tools/build.mjs
// src/site.html -> index.html, src/app.html -> app/index.html. In both templates:
//   /*@model*/            the model (src/model.js), so each page is one self-contained file
//   <!--@logo:ID-->       the logo (assets/banta-y-logo.svg) inline, its ids prefixed with ID
//   <!--@eq:NAME-->       a pre-rendered equation from src/equations.json (tools/render-equations.cjs)
//   {{path|format}}       a number from the research results (results.json of the dengue study)
// Formats: f0..f6 fixed decimals, pct0..pct2 (share as percent), int (thousands separators), e (scientific).
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(dirname(fileURLToPath(import.meta.url)));
const RESULTS = join(HERE, "..", "research", "where-people-go-dengue", "code", "results.json");

export function loadResults() {
  if (existsSync(RESULTS)) {
    const text = readFileSync(RESULTS, "utf8");
    writeFileSync(join(HERE, "src", "results-d1.json"), text);   // snapshot for building without the research folder
    return JSON.parse(text);
  }
  // fall back to the copy kept next to the app, so the site still builds without the research folder
  return JSON.parse(readFileSync(join(HERE, "src", "results-d1.json"), "utf8"));
}

function get(obj, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[/^\d+$/.test(k) ? +k : k]), obj);
}

export function fmt(v, f) {
  if (v === null || v === undefined || Number.isNaN(v)) throw new Error("missing value for format " + f);
  if (!f) return String(v);
  let m;
  if ((m = /^f(\d)$/.exec(f))) return Number(v).toLocaleString("en-US", { minimumFractionDigits: +m[1], maximumFractionDigits: +m[1] });
  if ((m = /^pct(\d)$/.exec(f))) return (100 * v).toLocaleString("en-US", { minimumFractionDigits: +m[1], maximumFractionDigits: +m[1] });
  if (f === "int") return Math.round(v).toLocaleString("en-US");
  if (f === "e") {
    const [mant, ex] = Number(v).toExponential(1).split("e");
    return mant + " × 10<sup>" + ex.replace("+", "").replace("-", "−") + "</sup>";
  }
  throw new Error("unknown format " + f);
}

function logo(id) {
  let svg = readFileSync(join(HERE, "assets", "banta-y-logo.svg"), "utf8");
  svg = svg.replace(/<title[^>]*>[\s\S]*?<\/title>/, "").replace(/ role="img" aria-labelledby="t"/, ' aria-hidden="true" focusable="false"');
  svg = svg.replace(/id="([^"]+)"/g, `id="${id}-$1"`).replace(/url\(#([^)]+)\)/g, `url(#${id}-$1)`);
  svg = svg.replace(/<!--[\s\S]*?-->/g, "").replace(/\n\s*/g, "");
  return svg.replace("<svg ", '<svg class="logo-svg" ');
}

export function build() {
  const model = readFileSync(join(HERE, "src", "model.js"), "utf8").trim();
  const eqs = JSON.parse(readFileSync(join(HERE, "src", "equations.json"), "utf8"));
  const res = loadResults();
  const jobs = [["src/site.html", "index.html"], ["src/app.html", "app/index.html"]];
  for (const [src, out] of jobs) {
    let html = readFileSync(join(HERE, src), "utf8");
    if (html.indexOf("/*@model*/") >= 0) html = html.replace("/*@model*/", () => model);
    html = html.replace(/<!--@logo:([\w-]+)-->/g, (_, id) => logo(id));
    html = html.replace(/<!--@eq:(\w+)-->/g, (_, name) => {
      if (!eqs[name]) throw new Error("unknown equation " + name);
      return '<div class="eq">' + eqs[name].map((p) => '<span class="eqp">' + p.svg + "</span>").join("") + "</div>";
    });
    html = html.replace(/\{\{([\w.]+)(?:\|(\w+))?\}\}/g, (_, path, f) => {
      const v = get(res, path);
      if (v === undefined) throw new Error("unknown result " + path + " in " + src);
      return fmt(v, f);
    });
    writeFileSync(join(HERE, out), html);
    console.log("wrote", out, (html.length / 1024).toFixed(0), "KB");
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) build();

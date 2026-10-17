// Checks the algorithms inside the BANTA-Y app against the Python results of the study.
//   node tests/verify.mjs
// The model code is taken from the built app (app/index.html, <script id="bantay-model">), so the test
// checks exactly what users run; it must equal src/model.js and the copy inlined in the website.
// Reference numbers: research/where-people-go-dengue/code/results.json (keys "d1" and "verification"),
// or the snapshot src/results-d1.json when the research folder is absent.
// Tolerances: integers must match exactly; real numbers to 1e-6 relative (most agree to about 1e-15).
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const HERE = dirname(dirname(fileURLToPath(import.meta.url)));
const RES_PATH = join(HERE, "..", "research", "where-people-go-dengue", "code", "results.json");
const RES = JSON.parse(readFileSync(existsSync(RES_PATH) ? RES_PATH : join(HERE, "src", "results-d1.json"), "utf8"));
const R = RES.d1;

/* ------------------------------------------------------------------ load the model from the built app */
function modelBlock(file) {
  const html = readFileSync(join(HERE, file), "utf8");
  const m = /<script id="bantay-model">\n?([\s\S]*?)\n?<\/script>/.exec(html);
  if (!m) throw new Error("no <script id=\"bantay-model\"> in " + file);
  return m[1].trim();
}
const appCode = modelBlock("app/index.html");
const srcCode = readFileSync(join(HERE, "src", "model.js"), "utf8").trim();
const ctx = { module: undefined };
vm.createContext(ctx);
vm.runInContext(appCode + "\n;globalThis.BantayModel = BantayModel;", ctx);
const M = ctx.BantayModel;

let passed = 0, failed = 0, worst = 0;
const fails = [];
function ok(cond, name, detail) {
  if (cond) passed++; else { failed++; fails.push(name + (detail ? " (" + detail + ")" : "")); }
}
function relErr(a, b) { return Math.abs(a - b) / Math.max(Math.abs(b), 1e-300); }
function close(a, b, name, tol) {
  tol = tol == null ? 1e-6 : tol;
  const e = b === 0 ? Math.abs(a) : relErr(a, b);
  if (isFinite(e)) worst = Math.max(worst, e);
  ok(isFinite(a) && e <= tol, name, `got ${a}, expected ${b}, rel err ${e.toExponential(2)}`);
}
function closeVec(a, b, name, tol) {
  ok(Array.isArray(b) && a.length === b.length, name + " length", `${a.length} vs ${b && b.length}`);
  for (let i = 0; i < b.length; i++) close(a[i], b[i], `${name}[${i}]`, tol);
}
function exactInt(a, b, name) { ok(Number.isInteger(a) && a === b, name, `got ${a}, expected ${b}`); }

/* ------------------------------------------------------------------ 0. the code users run */
ok(appCode === srcCode, "app/index.html inlines exactly src/model.js");
if (existsSync(join(HERE, "index.html"))) ok(modelBlock("index.html") === srcCode, "index.html (website demo) inlines exactly src/model.js");
ok(M.version === 1, "model version 1");

/* ------------------------------------------------------------------ 1. test network D1 */
const D = M.D1;
const net = M.buildNetwork(D, M.DEFAULT_PARAMS, 1);
close(net.kappa, R.kappa, "kappa", 1e-12);
close(M.kappa(M.DEFAULT_PARAMS), 0.5839135089893257, "kappa = 0.584", 1e-12);
R.rows.forEach((r, i) => {
  exactInt(D.rows[i].residents, r.residents, `D1 residents ${r.id}`);
  exactInt(D.rows[i].households, r.households, `D1 households ${r.id}`);
  ok(D.rows[i].mhat === r.mhat && D.rows[i].attract === r.attract && D.rows[i].away === r.away, `D1 inputs ${r.id}`);
  close(net.cost[i], r.cost, `team-days for full control ${r.id}`, 1e-12);
});
// P is stored rounded to 4 decimals in results.json
net.P.forEach((row, i) => row.forEach((p, j) => ok(Math.abs(Math.round(p * 1e4) / 1e4 - R.P[i][j]) < 1e-12, `P[${i}][${j}]`, `${p} vs ${R.P[i][j]}`)));
net.P.forEach((row, i) => close(row.reduce((a, b) => a + b, 0), 1, `row ${i} of P adds to 1`, 1e-12));

const an = M.analyse(net);
closeVec(an.present, R.present, "people present by day");
closeVec(an.m, R.m, "mosquitoes per person present");
closeVec(an.R_local, R.R_local, "local exposure numbers R_i");
close(an.r0, R.r0, "network R0 (1.2143)");
close(an.r0_sq, R.r0_sq, "R0 squared");
close(an.hom_r0, R.hom_r0, "province-average R0 (1.204)");
closeVec(an.iso_r0, R.iso_r0, "isolated R0");
close(an.r0_no_movement, R.r0_no_movement, "R0 if nobody moved (1.759)");
closeVec(an.shares, R.shares, "place shares");
closeVec(an.case_share, R.case_share, "cases by home address");
closeVec(an.grad, R.grad, "gradient of R0^2");
closeVec(an.hotspot_per_teamday, R.hotspot_per_teamday, "hotspot score per team-day");
ok(an.minR <= an.r0_sq && an.r0_sq <= an.maxR, "sandwich min R_i <= R0^2 <= max R_i on D1");
ok(Math.abs(an.shares.reduce((a, b) => a + b, 0) - 1) < 1e-12, "place shares add to 1 on D1");
ok(Math.round(1000 * an.shares[0]) / 10 === 42.6 && Math.round(1000 * an.case_share[1]) / 10 === 28.5, "D1 headline: 42.6% at B1, 28.5% of cases in B2");

/* ------------------------------------------------------------------ 2. five plans */
const st = M.strategies(net, R.target);
for (const k of ["uniform", "case_residence", "place_share", "certificate", "exact"]) {
  close(st[k].cost, R.strategies[k].cost, `${k} cost (team-days)`);
  close(st[k].r0, R.strategies[k].r0, `${k} R0 reached`);
  st[k].u.forEach((u, j) => ok(Math.abs(Math.round(u * 1e4) / 1e4 - R.strategies[k].u[j]) < 1.5e-4, `${k} u[${j}]`, `${u} vs ${R.strategies[k].u[j]}`));
}
ok(st.exact.lower <= st.exact.upper && (st.exact.upper - st.exact.lower) / st.exact.upper <= 1e-6, "exact plan: certified gap at most 1e-6", `[${st.exact.lower}, ${st.exact.upper}]`);
const pyUpper = R.strategies.exact.cost, pyLower = pyUpper * (1 - R.exact_gap);
ok(st.exact.lower <= pyUpper + 1e-9 && pyLower <= st.exact.upper + 1e-9, "JS and Python certified intervals overlap");
ok(st.exact.iterations === R.exact_iterations, "exact plan: same number of Newton steps as Python", `${st.exact.iterations} vs ${R.exact_iterations}`);
ok(st.exact.cost <= Math.min(st.uniform.cost, st.case_residence.cost, st.place_share.cost, st.certificate.cost), "least cost is the cheapest plan");
ok(st.certificate.r0 <= R.target + 1e-12, "certificate plan meets the target");
// headline percentages of the study
ok(Math.round(100 * (1 - st.exact.cost / st.uniform.cost)) === 40 && Math.round(100 * (1 - st.exact.cost / st.case_residence.cost)) === 42, "least cost is 40% below uniform and 42% below where-cases-live");

/* ------------------------------------------------------------------ 3. season */
const curve = M.seasonCurve(net, R.target, R.season.map((s) => s.s));
curve.forEach((c, i) => {
  close(c.r0, R.season[i].r0, `season ${c.s}: R0 without control`);
  if (R.season[i].cost === 0) ok(c.cost === 0, `season ${c.s}: no control needed (cost 0)`, `got ${c.cost}`);
  else close(c.cost, R.season[i].cost, `season ${c.s}: least cost`);
});
curve.forEach((c) => close(c.r0 * c.r0, c.s * an.r0_sq, `Proposition 10: R0^2 scales with the season (${c.s})`, 1e-9));

/* ------------------------------------------------------------------ 4. inversion */
const INV = R.inversion;
INV.cases_by_residence.forEach((c, i) => exactInt(D.cases[i], c, `D1 cases by residence ${i}`));
const inv = M.inferPlaces(net.P, net.N, INV.cases_by_residence);
closeVec(inv.rate, INV.rate_by_residence, "rate by residence", 1e-12);
closeVec(inv.z, INV.place_pressure_inferred, "inferred pressure by place");
closeVec(inv.infections, INV.infections_by_place_inferred, "inferred infections by place");
close(inv.varah, INV.varah, "Varah factor 5", 1e-12);
closeVec(D.truth, INV.infections_by_place_true, "model-truth infections by place (D1 only)", 1e-12);
// noise-free cases are recovered exactly (Proposition 11)
const zTrue = INV.place_pressure_true, yExact = net.P.map((row) => row.reduce((s, p, j) => s + p * zTrue[j], 0));
closeVec(M.nnls(net.P, yExact), zTrue, "exact recovery of place pressure from noise-free rates", 1e-9);

/* ------------------------------------------------------------------ 5. CUSUM */
const C = R.cusum;
const kt = C.mu0.map((m) => M.cusumK(m, 1.5));
kt.forEach((k, t) => close(k, 0.5 * C.mu0[t] / Math.log(1.5), `k_t week ${t + 1}`, 1e-14));
const cu = M.cusum(C.current, kt, C.h);
cu.S.forEach((s, t) => ok(Math.abs(s - C.S[t]) <= 1e-9 * Math.max(1, Math.abs(C.S[t])), `CUSUM S_t week ${t + 1}`, `${s} vs ${C.S[t]}`));
exactInt(cu.alarm + 1, C.alarm_cusum_week, "CUSUM alarm week (34)");
const th = M.thresholdRule(C.current, C.mu0, C.z);
closeVec(th.threshold, C.threshold, "single-week threshold", 1e-12);
exactInt(th.alarm + 1, C.alarm_threshold_week, "single-week alarm week (32)");
ok(JSON.stringify(D.alarm.counts) === JSON.stringify(C.current), "demo weekly counts equal the study's simulated year");
D.alarm.expected.forEach((e, t) => ok(Math.abs(e - C.mu0[t]) <= 0.005 + 1e-12, `demo expected count week ${t + 1} (2 decimals)`));
const cuDemo = M.cusum(D.alarm.counts, D.alarm.expected.map((m) => M.cusumK(m, D.alarm.theta)), D.alarm.h);
exactInt(cuDemo.alarm + 1, C.alarm_cusum_week, "demo CUSUM alarm week with 2-decimal expected counts");
exactInt(M.thresholdRule(D.alarm.counts, D.alarm.expected, D.alarm.z).alarm + 1, C.alarm_threshold_week, "demo single-week alarm week");
ok(D.alarm.h === C.h && Math.abs(D.alarm.z - C.z) < 1e-9, "demo h = 12.75 and z = 3.64");
// exact average run lengths (V8)
RES.verification.V8.arl.forEach((a) => close(M.arlMarkov(a.mu, a.k, a.h), a.markov, `ARL Markov mu=${a.mu} k=${a.k} h=${a.h}`));
RES.verification.V8.comparison.forEach((c) => {
  close(M.thresholdArl(c.mu, c.c), c.arl0_threshold, `threshold ARL0 mu=${c.mu} c=${c.c}`);
  for (const f of [1.5, 2]) {
    close(M.arlMarkov(c.mu * f, c.k, c.h), c["arl1_cusum_" + f], `CUSUM ARL1 x${f} mu=${c.mu} h=${c.h}`);
    close(M.thresholdArl(c.mu * f, c.c), c["arl1_threshold_" + f], `threshold ARL1 x${f} mu=${c.mu}`);
  }
});
// delay bound (Proposition 12 ii) on random series
let rs = 12345;
const rand = () => { rs = (rs * 1664525 + 1013904223) >>> 0; return rs / 4294967296; };
let delayViol = 0;
for (let trial = 0; trial < 500; trial++) {
  const T = 40, h = 2 + 20 * rand(), tau = Math.floor(rand() * 20), delta = 0.5 + 4 * rand();
  const k = Array.from({ length: T }, () => 1 + 10 * rand());
  const x = k.map((kt2, t) => t >= tau ? kt2 + delta + 3 * rand() : Math.max(0, kt2 - 5 + 6 * rand()));
  const a = M.cusum(x, k, h).alarm, bound = tau + M.delayBound(h, delta) - 1;
  if (bound < T && (a === null || a > bound)) delayViol++;
}
ok(delayViol === 0, "CUSUM delay bound holds on 500 random series", delayViol + " violations");

/* ------------------------------------------------------------------ 6. propositions on random networks */
function randomNet(n) {
  const omega = Array.from({ length: n }, () => 0.05 + 0.4 * rand());
  const attract = Array.from({ length: n }, () => 0.2 + 5 * rand());
  const pos = Array.from({ length: n }, () => [10 * rand(), 10 * rand()]);
  const P = M.residenceTimeMatrix(omega, attract, M.travelFromPositions(pos, 4, 0.3), 0.02 + 0.08 * rand());
  const N = Array.from({ length: n }, () => 500 + Math.round(8000 * rand()));
  const V = N.map((x) => x * (0.5 + 4 * rand()));
  const cost = N.map((x) => x / 4.1 / 50);
  return { P, N, V, cost, ubar: N.map(() => 0.8), kappa: M.kappa(M.DEFAULT_PARAMS), n };
}
let sandwichViol = 0, homViol = 0, shareErr = 0, gradErr = 0, eigErr = 0, cvxViol = 0, solverBad = 0, recErr = 0, instances = 0;
for (let trial = 0; trial < 60; trial++) {
  const n = 2 + Math.floor(rand() * 9), g = randomNet(n), k = g.kappa;
  const a = M.analyse(g);
  instances++;
  if (!(a.minR <= a.r0_sq * (1 + 1e-12) && a.r0_sq <= a.maxR * (1 + 1e-12))) sandwichViol++;
  if (!(a.r0_sq >= (a.hom_r0 * a.hom_r0) * (1 - 1e-12))) homViol++;
  shareErr = Math.max(shareErr, Math.abs(a.shares.reduce((s, x) => s + x, 0) - 1));
  // R0^2 by power iteration on the non-symmetric M = kappa D_N P W P^T (independent of the Jacobi solver)
  const Mh = M.hostHostMatrix(g.P, g.N, g.V, k);
  let v = new Array(n).fill(1), lam = 0;
  for (let it = 0; it < 5000; it++) {
    const w = Mh.map((row) => row.reduce((s, x, j) => s + x * v[j], 0));
    const nl = Math.max(...w.map(Math.abs)); v = w.map((x) => x / nl);
    if (Math.abs(nl - lam) < 1e-15 * nl) { lam = nl; break; }
    lam = nl;
  }
  eigErr = Math.max(eigErr, relErr(lam, a.r0_sq));
  // gradient by central differences
  for (let j = 0; j < n; j++) {
    const hgt = 1e-6, up = new Array(n).fill(0), dn = new Array(n).fill(0); up[j] = 0.1 + hgt; dn[j] = 0.1 - hgt;
    const fd = (M.r0Squared(g.P, g.N, g.V, k, up) - M.r0Squared(g.P, g.N, g.V, k, dn)) / (2 * hgt);
    const base = new Array(n).fill(0); base[j] = 0.1;
    const an2 = M.gradient(g.P, g.N, g.V, k, base)[j];
    gradErr = Math.max(gradErr, Math.abs(fd - an2) / Math.max(1e-9, Math.abs(an2)));
  }
  // convexity of R0^2(u) along a random segment (Proposition 7)
  const u1 = g.N.map(() => 0.8 * rand()), u2 = g.N.map(() => 0.8 * rand()), f1 = M.r0Squared(g.P, g.N, g.V, k, u1), f2 = M.r0Squared(g.P, g.N, g.V, k, u2);
  for (const t of [0.25, 0.5, 0.75]) {
    const um = u1.map((x, i) => (1 - t) * x + t * u2[i]);
    if (M.r0Squared(g.P, g.N, g.V, k, um) > (1 - t) * f1 + t * f2 + 1e-12) cvxViol++;
  }
  // solver: certified interval, feasibility, never worse than the certificate or the heuristics
  const target = Math.max(0.6, 0.85 * a.r0);
  if (M.r0Squared(g.P, g.N, g.V, k, g.ubar) < target * target && a.r0 > target) {
    const s2 = M.strategies(g, target);
    const e = s2.exact;
    const good = e.feasible && e.lower <= e.upper * (1 + 1e-12) && e.r0 <= target * (1 + 1e-9)
      && (e.upper - e.lower) <= 1e-6 * e.upper + 1e-9
      && ["uniform", "case_residence", "place_share", "certificate"].every((nm) => !s2[nm].feasible || e.cost <= s2[nm].cost * (1 + 1e-6))
      && (!s2.certificate.feasible || s2.certificate.r0 <= target * (1 + 1e-9));
    if (!good) solverBad++;
  }
  // exact inversion when every p_ii > 1/2
  if (M.varahBound(g.P) < Infinity) {
    const z = g.N.map(() => 0.02 * rand()), y = g.P.map((row) => row.reduce((s, p, j) => s + p * z[j], 0));
    const zh = M.nnls(g.P, y);
    recErr = Math.max(recErr, Math.max(...zh.map((x, j) => Math.abs(x - z[j]))) / Math.max(...z));
  }
}
ok(sandwichViol === 0, `sandwich bounds hold on ${instances} random networks`, sandwichViol + " violations");
ok(homViol === 0, "averaging never overstates R0 (Proposition 5)", homViol + " violations");
ok(shareErr < 1e-12, "place shares add to 1 on random networks", shareErr.toExponential(2));
ok(eigErr < 1e-9, "Jacobi R0^2 equals power iteration on the host-host matrix", eigErr.toExponential(2));
ok(gradErr < 1e-5, "gradient formula equals central differences", gradErr.toExponential(2));
ok(cvxViol === 0, "R0^2(u) is convex along random segments", cvxViol + " violations");
ok(solverBad === 0, "least-cost solver: certified, feasible, never beaten by another plan", solverBad + " bad cases");
ok(recErr < 1e-8, "NNLS recovers noise-free place pressures exactly", recErr.toExponential(2));

/* ------------------------------------------------------------------ 7. text input */
const wk = M.parseWeekly("week, cases, expected\n1, 5, 6.00\n2\t8\t6.5\n3;10;7\n\n4 4 6");
ok(JSON.stringify(wk.counts) === "[5,8,10,4]" && JSON.stringify(wk.expected) === "[6,6.5,7,6]", "parseWeekly reads commas, tabs, semicolons and spaces", JSON.stringify(wk));
const rows = [["name", "note"], ["B1 \"Poblacion\"", "school, market"], ["B2", "x"]];
ok(JSON.stringify(M.parseDelimited(M.toCSV(rows))) === JSON.stringify(rows), "CSV round trip with quotes and commas");
ok(JSON.stringify(M.parseNumbers("76, 91\n53\t39 24;25")) === "[76,91,53,39,24,25]", "parseNumbers");

/* ------------------------------------------------------------------ report */
console.log(`BANTA-Y model checks: ${passed} passed, ${failed} failed. Largest relative error against the Python results: ${worst.toExponential(2)}.`);
console.log(`D1: R0 ${an.r0.toFixed(4)}, team-days uniform ${st.uniform.cost.toFixed(2)}, where cases live ${st.case_residence.cost.toFixed(2)}, place share ${st.place_share.cost.toFixed(2)}, certificate ${st.certificate.cost.toFixed(2)}, least cost ${st.exact.cost.toFixed(2)} in [${st.exact.lower.toFixed(4)}, ${st.exact.upper.toFixed(4)}].`);
if (failed) { fails.slice(0, 40).forEach((f) => console.log("  FAIL:", f)); process.exit(1); }

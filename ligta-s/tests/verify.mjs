// Checks the LIGTA-S app's engine against the paper's Python model.
//   node ligta-s/tests/verify.mjs          (after node ligta-s/tools/build.mjs)
//
// It runs the engine exactly as shipped: the <script id="ligtas-engine"> block of app/index.html,
// between the markers LIGTAS-ENGINE:BEGIN and LIGTAS-ENGINE:END, on the demo data embedded in the
// same file (synthetic test network E1). Expected values come from
//   research/safe-shelter-open-schools/code/results.json   (key "e1", written by verify_evacuation.py)
//   tests/fixtures/random.json                             (random synthetic instances, make_fixtures.py)
//   tests/fixtures/e1-edits.json                           (random edits of E1, make_e1_edits.py)
// Whole numbers must match exactly; the paper rounds mean trip times to 2 decimals, so those are
// compared after the same rounding (other real values to a relative 1e-6).
//
// Some values are not fixed by the model: when several plans are optimal, the persons per tier of the
// time-only plan, and the longest trip of a plan, can differ between two correct solvers. Those are
// reported as "ties" (printed, not failed) and are listed in the summary. Everything that every optimal
// plan shares must match.
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const RESULTS = join(ROOT, "..", "research", "safe-shelter-open-schools", "code", "results.json");

/* ---------------------------------------------------------------- load the shipped engine and data */
const html = readFileSync(join(ROOT, "app", "index.html"), "utf8");
const m = html.match(/\/\* LIGTAS-ENGINE:BEGIN \*\/([\s\S]*?)\/\* LIGTAS-ENGINE:END \*\//);
if (!m) throw new Error("engine block not found in app/index.html");
const ctx = vm.createContext({ console });
vm.runInContext(m[1], ctx, { filename: "app/index.html#ligtas-engine" });
const E = ctx.LigtasEngine;
const dm = html.match(/<script type="application\/json" id="ligtas-demo">([\s\S]*?)<\/script>/);
const DATA = JSON.parse(dm[1]);
const R = JSON.parse(readFileSync(RESULTS, "utf8").replace(/\bInfinity\b/g, "1e999").replace(/\bNaN\b/g, "null"));
const E1 = R.e1;
const FIX = JSON.parse(readFileSync(join(HERE, "fixtures", "random.json"), "utf8"));

/* ---------------------------------------------------------------- tiny test harness */
let checks = 0, failed = 0;
const fails = [], ties = [];
const group = {};
function same(got, want) {
  if (typeof want === "number" && typeof got === "number") {
    if (!isFinite(want) || !isFinite(got)) return want === got;
    if (Number.isInteger(want)) return got === want;
    return Math.abs(got - want) <= 1e-6 * Math.max(1, Math.abs(want));
  }
  if (want === null || got === null) return want === got;
  return JSON.stringify(got) === JSON.stringify(want);
}
function eq(name, got, want, g) {
  checks++;
  group[g] = (group[g] || 0) + 1;
  if (!same(got, want)) { failed++; fails.push(`${name}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`); }
}
function tie(name, got, want) {
  if (!same(got, want)) ties.push(`${name}: app ${JSON.stringify(got)}, Python ${JSON.stringify(want)} (both optimal)`);
}
const r2 = (x) => Math.round(x * 100) / 100;
const fin = (x) => (x === Infinity || x === 1e999 ? null : x);
const sorted = (o) => Object.fromEntries(Object.entries(o).sort());

/* ---------------------------------------------------------------- test network E1 */
const inst = E.makeInstance(DATA);
const sid = (s) => inst.shelters[+s].id;
function byShelter(obj) { const o = {}; for (const k of Object.keys(obj)) if (obj[k] > 0) o[sid(k)] = obj[k]; return sorted(o); }

// shelters: capacities from floor areas (Sphere 3.5 m2) and 18 per classroom
for (const s of E1.shelters) {
  const sh = inst.shelters.find((x) => x.id === s.id);
  eq(`E1 ${s.id} non-school capacity`, sh.capEc, s.cap_ec, "E1 data");
  eq(`E1 ${s.id} open-space capacity`, sh.capOpen, s.cap_open, "E1 data");
  eq(`E1 ${s.id} classroom capacity`, sh.rooms * sh.q, s.room_cap, "E1 data");
  eq(`E1 ${s.id} accessible`, sh.accessible, s.accessible, "E1 data");
}
// origins and their nearest shelter under AL4 zones (any safe shelter)
{
  const sc = E.scenario({ zones: [], closed: [] });
  const T = E.travelTimes(inst, sc);
  E1.origins.forEach((o) => {
    const a = inst.origins.findIndex((x) => x.id === o.id);
    eq(`E1 ${o.id} population`, inst.origins[a].pop, o.pop, "E1 data");
    eq(`E1 ${o.id} vulnerable`, inst.origins[a].vul, o.vul, "E1 data");
    const best = Math.min(...T[a]);
    eq(`E1 ${o.id} nearest shelter minutes`, best, o.nearest_min, "E1 data");
  });
}
eq("capacity of a 63 m2 classroom", E.capFromArea(63), 18, "E1 data");

const UNIQUE = ["vul_placed", "placed", "unplaced", "person_minutes"];
const TIERS = ["persons_ec", "persons_open", "persons_room"];
const MAP = { vul_placed: "vulPlaced", placed: "placed", unplaced: "unplaced", persons_ec: "personsEc", persons_open: "personsOpen",
  persons_room: "personsRoom", rooms_closed_total: "roomsClosedTotal", learners_displaced: "learnersDisplaced",
  person_minutes: "personMinutes", max_time: "maxTime" };
for (const sp of DATA.scenarios) {
  const want = E1.scenarios[sp.id];
  const sc = E.scenario(sp);
  const lex = E.evaluate(inst, sc, "lex");
  const time = E.evaluate(inst, sc, "time");
  const near = E.nearest(inst, sc);
  const g = `E1 ${sp.id}`;
  eq(`${g} evacuees`, lex.demand, want.demand, g);
  eq(`${g} vulnerable`, lex.vulnerable, want.vulnerable, g);
  eq(`${g} nearest-site overflow`, near.overflow, want.nearest_overflow, g);
  eq(`${g} nearest-site person-minutes`, near.personMinutes, want.nearest_person_minutes, g);
  // school-preserving plan: every value in results.json
  for (const k of [...UNIQUE, ...TIERS, "rooms_closed_total", "learners_displaced", "max_time"]) eq(`${g} lex ${k}`, lex[MAP[k]], want.lex[k], g);
  eq(`${g} lex mean_time`, r2(lex.meanTime), want.lex.mean_time, g);
  eq(`${g} lex rooms_by_school`, byShelter(lex.roomsClosed), sorted(want.lex.rooms_by_school), g);
  eq(`${g} lex load`, byShelter(lex.load), sorted(want.lex.load), g);
  eq(`${g} clearance (lex)`, lex.clearance, want.clearance_lex, g);
  eq(`${g} clearance lower bound`, lex.clearanceLB, want.clearance_lb, g);
  // assignment table: persons by origin, shelter and space
  const tierName = ["non-school", "school open space", "classroom"];
  const got = {};
  lex.x.forEach((r) => { const s = lex.slots[r.k]; const k = `${inst.origins[r.a].id}|${inst.shelters[s.s].id}|${tierName[s.tier]}`; got[k] = (got[k] || 0) + r.f; });
  const exp = {};
  (want.assignment || []).forEach((r) => { exp[`${r.origin}|${r.shelter}|${r.space}`] = r.persons; });
  if (want.assignment) { if (same(sorted(got), sorted(exp))) eq(`${g} lex assignment`, 1, 1, g); else tie(`${g} lex assignment`, sorted(got), sorted(exp)); }
  // time-only plan: values shared by every fastest plan
  for (const k of UNIQUE) eq(`${g} time-only ${k}`, time[MAP[k]], want.blind[k], g);
  eq(`${g} time-only mean_time`, r2(time.meanTime), want.blind.mean_time, g);
  eq(`${g} time-only rooms_closed_total`, time.roomsClosedTotal, want.blind.rooms_closed_total, g);
  eq(`${g} time-only learners_displaced`, time.learnersDisplaced, want.blind.learners_displaced, g);
  eq(`${g} clearance (time-only)`, time.clearance, want.clearance_blind, g);
  // tier split of the time-only plan: fixed on AL3 (the paper's 40 classrooms), a tie elsewhere
  for (const k of [...TIERS, "max_time"]) {
    if (sp.id === "AL3") eq(`${g} time-only ${k}`, time[MAP[k]], want.blind[k], g);
    else tie(`${g} time-only ${k}`, time[MAP[k]], want.blind[k]);
  }
  if (sp.id === "AL3") eq(`${g} time-only rooms_by_school`, byShelter(time.roomsClosed), sorted(want.blind.rooms_by_school), g);
  // arrival curve of the school-preserving plan, every 2 minutes
  const sup = lex.supplies;
  const curve = want && E1.curves[sp.id].map((_, i) => E.arrivalsBy(inst, sc, 2 * i, sup.sup, sup.caps));
  eq(`${g} arrival curve`, curve, E1.curves[sp.id], g);
}

// bridges under Alert Level 4 with the AL4 plan held fixed
{
  const al4 = DATA.scenarios.find((s) => s.id === "AL4");
  const p = E.plan(inst, E.scenario(al4), "lex");
  const s = E.planSupplies(inst, p);
  eq("E1 bridges: AL4 clearance, all open", E.clearanceTime(inst, E.scenario(al4), s.sup, s.caps).T, E1.bridge_single.open, "E1 bridges");
  for (const [b, t] of Object.entries(E1.bridge_single.closed)) {
    const sc = E.scenario({ zones: al4.zones, closed: [b] });
    eq(`E1 bridge ${b} closed: clearance`, E.clearanceTime(inst, sc, s.sup, s.caps).T, t, "E1 bridges");
  }
  const groups = Object.entries(E1.channel_closures).map(([name, r]) => ({ name, tags: r.bridges }));
  const rows = E.closureStudy(DATA, al4, groups);
  rows.forEach((r) => {
    const w = E1.channel_closures[r.name], g = "E1 bridges";
    eq(`E1 channels ${r.name}: clearance, plan held fixed`, fin(r.clearanceFixedPlan), fin(w.clearance_fixed_plan), g);
    eq(`E1 channels ${r.name}: unplaced`, r.unplaced, w.unplaced, g);
    eq(`E1 channels ${r.name}: persons in classrooms`, r.personsRoom, w.persons_room, g);
    eq(`E1 channels ${r.name}: classrooms closed`, r.roomsClosed, w.rooms_closed, g);
    eq(`E1 channels ${r.name}: clearance, new plan`, fin(r.clearanceNewPlan), fin(w.clearance_new_plan), g);
    eq(`E1 channels ${r.name}: mean trip`, r2(r.meanTime), w.mean_time, g);
    tie(`E1 channels ${r.name}: longest trip`, r.maxTime, w.max_time);
  });
  const d = (n) => rows.find((r) => r.name === n);
  eq("E1 channel A adds 42 minutes", d("A").delta, 42, "E1 bridges");
  eq("E1 channel B adds 21 minutes", d("B").delta, 21, "E1 bridges");
}

// Ligtas Pinoy Center siting, compound scenario, 30-minute standard
{
  const S = E1.siting, g = "E1 siting";
  const al4l = DATA.scenarios.find((s) => s.id === "AL4+L");
  eq("E1 siting candidates", DATA.candidates.map((c) => c.node), S.candidates, g);
  eq("E1 siting standard", DATA.thetaSite, S.theta, g);
  const res = E.siting(DATA, al4l, S.theta, DATA.candidates, S.rows.length);
  eq("E1 siting candidate capacities", res.candidates.map((c) => c.cap), S.capacity, g);
  eq("E1 siting coverage now (phi0)", res.phi0, S.phi0, g);
  eq("E1 siting single-site gains", sorted(res.singleGains), sorted(S.single_gains), g);
  res.rows.forEach((r, i) => {
    const w = S.rows[i];
    eq(`E1 siting k=${r.k} greedy sites`, r.sites, w.sites, g);
    eq(`E1 siting k=${r.k} greedy gain`, r.gain, w.gain, g);
    eq(`E1 siting k=${r.k} best sites`, [...r.bestSites].sort(), [...w.best_sites].sort(), g);
    eq(`E1 siting k=${r.k} best gain`, r.bestGain, w.best_gain, g);
    eq(`E1 siting k=${r.k} unplaced`, r.unplaced, w.unplaced, g);
    eq(`E1 siting k=${r.k} persons in classrooms`, r.personsRoom, w.persons_room, g);
    eq(`E1 siting k=${r.k} classrooms closed`, r.roomsClosed, w.rooms_closed, g);
    eq(`E1 siting k=${r.k} learners displaced`, r.learners, w.learners, g);
    eq(`E1 siting k=${r.k} clearance`, r.clearance, w.clearance, g);
  });
}

/* ---------------------------------------------------------------- random synthetic instances */
FIX.plans.forEach((f, i) => {
  const I = E.makeInstance(f.data), sc = E.scenario(f.scenario), g = "random plans";
  const lex = E.plan(I, sc, "lex"), time = E.plan(I, sc, "time"), near = E.nearest(I, sc);
  for (const k of Object.keys(f.lex)) eq(`random ${i} lex ${k}`, lex[MAP[k]], f.lex[k], g);
  for (const k of Object.keys(f.blind)) eq(`random ${i} time-only ${k}`, time[MAP[k]], f.blind[k], g);
  eq(`random ${i} nearest overflow`, near.overflow, f.nearest.overflow, g);
  eq(`random ${i} nearest person-minutes`, near.personMinutes, f.nearest.person_minutes, g);
  // Proposition 4 on the app's own plan: K(x) <= ceil(Y*/q) + m - 1
  const m = Object.keys(lex.roomsClosed).length;
  checks++; group[g]++;
  if (!(lex.roomsClosedTotal <= Math.ceil(lex.personsRoom / 18) + Math.max(0, m - 1))) { failed++; fails.push(`random ${i} packing bound`); }
  tie(`random ${i} classrooms closed`, lex.roomsClosedTotal, f.lex_rooms);
  const sup = {}, caps = {};
  for (const k of Object.keys(f.supplies)) sup[I.index[k]] = f.supplies[k];
  for (const k of Object.keys(f.caps)) caps[I.index[k]] = f.caps[k];
  eq(`random ${i} clearance time`, fin(E.clearanceTime(I, sc, sup, caps).T), f.clearance, "random clearance");
  eq(`random ${i} lower bound`, fin(E.clearanceLowerBound(I, sc, sup, caps)), f.lower_bound, "random clearance");
});
FIX.siting.forEach((f, i) => {
  const I = E.makeInstance(f.data), sc = E.scenario(f.scenario), g = "random siting";
  const prob = new E.SitingProblem(I, sc, f.theta, f.candidates);
  const gr = prob.greedy(f.k), best = prob.best(f.k);
  eq(`random siting ${i} phi0`, prob.phi0, f.phi0, g);
  eq(`random siting ${i} greedy gain`, prob.gain(gr.sites), f.greedy_gain, g);
  eq(`random siting ${i} best gain`, best.gain, f.best_gain, g);
  // the guarantee of Proposition 10
  checks++; group[g]++;
  const bound = 1 - Math.pow(1 - 1 / f.k, f.k);
  if (!(prob.gain(gr.sites) >= bound * best.gain - 1e-9)) { failed++; fails.push(`random siting ${i}: greedy below the 1-(1-1/k)^k bound`); }
});

/* ---------------------------------------------------------------- edited copies of E1 */
// What app users do: start from E1 and change populations, floor areas, classrooms, accessibility,
// the trip limit, the zones and closed bridges (tests/make_e1_edits.py, solved by evacmodel.py).
const EDITS = JSON.parse(readFileSync(join(HERE, "fixtures", "e1-edits.json"), "utf8"));
EDITS.cases.forEach((c, i) => {
  const d = JSON.parse(JSON.stringify(DATA)), g = "E1 edits";
  d.thetaMax = c.thetaMax;
  c.origins.forEach(([id, pop, vul]) => { const o = d.origins.find((x) => x.id === id); o.pop = pop; o.vul = vul; });
  c.shelters.forEach((e) => {
    const s = d.shelters.find((x) => x.id === e.id);
    if (e.area != null) { if (s.kind === "school") s.areaOpen = e.area; else s.areaNonSchool = e.area; }
    s.rooms = e.rooms; s.learnersPerRoom = e.learnersPerRoom; s.accessible = e.accessible;
  });
  const I = E.makeInstance(d), sc = E.scenario(c.scenario);
  const lex = E.plan(I, sc, "lex"), time = E.plan(I, sc, "time"), near = E.nearest(I, sc);
  for (const k of Object.keys(c.lex)) eq(`E1 edit ${i} lex ${k}`, lex[MAP[k]], c.lex[k], g);
  for (const k of Object.keys(c.blind)) eq(`E1 edit ${i} time-only ${k}`, time[MAP[k]], c.blind[k], g);
  eq(`E1 edit ${i} nearest overflow`, near.overflow, c.nearest.overflow, g);
  eq(`E1 edit ${i} nearest person-minutes`, near.personMinutes, c.nearest.person_minutes, g);
  // the app's own plan is feasible: tier capacities, accessible shelters for the vulnerable, trip limit
  const use = lex.slots.map(() => 0);
  let ok = true;
  lex.x.forEach((r) => {
    const s = lex.slots[r.k];
    use[r.k] += r.f;
    if ((r.cls === "V" && !s.acc) || !(lex.T[r.a][s.s] <= I.thetaMax)) ok = false;
  });
  use.forEach((u, k) => { if (u > lex.slots[k].cap) ok = false; });
  eq(`E1 edit ${i} plan feasible`, ok, true, g);
  const sup = {}, caps = {};
  for (const k of Object.keys(c.supplies)) sup[I.index[k]] = c.supplies[k];
  for (const k of Object.keys(c.caps)) caps[I.index[k]] = c.caps[k];
  eq(`E1 edit ${i} clearance time`, fin(E.clearanceTime(I, sc, sup, caps).T), c.clearance, g);
  eq(`E1 edit ${i} lower bound`, fin(E.clearanceLowerBound(I, sc, sup, caps)), c.lower_bound, g);
});

/* ---------------------------------------------------------------- report */
console.log("LIGTA-S engine", E.version, "vs the Python model of the paper");
for (const [g, n] of Object.entries(group)) console.log(`  ${g.padEnd(18)} ${n} checks`);
if (ties.length) {
  console.log(`\nTies (several optimal plans; not a property of the model, not failed): ${ties.length}`);
  ties.slice(0, 12).forEach((t) => console.log("  " + t));
  if (ties.length > 12) console.log(`  ... and ${ties.length - 12} more`);
}
if (fails.length) {
  console.log("\nFAILED:");
  fails.slice(0, 40).forEach((f) => console.log("  " + f));
}
console.log(`\n${checks - failed} of ${checks} checks passed${failed ? `, ${failed} FAILED` : ""}.`);
writeFileSync(join(HERE, "verify-result.json"), JSON.stringify({
  engine: E.version, checks, passed: checks - failed, failed, ties: ties.length,
  note: "Written by tests/verify.mjs. The website shows passed / checks.",
}, null, 1) + "\n");
process.exit(failed ? 1 : 0);

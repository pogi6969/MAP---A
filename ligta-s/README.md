# LIGTA-S

LIGTA-S (said like *ligtas*, "LIG-tas", the Filipino word for safe) plans evacuations in Albay by hazard zone, shelter capacity and vulnerability while keeping classrooms open. It is the app of the study *Safe Shelter, Open Schools: A Verified Network-Flow Model for Planning Evacuations in Albay by Hazard Zone, Shelter Capacity, and Vulnerability While Keeping Classrooms Open* (Legazpi City Science High School, Mathematics and Computational Sciences, Team).

- Website: https://pogi6969.github.io/MAP---A/ligta-s/
- App: https://pogi6969.github.io/MAP---A/ligta-s/app/
- Paper: [`../research/safe-shelter-open-schools/paper/Safe-Shelter-Open-Schools_MCS-T.pdf`](../research/safe-shelter-open-schools/paper/Safe-Shelter-Open-Schools_MCS-T.pdf)

The demo data is **test network E1, a synthetic volcano** from the paper. Its places and numbers are made up to test the method; they are not Albay data. LIGTA-S is a planning aid, not an evacuation order and not medical advice.

## What the app does

1. **Planner**: editable origins (zones, population, vulnerable residents) and shelters (non-school floor area, school open-space floor area, classrooms, learners per classroom, accessibility, zones); scenarios Alert Level 3, Alert Level 4 and Alert Level 4 + lahar (bridges closed); trip limit θmax. It computes
   - the **school-preserving plan**: the exact lexicographic optimum (most vulnerable placed, most placed, fewest persons in classrooms, fewest in school open spaces, fewest person-minutes). Two maximum flows (Dinic) fix the first two levels, then a minimum-cost flow with **vector costs** (classroom, open space, minutes) compared lexicographically, solved by successive shortest paths with a queue-based Bellman-Ford. No big-M numbers;
   - the **time-only plan** (fewest person-minutes; ties broken toward non-school space) and the **nearest-site rule** with overflow;
   - persons per tier, classrooms closed (packed 18 per room), learners displaced, classroom-days for a chosen stay, mean and longest trip.
2. **Clearance time**: maximum flow (Dinic) on the time-expanded network, doubling then bisection, with the static lower bound of Proposition 8. Tap bridges on the map or close a whole lahar channel to see the change in clearance time (plan held fixed) and who is trapped (fresh plan).
3. **Ligtas Pinoy Center siting**: candidate sites with floor areas, a travel-time standard (30 minutes by default), greedy choice of k sites with the 1 − (1 − 1/k)^k ≥ 63.2% guarantee, checked against every set of k sites, and the plan recomputed with the new centers.
4. **Resident mode**: choose a barangay to see the assigned shelter at each alert level, the trip time and accessibility, with a switch for households with a vulnerable member.
5. **Capacity calculator**: floor area to persons at 3.5 m² (Sphere Handbook, 2018); classrooms to evacuees at 18 per 63 m² room; evacuees to classrooms closed, learners displaced and classroom-days.
6. **Data**: edits are saved in the browser (localStorage, wrapped in try/catch); export and import JSON, and CSV per table (origins, shelters, roads, map points).

## Files

- `index.html` – the website: hero, why it matters (cited facts), install band, features, a live demo on test network E1, "How MCS comes into play" with typeset equations, the paper, the team, disclaimer and privacy. **Built** from `src/`.
- `app/index.html` – the app, one self-contained file (styles, demo data, engine, map and interface inlined), so it also works when downloaded. **Built** from `src/`.
- `manifest.webmanifest` – name, colours, icons, `start_url` `app/` and scope `./`.
- `sw.js` – service worker with a versioned offline cache (`ligta-s-v1`, prefix `ligta-s-`). It only handles `/ligta-s/` files and the website's Google Fonts.
- `icons/` – `icon-192.png`, `icon-512.png`, `maskable-192.png`, `maskable-512.png`, `apple-touch-icon.png`, `favicon-32.png`, `favicon.ico`, `logo-256.png`.
- `assets/` – `logo.svg`, the school seal (`legasci_seal.png`, `legasci-seal.webp`), the school building illustration (`school_building.webp`) and app screenshots used on the website (`screens/`).
- `src/` – sources:
  - `engine.js` – all algorithms (plain ES5, no dependencies; also loads in Node);
  - `map.js` – SVG map of a road network, hazard zones, shelters and flows;
  - `app.html`, `app.css`, `app.js` – the app's template, styles and interface;
  - `site.html`, `site.css`, `site.js` – the website's template, styles and scripts;
  - `e1-data.json` – test network E1, exported from the paper's Python code by `export_e1.py`;
  - `equations.json` – the paper's equations pre-rendered to SVG by `render_equations.cjs` (MathJax 3), so the website needs no math script; long equations also come broken over two lines for phones;
  - `logo/` – the logo (`make_logo.py` writes the SVG variants, `render_icons.cjs` renders the PNG icons).
- `tools/build.mjs` – builds `app/index.html` and `index.html`.
- `tests/verify.mjs` – checks the shipped engine against the paper's Python model; `tests/ui-check.mjs` – clicks through the website and the app in headless Chromium; `tests/make_fixtures.py` and `tests/fixtures/random.json` – random synthetic instances solved by the Python model; `tests/make_e1_edits.py` and `tests/fixtures/e1-edits.json` – random edits of test network E1 solved by the Python model.

## Build and test

```sh
python3 ligta-s/src/export_e1.py        # only when the paper's test network changes
node ligta-s/tools/build.mjs             # writes app/index.html and index.html
node ligta-s/tests/verify.mjs            # engine vs the Python model (writes tests/verify-result.json)
node ligta-s/tools/build.mjs             # again, so the website shows the new check count
node ligta-s/tests/ui-check.mjs [dir]    # headless Chromium, 1440x900 and 390x844, light and dark
```

`tests/verify.mjs` runs the `<script id="ligtas-engine">` block of the built `app/index.html` (between `LIGTAS-ENGINE:BEGIN` and `LIGTAS-ENGINE:END`) on the demo data embedded in the same file, and compares it with `research/safe-shelter-open-schools/code/results.json` (key `e1`), with 160 random synthetic instances (`tests/fixtures/random.json`) and with 100 random edits of E1 of the kind app users make: populations, floor areas, classrooms, accessibility, trip limit, zones and closed bridges (`tests/fixtures/e1-edits.json`, from `tests/make_e1_edits.py`). Whole numbers must match exactly, mean trip times after the paper's rounding to 2 decimals. Latest run: **3,659 of 3,659 checks passed**. On E1 it reproduces, among others, Alert Level 3: 14 classrooms, 240 persons in classrooms, 532 learners, 48,640 person-minutes, mean trip 31.18 min (time-only plan: 40 classrooms, 1,702 learners, 29.48 min; nearest-site rule: 298 arrive at full shelters); clearance times 53 / 53 / 74 min with lower bounds 34 / 28 / 28; channel A +42 min, channel B +21 min, both channels 450 trapped; siting gains 400, 750, 900 with sites TS; TS, TNE; TS, TNE, TSW.

When several plans are optimal, two correct solvers may split evacuees differently. The app breaks such ties by a fixed rule that never changes a value the model fixes (school open space goes first to the origins lower in the table); with it the app's "Who goes where" table at Alert Level 3 is exactly the paper's Table 13. What can still differ from the Python run: the origin-to-shelter assignment at Alert Level 4 and in the compound scenario, the longest trip after a channel closure, and the tier split of the time-only plan at Alert Level 4 (the app's fastest plan uses the fewest classrooms, 420 in school open space and 1,070 in classrooms; the paper's Table 12 lists another equally fast plan with 410 and 1,080; both close 60 classrooms and displace 2,502 learners). The test prints these as ties and does not fail on them.

## Publish

GitHub Pages serves this folder with the rest of the repository (Settings → Pages → Deploy from a branch → `main`, `/ (root)`). Installing needs HTTPS. Test locally from the repository root with `python3 -m http.server 8000`, then open http://localhost:8000/ligta-s/.

After changing the app, the icons or the manifest, rebuild, and bump `VERSION` in `sw.js` so installed copies refresh. The MAP-A service worker at the site root leaves `/ligta-s/` alone.

## Team

Researchers: Brimbuela, Peter John A.; **De Asis, Dave Justin Ll.** (lead researcher and founder); Shin, Yeaseong. Research adviser: Calleja, Dick Anthony M. Legazpi City Science High School, Bitano, Legazpi City, Albay, Bicol Region (Region V), Philippines. Category: Mathematics and Computational Sciences, Team (MCS-T).

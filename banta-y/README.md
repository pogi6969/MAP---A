# BANTA-Y

BANTA-Y (say *BAN-tai*, from *bantay*: to watch, to guard) ranks dengue hotspots by where people spend the day, finds the least-cost vector-control plan with a certified gap, traces cases from home addresses to places of infection, and raises an early CUSUM alarm. This folder holds the BANTA-Y website and the BANTA-Y app (version 1). Visitors install the app from the website on Android, iPhone, iPad and computers, and it works without a signal once installed.

It is the app of the study *Where People Go, Dengue Goes: A Verified Mobility-Coupled Network Model for Ranking Dengue Hotspots, Issuing Early Warnings, and Allocating Vector Control at Least Cost in Albay* (Legazpi City Science High School, Mathematics and Computational Sciences, Team). The paper is `../research/where-people-go-dengue/paper/Where-People-Go-Dengue-Goes_MCS-T.pdf`; the Python model and its verification are in `../research/where-people-go-dengue/code/`.

## Files

- `index.html` – the website: hero, why place matters, install section, features, a live demo on the test network D1, how MCS comes into play (equations pre-rendered to SVG), the research, the team, privacy. Built from `src/site.html`.
- `app/index.html` – the app, one self-contained file (no outside code, fonts or requests). The website's Install button installs it, and it can be downloaded as one file. Built from `src/app.html`.
- `manifest.webmanifest` – name, colours, icons, start page `app/` and scope `./` used when installing.
- `sw.js` – service worker (cache prefix `banta-y-`) that keeps an offline copy of the app and the website. Its scope is this folder only; the MAP-A service worker at the site root leaves `/banta-y/` alone.
- `icons/`, `favicon.ico` – app icons and favicons made from the BANTA-Y logo.
- `assets/banta-y-logo.svg` – the logo: a gold guard shield holding a watchful eye whose iris is a network of barangays. `banta-y-logo-256.png` is a PNG copy.
- `assets/shot-*.webp`, `assets/app-phone.webp` – app screenshots shown on the website (synthetic test network D1).
- `assets/legasci_seal.png`, `assets/legasci-seal.webp`, `assets/school-building.webp` – the school seal and building.
- `src/model.js` – the model: residence-time matrix, R0 by a Jacobi eigen-solver, local exposure numbers, place shares, the five control plans (uniform, where cases live, place-share heuristic, linear-program certificate by a dense simplex, exact least cost by a barrier interior-point method with a certified dual lower bound), Lawson–Hanson NNLS inversion with the Varah bound, Poisson CUSUM with exact average run lengths. A JavaScript port of `denguemodel.py`; the build inlines it into both pages.
- `src/app.html`, `src/site.html` – page templates. `src/equations.json` – pre-rendered equations. `src/results-d1.json` – snapshot of the study's `results.json`, used when the research folder is absent.
- `tools/` – `build.mjs` (build both pages), `make-icons.mjs` (icons from the logo), `make-shots.mjs` (website screenshots of the app), `render-equations.cjs` (equations to SVG with MathJax).
- `tests/verify.mjs` – checks the model inside the built app against the Python results. `tests/qa.mjs` – browser check of the website and the app.

## Publish

Installing needs HTTPS. With GitHub Pages (Settings → Pages → Deploy from a branch → `main`, `/ (root)`):

- Website: https://pogi6969.github.io/MAP---A/banta-y/
- App: https://pogi6969.github.io/MAP---A/banta-y/app/

Test locally from the repository root with `python3 -m http.server 8000`, then open http://localhost:8000/banta-y/.

After changing the app, the icons or the manifest, bump `VERSION` in `sw.js` so installed copies refresh.

## Build and check

```
node tools/build.mjs          # src/*.html + src/model.js + equations + results  ->  index.html, app/index.html
node tests/verify.mjs         # model checks against results.json (500 checks)
node tests/qa.mjs [outdir]    # headless Chromium at 1440x900 and 390x844, screenshots in outdir
node tools/make-shots.mjs     # refresh the website's app screenshots (after a build)
node tools/make-icons.mjs     # refresh the icons from assets/banta-y-logo.svg
```

The build fills `{{d1.r0|f3}}`-style placeholders in the templates from the study's `results.json`, so the numbers on the website are the numbers of the paper. `tests/verify.mjs` takes the model code from the built `app/index.html` (and checks it equals `src/model.js` and the copy in the website). On the test network D1 it reproduces R0 = 1.2143, the place shares, the local exposure numbers, the five plans (37.47, 38.88, 29.54, 26.49 and 22.60 team-days, with the same 109 Newton steps as Python), the season curve, the inversion of the cases by residence, the CUSUM statistic and alarm weeks (34 and 32) and the exact average run lengths, with a largest relative error of about 1e-11. It also checks the propositions on random networks.

## Honesty notes

- The test network D1 is synthetic: six made-up barangays used to check the method. Its numbers are labelled as a test network everywhere and are not real Albay data.
- Real-world facts on the website (the 2026 Albay dengue state of calamity and case counts, the national count, *Aedes aegypti* behaviour, the temperature range, the DOH 4S) are cited to their sources.
- BANTA-Y is a planning aid. It is not an official order and not medical advice.

## Team

Researchers: Brimbuela, Peter John A.; **De Asis, Dave Justin Ll.** (lead researcher and founder); Shin, Yeaseong. Research adviser: Calleja, Dick Anthony M. Legazpi City Science High School, Bitano, Legazpi City, Albay, Bicol Region (Region V), Philippines. Category: Mathematics and Computational Sciences, Team (MCS-T).

# MAP---A

MAP-A: routes, travel times and fares for public transport across all 18 cities and municipalities of Albay, with a hospital mode. This repository holds the MAP-A website and the MAP-A app (version 49). Visitors install the app from the website on Android, iPhone, iPad and computers, and it opens without a signal once installed.

## Files

- `index.html` – the website: features, fare calculator, hospital mode, coverage map and the install section
- `app/index.html` – the MAP-A app; the website's Install button installs this, and it can also be downloaded as one file
- `manifest.webmanifest` – app name, colours, icons and start page (`app/`) used when installing
- `sw.js` – service worker that keeps an offline copy of the app and the website
- `icons/`, `favicon.ico` – app icons made from the official logo
- `assets/official-logo.webp` – the official logo of the Landmark-Anchored Research Initiative
- `care/` – **MAP-A Care**, the hospital app of the revised paper (*Right Hospital, Right Bed, Right Time*). It runs on the MAP-A network and adds the patient's needed services and walking ability, backup hospitals, the payment, need and mobility gaps, and planning tools: catchment maps, beds per person and bed deserts, surge assignment, critical roads and Malasakit Center site selection. It has its own manifest, service worker (`care/sw.js`, caches named `mapa-care-`) and icons, so it installs as a separate app.
- `research/` – the revised paper (`.docx`, `.pdf`) and `verify_patient_extensions.py`, which reproduces the paper's new tables

## Publish

Installing needs HTTPS. With GitHub Pages: Settings → Pages → Build and deployment → Deploy from a branch → `main` and `/ (root)` → Save.

- Website: https://pogi6969.github.io/MAP---A/
- App: https://pogi6969.github.io/MAP---A/app/
- MAP-A Care: https://pogi6969.github.io/MAP---A/care/

Test locally with `python3 -m http.server 8000`, then open http://localhost:8000.

After changing the app, the icons or the manifest, bump `VERSION` in `sw.js` so installed copies refresh. For MAP-A Care, bump `VERSION` in `care/sw.js`.

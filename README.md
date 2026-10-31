# MAP---A

MAP-A: routes, travel times and fares for public transport across all 18 cities and municipalities of Albay, with a hospital mode. This repository holds the MAP-A website and the MAP-A app (version 49). Visitors install the app from the website on Android, iPhone, iPad and computers, and it opens without a signal once installed.

## Files

- `index.html` – the website: features, fare calculator, hospital mode, coverage map and the install section
- `app/index.html` – the MAP-A app; the website's Install button installs this, and it can also be downloaded as one file
- `manifest.webmanifest` – app name, colours, icons and start page (`app/`) used when installing
- `sw.js` – service worker that keeps an offline copy of the app and the website
- `icons/`, `favicon.ico` – icons made from the MAP-A logo
- `assets/map-a-app-logo.png` – the MAP-A logo, used for the icons, in the app and on the website
- `assets/map-a-interface-logo.png` – the MAP-A interface logo (the red pin on its own)
- `assets/official-logo.webp` – the earlier logo of the Landmark-Anchored Research Initiative (no longer shown)
- `hardware/sensor-cover/` – 3D model of the LED strip sensor cover (STEP, STL and source)

## Publish

Installing needs HTTPS. With GitHub Pages: Settings → Pages → Build and deployment → Deploy from a branch → `main` and `/ (root)` → Save.

- Website: https://pogi6969.github.io/MAP---A/
- App: https://pogi6969.github.io/MAP---A/app/

Test locally with `python3 -m http.server 8000`, then open http://localhost:8000.

After changing the app, the icons or the manifest, bump `VERSION` in `sw.js` so installed copies refresh.

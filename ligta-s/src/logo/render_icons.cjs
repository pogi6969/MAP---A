// Renders the logo SVGs to PNG icons with headless Chromium, then the .ico with Python/PIL.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
const here = __dirname, out = path.join(here, '..', '..', 'icons');
const jobs = [
  ['logo-square.svg', 'icon-192.png', 192], ['logo-square.svg', 'icon-512.png', 512],
  ['logo-maskable.svg', 'maskable-192.png', 192], ['logo-maskable.svg', 'maskable-512.png', 512],
  ['logo-square.svg', 'apple-touch-icon.png', 180], ['logo-small.svg', 'favicon-32.png', 32],
  ['logo-small.svg', 'favicon-16.png', 16], ['logo-small.svg', 'favicon-48.png', 48],
  ['logo-rounded.svg', 'logo-256.png', 256]
];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  for (const [src, dst, size] of jobs) {
    const svg = fs.readFileSync(path.join(here, src), 'utf8');
    await p.setViewportSize({ width: size, height: size });
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg.replace('width="512" height="512"', `width="${size}" height="${size}"`)}</body></html>`);
    await p.screenshot({ path: path.join(out, dst), omitBackground: true, clip: { x: 0, y: 0, width: size, height: size } });
  }
  await b.close();
})();

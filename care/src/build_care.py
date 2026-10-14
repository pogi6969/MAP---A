"""Assemble care/index.html: the MAP-A app shell and engine, rebranded, with the MAP-A Care module.

Run from the repository root:  python3 care/src/build_care.py .
Edit care.js and care.css here, never care/index.html, which this script overwrites."""
import os
import sys

REPO = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(REPO, "app", "index.html"), encoding="utf-8").read()
care_js = open(os.path.join(HERE, "care.js"), encoding="utf-8").read()
care_css = open(os.path.join(HERE, "care.css"), encoding="utf-8").read()


def rep(s, old, new, count=1):
    n = s.count(old)
    if n < 1:
        raise SystemExit("not found: " + old[:80])
    if count == 1 and n != 1:
        raise SystemExit("not unique (%d): %s" % (n, old[:80]))
    return s.replace(old, new)


s = src
# ---- head
s = rep(s, '<link rel="manifest" href="../manifest.webmanifest">', '<link rel="manifest" href="manifest.webmanifest">')
s = rep(s, '<link rel="icon" href="../favicon.ico" sizes="48x48">\n', '')
s = rep(s, '<link rel="icon" href="../icons/favicon-32.png" type="image/png" sizes="32x32">',
        '<link rel="icon" href="icons/favicon-32.png" type="image/png" sizes="32x32">')
s = rep(s, '<link rel="apple-touch-icon" href="../icons/apple-touch-icon.png">',
        '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n'
        '<meta name="description" content="MAP-A Care finds the nearest hospital in Albay that can treat the patient, '
        'has a bed and fits what the family can pay, by ambulance or by public transport, with planning tools for '
        'the health office.">')
s = rep(s, '<meta name="apple-mobile-web-app-title" content="MAP-A">', '<meta name="apple-mobile-web-app-title" content="MAP-A Care">')
s = rep(s, '<title>Albay Open Transit · Maps v49</title>', '<title>MAP-A Care · Right hospital, right bed, right time</title>')
s = rep(s, '</head>', '<style id="care-css">\n' + care_css + '</style>\n</head>')
# ---- splash
s = rep(s, 'aria-label="Loading MAP-A"', 'aria-label="Loading MAP-A Care"')
s = rep(s, '<div class="sp-title">MAP&#8209;A</div>', '<div class="sp-title">MAP&#8209;A Care</div>')
i = s.index('<div class="sp-foot">')
j = s.index('</div>', i) + len('</div>')
s = s[:i] + ('<div class="sp-foot">Right hospital, right bed, right time &middot; 18 LGUs &middot; '
             'Districts I–III &middot; v1.0</div>') + s[j:]
# ---- bottom bar
i = s.index('<nav class="nav" id="bottomNav"')
j = s.index('</nav>', i) + len('</nav>')
s = s[:i] + '''<nav class="nav" id="bottomNav" aria-label="Main">
  <button data-tab="hosp" aria-current="true"><b class="mi"></b>Care</button>
  <button data-tab="plan"><b class="mi"></b>Plan</button>
  <button data-tab="beds"><b class="mi"></b>Beds</button>
  <button data-tab="map"><b class="mi"></b>Map</button>
  <button data-tab="dir"><b class="mi"></b>Directions</button>
  <button data-tab="more"><b class="mi"></b>More</button>
</nav>''' + s[j:]
# ---- the care module goes at the end of the main script
marker = '<script>\n/* Installed app'
k = s.index(marker)
end = s.rindex('</script>', 0, k)
s = s[:end] + care_js + '\n' + s[end:]
# ---- its own service worker
s = rep(s, '/* Installed app: the site\'s service worker keeps a copy of MAP-A so it opens without a signal. */',
        '/* Installed app: MAP-A Care\'s own service worker keeps a copy so it opens without a signal. */')
s = rep(s, 'navigator.serviceWorker.register("../sw.js", { scope: "../" })',
        'navigator.serviceWorker.register("sw.js", { scope: "./" })')

out = os.path.join(REPO, "care", "index.html")
open(out, "w", encoding="utf-8").write(s)
print("wrote", out, len(s))

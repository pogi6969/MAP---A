/* LIGTA-S service worker: keeps a copy of the app and the website so the installed app opens without a signal.
   Its scope is /ligta-s/ only (the MAP-A service worker at the site root leaves these pages alone).
   Pages come from the network when online, so updates show at once, and from the copy when offline.
   Bump VERSION after changing the app, the icons or the manifest. */
var VERSION = "ligta-s-v1";
var PRECACHE = ["app/", "./", "manifest.webmanifest", "icons/favicon.ico", "icons/favicon-32.png",
  "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(VERSION)
      .then(function (cache) { return cache.addAll(PRECACHE.map(function (u) { return new Request(u, { cache: "reload" }); })); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys.filter(function (k) { return k.indexOf("ligta-s-") === 0 && k !== VERSION; })
          .map(function (k) { return caches.delete(k); }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

function keep(cache, req, res) {
  return cache.put(req, res).catch(function () {});
}

/* Pages: the network first, checked with the server every time, the saved copy when offline.
   Anything under app/ falls back to the app, everything else to the website. */
function page(event) {
  var req = event.request;
  var home = new URL(req.url).pathname.indexOf("/ligta-s/app/") !== -1 ? "app/" : "./";
  return fetch(req, { cache: "no-cache" }).then(function (res) {
    if (res.ok) {
      var copy = res.clone();
      event.waitUntil(caches.open(VERSION).then(function (cache) { return keep(cache, req, copy); }));
    }
    return res;
  }).catch(function () {
    return caches.open(VERSION).then(function (cache) {
      return cache.match(req, { ignoreSearch: true }).then(function (hit) { return hit || cache.match(home); });
    }).then(function (hit) { return hit || Response.error(); });
  });
}

/* Icons, images, the manifest and the website's typefaces: the saved copy at once, refreshed in the background. */
function asset(event) {
  var req = event.request;
  return caches.open(VERSION).then(function (cache) {
    return cache.match(req).then(function (hit) {
      var fresh = fetch(req).then(function (res) {
        if (res.ok || res.type === "opaque") return keep(cache, req, res.clone()).then(function () { return res; });
        return res;
      });
      if (!hit) return fresh;
      event.waitUntil(fresh.catch(function () {}));
      return hit;
    });
  });
}

self.addEventListener("fetch", function (event) {
  var req = event.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin === self.location.origin) {
    /* only this app's own files; the paper PDF and the rest of the site are not cached */
    if (url.pathname.indexOf("/ligta-s/") === -1) return;
    event.respondWith(req.mode === "navigate" ? page(event) : asset(event));
    return;
  }
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    event.respondWith(asset(event));
  }
});

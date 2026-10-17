/* MAP-A service worker: keeps a copy of the app and the website so the installed app opens without a signal.
   Pages come from the network when online, so updates show at once, and from the copy when offline.
   Bump VERSION after changing the icons or the manifest. */
var VERSION = "map-a-v6";
var PRECACHE = ["app/", "./", "manifest.webmanifest", "favicon.ico", "icons/favicon-32.png", "icons/app-favicon.ico", "icons/app-favicon-32.png", "icons/icon-192.png", "icons/apple-touch-icon.png"];

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
        return Promise.all(keys.filter(function (k) { return k.indexOf("map-a-") === 0 && k !== VERSION; })
          .map(function (k) { return caches.delete(k); }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

function keep(cache, req, res) {
  return cache.put(req, res).catch(function () {});
}

/* Pages: the network first, checked with the server every time so a new version shows at once,
   the saved copy when offline. Anything under app/ falls back to the app. */
function page(event) {
  var req = event.request;
  var home = new URL(req.url).pathname.indexOf("/app/") !== -1 ? "app/" : "./";
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

/* Icons, the manifest and the typefaces: the saved copy at once, refreshed in the background. */
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
  /* LIGTA-S and BANTA-Y have their own service workers; leave their pages alone. */
  if (/\/(ligta-s|banta-y)\//.test(new URL(req.url).pathname)) return;
  if (req.mode === "navigate") {
    event.respondWith(page(event));
    return;
  }
  var host = new URL(req.url);
  if (host.origin === self.location.origin || host.hostname === "fonts.googleapis.com" || host.hostname === "fonts.gstatic.com") {
    event.respondWith(asset(event));
  }
});

/* MAP-A Care service worker: keeps a copy of the app so it opens without a signal.
   The page comes from the network when online, so updates show at once, and from the copy when offline.
   Its caches are named "mapa-care-" so the MAP-A worker, which clears "map-a-" caches, leaves them alone.
   Bump VERSION after changing the icons or the manifest. */
var VERSION = "mapa-care-v1";
var PRECACHE = ["./", "manifest.webmanifest", "icons/favicon-32.png", "icons/icon-192.png", "icons/apple-touch-icon.png"];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(VERSION)
      .then(function (cache) { return cache.addAll(PRECACHE); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys.filter(function (k) { return k.indexOf("mapa-care-") === 0 && k !== VERSION; })
          .map(function (k) { return caches.delete(k); }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

function keep(cache, req, res) {
  return cache.put(req, res).catch(function () {});
}

function page(event) {
  var req = event.request;
  return fetch(req).then(function (res) {
    if (res.ok) {
      var copy = res.clone();
      event.waitUntil(caches.open(VERSION).then(function (cache) { return keep(cache, req, copy); }));
    }
    return res;
  }).catch(function () {
    return caches.open(VERSION).then(function (cache) {
      return cache.match(req, { ignoreSearch: true }).then(function (hit) { return hit || cache.match("./"); });
    }).then(function (hit) { return hit || Response.error(); });
  });
}

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
  if (req.mode === "navigate") {
    event.respondWith(page(event));
    return;
  }
  if (new URL(req.url).origin === self.location.origin) event.respondWith(asset(event));
});

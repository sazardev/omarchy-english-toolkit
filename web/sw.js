/* Cache-first so the reference works with no network at all, including
 * the font and the data. Bump CACHE when any of the three change. */
const CACHE = "verbs-v1";
const ASSETS = [
  "./",
  "index.html",
  "style.css",
  "app.js",
  "data/verbs.json",
  "assets/geist.ttf",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(ASSETS))
      .then(() => self.skipWaiting())
      .catch(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then((hit) => {
      if (hit) {
        // refresh in the background, but never block on the network
        fetch(e.request).then((r) => {
          if (r && r.ok) caches.open(CACHE).then((c) => c.put(e.request, r));
        }).catch(() => {});
        return hit;
      }
      return fetch(e.request)
        .then((r) => {
          if (r && r.ok) {
            const copy = r.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copy));
          }
          return r;
        })
        .catch(() => caches.match("index.html"));
    })
  );
});

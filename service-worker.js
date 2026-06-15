const CACHE_VERSION = "swiss-italy-honeymoon-guide-v20260615-mapconfig";
const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./milano_honeymoon_guide.html",
  "./manifest.webmanifest",
  "./assets/cover-pattern.svg",
  "./assets/basecamp-map.svg",
  "./assets/basecamp-map.png",
  "./assets/shopping-map.svg",
  "./assets/shopping-map.png",
  "./assets/map-data.json"
];

const GUIDE_URL = "./milano_honeymoon_guide.html";
const SECRET_CONFIG_RE = /\/assets\/google-maps-config(?:\.local)?\.(?:json|js)$/;

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION)
          .map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

function isSameOrigin(requestUrl) {
  return requestUrl.origin === self.location.origin;
}

async function networkFirstNavigation(request) {
  try {
    const response = await fetch(request);
    if (response && response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cachedGuide = await caches.match(GUIDE_URL);
    if (cachedGuide) return cachedGuide;
    const cachedIndex = await caches.match("./index.html");
    if (cachedIndex) return cachedIndex;
    throw new Error("offline-navigation-cache-miss");
  }
}

async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);
  const fetchPromise = fetch(request)
    .then((response) => {
      if (response && response.ok) {
        const copy = response.clone();
        caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
      }
      return response;
    })
    .catch(() => {
      return null;
    });

  if (cached) return cached;

  const response = await fetchPromise;
  if (response) return response;
  throw new Error("offline-cache-miss");
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const requestUrl = new URL(request.url);
  if (!isSameOrigin(requestUrl)) return;

  if (SECRET_CONFIG_RE.test(requestUrl.pathname)) {
    event.respondWith(fetch(request));
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(networkFirstNavigation(request));
    return;
  }

  event.respondWith(staleWhileRevalidate(request));
});

// Service Worker for 医学研究热点图谱 - Cache First Strategy
const CACHE_NAME = 'med-hotspot-v2';
const ASSETS_TO_CACHE = [
  '/medical-bibliometrics-hotspot/',
  '/medical-bibliometrics-hotspot/index.html',
  '/medical-bibliometrics-hotspot/manifest.json',
  '/medical-bibliometrics-hotspot/data.json',
  '/medical-bibliometrics-hotspot/icons/favicon.svg',
  '/medical-bibliometrics-hotspot/icons/icon-192.png',
  '/medical-bibliometrics-hotspot/icons/icon-512.png',
  '/medical-bibliometrics-hotspot/icons/apple-touch-icon.png',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap'
];

// Install: pre-cache all assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('SW: Pre-cache failed for some assets:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch: cache-first with network fallback
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip chrome-extension and other non-http requests
  const url = new URL(event.request.url);
  if (!url.protocol.startsWith('http')) return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) {
        // Return cached, update in background
        fetchAndCache(event.request, CACHE_NAME);
        return cached;
      }
      return fetchAndCache(event.request, CACHE_NAME);
    })
  );
});

function fetchAndCache(request, cacheName) {
  return fetch(request).then((response) => {
    if (!response || response.status !== 200 || response.type !== 'basic') {
      return response;
    }
    const clone = response.clone();
    caches.open(cacheName).then((cache) => {
      cache.put(request, clone);
    });
    return response;
  }).catch(() => {
    // Offline fallback - return cached index for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/medical-bibliometrics-hotspot/');
    }
    return new Response('Offline', { status: 503 });
  });
}

/// <reference lib="webworker" />

// This service worker is meant to run in a worker context, not in the browser window
// eslint-disable-next-line no-restricted-globals
const workerSelf = self as unknown as ServiceWorkerGlobalScope;

const CACHE_NAME = 'ade-platform-v1';
const STATIC_ASSETS = [
  '/static/js/main.js',
  '/static/css/styles.css',
  '/api/ai/models',
  '/manifest.json',
  '/favicon.ico'
];

// Performance tracking function
const trackPerformance = (metricName: string, value: number) => {
  workerSelf.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage({
        type: 'PERFORMANCE_METRIC',
        metric: {
          name: metricName,
          value,
          timestamp: Date.now()
        }
      });
    });
  });
};

// Install event - cache static assets
workerSelf.addEventListener('install', (event) => {
  const startTime = performance.now();
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).then(() => {
        const duration = performance.now() - startTime;
        trackPerformance('sw-install', duration);
      });
    })
  );
});

// Activate event - clean up old caches
workerSelf.addEventListener('activate', (event) => {
  const startTime = performance.now();

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      ).then(() => {
        const duration = performance.now() - startTime;
        trackPerformance('sw-activate', duration);
      });
    })
  );
});

// Fetch event - serve from cache, falling back to network
workerSelf.addEventListener('fetch', (event) => {
  const startTime = performance.now();

  // Skip cross-origin requests
  if (!event.request.url.startsWith(workerSelf.location.origin)) {
    return;
  }

  // API requests - network first, then cache
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
          const duration = performance.now() - startTime;
          trackPerformance('sw-api-fetch', duration);
          return response;
        })
        .catch(() => {
          return caches.match(event.request).then(response => {
            const duration = performance.now() - startTime;
            if (response) {
              trackPerformance('sw-api-cache-hit', duration);
            } else {
              trackPerformance('sw-api-cache-miss', duration);
            }
            return response;
          });
        })
    );
    return;
  }

  // Static assets - cache first, then network
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        const duration = performance.now() - startTime;
        trackPerformance('sw-cache-hit', duration);
        return response;
      }

      return fetch(event.request).then((response) => {
        // Don't cache non-successful responses
        if (!response || response.status !== 200 || response.type !== 'basic') {
          const duration = performance.now() - startTime;
          trackPerformance('sw-fetch-error', duration);
          return response;
        }

        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone);
        });

        const duration = performance.now() - startTime;
        trackPerformance('sw-network-fetch', duration);
        return response;
      });
    })
  );
});

// Handle messages from clients
workerSelf.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    workerSelf.skipWaiting();
  }
});
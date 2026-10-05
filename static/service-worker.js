// Service Worker для weather-msk
// Кэширует статику и страницы, обеспечивает офлайн-режим.

const CACHE_NAME = "weather-msk-v1";
const STATIC_CACHE = "weather-msk-static-v1";

// Страницы и ресурсы для предварительного кэширования
const PRECACHE_URLS = [
  "/",
  "/forecast",
  "/synoptic-maps",
  "/climate",
  "/theory",
  "/bibliography",
  "/static/leaflet/leaflet.css",
  "/static/leaflet/leaflet.js",
  "/static/manifest.json",
];

// Установка — предзагрузка
self.addEventListener("install", function(event) {
  console.log("[SW] install");
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE_URLS.map(function(url) {
        return new Request(url, { credentials: "same-origin" });
      })).catch(function(err) {
        console.warn("[SW] некоторые URL не закэшированы:", err);
      });
    }).then(function() {
      return self.skipWaiting();
    })
  );
});

// Активация — чистка старых кэшей
self.addEventListener("activate", function(event) {
  console.log("[SW] activate");
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(
        names.map(function(name) {
          if (name !== CACHE_NAME && name !== STATIC_CACHE) {
            console.log("[SW] удаляю старый кэш:", name);
            return caches.delete(name);
          }
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Перехват запросов
self.addEventListener("fetch", function(event) {
  var url = new URL(event.request.url);

  // Запросы к API — всегда сеть (свежие данные)
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(event.request).catch(function() {
        return new Response(JSON.stringify({ error: "offline" }), {
          headers: { "Content-Type": "application/json" }
        });
      })
    );
    return;
  }

  // Только GET
  if (event.request.method !== "GET") {
    return;
  }

  // Статика (leaflet, иконки, manifest) — cache-first
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        return cached || fetch(event.request).then(function(resp) {
          if (resp.status === 200) {
            var respClone = resp.clone();
            caches.open(STATIC_CACHE).then(function(cache) {
              cache.put(event.request, respClone);
            });
          }
          return resp;
        });
      })
    );
    return;
  }

  // Страницы — network-first с fallback на кэш
  event.respondWith(
    fetch(event.request).then(function(resp) {
      if (resp.status === 200) {
        var respClone = resp.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, respClone);
        });
      }
      return resp;
    }).catch(function() {
      return caches.match(event.request).then(function(cached) {
        if (cached) return cached;
        // Если нет в кэше — показываем заглушку
        return caches.match("/").then(function(home) {
          return home || new Response(
            "<h1>Нет соединения</h1><p>Проверьте интернет.</p>",
            { headers: { "Content-Type": "text/html; charset=utf-8" } }
          );
        });
      });
    })
  );
});

// Push-уведомления (заготовка)
self.addEventListener("push", function(event) {
  var data = { title: "Weather-msk", body: "Новое обновление" };
  if (event.data) {
    try { data = event.data.json(); } catch (e) {}
  }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/static/icons/icon-192.png",
      badge: "/static/icons/icon-192.png",
    })
  );
});

// Клик по уведомлению — открываем приложение
self.addEventListener("notificationclick", function(event) {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window" }).then(function(clientList) {
      for (var i = 0; i < clientList.length; i++) {
        if (clientList[i].url && "focus" in clientList[i]) {
          return clientList[i].focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow("/");
      }
    })
  );
});

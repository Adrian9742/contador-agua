// Service Worker — Contador de Água
// Cache básico para funcionamento offline parcial

const CACHE = "agua-v1"
const ASSETS = [
  "/",
  "/auth",
  "/icon.svg",
  "/icon-dark-32x32.png",
  "/icon-light-32x32.png",
  "/apple-icon.png",
]

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS))
  )
  self.skipWaiting()
})

self.addEventListener("activate", (event) => {
  event.waitUntil(clients.claim())
})

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => {
      // Tenta rede primeiro, fallback pra cache
      return fetch(event.request)
        .then((res) => {
          // Atualiza cache com resposta nova
          const clone = res.clone()
          caches.open(CACHE).then((cache) => cache.put(event.request, clone))
          return res
        })
        .catch(() => cached || new Response("Offline", { status: 503 }))
    })
  )
})

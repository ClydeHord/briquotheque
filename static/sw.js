/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
/* Briquothèque — mode hors ligne.
   Pages, scripts et données : réseau d'abord, sinon dernière copie sur l'appareil.
   Images : copie sur l'appareil d'abord. Une photo personnelle ne change jamais (son adresse est son contenu) ; une image du
   catalogue peut changer de source sur le serveur : sa copie est relue en fond quand elle a plus de 30 jours. */
const SHELL = "bq-shell-v2", DATA = "bq-data-v2", IMGS = "bq-img-v3";   // (bq-img-v3, 16/11/2026 : les copies d'images gardées jusque-là sont effacées et refaites)
const IMG_RECHECK = 30 * 86400e3;   // image du catalogue gardée depuis plus de 30 jours : relue en fond (sa source a pu changer sur le serveur)
const SHELL_FILES = ["/", "/app.js", "/style.css", "/flags.woff2", "/manifest.json", "/icon.svg", "/fig-head.svg", "/bo.js", "/bo-plus.js", "/bo-max.js"];   // (bo*.js : personnalisation du back office, gardée aussi hors ligne)
const NET_TIMEOUT = 6000;   // serveur injoignable sans erreur immédiate (mobile) : on bascule sur la copie
/* serveur éteint derrière le proxy (nginx) : le proxy répond lui-même 502 / 503 / 504, sans la signature X-Bq de l'appli → traité comme une coupure */
const proxyDown = r => r && typeof r === "object" && r.status >= 500 && !r.headers.get("X-Bq");

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(SHELL);
    for (const u of SHELL_FILES) {
      try { const r = await fetch(u, { cache: "no-store" }); if (r.ok && !r.redirected) await c.put(u, r); } catch {}
    }
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (![SHELL, DATA, IMGS].includes(k)) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener("message", e => {   // déconnexion : on efface les copies
  if (e.data === "clear") e.waitUntil(Promise.all([SHELL, DATA, IMGS].map(k => caches.delete(k))));
});

async function fromCache(req, cacheName, key, flag = "X-From-Cache") {
  const hit = await (await caches.open(cacheName)).match(key || req);
  if (!hit) return null;
  const h = new Headers(hit.headers); h.set(flag, "1");   // X-From-Cache : hors ligne ; X-Cache-Slow : serveur lent (pas une coupure)
  return new Response(await hit.blob(), { status: hit.status, statusText: hit.statusText, headers: h });
}

/* réseau d'abord. Serveur LENT (> 6 s) : la copie s'il y en a une, sans signaler de coupure, sinon on attend la réponse.
   Réseau EN ÉCHEC (vraie coupure) : la copie, sinon « hors ligne ». */
async function networkFirst(req, cacheName, key) {
  const keep = r => { if (r && r.ok && !r.redirected) { const copy = r.clone(); caches.open(cacheName).then(c => c.put(key || req, copy)); } return r; };
  const net = fetch(req);
  let r;
  try { r = await Promise.race([net, new Promise(res => setTimeout(() => res("slow"), NET_TIMEOUT))]); } catch { r = null; }
  if (proxyDown(r)) r = null;
  if (r === "slow") {
    const c = await fromCache(req, cacheName, key, "X-Cache-Slow");
    if (c) { net.then(keep).catch(() => {}); return c; }   // la vraie réponse remplacera la copie pour la prochaine fois
    try { r = await net; } catch { r = null; }
    if (proxyDown(r)) r = null;
  }
  if (r) return keep(r);
  const c = await fromCache(req, cacheName, key);
  if (c) return c;
  if (req.mode === "navigate") { const sh = await fromCache(req, SHELL, "/"); if (sh) return sh; }
  return new Response(JSON.stringify({ erreur: "Hors ligne : donnée pas encore disponible sur cet appareil" }),
    { status: 503, headers: { "Content-Type": "application/json; charset=utf-8", "X-Offline": "1" } });
}

async function cacheFirst(req, e) {   // e (image du catalogue) : la vieille copie est rendue tout de suite, puis relue en fond pour la prochaine fois
  const c = await caches.open(IMGS);
  const hit = await c.match(req);
  if (hit) {
    const d = e ? Date.parse(hit.headers.get("date") || "") : 0;
    if (d && Date.now() - d > IMG_RECHECK) e.waitUntil(fetch(req.url, { cache: "reload" })
      .then(r => r.ok && !r.redirected && /^image\//.test(r.headers.get("content-type") || "") ? c.put(req, r) : null).catch(() => {}));
    return hit;
  }
  try {
    const r = await fetch(req);
    if (r.ok || r.type === "opaque") c.put(req, r.clone());
    return r;
  } catch { return new Response("", { status: 504 }); }
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;   // modifications : toujours le réseau
  const u = new URL(req.url);
  if (u.origin !== location.origin) {   // photos Rebrickable
    if (u.hostname === "cdn.rebrickable.com") e.respondWith(cacheFirst(req));
    return;
  }
  const p = u.pathname;
  if (p.startsWith("/api/docs") || p === "/api/ping" || p === "/api/refresh" || p === "/sw.js" || p === "/login" || p.startsWith("/wishlist") || p.startsWith("/collection")
    || p.startsWith("/api/bo/") || p.startsWith("/backoffice") || p.startsWith("/admin") || p.startsWith("/p/") || p.startsWith("/bo-img/")) return;   // (back office : jamais de copie hors ligne)
  if (p === "/api/img") return e.respondWith(cacheFirst(req, e));
  if (p.startsWith("/api/upload/")) return e.respondWith(cacheFirst(req));
  if (p.startsWith("/api/")) return e.respondWith(networkFirst(req, DATA));
  if (req.mode === "navigate") { if (p === "/") e.respondWith(networkFirst(req, SHELL, "/")); return; }   // seule la page de l'appli est gardée pour le hors-ligne (une autre page visitée ne prend pas sa place)
  if (SHELL_FILES.includes(p)) return e.respondWith(networkFirst(req, SHELL));
});
try { importScripts("/perso-sw.js"); } catch {}   /* (extensions locales, facultatives ; absentes : rien) */

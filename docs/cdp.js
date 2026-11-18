/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
// Client minimal du protocole Chrome DevTools (WebSocket écrit à la main) : Node 20, aucune dépendance.
// Sert à la documentation : captures d'écran de la démo (captures.js, captures_bo.js).
const http = require("http"), crypto = require("crypto"), { spawn } = require("child_process"), os = require("os"), path = require("path");

/* GET http → JSON (adresse du WebSocket de Chromium) */
function getJSON(url) {
  return new Promise((ok, ko) => http.get(url, r => { let d = ""; r.on("data", c => d += c); r.on("end", () => { try { ok(JSON.parse(d)); } catch (e) { ko(e); } }); }).on("error", ko));
}

/* Connexion WebSocket au navigateur : send(méthode, paramètres, session) → promesse du résultat ; on(f) : événements */
function connect(wsUrl) {
  const u = new URL(wsUrl);
  return new Promise((ok, ko) => {
    const key = crypto.randomBytes(16).toString("base64");
    const req = http.request({ host: u.hostname, port: u.port, path: u.pathname, headers: { Connection: "Upgrade", Upgrade: "websocket", "Sec-WebSocket-Key": key, "Sec-WebSocket-Version": "13" } });
    req.on("upgrade", (res, sock) => {
      let buf = Buffer.alloc(0), id = 0; const pending = new Map(), listeners = [];
      sock.on("data", d => {   // trames reçues (texte seulement) : réponses aux appels, ou événements
        buf = Buffer.concat([buf, d]);
        for (;;) {
          if (buf.length < 2) return;
          let len = buf[1] & 127, off = 2;
          if (len === 126) { if (buf.length < 4) return; len = buf.readUInt16BE(2); off = 4; }
          else if (len === 127) { if (buf.length < 10) return; len = Number(buf.readBigUInt64BE(2)); off = 10; }
          if (buf.length < off + len) return;
          const op = buf[0] & 15, payload = buf.slice(off, off + len); buf = buf.slice(off + len);
          if (op !== 1) continue;
          const msg = JSON.parse(payload.toString());
          if (msg.id && pending.has(msg.id)) { const p = pending.get(msg.id); pending.delete(msg.id); msg.error ? p.ko(new Error(msg.error.message)) : p.ok(msg.result); }
          else listeners.forEach(f => f(msg));
        }
      });
      const send = (method, params = {}, sessionId) => new Promise((ok2, ko2) => {   // trame masquée (obligatoire côté client)
        const mid = ++id; pending.set(mid, { ok: ok2, ko: ko2 });
        const data = Buffer.from(JSON.stringify({ id: mid, method, params, ...(sessionId ? { sessionId } : {}) }));
        const mask = crypto.randomBytes(4); let head;
        if (data.length < 126) head = Buffer.from([0x81, 0x80 | data.length]);
        else if (data.length < 65536) { head = Buffer.alloc(4); head[0] = 0x81; head[1] = 0x80 | 126; head.writeUInt16BE(data.length, 2); }
        else { head = Buffer.alloc(10); head[0] = 0x81; head[1] = 0x80 | 127; head.writeBigUInt64BE(BigInt(data.length), 2); }
        const masked = Buffer.alloc(data.length); for (let i = 0; i < data.length; i++) masked[i] = data[i] ^ mask[i % 4];
        sock.write(Buffer.concat([head, mask, masked]));
      });
      ok({ send, on: f => listeners.push(f), close: () => sock.destroy() });
    });
    req.on("error", ko); req.end();
  });
}

/* Lance Chromium sans fenêtre (profil temporaire) ; renvoie le processus et l'adresse de débogage */
async function launch(port = 9344) {
  const dir = path.join(os.tmpdir(), "bq-docs-chrome");
  const bin = process.env.CHROMIUM || "chromium";
  const proc = spawn(bin, ["--headless=new", "--no-sandbox", "--disable-gpu", `--remote-debugging-port=${port}`, `--user-data-dir=${dir}`,
    "--hide-scrollbars", "--lang=fr-FR", "about:blank"], { stdio: "ignore" });
  for (let k = 0; k < 50; k++) { try { const v = await getJSON(`http://127.0.0.1:${port}/json/version`); return { proc, ws: v.webSocketDebuggerUrl }; } catch { await new Promise(r => setTimeout(r, 200)); } }
  throw new Error("Chromium ne démarre pas");
}

/* Ouvre un onglet ; renvoie S(méthode, paramètres) lié à cet onglet */
async function tab(b) {
  const { targetId } = await b.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await b.send("Target.attachToTarget", { targetId, flatten: true });
  return (m, p) => b.send(m, p, sessionId);
}
module.exports = { launch, connect, tab };

# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Briquothèque — BACK OFFICE : accès (mot de passe à part, sessions, page d'entrée).

Le back office (/backoffice) a SON mot de passe, distinct de celui de l'application :
  - il se crée à la première visite (il faut être connecté à la Briquothèque ce jour-là), avec les avertissements d'usage ;
  - il ouvre aussi l'application (c'est la clé maîtresse : le back office peut changer le mot de passe de la Briquothèque) ;
  - perdu, il ne se retrouve pas : il faut supprimer data/backoffice_auth.json sur le serveur, puis refaire la première visite.

Fichier : data/backoffice_auth.json  {salt, hash, created, changed, seen, sessions: {empreinte du jeton: fin}, remote_tools}
  (même calcul d'empreinte que auth.py : PBKDF2-SHA256, 200 000 tours — le mot de passe lui-même n'est écrit nulle part).
Cookie : « <cookie de l'appli>_office », HttpOnly, SameSite=Strict (jamais envoyé depuis un autre site), Secure en HTTPS.
Essais ratés : comptés avec ceux de l'application (auth.record_failure : blocage 15 min, bannissement d'une adresse publique).
"""
import hashlib
import hmac
import json
import os
import secrets
import threading
import time

_lock = threading.RLock()
_srv = None            # le module server (donné par init)
FILE = "backoffice_auth.json"
SESSION_HOURS = 12     # session ordinaire
REMEMBER_DAYS = 30     # « Rester connecté sur cet ordinateur »
MIN_LEN = 10           # longueur minimale d'un mot de passe


def init(srv):
    global _srv
    _srv = srv


def _path():
    return os.path.join(_srv.DATA, FILE)


def _read():
    try:
        with open(_path(), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _write(d):
    tmp = _path() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    os.chmod(tmp, 0o600)
    os.replace(tmp, _path())


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()


def _journal(action, detail=""):
    try:
        _srv.backoffice_outils.journal(action, detail)
    except Exception:
        pass


def configured():
    d = _read()
    return isinstance(d.get("hash"), str) and isinstance(d.get("salt"), str) and bool(d["hash"]) and bool(d["salt"])


def set_password(password):
    """Nouveau mot de passe du back office : toutes ses sessions sont fermées."""
    salt = secrets.token_hex(16)
    with _lock:
        d, now = _read(), int(time.time())
        d.update({"salt": salt, "hash": _hash(password, salt), "changed": now, "sessions": {}})
        d.setdefault("created", now)
        _write(d)


def adopt_app_password():
    """Le back office prend le mot de passe de l'application (même empreinte, sans le connaître)."""
    a = _srv.auth._read()
    if not isinstance(a.get("hash"), str) or not isinstance(a.get("salt"), str):
        return False
    with _lock:
        d, now = _read(), int(time.time())
        d.update({"salt": a["salt"], "hash": a["hash"], "changed": now, "sessions": {}})
        d.setdefault("created", now)
        _write(d)
    return True


def check(password):
    d = _read()
    try:
        return configured() and isinstance(password, str) and hmac.compare_digest(_hash(password, d["salt"]), d["hash"])
    except (ValueError, TypeError):   # fichier abîmé, texte impossible à encoder : refusé, jamais d'erreur
        return False


def _app_check(password):
    try:
        return isinstance(password, str) and _srv.auth.check_password(password)
    except (ValueError, TypeError):
        return False


def _sessions(d):
    s = d.get("sessions")
    now = time.time()
    return {k: v for k, v in s.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and v > now} if isinstance(s, dict) else {}


def new_session(remember=False):
    token = secrets.token_urlsafe(32)
    with _lock:
        d = _read()
        s = _sessions(d)
        s[hashlib.sha256(token.encode()).hexdigest()] = time.time() + (REMEMBER_DAYS * 86400 if remember else SESSION_HOURS * 3600)
        d["sessions"] = s
        _write(d)
    return token


def valid(token):
    if not token or not isinstance(token, str):
        return False
    return hashlib.sha256(token.encode("utf-8", "replace")).hexdigest() in _sessions(_read())


def end(token):
    if not token:
        return
    with _lock:
        d = _read()
        s = _sessions(d)
        s.pop(hashlib.sha256(token.encode("utf-8", "replace")).hexdigest(), None)
        d["sessions"] = s
        _write(d)


def cookie_name():
    return _srv.auth.COOKIE + "_office"


def token_of(h):
    name = cookie_name()
    for part in (h.headers.get("Cookie") or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k == name:
            return v
    return None


def logged(h):
    """La requête porte-t-elle une session valide du back office ?"""
    return valid(token_of(h))


def cookie(token, clear=False, remember=False, secure=False):
    sec = "; Secure" if secure else ""
    if clear:
        return f"{cookie_name()}=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict{sec}"
    age = f"; Max-Age={REMEMBER_DAYS * 86400}" if remember else ""
    return f"{cookie_name()}={token}; Path=/{age}; HttpOnly; SameSite=Strict{sec}"


def remote_tools():
    """Outils sensibles (code, fichiers bruts, démarrage, secours) permis hors du réseau local ? (réglé dans « Mots de passe et sécurité »)"""
    return _read().get("remote_tools") is True


def info(h):
    """État de l'accès, pour la page d'entrée et la rubrique « Mots de passe et sécurité »."""
    d, lg = _read(), logged(h)
    o = {"configured": configured(), "logged": lg, "app": _srv.auth.valid_session(h.token()), "min": MIN_LEN}
    if lg:
        o.update({"seen": bool(d.get("seen")), "created": d.get("created") or 0, "changed": d.get("changed") or 0, "remote_tools": remote_tools(),
                  "local": _srv.backoffice_outils.local_only(h), "sessions": len(_sessions(d)),
                  "same": bool(d.get("hash")) and d.get("hash") == _srv.auth._read().get("hash"),
                  "session_hours": SESSION_HOURS, "remember_days": REMEMBER_DAYS})
    return o


def entry(h):
    """Ce que /backoffice doit montrer : ("admin", None) → l'écran du back office ; ("page", octets) → la page d'entrée."""
    d = _read()
    if not configured():
        state = "setup" if _srv.auth.valid_session(h.token()) else "need-app"
    elif not logged(h):
        state = "login"
    elif not d.get("seen"):
        state = "welcome"
    else:
        return "admin", None
    st = json.dumps({"state": state, "min": MIN_LEN, "hours": SESSION_HOURS, "days": REMEMBER_DAYS})
    return "page", ENTRY.replace("__STATE__", st.replace("</", "<\\/")).encode("utf-8")


def api(h, method, name, b):
    """Routes /api/bo/acces (GET) et /api/bo/login | setup | logout | compris | password | app-password | options (POST)."""
    A, ip = _srv.auth, h.client_ip()
    b = b if isinstance(b, dict) else {}
    text = lambda k: b.get(k) if isinstance(b.get(k), str) else ""

    def out(obj, status=200, cookies=()):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        h.send_response(status)
        h.send_header("Content-Type", "application/json; charset=utf-8")
        for c in cookies:
            h.send_header("Set-Cookie", c)
        h.send_header("Cache-Control", "no-store")
        h.send_header("Content-Length", str(len(body)))
        h.end_headers()
        h.wfile.write(body)

    def refuse(msg, status=400, **more):
        out({"erreur": msg, **more}, status)

    def failed(what, msg, status=403):   # mot de passe faux : compté (blocage, bannissement), réponse ralentie
        A.record_failure(ip, what)
        time.sleep(1)
        _journal("refusé", what)
        refuse(msg, status)

    if name == "acces" and method == "GET":
        return out(info(h))
    if method != "POST":
        return refuse("Introuvable", 404)
    if name in ("login", "setup", "password", "app-password") and A.too_many_attempts(ip):
        return refuse("Trop de tentatives. Réessayer dans 15 minutes.", 429)
    if name == "login":   # {password, remember}
        if not configured():
            return refuse("Le mot de passe du back office n'est pas encore créé : ouvrir /backoffice", 409)
        if not check(text("password")):
            return failed("mot de passe du back office", "Mot de passe incorrect", 401)
        A.clear_failures(ip)
        remember = b.get("remember") is True
        cookies = [cookie(new_session(remember), remember=remember, secure=h.is_https())]
        if not A.valid_session(h.token()):   # ce mot de passe ouvre aussi l'application (l'aperçu du back office en a besoin)
            cookies.append(A.cookie_header(A.new_session(False), remember=False, secure=h.is_https()))
        _journal("connexion au back office")
        return out({"ok": True, "seen": bool(_read().get("seen"))}, cookies=cookies)
    if name == "setup":   # {password, same, compris} : première visite — il faut être connecté à l'application
        if configured():
            return refuse("Le mot de passe du back office existe déjà", 403)
        if not A.valid_session(h.token()):
            return refuse("Connexion à la Briquothèque d'abord", 401)
        if b.get("compris") is not True:
            return refuse("Cocher d'abord « J'ai lu et compris ».")
        pw = text("password")
        if b.get("same") is True:   # le même que celui de l'application : on le redemande, puis on reprend son empreinte
            if not _app_check(pw):
                return failed("mot de passe (création du back office)", "Ce n'est pas le mot de passe de la Briquothèque")
            adopt_app_password()
        else:
            if len(pw) < MIN_LEN:
                return refuse(f"Le mot de passe doit faire au moins {MIN_LEN} caractères")
            try:
                set_password(pw)
            except (ValueError, TypeError):
                return refuse("Ce mot de passe contient des caractères inutilisables")
        with _lock:
            d = _read()
            d["seen"] = int(time.time())
            _write(d)
        _journal("mot de passe du back office créé")
        return out({"ok": True}, cookies=[cookie(new_session(False), secure=h.is_https())])
    if not logged(h):
        return refuse("Connexion au back office requise", 401, besoin="bo")
    if name == "logout":
        end(token_of(h))
        return out({"ok": True}, cookies=[cookie("", clear=True, secure=h.is_https())])
    if name == "compris":   # les avertissements de la première entrée ont été lus
        with _lock:
            d = _read()
            d["seen"] = int(time.time())
            _write(d)
        return out({"ok": True})
    if name == "password":   # {current, new} : changer le mot de passe du back office
        if not check(text("current")):
            return failed("mot de passe actuel du back office", "Mot de passe actuel du back office incorrect")
        new = text("new")
        if len(new) < MIN_LEN:
            return refuse(f"Le nouveau mot de passe doit faire au moins {MIN_LEN} caractères")
        try:
            set_password(new)   # ferme toutes les sessions du back office…
        except (ValueError, TypeError):
            return refuse("Ce mot de passe contient des caractères inutilisables")
        _journal("mot de passe du back office changé")
        return out({"ok": True}, cookies=[cookie(new_session(False), secure=h.is_https())])   # …sauf celle-ci, rouverte
    if name == "app-password":   # {bo, new} : changer le mot de passe de l'APPLICATION, sans connaître l'ancien (secours)
        if not check(text("bo")):
            return failed("mot de passe du back office (changement de celui de l'appli)", "Mot de passe du back office incorrect")
        new = text("new")
        if len(new) < MIN_LEN:
            return refuse(f"Le nouveau mot de passe doit faire au moins {MIN_LEN} caractères")
        try:
            A.set_password(new)   # ferme toutes les sessions de l'application (tous les appareils devront se reconnecter)
        except (ValueError, TypeError):
            return refuse("Ce mot de passe contient des caractères inutilisables")
        _journal("mot de passe de l'application changé depuis le back office")
        return out({"ok": True}, cookies=[A.cookie_header(A.new_session(False), remember=False, secure=h.is_https())])
    if name == "options":   # {remote_tools: oui/non} (depuis le réseau local seulement) · {logout_all: true}
        cookies = []
        if "remote_tools" in b:
            if not _srv.backoffice_outils.local_only(h):
                return refuse("Ce réglage ne se change que depuis le réseau local (à la maison) : c'est lui qui protège le serveur depuis Internet.", 403)
            with _lock:
                d = _read()
                d["remote_tools"] = b.get("remote_tools") is True
                _write(d)
            _journal("outils sensibles depuis Internet", "permis" if b.get("remote_tools") is True else "interdits")
        if b.get("logout_all") is True:   # fermer toutes les sessions du back office (les autres appareils) ; celle-ci est rouverte
            with _lock:
                d = _read()
                d["sessions"] = {}
                _write(d)
            cookies = [cookie(new_session(False), secure=h.is_https())]
            _journal("sessions du back office fermées")
        if cookies:   # la réponse décrit l'état APRÈS (la session vient d'être rouverte)
            return out({**info(h), "logged": True, "sessions": 1, "remote_tools": remote_tools(), "seen": True,
                        "local": _srv.backoffice_outils.local_only(h)}, cookies=cookies)
        return out(info(h))
    return refuse("Introuvable", 404)


# Page d'entrée du back office : écrite ici (aucun fichier de static/ n'est nécessaire — elle marche même si l'écran est cassé).
ENTRY = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Back office — Briquothèque</title>
<style>
:root{--bg:#f4f5f7;--panel:#fff;--ink:#1b1d22;--muted:#6b7280;--line:#e4e6eb;--red:#d01012;--warn:#fff7e0;--warn-b:#f2c94c}
@media (prefers-color-scheme:dark){:root{--bg:#14161b;--panel:#1c1f26;--ink:#f1f2f4;--muted:#9aa1ad;--line:#2c313b;--warn:#3a3118;--warn-b:#8a6d1a}}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:18px;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{width:min(560px,100%);background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:26px 26px 22px;box-shadow:0 10px 30px rgba(0,0,0,.08)}
h1{font-size:22px;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 16px}
.warn{background:var(--warn);border:1px solid var(--warn-b);border-radius:12px;padding:12px 14px;margin:0 0 12px}.warn b{display:block;margin-bottom:2px}
.warn ul{margin:6px 0 0;padding-left:20px}.warn li{margin:3px 0}
label{display:block;font-weight:600;margin:12px 0 4px}input[type=password],input[type=text]{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);font:inherit}
.chk{display:flex;gap:9px;align-items:flex-start;font-weight:500;margin:12px 0 0}.chk input{margin-top:4px;width:17px;height:17px;flex:none}
button,.btn{display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:10px;padding:11px 16px;font:inherit;font-weight:700;cursor:pointer;text-decoration:none}
button.primary{background:var(--red);border-color:var(--red);color:#fff;width:100%;margin-top:16px}button:disabled{opacity:.55;cursor:default}
.msg{min-height:22px;margin:10px 0 0;color:var(--red);font-weight:600}.foot{display:flex;gap:10px;justify-content:space-between;flex-wrap:wrap;margin-top:16px;font-size:13.5px}
.foot a{color:var(--muted)}.hint{color:var(--muted);font-size:13.5px;margin:4px 0 0}[hidden]{display:none!important}
.tabs{display:flex;gap:8px;margin:14px 0 0}.tabs button{flex:1;font-weight:600;padding:9px 10px}.tabs button.on{border-color:var(--red);color:var(--red)}
</style></head><body><main>
<h1>🛠 Back office</h1><p class="sub">Briquothèque — personnaliser et réparer l'application, sans code.</p>
<div class="warn" id="device" hidden><b>📱 Écran trop petit</b>Le back office est pensé pour un <b style="display:inline">ordinateur</b> (grand écran, souris).
Sur tablette ou téléphone il est <b style="display:inline">déconseillé</b> : « cliquer pour modifier » et « déplacer à la souris » y sont peu pratiques, et les panneaux sont à l'étroit.</div>
<div id="box"></div>
<p class="msg" id="msg" role="alert"></p>
<div class="foot"><a href="/">← Retour à la Briquothèque</a><a href="/backoffice/secours">Secours (code de l'application)</a></div>
</main>
<script>
const S = __STATE__, $ = s => document.querySelector(s), box = $("#box"), msg = $("#msg");
if (matchMedia("(max-width: 900px)").matches || /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || (navigator.maxTouchPoints > 1 && innerWidth < 1100)) $("#device").hidden = false;
const WARN = `<div class="warn"><b>⚠️ Ici, les entrailles de la Briquothèque.</b>
<ul><li>Tout ce qui se règle ici change <b style="display:inline">réellement</b> le site (apparence, fiches, données, et même le code) : à manier avec prudence.
Les réglages d'apparence passent par un brouillon et se publient ; les outils du serveur agissent tout de suite.</li>
<li>Avant un gros changement : <b style="display:inline">Sauvegardes → Créer une sauvegarde</b>. En cas de souci d'affichage, ajouter <code>?bo=off</code> à l'adresse du site.</li></ul></div>
<div class="warn"><b>🔑 Le mot de passe du back office ne doit surtout pas se perdre.</b>Il ne peut pas être retrouvé depuis l'application.
S'il est perdu, il faudra supprimer le fichier <code>data/backoffice_auth.json</code> sur le serveur (accès aux fichiers nécessaire), puis revenir ici en créer un nouveau. À noter en lieu sûr.</div>
<div class="warn"><b>🖥️ Optimisé pour ordinateur.</b>Tablette et téléphone sont déconseillés.</div>`;
async function post(name, body) {
  const r = await fetch("/api/bo/" + name, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.erreur || "Erreur " + r.status);
  return d;
}
const go = () => location.replace("/backoffice");
function run(btn, fn) { return async e => { e && e.preventDefault(); msg.textContent = ""; btn.disabled = true; try { await fn(); } catch (err) { msg.textContent = err.message; btn.disabled = false; } }; }
if (S.state === "need-app") {
  box.innerHTML = `<p>Le back office n'a pas encore de mot de passe. Pour le créer, <b>se connecter d'abord à la Briquothèque</b>, puis revenir ici.</p><a class="btn" href="/login">Se connecter à la Briquothèque</a>`;
} else if (S.state === "setup") {
  let same = false;
  box.innerHTML = `<p><b>Première visite :</b> choisir le mot de passe du back office.</p>` + WARN + `
    <div class="tabs"><button type="button" id="tNew" class="on">Un mot de passe à part</button><button type="button" id="tSame">Le même que la Briquothèque</button></div>
    <form id="f"><div id="pNew"><label for="p1">Mot de passe du back office (${S.min} caractères au moins)</label><input type="password" id="p1" autocomplete="new-password">
      <label for="p2">Le même, une seconde fois</label><input type="password" id="p2" autocomplete="new-password"></div>
      <div id="pSame" hidden><label for="p3">Le mot de passe de la Briquothèque (pour confirmer)</label><input type="password" id="p3" autocomplete="current-password">
      <p class="hint">Le back office s'ouvrira avec ce même mot de passe, modifiable ensuite dans « Mots de passe et sécurité ».</p></div>
      <label class="chk"><input type="checkbox" id="ok"><span>J'ai lu et compris : c'est à manier avec prudence, et je ne dois pas perdre ce mot de passe.</span></label>
      <button class="primary" id="b">Créer le mot de passe et entrer</button></form>`;
  const tab = s => { same = s; $("#tNew").classList.toggle("on", !s); $("#tSame").classList.toggle("on", s); $("#pNew").hidden = s; $("#pSame").hidden = !s; msg.textContent = ""; };
  $("#tNew").onclick = () => tab(false); $("#tSame").onclick = () => tab(true);
  $("#f").onsubmit = run($("#b"), async () => {
    if (!$("#ok").checked) throw new Error("Cocher d'abord « J'ai lu et compris ».");
    if (!same) { if ($("#p1").value.length < S.min) throw new Error("Le mot de passe doit faire au moins " + S.min + " caractères."); if ($("#p1").value !== $("#p2").value) throw new Error("Les deux mots de passe ne sont pas identiques."); }
    await post("setup", { password: same ? $("#p3").value : $("#p1").value, same, compris: true }); go();
  });
} else if (S.state === "welcome") {
  box.innerHTML = `<p><b>Bienvenue.</b> Avant d'entrer, trois choses à savoir :</p>` + WARN + `
    <label class="chk"><input type="checkbox" id="ok"><span>J'ai lu et compris : c'est à manier avec prudence, et je ne dois pas perdre ce mot de passe.</span></label>
    <button class="primary" id="b">Entrer dans le back office</button>`;
  $("#b").onclick = run($("#b"), async () => { if (!$("#ok").checked) throw new Error("Cocher d'abord « J'ai lu et compris »."); await post("compris"); go(); });
} else {
  box.innerHTML = `<form id="f"><label for="p">Mot de passe du back office</label><input type="password" id="p" autocomplete="current-password" autofocus>
    <label class="chk"><input type="checkbox" id="rem"><span>Rester connecté sur cet ordinateur (${S.days} jours ; sinon ${S.hours} heures)</span></label>
    <button class="primary" id="b">Entrer</button></form>
    <p class="hint">Ce mot de passe est celui du <b>back office</b> (il peut être différent de celui de la Briquothèque). Après 10 essais ratés, l'adresse est bloquée.</p>`;
  $("#f").onsubmit = run($("#b"), async () => { await post("login", { password: $("#p").value, remember: $("#rem").checked }); go(); });
  fetch("/api/bo/acces").then(r => r.json()).then(d => { if (d.logged) go(); }).catch(() => {});   // déjà connecté (lien venu d'un autre site : le cookie n'avait pas suivi)
}
</script></body></html>
"""

# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Authentification par mot de passe unique + sessions par cookie."""
import hashlib
import hmac
import json
import os
import secrets
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("BQ_DATA") or os.path.join(ROOT, "data")   # BQ_DATA : instance de démonstration
AUTH_FILE = os.path.join(DATA_DIR, "auth.json")
SESSION_DAYS = 365       # « Rester connecté »
SHORT_SESSION_HOURS = 12  # sinon : jusqu'à la fermeture du navigateur (12 h max)
COOKIE = os.environ.get("BQ_COOKIE") or "bq_session"   # copie de travail : son propre cookie (BQ_COOKIE)
_lock = threading.Lock()
_fails = {}  # ip -> [nb échecs, horodatage]


def _read():
    try:
        with open(AUTH_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write(data):
    tmp = AUTH_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.chmod(tmp, 0o600)
    os.replace(tmp, AUTH_FILE)


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()


def is_configured():
    return "hash" in _read()


def set_password(password):
    salt = secrets.token_hex(16)
    with _lock:
        data = _read()
        data.update({"salt": salt, "hash": _hash(password, salt), "sessions": {}})
        _write(data)


def check_password(password):
    data = _read()
    if "hash" not in data:
        return False
    return hmac.compare_digest(_hash(password, data["salt"]), data["hash"])


MAX_FAILS = 10
BANS_FILE = os.path.join(DATA_DIR, "bans.json")


def _bans():
    try:
        with open(BANS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


BAN_SECONDS = 4 * 3600   # un bannissement dure 4 heures


def _active(v):
    return time.time() - v.get("since", 0) < BAN_SECONDS


def is_banned(ip):
    v = _bans().get(ip)
    return bool(v) and _active(v)


def list_bans():
    return [{"ip": k, **v, "until": v.get("since", 0) + BAN_SECONDS}
            for k, v in sorted(_bans().items(), key=lambda kv: -kv[1].get("since", 0)) if _active(v)]


def ban(ip, reason):
    with _lock:
        b = {k: v for k, v in _bans().items() if _active(v)}   # on oublie les bannissements expirés
        b[ip] = {"since": int(time.time()), "reason": reason}
        tmp = BANS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(b, f, indent=1)
        os.chmod(tmp, 0o600)
        os.replace(tmp, BANS_FILE)


def unban(ip):
    with _lock:
        b = _bans()
        b.pop(ip, None)
        tmp = BANS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(b, f, indent=1)
        os.replace(tmp, BANS_FILE)
    _fails.pop(ip, None)


def is_public(ip):
    import ipaddress
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


def too_many_attempts(ip):
    n, t = _fails.get(ip, (0, 0))
    if time.time() - t > 900:
        _fails.pop(ip, None)
        return False
    return n >= MAX_FAILS


def record_failure(ip, what="mot de passe"):
    """Compte un échec ; une adresse publique est bannie au 10e (une adresse locale est bloquée 15 min)."""
    n, t = _fails.get(ip, (0, 0))
    n = n + 1 if time.time() - t <= 900 else 1
    _fails[ip] = (n, time.time())
    if n >= MAX_FAILS and is_public(ip) and not is_banned(ip):
        ban(ip, f"{n} échecs ({what})")
    return n


def clear_failures(ip):
    _fails.pop(ip, None)


def new_session(remember=True):
    token = secrets.token_urlsafe(32)
    with _lock:
        data = _read()
        now = time.time()
        sess = {k: v for k, v in data.get("sessions", {}).items() if v > now}
        ttl = SESSION_DAYS * 86400 if remember else SHORT_SESSION_HOURS * 3600
        sess[hashlib.sha256(token.encode()).hexdigest()] = now + ttl
        data["sessions"] = sess
        _write(data)
    return token


def valid_session(token):
    if not token:
        return False
    exp = _read().get("sessions", {}).get(hashlib.sha256(token.encode()).hexdigest())
    return bool(exp and exp > time.time())


def end_session(token):
    if not token:
        return
    with _lock:
        data = _read()
        data.get("sessions", {}).pop(hashlib.sha256(token.encode()).hexdigest(), None)
        _write(data)


def token_from_cookie(header):
    for part in (header or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k == COOKIE:
            return v
    return None


def cookie_header(token, clear=False, remember=True, secure=False):
    sec = "; Secure" if secure else ""   # HTTPS (derrière nginx) : le cookie ne circule jamais en clair
    if clear:
        return f"{COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax{sec}"
    age = f"; Max-Age={SESSION_DAYS * 86400}" if remember else ""   # sans Max-Age : cookie de session
    return f"{COOKIE}={token}; Path=/{age}; HttpOnly; SameSite=Lax{sec}"

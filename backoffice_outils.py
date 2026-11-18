# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Briquothèque — BACK OFFICE, outils du serveur (rubriques « Serveur » de /backoffice).

But : ne plus jamais avoir besoin d'une ligne de commande. Tout passe par /api/bo/x/<outil> (toujours derrière la connexion) :
  état, journal            → ce que fait le serveur, la place sur le disque, les dernières lignes du journal
  sauvegardes              → créer, télécharger, déposer, restaurer une copie de la collection ; tout exporter / restaurer en .zip
  redémarrage              → relance le serveur (systemd le redémarre ; sinon il se relance lui-même)
  fichiers de données      → voir et corriger n'importe quel fichier .json de data/ (une copie est gardée avant chaque écriture)
  paramètres               → durées, quotas, tailles (appliqués tout de suite) ; port, proxy, démo (au redémarrage)
  code                     → lire et modifier les fichiers de l'application ; chaque version précédente est gardée et peut être remise ;
                             un fichier .py qui empêche le serveur de démarrer est remis automatiquement (garde de démarrage, en haut de server.py)
  corrections du catalogue → nom, thème, année, pièces, image, prix d'un set ou d'une figurine, corrigés par-dessus le catalogue

Deux verrous pour les outils sensibles (fichiers, paramètres, code, redémarrage, restauration .zip) :
  « mode expert » : le mot de passe est redemandé (valable 2 heures) ;
  « réseau local » : le code, le port / proxy et la restauration .zip ne se manipulent que depuis le réseau local.
Chaque action est notée dans data/backoffice_journal.log.
"""
import hashlib
import io
import ipaddress
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile

START = time.time()
_lock = threading.RLock()
_expert = {}     # empreinte du jeton de session → heure de fin du mode expert
_defaults = {}   # valeur d'origine de chaque paramètre (lue au démarrage)
_srv = None      # le module server (donné par init)
EXPERT_SECONDS = 2 * 3600
KEEP_CODE = 30   # versions gardées par fichier de code
KEEP_FILE = 20   # copies gardées par fichier de données
DENY = {"auth.json", "bans.json", "backoffice_boot.json", "backoffice_auth.json"}   # jamais montrés ni modifiés par l'éditeur de fichiers
CODE_EXT = (".py", ".js", ".css", ".html", ".json", ".svg", ".md")

# paramètres réglables : (clé « module.NOM », libellé, aide, unité, diviseur d'affichage, mini, maxi)
PARAMS = [
    ("server.CACHE_TTL", "Fiches du catalogue : relues toutes les…", "Durée pendant laquelle une fiche de set ou de figurine est gardée avant d'être redemandée.", "heures", 3600, 1, 24 * 60),
    ("server.MARKET_TTL", "Annonces d'un set : relevées toutes les…", "", "jours", 86400, 1, 90),
    ("server.MOC_REPRICE", "MOC : rechiffrés toutes les…", "", "jours", 86400, 1, 90),
    ("server.BL_DAY_MAX", "BrickLink : appels par jour, au plus", "La limite de BrickLink est de 5 000 par jour.", "appels", 1, 100, 5000),
    ("server.BL_BG_DAY", "BrickLink : appels de la passe de nuit", "", "appels", 1, 0, 5000),
    ("server.BL_BG_HOUR", "Passe de nuit : heure de départ", "", "h", 1, 0, 23),
    ("server.REFRESH_MIN_GAP", "Actualisation complète : pas plus d'une toutes les…", "", "minutes", 60, 1, 24 * 60),
    ("server.IMG_LIMIT", "Images gardées sur le serveur : ménage au-delà de…", "", "Mo", 1024 * 1024, 100, 20000),
    ("server.IMG_TARGET", "Images : le ménage redescend à…", "Doit rester en dessous de la limite.", "Mo", 1024 * 1024, 50, 20000),
    ("server.HD_MAX", "Images en grand : côté maximal", "", "pixels", 1, 600, 4000),
    ("server.DEMO_RESET", "Démonstration : remise à zéro toutes les…", "", "heures", 3600, 1, 24 * 30),
    ("auth.SESSION_DAYS", "« Rester connecté » : durée", "", "jours", 1, 1, 3650),
    ("auth.SHORT_SESSION_HOURS", "Connexion simple : durée", "", "heures", 1, 1, 24 * 30),
    ("auth.MAX_FAILS", "Mots de passe faux avant blocage de l'adresse", "", "essais", 1, 3, 1000),
    ("auth.BAN_SECONDS", "Durée d'un blocage", "", "heures", 3600, 0.1, 24 * 365),
    ("server.PHOTO_TODO_GAP", "Tâche « Photo à faire » : vérifiée toutes les…", "Posée d'office sur une figurine sans aucune image disponible ni photo. 0 = jamais (les tâches déjà posées restent : retirez-les à la main).", "heures", 3600, 0, 24 * 30),
    ("sources.RB_GAP", "Rebrickable : pause entre deux requêtes", "Leur limite est d'une requête par seconde.", "secondes", 1, 1, 60),
]
ENV = [   # réglages lus au démarrage (data/backoffice_env.json, appliqués par la garde de démarrage de server.py)
    ("PORT", "Port d'écoute du serveur", "Attention : en le changeant, l'adresse du site change (http://…:PORT). Votre proxy doit suivre."),
    ("BQ_PROXIES", "Adresse(s) du proxy de confiance", "Adresse(s) IP de votre nginx, séparées par des virgules : lui seul peut annoncer l'adresse réelle des visiteurs."),
    ("BQ_DEMO_SITE", "Démonstration publique /demo", "1 = activée, vide = désactivée."),
]
FILE_DOC = {
    "collection.json": "La collection : listes et fiches", "settings.json": "Réglages de l'application (clés API comprises)",
    "cache_sets.json": "Catalogue : fiches des sets et des figurines", "history.json": "Historique de la valeur", "notes.json": "Notes libres (À faire)",
    "shares.json": "Liens de partage", "visits.json": "Visites des pages publiques", "backoffice.json": "Back office : réglages publiés",
    "backoffice_brouillon.json": "Back office : brouillon", "backoffice_catalogue.json": "Back office : corrections du catalogue",
    "backoffice_params.json": "Back office : paramètres du serveur", "backoffice_env.json": "Back office : port, proxy, démo",
    "cache_names_fr.json": "Noms français", "cache_parts.json": "Pièces (catalogue)", "cache_part_prices.json": "Prix des pièces",
    "cache_novelties.json": "Nouveautés LEGO", "cache_lego_prices.json": "Prix publics LEGO", "moc_review.json": "MOC : relectures",
}
FIX_KEYS = ("name", "theme", "subtheme", "year", "pieces", "image", "retail", "new_value", "used_value", "value", "used")


def init(srv):
    """Appelé une fois par server.py : garde le module, relève les valeurs d'origine des paramètres, applique ceux réglés."""
    global _srv
    _srv = srv
    for key, *_ in PARAMS:
        mod, name = _mod(key)
        if mod is not None and hasattr(mod, name):
            _defaults[key] = getattr(mod, name)
    for key, val in (_read("backoffice_params.json") or {}).items():
        _set_param(key, val)


def _mod(key):
    m, name = key.split(".", 1)
    return ({"server": _srv, "auth": getattr(_srv, "auth", None), "sources": getattr(_srv, "sources", None)}.get(m), name)


def _set_param(key, raw):
    mod, name = _mod(key)
    if key in _defaults and mod is not None and isinstance(raw, (int, float)) and not isinstance(raw, bool):
        setattr(mod, name, type(_defaults[key])(raw) if isinstance(_defaults[key], int) else float(raw))


def _p(*a):
    return os.path.join(_srv.DATA, *a)


def _read(name, default=None):
    try:
        with open(_p(name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write(name, obj):
    tmp = _p(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _p(name))


def journal(action, detail=""):
    """Une ligne par action faite depuis les outils (qui a fait quoi, quand)."""
    try:
        with open(_p("backoffice_journal.log"), "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{action}\t{str(detail)[:300]}\n")
    except OSError:
        pass


# ----------------------------------------------------------------------------- verrous
def _tok(h):
    return hashlib.sha256((h.token() or "").encode()).hexdigest()


def expert_ok(h):
    """Connecté au back office : son mot de passe vaut le « mode expert » d'avant (gardé pour une installation sans mot de passe à part)."""
    try:
        if _srv.backoffice_acces.logged(h):
            return True
    except Exception:
        pass
    return _expert.get(_tok(h), 0) > time.time()


def local_only(h):
    """La requête vient-elle du réseau local (en direct, ou par un proxy qui annonce une adresse locale) ?"""
    addrs = [h.client_address[0]] + [x.strip() for k in ("X-Real-IP", "X-Forwarded-For") for x in (h.headers.get(k) or "").split(",") if x.strip()]
    if h.client_address[0] in getattr(_srv, "TRUSTED_PROXIES", ()) and len(addrs) == 1:
        return False   # venue du proxy sans adresse annoncée : on ne peut pas savoir d'où elle vient
    try:
        return all((lambda i: i.is_private or i.is_loopback or i.is_link_local)(ipaddress.ip_address(a)) for a in addrs)
    except ValueError:
        return False


class Refus(Exception):
    def __init__(self, msg, status=400, code=""):
        super().__init__(msg)
        self.status, self.code = status, code


def sensitive_ok(h):
    """Outils sensibles (code, fichiers bruts, démarrage, restauration .zip, secours) : depuis le réseau local — ou de partout si le
    propriétaire l'a permis dans « Mots de passe et sécurité » (réglage qui, lui, ne se change que depuis le réseau local)."""
    try:
        return local_only(h) or _srv.backoffice_acces.remote_tools()
    except Exception:
        return False


def _need(h, local=False):
    if not expert_ok(h):
        raise Refus("Mode expert requis : redonnez votre mot de passe", 403, "expert")
    if local and not sensitive_ok(h):
        raise Refus("Cette action n'est permise que depuis le réseau local (chez vous). Pour la permettre aussi depuis Internet : rubrique "
                    "« Mots de passe et sécurité » → « Outils sensibles depuis Internet » (à régler depuis chez vous).", 403, "local")


# ----------------------------------------------------------------------------- état, journal
def _size(path):
    total = n = 0
    try:
        for e in os.scandir(path):
            if e.is_dir(follow_symlinks=False):
                t, k = _size(e.path)
                total, n = total + t, n + k
            elif e.is_file(follow_symlinks=False):
                total, n = total + e.stat().st_size, n + 1
    except OSError:
        pass
    return total, n


def status(h):
    srv = _srv
    st = os.statvfs(srv.DATA)
    mem = {}
    try:
        for line in open("/proc/meminfo"):
            k, v = line.split(":", 1)
            if k in ("MemTotal", "MemAvailable"):
                mem[k] = int(v.split()[0]) * 1024
    except OSError:
        pass
    db = srv.load_db()
    folders = []
    for name, label in (("images", "Images du catalogue (copies locales)"), ("uploads", "Vos photos"), ("thumbs", "Vignettes"), ("backups", "Sauvegardes"), ("backoffice_code", "Anciennes versions du code")):
        t, n = _size(_p(name))
        if n:
            folders.append({"name": label, "size": t, "files": n})
    jsons = sum(os.path.getsize(_p(f)) for f in os.listdir(srv.DATA) if f.endswith(".json") and os.path.isfile(_p(f)))
    try:
        bk = sorted(os.listdir(srv.BACKUP_DIR))
        last_bk = max((os.path.getmtime(os.path.join(srv.BACKUP_DIR, f)) for f in bk if f.endswith(".json")), default=0)
    except OSError:
        last_bk = 0
    try:
        jl = open(_p("backoffice_journal.log"), encoding="utf-8").read().splitlines()[-25:]
    except OSError:
        jl = []
    boot = _read("backoffice_boot.json") or {}
    return {"uptime": int(time.time() - START), "python": sys.version.split()[0], "pid": os.getpid(), "port": getattr(srv, "PORT", 0),
            "systemd": bool(os.environ.get("INVOCATION_ID")), "copie": bool(getattr(srv, "COPIE", False)), "node": bool(shutil.which("node")),
            "disk": {"free": st.f_bavail * st.f_frsize, "total": st.f_blocks * st.f_frsize}, "mem": {"free": mem.get("MemAvailable", 0), "total": mem.get("MemTotal", 0)},
            "load": os.getloadavg()[0], "items": len(db.get("items", [])), "lists": len(db.get("lists", [])), "json": jsons, "folders": folders,
            "last_backup": int(last_bk), "journal": list(reversed(jl)), "expert": expert_ok(h), "expert_left": max(0, int(_expert.get(_tok(h), 0) - time.time())),
            "local": local_only(h), "restored": boot.get("restored") or [], "pending": sorted((boot.get("pending") or {}).keys())}


def log_tail(q):
    n = max(20, min(2000, int((q.get("n") or ["300"])[0] or 300)))
    flt = (q.get("q") or [""])[0].lower()
    try:
        with open(_p("server.log"), "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 600_000))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return {"lines": [], "size": 0}
    if flt:
        lines = [l for l in lines if flt in l.lower()]
    return {"lines": lines[-n:], "size": size}


# ----------------------------------------------------------------------------- sauvegardes
def _bk_name(name):
    if not re.fullmatch(r"[\w.-]{1,120}\.json", name or "") or not os.path.isfile(os.path.join(_srv.BACKUP_DIR, name)):
        raise Refus("Sauvegarde introuvable", 404)
    return os.path.join(_srv.BACKUP_DIR, name)


def backups():
    out = []
    try:
        for f in sorted(os.listdir(_srv.BACKUP_DIR), reverse=True):
            full = os.path.join(_srv.BACKUP_DIR, f)
            if f.endswith(".json") and os.path.isfile(full):
                out.append({"name": f, "size": os.path.getsize(full), "t": int(os.path.getmtime(full))})
    except OSError:
        pass
    return out


def _check_db(d):
    if not (isinstance(d, dict) and isinstance(d.get("lists"), list) and isinstance(d.get("items"), list)
            and all(isinstance(i, dict) and i.get("id") for i in d["items"]) and all(isinstance(l, dict) and l.get("id") for l in d["lists"])):
        raise Refus("Ce fichier n'est pas une sauvegarde de la collection (il faut des « lists » et des « items »)")
    return d


def _lot_after_restore():
    """Sauvegarde d'avant le 16/11/2026 restaurée : ses lots de figurines aux pièces échangées passent au comptage « lot entier » (server.lot_swaps_migrate)."""
    try:
        _srv.lot_swaps_migrate()
    except Exception as e:
        journal("conversion des lots", f"impossible : {e}")


def restore(name):
    """La collection redevient celle de la sauvegarde ; l'état actuel est d'abord sauvegardé."""
    with open(_bk_name(name), encoding="utf-8") as f:
        d = _check_db(json.load(f))
    with _srv.lock:
        _srv.backup_db("avant-restauration")
        _srv._save(_srv.DB_FILE, d)
        _lot_after_restore()
    journal("restauration", f"{name} ({len(d['items'])} fiches)")
    return {"ok": True, "items": len(d["items"])}


def export_zip(photos):
    """Toutes les données (fichiers .json, sans le mot de passe ni les caches d'images), et les photos si demandé."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(_srv.DATA)):
            if f.endswith(".json") and f not in DENY and os.path.isfile(_p(f)):
                z.write(_p(f), f)
        if photos and os.path.isdir(_p("uploads")):
            for f in sorted(os.listdir(_p("uploads"))):
                if re.fullmatch(r"[0-9a-f]{16,40}", f):
                    z.write(_p("uploads", f), "uploads/" + f)
    return buf.getvalue()


def import_zip(raw):
    """Restaure un export .zip : chaque fichier remplacé est d'abord copié dans backups/avant-zip-<date>/."""
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise Refus("Ce fichier n'est pas un .zip lisible")
    names = [n for n in z.namelist() if (re.fullmatch(r"[\w.-]{1,80}\.json", n) and n not in DENY) or re.fullmatch(r"uploads/[0-9a-f]{16,40}", n)]
    sizes = {i.filename: i.file_size for i in z.infolist()}
    if sum(sizes.get(n, 0) for n in names) > 1_500_000_000 or any(sizes.get(n, 0) > 300_000_000 for n in names):   # (.zip piégé : petit fichier, contenu démesuré)
        raise Refus("Ce .zip contient des fichiers démesurés : il n'est pas restauré")
    if "collection.json" not in names:
        raise Refus("Ce .zip ne contient pas « collection.json » : ce n'est pas un export de Briquothèque")
    _check_db(json.loads(z.read("collection.json").decode("utf-8")))
    keep = _p("backups", "avant-zip-" + time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(keep, exist_ok=True)
    with _srv.lock:
        os.makedirs(_p("uploads"), exist_ok=True)
        for n in names:
            dst = _p(*n.split("/"))
            if n.endswith(".json"):
                json.loads(z.read(n).decode("utf-8"))   # illisible : rien n'est écrit pour ce fichier (exception → refus)
                if os.path.isfile(dst):
                    shutil.copy(dst, os.path.join(keep, n))
            elif os.path.isfile(dst):
                continue   # photo déjà là
            with open(dst + ".tmp", "wb") as f:
                f.write(z.read(n))
            os.replace(dst + ".tmp", dst)
    _lot_after_restore()
    journal("restauration zip", f"{len(names)} fichiers")
    return {"ok": True, "files": len(names)}


def restart_soon(delay=0.8):
    """Relance le serveur : sous systemd, il s'arrête (code 3) et systemd le redémarre ; sinon il se relance lui-même."""
    journal("redémarrage")

    def go():
        time.sleep(delay)
        if os.environ.get("INVOCATION_ID"):
            os._exit(3)
        os.execv(sys.executable, [sys.executable, "-u", os.path.join(_srv.ROOT, "server.py")])
    threading.Thread(target=go, daemon=True).start()


# ----------------------------------------------------------------------------- fichiers de données (.json)
def _file(name):
    if not re.fullmatch(r"[\w.-]{1,80}\.json", name or "") or name in DENY or not os.path.isfile(_p(name)):
        raise Refus("Fichier introuvable", 404)
    return _p(name)


def files():
    out = []
    for f in sorted(os.listdir(_srv.DATA)):
        if f.endswith(".json") and f not in DENY and os.path.isfile(_p(f)):
            out.append({"name": f, "size": os.path.getsize(_p(f)), "t": int(os.path.getmtime(_p(f))), "doc": FILE_DOC.get(f, "")})
    return out


def _kind(v):
    return "dict" if isinstance(v, dict) else "list" if isinstance(v, list) else "bool" if isinstance(v, bool) else "num" if isinstance(v, (int, float)) else "null" if v is None else "str"


def _walk(doc, path):
    cur = doc
    for k in path:
        if isinstance(cur, dict) and isinstance(k, str) and k in cur:
            cur = cur[k]
        elif isinstance(cur, list) and isinstance(k, int) and 0 <= k < len(cur):
            cur = cur[k]
        else:
            raise Refus("Cet endroit du fichier n'existe plus (rechargez)", 404)
    return cur


def _hint(v):
    """Aperçu d'une valeur composée : pour s'y retrouver dans une longue liste (nom, numéro…)."""
    if isinstance(v, dict):
        for k in ("name", "nom", "label", "custom_name", "display_name", "number", "id", "title"):
            if isinstance(v.get(k), (str, int)) and str(v[k]).strip():
                return str(v[k])[:60]
        info = v.get("info")
        if isinstance(info, dict) and info.get("name"):
            return str(info["name"])[:60]
    return ""


def json_view(q):
    doc = _read(os.path.basename(_file((q.get("file") or [""])[0])))
    try:
        path = json.loads((q.get("path") or ["[]"])[0])
    except ValueError:
        path = []
    node = _walk(doc, path if isinstance(path, list) else [])
    flt = (q.get("q") or [""])[0].lower()
    start = max(0, int((q.get("start") or ["0"])[0] or 0))
    k = _kind(node)
    if k not in ("dict", "list"):
        return {"t": k, "v": node}
    rows = []
    for key, v in (node.items() if k == "dict" else enumerate(node)):
        kv = _kind(v)
        row = {"k": key, "t": kv}
        if kv in ("dict", "list"):
            row["n"], row["hint"] = len(v), _hint(v)
        else:
            row["v"] = v if not isinstance(v, str) or len(v) <= 400 else v[:400] + "…"
            row["long"] = isinstance(v, str) and len(v) > 400
        if flt and flt not in (str(key) + " " + str(row.get("hint", "")) + " " + str(row.get("v", ""))).lower():
            continue
        rows.append(row)
    return {"t": k, "n": len(node), "found": len(rows), "start": start, "rows": rows[start:start + 200]}


def json_find(q):
    """Recherche dans tout le fichier : les 60 premiers endroits dont la clé ou la valeur contient le texte."""
    doc = _read(os.path.basename(_file((q.get("file") or [""])[0])))
    flt = (q.get("q") or [""])[0].lower().strip()
    out = []
    if len(flt) < 2:
        return {"hits": out}

    def go(node, path):
        if len(out) >= 60:
            return
        for key, v in (node.items() if isinstance(node, dict) else enumerate(node)):
            if len(out) >= 60:
                return
            if isinstance(v, (dict, list)):
                if isinstance(key, str) and flt in key.lower():
                    out.append({"path": path + [key], "v": _hint(v) or _kind(v)})
                go(v, path + [key])
            elif flt in str(key).lower() or (v is not None and flt in str(v).lower()):
                out.append({"path": path + [key], "v": str(v)[:120]})
    if isinstance(doc, (dict, list)):
        go(doc, [])
    return {"hits": out}


def json_edit(b):
    """{file, path, op: "set" | "del" | "add", key?, value} — une copie du fichier est gardée avant (backups/fichiers/)."""
    name = os.path.basename(_file(b.get("file")))
    path, op = b.get("path") or [], b.get("op")
    if not isinstance(path, list) or op not in ("set", "del", "add"):
        raise Refus("Demande illisible")
    with _srv.lock:
        doc = _read(name)
        if op == "add":
            node = _walk(doc, path)
            if isinstance(node, dict):
                key = str(b.get("key") or "").strip()
                if not key or key in node:
                    raise Refus("Donnez un nom de ligne qui n'existe pas déjà")
                node[key] = b.get("value")
            elif isinstance(node, list):
                node.append(b.get("value"))
            else:
                raise Refus("On ne peut ajouter une ligne que dans un groupe ou une liste")
        else:
            if not path:
                raise Refus("Le fichier entier ne se remplace pas ici")
            parent = _walk(doc, path[:-1])
            _walk(doc, path)
            if op == "set":
                parent[path[-1]] = b.get("value")
            else:
                del parent[path[-1]]
        if name == "collection.json":
            _check_db(doc)
        keep = _p("backups", "fichiers")
        os.makedirs(keep, exist_ok=True)
        shutil.copy(_p(name), os.path.join(keep, f"{name[:-5]}-{time.strftime('%Y%m%d-%H%M%S')}.json"))
        mine = sorted(f for f in os.listdir(keep) if f.startswith(name[:-5] + "-"))
        for old in mine[:-KEEP_FILE]:
            os.remove(os.path.join(keep, old))
        _srv._save(_p(name), doc)
    journal("fichier " + op, f"{name} {json.dumps(path, ensure_ascii=False)[:160]}")
    return {"ok": True}


# ----------------------------------------------------------------------------- paramètres
def params():
    saved = _read("backoffice_params.json") or {}
    out = []
    for key, label, doc, unit, div, lo, hi in PARAMS:
        if key not in _defaults:
            continue
        mod, name = _mod(key)
        cur = getattr(mod, name)
        out.append({"key": key, "label": label, "doc": doc, "unit": unit, "value": round(cur / div, 3), "default": round(_defaults[key] / div, 3), "min": lo, "max": hi, "changed": key in saved})
    env = _read("backoffice_env.json") or {}
    return {"params": out, "env": [{"key": k, "label": l, "doc": d, "value": env.get(k), "now": os.environ.get(k, "")} for k, l, d in ENV]}


def param_set(b):
    key = b.get("key")
    row = next((p for p in PARAMS if p[0] == key), None)
    if not row or key not in _defaults:
        raise Refus("Paramètre inconnu")
    saved = _read("backoffice_params.json") or {}
    if b.get("value") in (None, ""):
        saved.pop(key, None)
        raw = _defaults[key]
    else:
        try:
            v = float(str(b["value"]).replace(",", "."))
        except ValueError:
            raise Refus("Il faut un nombre")
        if not row[5] <= v <= row[6]:
            raise Refus(f"Valeur possible : de {row[5]} à {row[6]} {row[3]}")
        raw = v * row[4]
        raw = int(round(raw)) if isinstance(_defaults[key], int) else raw
        saved[key] = raw
    _write("backoffice_params.json", saved)
    _set_param(key, raw)
    journal("paramètre", f"{key} = {raw}")
    return {"ok": True}


def env_set(b):
    key, val = b.get("key"), str(b.get("value") or "").strip()
    if key not in [k for k, *_ in ENV]:
        raise Refus("Réglage inconnu")
    if key == "PORT" and val and not (val.isdigit() and 1024 <= int(val) <= 65535):
        raise Refus("Port : un nombre de 1024 à 65535")
    if key == "BQ_PROXIES" and val:
        try:
            [ipaddress.ip_address(x.strip()) for x in val.split(",") if x.strip()]
        except ValueError:
            raise Refus("Adresse IP illisible")
    if key == "BQ_DEMO_SITE" and val not in ("", "1"):
        raise Refus("1 ou vide")
    env = _read("backoffice_env.json") or {}
    if b.get("value") is None:
        env.pop(key, None)
    else:
        env[key] = val
    _write("backoffice_env.json", env)
    journal("réglage de démarrage", f"{key} = {val}")
    return {"ok": True, "restart": True}


# ----------------------------------------------------------------------------- code de l'application
def _code_path(rel):
    rel = str(rel or "").replace("\\", "/")
    if not re.fullmatch(r"(static/)?[\w.-]{1,80}", rel) or not rel.endswith(CODE_EXT) or rel.startswith("."):
        raise Refus("Fichier non modifiable ici", 404)
    full = os.path.join(_srv.ROOT, *rel.split("/"))
    if not os.path.isfile(full):
        raise Refus("Fichier introuvable", 404)
    return rel, full


def _code_keep(rel):
    return _p("backoffice_code", rel.replace("/", "__"))


def code_versions(rel):
    d = _code_keep(rel)
    try:
        return [{"id": f, "size": os.path.getsize(os.path.join(d, f))} for f in sorted(os.listdir(d), reverse=True) if re.fullmatch(r"\d{8}-\d{6}", f)]
    except OSError:
        return []


def code_files():
    out = []
    root = _srv.ROOT
    for sub in ("", "static"):
        for f in sorted(os.listdir(os.path.join(root, sub))):
            rel = (sub + "/" if sub else "") + f
            full = os.path.join(root, sub, f)
            if os.path.isfile(full) and f.endswith(CODE_EXT) and (sub or f.endswith(".py")) and os.path.getsize(full) < 3_000_000:
                out.append({"file": rel, "size": os.path.getsize(full), "t": int(os.path.getmtime(full)), "versions": len(code_versions(rel))})
    return out


def code_check(rel, text):
    """Vérifie la syntaxe avant d'écrire : Python (compilation), JavaScript (node --check, s'il est installé), JSON."""
    if rel.endswith(".py"):
        try:
            compile(text, rel, "exec")
        except SyntaxError as e:
            raise Refus(f"Erreur de syntaxe Python, ligne {e.lineno} : {e.msg}" + (f" → {e.text.strip()[:120]}" if e.text else ""))
        if rel == "server.py" and "_bo_boot()" not in text:
            raise Refus("La « garde de démarrage » (tout en haut de server.py) a disparu : elle doit rester, c'est elle qui remet l'ancienne version si le serveur ne démarre plus")
    elif rel.endswith(".json"):
        try:
            json.loads(text)
        except ValueError as e:
            raise Refus(f"JSON illisible : {e}")
    elif rel.endswith(".js") and shutil.which("node"):
        tmp = _p("backoffice_verif.js")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True, timeout=30)
            if r.returncode:
                err = (r.stderr or "").replace(tmp, rel).strip().splitlines()
                m = re.search(r":(\d+)", err[0]) if err else None
                raise Refus(f"Erreur de syntaxe JavaScript{', ligne ' + m.group(1) if m else ''} : " + " ".join(l.strip() for l in err[1:5])[:300])
        except subprocess.TimeoutExpired:
            pass
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass


def code_save(rel, text, why="modification"):
    """Écrit un fichier de code : syntaxe vérifiée, version précédente gardée ; un .py est mis « à l'essai » jusqu'au prochain démarrage réussi."""
    rel, full = _code_path(rel)
    if not isinstance(text, str) or len(text) > 3_000_000:
        raise Refus("Contenu illisible ou trop volumineux")
    text = text.replace("\r\n", "\n")
    code_check(rel, text)
    with _lock:
        with open(full, encoding="utf-8") as f:
            old = f.read()
        if old == text:
            return {"ok": True, "same": True}
        keep = _code_keep(rel)
        os.makedirs(keep, exist_ok=True)
        vid = time.strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(keep, vid), "w", encoding="utf-8") as f:
            f.write(old)
        for extra in sorted(os.listdir(keep), reverse=True)[KEEP_CODE:]:
            os.remove(os.path.join(keep, extra))
        with open(full + ".tmp", "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(full + ".tmp", full)
        if rel.endswith(".py"):   # à l'essai : si le serveur ne redémarre pas avec, la garde de démarrage remet cette version-ci
            boot = _read("backoffice_boot.json") or {}
            pend = boot.get("pending") or {}
            pend.setdefault(rel, os.path.join(keep, vid))
            _write("backoffice_boot.json", {"pending": pend, "tries": 0})
    journal("code " + why, rel)
    return {"ok": True, "version": vid, "restart": rel.endswith(".py")}


def code_restore(rel, vid):
    rel, _ = _code_path(rel)
    if not re.fullmatch(r"\d{8}-\d{6}", str(vid or "")):
        raise Refus("Version introuvable", 404)
    try:
        with open(os.path.join(_code_keep(rel), vid), encoding="utf-8") as f:
            return code_save(rel, f.read(), "version remise")
    except OSError:
        raise Refus("Version introuvable", 404)


def boot_ok():
    """Le serveur a démarré : le code « à l'essai » est validé."""
    boot = _read("backoffice_boot.json")
    if boot and boot.get("pending"):
        _write("backoffice_boot.json", {"pending": {}, "tries": 0, **({"restored": boot["restored"]} if boot.get("restored") else {})})


RESCUE = """<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Secours — Briquothèque</title>
<style>body{font:15px system-ui,sans-serif;max-width:760px;margin:30px auto;padding:0 16px;color:#1b1d22;background:#fff}h1{font-size:22px}table{border-collapse:collapse;width:100%}td,th{padding:6px 8px;border-bottom:1px solid #ddd;text-align:left}
button{padding:6px 12px;border-radius:8px;border:1px solid #999;background:#fff;cursor:pointer;margin:2px}input{padding:7px;border:1px solid #999;border-radius:8px}.n{background:#fff4d6;padding:10px 12px;border-radius:10px}</style>
<h1>🛟 Secours du back office</h1>
<p class="n">Cette page ne dépend d'aucun autre fichier : elle sert quand une modification du code a cassé le site ou le back office.
Donnez le <b>mot de passe du back office</b>, affichez les versions gardées, puis remettez la version précédente du fichier fautif.
Par sécurité, elle ne répond que depuis le réseau local (sauf si « Outils sensibles depuis Internet » a été permis).</p>
<p><label>Mot de passe du back office : <input type="password" id="pw" autocomplete="current-password"></label></p>
<p><button onclick="list()">📂 Afficher les versions gardées</button> <button onclick="act({restart:1})">↻ Redémarrer le serveur</button> &nbsp; <a href="/backoffice">← Back office</a> &nbsp; <a href="/?bo=off">Le site sans personnalisation</a></p>
<table id="t" hidden><tr><th>Fichier</th><th>Versions gardées (la plus récente d'abord)</th></tr></table>
<p id="out" style="font-weight:700"></p>
<script>
const out=document.getElementById("out"),pw=()=>document.getElementById("pw").value;
async function call(b){b.password=pw();if(!b.password){out.textContent="Donnez d'abord le mot de passe du back office.";return null}out.textContent="…";
 try{const r=await fetch("/api/bo/x/rescue",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});const d=await r.json().catch(()=>({}));
  if(!r.ok){out.textContent="✘ "+(d.erreur||"Erreur "+r.status);return null}return d}catch(e){out.textContent="✘ Serveur injoignable (il redémarre peut-être) : réessayez dans quelques secondes.";return null}}
async function list(){const d=await call({list:1});if(!d)return;const t=document.getElementById("t");t.hidden=false;while(t.rows.length>1)t.deleteRow(1);out.textContent=d.files.length?"":"Aucune version précédente : aucun fichier n'a été modifié depuis le back office.";
 for(const f of d.files){const r=t.insertRow(),a=r.insertCell(),b=r.insertCell();a.textContent=f.file;a.style.fontWeight="700";
  for(const id of f.versions){const x=document.createElement("button");x.textContent=id.slice(6,8)+"/"+id.slice(4,6)+" "+id.slice(9,11)+":"+id.slice(11,13);x.onclick=()=>act({file:f.file,id});b.append(x)}}}
async function act(b){if(b.file&&!confirm("Remettre "+b.file+" dans sa version du "+b.id+" ?"))return;const d=await call(b);if(d)out.textContent=d.restart?"✔ Fait. Le serveur redémarre : rechargez cette page dans dix secondes.":"✔ Fait."}
</script></html>"""


def rescue_page():
    return RESCUE.encode("utf-8")


def rescue_list():
    return [{"file": f["file"], "versions": [v["id"] for v in code_versions(f["file"])[:8]]} for f in code_files() if f["versions"]]


# ----------------------------------------------------------------------------- images envoyées depuis le back office (boutons, pages, logo)
IMG_DIR = "backoffice_images"
IMG_MAX = 4 * 1024 * 1024
IMG_TYPES = {"png": "image/png", "jpg": "image/jpeg", "gif": "image/gif", "webp": "image/webp", "svg": "image/svg+xml", "ico": "image/x-icon", "avif": "image/avif"}


def _img_kind(raw):
    """Type d'une image d'après son contenu (jamais d'après le nom donné) ; None si ce n'en est pas une."""
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if raw[:3] == b"\xff\xd8\xff":
        return "jpg"
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "webp"
    if raw[:4] == b"\x00\x00\x01\x00":
        return "ico"
    if raw[4:12] in (b"ftypavif", b"ftypavis"):
        return "avif"
    head = raw[:2000].lstrip(b"\xef\xbb\xbf \t\r\n").lower()
    if (head.startswith(b"<svg") or head.startswith(b"<?xml") or head.startswith(b"<!--") or head.startswith(b"<!doctype svg")) and b"<svg" in raw[:4000].lower():
        return "svg"
    return None


def images():
    out = []
    try:
        for f in sorted(os.listdir(_p(IMG_DIR))):
            if re.fullmatch(r"[0-9a-f]{16}\.(png|jpg|gif|webp|svg|ico|avif)", f):
                st = os.stat(_p(IMG_DIR, f))
                out.append({"name": f, "url": "/bo-img/" + f, "size": st.st_size, "t": int(st.st_mtime)})
    except OSError:
        pass
    labels = _read("backoffice_images.json") or {}
    for o in out:
        o["label"] = str(labels.get(o["name"]) or "")[:80]
    return sorted(out, key=lambda o: -o["t"])


def image_add(raw, label=""):
    if not raw:
        raise Refus("Aucune image reçue")
    if len(raw) > IMG_MAX:
        raise Refus("Image trop lourde (4 Mo au plus) : réduisez-la d'abord")
    kind = _img_kind(raw)
    if not kind:
        raise Refus("Ce fichier n'est pas une image reconnue (PNG, JPEG, GIF, WebP, SVG, ICO, AVIF)")
    if kind == "svg" and re.search(rb"(?i)<script|\bon[a-z]+\s*=|javascript:|<foreignobject|<iframe|<embed|<object", raw):
        raise Refus("Cette image SVG contient du code (script) : elle n'est pas acceptée")
    if len(images()) >= 400:
        raise Refus("Trop d'images (400) : supprimez-en d'abord")
    name = hashlib.sha256(raw).hexdigest()[:16] + "." + kind
    os.makedirs(_p(IMG_DIR), exist_ok=True)
    with open(_p(IMG_DIR, name) + ".tmp", "wb") as f:
        f.write(raw)
    os.replace(_p(IMG_DIR, name) + ".tmp", _p(IMG_DIR, name))
    label = re.sub(r"[\x00-\x1f<>]", "", str(label or ""))[:80]
    if label:
        labels = _read("backoffice_images.json") or {}
        labels[name] = label
        _write("backoffice_images.json", labels)
    journal("image ajoutée", name)
    return {"ok": True, "name": name, "url": "/bo-img/" + name, "images": images()}


def image_del(name):
    if not re.fullmatch(r"[0-9a-f]{16}\.(png|jpg|gif|webp|svg|ico|avif)", str(name or "")):
        raise Refus("Image introuvable", 404)
    try:
        os.remove(_p(IMG_DIR, name))
    except OSError:
        raise Refus("Image introuvable", 404)
    labels = _read("backoffice_images.json") or {}
    if labels.pop(name, None) is not None:
        _write("backoffice_images.json", labels)
    journal("image supprimée", name)
    return {"ok": True, "images": images()}


def image_send(h, name):
    """/bo-img/<nom> : image publique (elle habille des pages vues par tous). Servie telle quelle, sans jamais être exécutée."""
    m = re.fullmatch(r"[0-9a-f]{16}\.(png|jpg|gif|webp|svg|ico|avif)", name or "")
    try:
        if not m:
            raise OSError
        with open(_p(IMG_DIR, name), "rb") as f:
            body = f.read()
    except OSError:
        return h.error("Image introuvable", 404)
    h.send_response(200)
    h.send_header("Content-Type", IMG_TYPES[m.group(1)])
    h.send_header("Content-Length", str(len(body)))
    h.send_header("Cache-Control", "public, max-age=31536000, immutable")   # (le nom vient du contenu : une image modifiée change de nom)
    h.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; sandbox")   # un SVG ouvert seul ne peut rien exécuter
    h.end_headers()
    h.wfile.write(body)


# ----------------------------------------------------------------------------- corrections du catalogue
_fix = {"m": -1, "d": {}}


def fixes():
    try:
        m = os.path.getmtime(_p("backoffice_catalogue.json"))
    except OSError:
        return {}
    if _fix["m"] != m:
        _fix["m"], _fix["d"] = m, _read("backoffice_catalogue.json") or {}
    return _fix["d"]


def fix(info, key):
    """Fiche du catalogue corrigée (nom, thème, année, pièces, image, prix) : appelé par enrich() de server.py."""
    if _srv is None:
        return info
    f = fixes().get(key)
    if not f or not isinstance(info, dict):
        return info
    return {**info, **{k: v for k, v in f.items() if k in FIX_KEYS and v not in (None, "")}, "bo_fix": True}


def fix_set(b):
    key = str(b.get("key") or "").strip()
    if not re.fullmatch(r"(fig:)?[\w.-]{1,40}", key):
        raise Refus("Numéro illisible")
    all_ = dict(fixes())
    f = b.get("fields")
    if not f:
        all_.pop(key, None)
    else:
        clean = {}
        for k in FIX_KEYS:
            v = f.get(k)
            if v in (None, ""):
                continue
            if k in ("pieces", "retail", "new_value", "used_value", "value", "used"):
                try:
                    v = float(str(v).replace(",", "."))
                    v = int(v) if k == "pieces" else round(v, 2)
                except ValueError:
                    raise Refus(f"« {k} » : il faut un nombre")
            else:
                v = str(v)[:400]
            clean[k] = v
        if clean:
            all_[key] = {**clean, **({"label": str(b.get("label"))[:120]} if b.get("label") else {})}
        else:
            all_.pop(key, None)
    _write("backoffice_catalogue.json", all_)
    _fix["m"] = -1
    journal("catalogue", key)
    return {"ok": True, "fixes": all_}


def catalog_find(q):
    """Fiches du catalogue qui correspondent (numéro ou nom) : pour choisir celle à corriger."""
    s = (q.get("q") or [""])[0].lower().strip()
    cache = _srv._load(_srv.CACHE_FILE, {})
    out = []
    for k, v in cache.items():
        if isinstance(v, dict) and s and (s in k.lower() or s in str(v.get("name") or "").lower()):
            out.append({"key": k, "name": v.get("name"), **{x: v.get(x) for x in FIX_KEYS if v.get(x) not in (None, "")}})
            if len(out) >= 40:
                break
    return {"hits": out}


# ----------------------------------------------------------------------------- valeurs en masse (import d'un tableur)
def values_bulk(b):
    """{rows: [{id, x: {champ: valeur}}]} : complète les champs personnalisés de plusieurs fiches (sauvegarde avant)."""
    import backoffice
    rows = b.get("rows")
    if not isinstance(rows, list) or len(rows) > 20000:
        raise Refus("Tableau illisible")
    n = 0
    with _srv.lock:
        db = _srv.load_db()
        by = {i["id"]: i for i in db["items"]}
        _srv.backup_db("tableur")
        for r in rows:
            it = by.get(str((r or {}).get("id") or ""))
            x = backoffice.clean_x((r or {}).get("x"))
            if not it or not isinstance((r or {}).get("x"), dict):
                continue
            cur = dict(it.get("x") or {})
            for k, v in (r["x"] or {}).items():
                if v in (None, "", []):
                    cur.pop(k, None)
                elif k in x:
                    cur[k] = x[k]
            if cur != (it.get("x") or {}):
                if cur:
                    it["x"] = cur
                else:
                    it.pop("x", None)
                n += 1
        if n:
            _srv._save(_srv.DB_FILE, db)
    journal("tableur", f"{n} fiches complétées")
    return {"ok": True, "changed": n}


# ----------------------------------------------------------------------------- aiguillage
def _bytes(h, body, ctype, name=None):
    h.send_response(200)
    h.send_header("Content-Type", ctype)
    h.send_header("Content-Length", str(len(body)))
    h.send_header("Cache-Control", "no-store")
    if name:
        h.send_header("Content-Disposition", f'attachment; filename="{name}"')
    h.end_headers()
    h.wfile.write(body)


def api(h, method, name, q, b):
    """Toutes les routes /api/bo/x/<name>. Renvoie toujours une réponse (erreurs en français)."""
    one = lambda k: (q.get(k) or [""])[0]
    try:
        if method == "GET":
            if name == "status":
                return h.send_json(status(h))
            if name == "log":
                return h.send_json(log_tail(q))
            if name == "backups":
                return h.send_json({"backups": backups()})
            if name == "backup-file":
                with open(_bk_name(one("name")), "rb") as f:
                    return _bytes(h, f.read(), "application/json", one("name"))
            if name == "export":
                journal("export zip", "avec photos" if one("photos") else "sans photos")
                return _bytes(h, export_zip(bool(one("photos"))), "application/zip", "briquotheque-donnees-" + time.strftime("%Y-%m-%d") + ".zip")
            if name == "fixes":
                return h.send_json({"fixes": fixes()})
            if name == "catalog":
                return h.send_json(catalog_find(q))
            if name == "params":
                return h.send_json({**params(), "expert": expert_ok(h), "local": sensitive_ok(h)})
            if name == "images":
                return h.send_json({"images": images()})
            if name in ("files", "json", "json-find", "file-raw"):
                _need(h)
                if name == "files":
                    return h.send_json({"files": files()})
                if name == "json":
                    return h.send_json(json_view(q))
                if name == "json-find":
                    return h.send_json(json_find(q))
                with open(_file(one("file")), "rb") as f:
                    return _bytes(h, f.read(), "application/json", one("file"))
            if name in ("code-files", "code", "code-version"):
                _need(h, local=True)
                if name == "code-files":
                    return h.send_json({"files": code_files(), "node": bool(shutil.which("node"))})
                rel, full = _code_path(one("file"))
                if name == "code":
                    with open(full, encoding="utf-8") as f:
                        return h.send_json({"file": rel, "content": f.read(), "versions": code_versions(rel)})
                if not re.fullmatch(r"\d{8}-\d{6}", one("id")):
                    raise Refus("Version introuvable", 404)
                with open(os.path.join(_code_keep(rel), one("id")), encoding="utf-8") as f:
                    return h.send_json({"file": rel, "id": one("id"), "content": f.read()})
            raise Refus("Outil inconnu", 404)
        # ---- POST
        if name == "expert":   # {password} : mode expert pour 2 heures ; {off: true} : le quitter
            if b.get("off"):
                _expert.pop(_tok(h), None)
                return h.send_json({"ok": True, "expert": False})
            if not _srv.auth.check_password(str(b.get("password") or "")):
                time.sleep(1.2)
                journal("mode expert refusé")
                raise Refus("Mot de passe incorrect", 403)
            _expert[_tok(h)] = time.time() + EXPERT_SECONDS
            journal("mode expert")
            return h.send_json({"ok": True, "expert": True})
        if name == "rescue":   # page de secours : mot de passe du back office à chaque fois (celui de l'appli s'il n'existe pas encore)
            if not sensitive_ok(h):
                raise Refus("Le secours n'est possible que depuis le réseau local", 403)
            ip, acc, pw = h.client_ip(), _srv.backoffice_acces, b.get("password") if isinstance(b.get("password"), str) else ""
            if _srv.auth.too_many_attempts(ip):
                raise Refus("Trop de tentatives. Réessayez dans 15 minutes.", 429)
            try:
                good = acc.check(pw) if acc.configured() else _srv.auth.check_password(pw)
            except (ValueError, TypeError):
                good = False
            if not good:
                _srv.auth.record_failure(ip, "mot de passe (secours du back office)")
                time.sleep(1.2)
                journal("secours refusé")
                raise Refus("Mot de passe incorrect", 403)
            _srv.auth.clear_failures(ip)
            if b.get("list"):
                return h.send_json({"files": rescue_list()})
            if b.get("file"):
                r = code_restore(b.get("file"), b.get("id"))
                if r.get("restart"):
                    restart_soon()
                return h.send_json(r)
            restart_soon()
            return h.send_json({"ok": True, "restart": True})
        if name == "backup":
            _srv.backup_db("manuelle")
            journal("sauvegarde")
            return h.send_json({"ok": True, "backups": backups()})
        if name == "backup-upload":   # {name, content} : une sauvegarde gardée ailleurs, redéposée ici
            d = _check_db(json.loads(str(b.get("content") or "")))
            n = "collection-" + time.strftime("%Y-%m-%d") + "-deposee-" + time.strftime("%H%M%S") + ".json"
            os.makedirs(_srv.BACKUP_DIR, exist_ok=True)
            with open(os.path.join(_srv.BACKUP_DIR, n), "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
            journal("sauvegarde déposée", n)
            return h.send_json({"ok": True, "name": n, "backups": backups()})
        if name == "backup-delete":
            os.remove(_bk_name(b.get("name")))
            journal("sauvegarde supprimée", b.get("name"))
            return h.send_json({"ok": True, "backups": backups()})
        if name == "restore":
            return h.send_json({**restore(b.get("name")), "backups": backups()})
        if name == "image":   # corps = le fichier ; ?label=… : son nom d'usage
            return h.send_json(image_add(h.body(), (q.get("label") or [""])[0]))
        if name == "image-delete":
            return h.send_json(image_del(b.get("name")))
        if name == "fix":
            return h.send_json(fix_set(b))
        if name == "values-bulk":
            return h.send_json(values_bulk(b))
        if name == "param":
            _need(h)
            return h.send_json({**param_set(b), **params()})
        if name == "json-edit":
            _need(h)
            return h.send_json(json_edit(b))
        if name == "restart":
            _need(h)
            restart_soon()
            return h.send_json({"ok": True})
        if name == "env":
            _need(h, local=True)
            return h.send_json({**env_set(b), **params()})
        if name == "code-save":
            _need(h, local=True)
            return h.send_json(code_save(b.get("file"), b.get("content")))
        if name == "code-restore":
            _need(h, local=True)
            return h.send_json(code_restore(b.get("file"), b.get("id")))
        if name == "import-zip":
            _need(h, local=True)
            r = import_zip(h.body())
            restart_soon(1.5)
            return h.send_json({**r, "restart": True})
        raise Refus("Outil inconnu", 404)
    except Refus as e:
        return h.send_json({"erreur": str(e), **({"besoin": e.code} if e.code else {})}, e.status)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, RecursionError, zipfile.BadZipFile) as e:
        return h.send_json({"erreur": f"Action impossible : {e}"}, 400)

#!/usr/bin/env python3
# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Briquothèque — gestionnaire de collection LEGO (serveur local, sans dépendance).

Lancement :  python3 server.py   puis ouvrir http://localhost:8765
"""
import hashlib
import ipaddress
import json
import mimetypes
import os
import re
import secrets
import subprocess
import tempfile
import threading
import time
import urllib.parse
import uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
perso = None   # extensions locales (fichiers privés facultatifs ; absents : rien ne change)

import copy
import http.client
import secrets
import shutil
import subprocess
import sys
from http.cookies import SimpleCookie


# ── GARDE DE DÉMARRAGE DU BACK OFFICE ─────────────────────────────────────────────────────────────────────────────
# À NE PAS RETIRER NI DÉPLACER : elle doit rester ici, AVANT les imports de l'application (auth, sources, backoffice…).
#   1) elle applique les réglages de démarrage faits dans le back office (data/backoffice_env.json : port, proxy, démo) ;
#   2) si un fichier .py modifié depuis le back office empêche le serveur de démarrer, elle remet sa version précédente
#      (au 2e démarrage raté) et relance le serveur. Le code « à l'essai » est noté dans data/backoffice_boot.json.
def _bo_boot():
    if os.environ.get("BQ_DEMO") == "1":
        return
    root = os.path.dirname(os.path.abspath(__file__))
    data = os.environ.get("BQ_DATA") or os.path.join(root, "data")
    try:
        with open(os.path.join(data, "backoffice_env.json"), encoding="utf-8") as f:
            for k, v in json.load(f).items():
                if k not in ("PORT", "BQ_PROXIES", "BQ_DEMO_SITE") or not isinstance(v, str) or (k == "BQ_DEMO_SITE" and os.environ.get("BQ_COPIE") == "1"):
                    continue   # (la copie de travail n'a jamais de démo)
                if v:
                    os.environ[k] = v
                else:
                    os.environ.pop(k, None)
    except (OSError, ValueError, AttributeError):
        pass
    path = os.path.join(data, "backoffice_boot.json")
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
        pend = st.get("pending") or {}
    except (OSError, ValueError, AttributeError):
        return
    if not pend:
        return
    restored = False
    st["tries"] = int(st.get("tries") or 0) + 1
    if st["tries"] >= 2:   # un démarrage a déjà échoué avec ce code : les versions précédentes sont remises
        for rel, bak in pend.items():
            try:
                shutil.copy(bak, os.path.join(root, *str(rel).split("/")))
            except OSError as e:
                print("Garde de démarrage : impossible de remettre", rel, e, flush=True)
        print("Garde de démarrage : le serveur ne démarrait plus — version précédente remise pour", ", ".join(sorted(pend)), flush=True)
        st, restored = {"pending": {}, "tries": 0, "restored": sorted(pend), "restored_at": int(time.time())}, True
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(st, f)
    except OSError:
        pass
    if restored:
        os.execv(sys.executable, [sys.executable, "-u", os.path.abspath(__file__)])   # relance avec le code remis


_bo_boot()
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────

import auth
import sources
import backoffice   # back office : personnalisation sans code (page /backoffice, réglages data/backoffice.json)
import backoffice_outils   # back office : outils du serveur (sauvegardes, fichiers, paramètres, code… — /api/bo/x/…)
import backoffice_acces   # back office : son mot de passe, ses sessions, sa page d'entrée (/backoffice)

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, "static")
DATA = os.environ.get("BQ_DATA") or os.path.join(ROOT, "data")
DEMO = os.environ.get("BQ_DEMO") == "1"
COPIE = os.environ.get("BQ_COPIE") == "1"   # copie de travail (back office) : aucune tâche de fond, aucun relevé de prix automatique
backoffice.init(DATA)
DEMO_COOKIE = "d2"   # valeur du cookie de la démo (les anciens cookies « 1 » ne comptent plus)
if os.environ.get("BQ_SIMULATE_OUTAGE") == "1":   # tests : tous les sites extérieurs « en panne » (l'appli doit rester utilisable)
    import urllib.request as _ur, urllib.error as _ue
    def _down(*a, **k):
        raise _ue.URLError("panne simulée")
    _ur.urlopen = _down
    _ur.OpenerDirector.open = lambda self, *a, **k: _down()   # instance de démonstration publique (sans connexion, données remises à zéro)
DB_FILE = os.path.join(DATA, "collection.json")
CACHE_FILE = os.path.join(DATA, "cache_sets.json")
IMG_DIR = os.path.join(ROOT, "data", "images")   # partagé avec la démo (même cache d'images, limité en taille)
UPLOAD_DIR = os.path.join(DATA, "uploads")
CACHE_TTL = 24 * 3600
PORT = int(os.environ.get("PORT", "8765"))
HOST = os.environ.get("HOST", "0.0.0.0")
# proxys de confiance (nginx…) : seules ces adresses (et la machine elle-même) peuvent annoncer l'adresse réelle du visiteur
# (en-têtes X-Real-IP / X-Forwarded-For / X-Forwarded-Proto). Ex. : BQ_PROXIES=192.168.1.10,192.168.1.11
TRUSTED_PROXIES = {x.strip() for x in os.environ.get("BQ_PROXIES", "").split(",") if x.strip()}
DEMO_SITE = os.environ.get("BQ_DEMO_SITE") == "1"   # démonstration publique /demo : désactivée par défaut
SEED_DIR = os.path.join(ROOT, "seed", "data")   # exemples livrés : copiés dans data/ au premier lancement
_setup = {"code": None}   # code d'installation (première installation depuis Internet)


def install_seed():
    """Premier lancement (pas encore de collection) : copie les exemples livrés — une fiche de démo de chaque type et un
    inventaire, avec les données de catalogue utiles pour qu'ils s'affichent même sans clé API. Rien n'est écrasé."""
    if DEMO or os.path.exists(DB_FILE) or not os.path.isdir(SEED_DIR):
        return False
    for dp, _, files in os.walk(SEED_DIR):
        rel = os.path.relpath(dp, SEED_DIR)
        os.makedirs(os.path.join(DATA, rel), exist_ok=True)
        for f in files:
            dst = os.path.join(DATA, rel, f)
            if not os.path.exists(dst):
                shutil.copy(os.path.join(dp, f), dst)
    print("Premier lancement : exemples installés (liste « Exemples »).", flush=True)
    return True


def _self_ips():
    """Adresses de cette machine (ses propres visites des pages publiques, des tests par exemple, ne comptent pas)."""
    import socket
    out = {"127.0.0.1", "::1"}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as so:   # adresse de la carte réseau principale (aucun paquet envoyé)
            so.connect(("192.0.2.1", 9))
            out.add(so.getsockname()[0])
    except OSError:
        pass
    return out


SELF_IPS = _self_ips()

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
# Verrou des fichiers JSON (lecture-modification-écriture). Réentrant : une fonction qui le tient peut en appeler
# une autre qui le reprend (sinon le fil se bloquerait lui-même, et tout le serveur avec lui).
lock = threading.RLock()

try:   # diagnostic d'un blocage : « kill -USR1 <pid> » écrit les piles de tous les fils dans data/threads.txt
    import faulthandler
    import signal
    _fh = open(os.path.join(DATA, "threads.txt"), "a")
    faulthandler.register(signal.SIGUSR1, file=_fh, all_threads=True)
except Exception:
    pass


# ---------------------------------------------------------------- stockage
def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


_UP_RE = re.compile(r"/api/upload/([0-9a-f]{16,40})")


# ---- PRIORITÉ À L'ÉCRAN (22/11) : les tâches de fond passent après ce qui est en cours à l'écran (voir p_priorite_ecran.py)
import urllib.request as _ur_prio
_PRIO = {"t": 0.0}
_prio_tl = threading.local()
_PRIO_POLL = ("/api/ping", "/api/novelties/count", "/api/visits", "/api/scan-status", "/api/moc-scan-status", "/api/offline-pack", "/api/bo/x/status")


def prio_seen(path):
    """Requête de l'appli : l'écran est actif (sauf appels automatiques)."""
    poll = str(path or "").startswith(_PRIO_POLL)
    _prio_tl.fg = not poll
    if not poll:
        _PRIO["t"] = time.time()


def prio_wait(maxw=20):
    """Tâche de fond : attendre que l'écran soit calme depuis 3 s (au plus maxw secondes)."""
    if getattr(_prio_tl, "fg", False):
        return
    end = time.time() + maxw
    while time.time() - _PRIO["t"] < 3 and time.time() < end:
        time.sleep(0.5)


_urlopen0 = _ur_prio.urlopen


def _urlopen_prio(*a, **k):
    prio_wait()
    return _urlopen0(*a, **k)


_ur_prio.urlopen = _urlopen_prio
_start0, _run0 = threading.Thread.start, threading.Thread.run


def _start_prio(self):
    self._bq_fg = getattr(_prio_tl, "fg", False)   # lancée par une action à l'écran : elle en garde la priorité
    return _start0(self)


def _run_prio(self):
    tgt = getattr(self, "_target", None)
    if getattr(tgt, "__name__", "") == "process_request_thread" or getattr(self, "_bq_fg", False):
        _prio_tl.fg = bool(getattr(self, "_bq_fg", False))
    else:
        try:
            os.setpriority(os.PRIO_PROCESS, threading.get_native_id(), 10)   # (tâche de fond : priorité processeur basse)
        except Exception:
            pass
    return _run0(self)


threading.Thread.start, threading.Thread.run = _start_prio, _run_prio


def _save(path, data):
    if path == DB_FILE and not DEMO:
        try:
            lists_warm()   # (la collection recalculée en coulisse : prête pour l'écran — 22/11)
        except NameError:
            pass
    tmp = path + ".tmp"
    if path == DB_FILE and isinstance(data, dict):   # collection : liens parent / enfant vérifiés à chaque enregistrement (links_fix)
        try:
            _nl = links_fix(data)
            if _nl:
                print(f"Liens entre fiches : {_nl} correction(s) à l'enregistrement (fiche remise seule, ou marque « d'origine » retirée)", flush=True)
        except Exception as e:
            print("Vérification des liens impossible :", e, flush=True)
        try:
            _np = fig_photos_on_sheets(data)
            if _np:
                print(f"Figurines : leurs données rangées sur leur propre fiche ({_np} mise(s) à jour)", flush=True)
        except Exception as e:
            print("Images des figurines : rangement impossible :", e, flush=True)
        try:
            _pm = parts_merge_same(data)
            if _pm:
                print(f"Pièces en double regroupées : {_pm} ligne(s) fondue(s) dans une autre", flush=True)
        except Exception as e:
            print("Regroupement des pièces impossible :", e, flush=True)
        try:
            _nm = figs_merge_identical(data)
            if _nm:
                print(f"Fiches identiques regroupées : {_nm} fiche(s) fondue(s) dans une autre (nombre d'exemplaires additionné)", flush=True)
        except Exception as e:
            print("Regroupement des fiches identiques impossible :", e, flush=True)
    compact = os.path.basename(path).startswith("cache_")   # caches : format compact (plus petit, plus rapide) ; collection : lisible
    track = os.path.basename(path) in ("collection.json", "notes.json")   # photos qui ne servent plus : supprimées tout de suite
    before = set()
    if track and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            before = set(_UP_RE.findall(f.read()))
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, **({"separators": (",", ":")} if compact else {"indent": 1}))
    if track:
        with open(tmp, encoding="utf-8") as f:
            gone = before - set(_UP_RE.findall(f.read()))
    os.replace(tmp, path)
    if track and gone:   # plus citées : gardées 2 jours (une fiche réenregistrée depuis un autre appareil peut encore les citer), puis effacées
        try:
            orph = _load(ORPHANS_FILE, {})
            now = int(time.time())
            for h in gone:
                orph.setdefault(h, now)
            with open(ORPHANS_FILE + ".tmp", "w", encoding="utf-8") as f:
                json.dump(orph, f)
            os.replace(ORPHANS_FILE + ".tmp", ORPHANS_FILE)
        except Exception as e:
            print("Ménage des photos impossible :", e, flush=True)


FIG_OWN_MAP = {"photo_url": "photo_url", "alt_photos": "alt_photos", "alt_names": "alt_names", "alt_hidden": "alt_hidden", "main_name": "main_name",
               "name": "display_name", "rb_fig": "rb_fig", "fig_swaps": "fig_swaps", "swap_price": "swap_price", "accessories": "accessories"}   # set (fig_mods) → fiche
FIG_OWN_LOT = ("fig_swaps", "swap_price", "accessories")   # valables pour le LOT de la figurine dans le set : déplacés si elle y a UNE seule fiche
FIG_IMG_KEYS = ("photo_url", "alt_photos", "alt_names", "alt_hidden", "main_name")   # (les images : toujours sur la fiche, p_photos_fiches.py)


def fig_name_spread(db, number, old, new, skip=None):
    """Nom donné à une figurine : ses autres fiches (même numéro) sans nom à elles, ou qui avaient l'ancien nom, le prennent aussi
    (un nom différent choisi exprès n'est jamais écrasé). Rend le nombre de fiches renommées."""
    old, new, n = old or "", new or "", 0
    if old == new or not number:
        return 0
    for x in db.get("items") or []:
        if x is skip or not isinstance(x, dict) or x.get("kind") != "fig" or x.get("number") != number or x.get("indiv_copy"):
            continue
        if (x.get("display_name") or "") in ("", old) and (x.get("display_name") or "") != new:
            if new:
                x["display_name"] = new
            else:
                x.pop("display_name", None)
            n += 1
    return n


def fig_photos_on_sheets(db):
    """Tout ce qui appartient à une figurine d'origine est rangé dans SA fiche (règle du 20/11) — images, nom, pièces échangées, chiffrage,
    accessoires, version Rebrickable ; le set n'en garde qu'une copie (fig_mods[n°], marquée « _own »). Modifié par le set depuis la dernière
    copie → reporté sur la fiche ; sinon la fiche fait foi et le set est recopié. Rend le nombre de changements."""
    import copy as _cp
    items = db.get("items") or []
    H = {i.get("id"): i for i in items if isinstance(i, dict)}
    kids = {}
    for i in items:
        if isinstance(i, dict) and i.get("set_orig") and i.get("attached_to") in H:
            kids.setdefault((i["attached_to"], i.get("number")), []).append(i)
    n = 0
    for (hid, num), ks in kids.items():
        h = H[hid]
        keys = [k for k in FIG_OWN_MAP if len(ks) == 1 or k not in FIG_OWN_LOT]   # (lot : seulement avec une seule fiche)
        mods = h.get("fig_mods") if isinstance(h.get("fig_mods"), dict) else {}
        m = mods.get(num) if isinstance(mods.get(num), dict) else {}
        cur = {k: _cp.deepcopy(m[k]) for k in keys if m.get(k)}
        mark = m.get("_own")
        if mark is None:   # première fois : ce que le set gardait va sur la fiche là où elle n'a rien (jamais écrasé)
            for c in ks:
                for k, v in cur.items():
                    if not c.get(FIG_OWN_MAP[k]):
                        c[FIG_OWN_MAP[k]] = _cp.deepcopy(v); n += 1
        elif cur != {k: v for k, v in mark.items() if k in keys}:   # modifié « par le set » depuis la dernière copie : reporté sur la fiche
            for c in ks:
                for k in keys:
                    f = FIG_OWN_MAP[k]
                    if k in cur:
                        if c.get(f) != cur[k]:
                            if k == "name":   # (renommée par le set : ses autres fiches aussi)
                                fig_name_spread(db, num, c.get(f), cur[k], skip=c)
                            c[f] = _cp.deepcopy(cur[k]); n += 1
                    elif k in mark and c.get(f):
                        c.pop(f, None); n += 1
        src = next((c for c in ks if any(c.get(FIG_OWN_MAP[k]) for k in keys)), ks[0])   # la fiche fait foi : sa copie dans le set
        want = {k: _cp.deepcopy(src[FIG_OWN_MAP[k]]) for k in keys if src.get(FIG_OWN_MAP[k])}
        if not want and num not in mods:
            continue
        nm = {k: v for k, v in m.items() if k not in keys and k not in ("_own", "_img")}
        nm.update(_cp.deepcopy(want)); nm["_own"] = _cp.deepcopy(want)
        if nm != m:
            mods[num] = nm; h["fig_mods"] = mods; n += 1
    for h in items:   # figurine partie du set : la copie gardée par le set n'a plus lieu d'être (la fiche a tout)
        mods = h.get("fig_mods") if isinstance(h, dict) and isinstance(h.get("fig_mods"), dict) else None
        if not mods:
            continue
        for num in list(mods):
            m = mods[num]
            if not isinstance(m, dict) or (h.get("id"), num) in kids:
                continue
            mk = m.get("_own", m.get("_img"))
            if mk is not None and {k: m[k] for k in mk if k in m} == mk:
                rest = {k: v for k, v in m.items() if k not in mk and k not in ("_own", "_img")}
                if rest:
                    mods[num] = rest
                else:
                    del mods[num]
                n += 1
    return n


def parts_merge_same(db):
    """Pièces à commander : une seule ligne par (liste, référence, couleur, état reçue ou non) — quantités additionnées, liens et notes gardés.
    La ligne gardée est la plus ancienne. Rend le nombre de lignes fondues."""
    groups = {}
    for it in db.get("items") or []:
        if isinstance(it, dict) and it.get("kind") == "part" and it.get("part_num"):
            groups.setdefault((it.get("list_id"), str(it.get("part_num")), str(it.get("color_id")), bool(it.get("got")),
                               bool(it.get("ordered") or it.get("cmd_m"))), []).append(it)   # (commandée : jamais fondue avec une nouvelle ligne — 22/11)
    gone = set()
    for same in groups.values():
        if len(same) < 2:
            continue
        same.sort(key=lambda i: (i.get("added_at") or 0, i["id"]))
        keep = same[0]
        for o in same[1:]:
            try:
                keep["quantity"] = int(keep.get("quantity", 1) or 1) + int(o.get("quantity", 1) or 1)
            except (TypeError, ValueError):
                continue
            links = list(keep.get("inv_links") or [])
            for ln in o.get("inv_links") or []:
                if ln not in links:
                    links.append(ln)
            if links:
                keep["inv_links"] = links
            if (o.get("notes") or "").strip() and (o.get("notes") or "").strip() not in (keep.get("notes") or ""):
                keep["notes"] = ((keep.get("notes") or "").strip() + "\n" + o["notes"].strip()).strip()
            for k in ("part_name", "bricklink", "color_name", "color_rgb", "element_id", "image"):
                if not keep.get(k) and o.get(k):
                    keep[k] = o[k]
            gone.add(o["id"])
        keep["updated_at"] = int(time.time())
    if gone:
        db["items"] = [i for i in db["items"] if i.get("id") not in gone]
    return len(gone)


FIG_SAME_SKIP = ("id", "added_at", "updated_at", "quantity")   # ce qui peut différer entre deux fiches « identiques »


def figs_merge_identical(db):
    """Fiches de figurine strictement identiques au même endroit (même set/MOC, ou seules dans la même liste) : une seule, avec le nombre
    d'exemplaires additionné ; la plus ancienne est gardée. Jamais : figurine d'origine, exemplaire mis à part, copie pas encore modifiée,
    copie en attente ; ni si le back office le demande (noMerge). Rend le nombre de fiches fondues."""
    try:
        if bo_behav("noMerge"):
            return 0
    except Exception:
        pass
    groups = {}
    for it in db.get("items") or []:
        if not isinstance(it, dict) or it.get("kind") != "fig" or it.get("set_orig") or it.get("indiv") or it.get("indiv_copy") or it.get("dup_pending"):
            continue
        k = json.dumps({x: v for x, v in it.items() if x not in FIG_SAME_SKIP}, sort_keys=True, ensure_ascii=False)
        groups.setdefault(k, []).append(it)
    gone = set()
    for same in groups.values():
        if len(same) < 2:
            continue
        same.sort(key=lambda i: (i.get("added_at") or 0, i["id"]))
        keep = same[0]
        try:
            keep["quantity"] = sum(max(1, int(i.get("quantity", 1) or 1)) for i in same)
        except (TypeError, ValueError):
            continue
        keep["updated_at"] = int(time.time())
        gone |= {i["id"] for i in same[1:]}
    if gone:
        db["items"] = [i for i in db["items"] if i.get("id") not in gone]
    return len(gone)


def _upload_refs():
    """Photos (envoyées) citées dans les données : fiches, notes, scans, liens… (pas les caches ni les sauvegardes)."""
    refs = set()
    for name in os.listdir(DATA):
        if name.endswith(".json") and not name.startswith("cache_"):
            try:
                with open(os.path.join(DATA, name), encoding="utf-8") as f:
                    refs |= set(_UP_RE.findall(f.read()))
            except OSError:
                pass
    return refs


def uploads_drop(hashes):
    """Supprime ces photos (et leurs miniatures) si plus rien ne les cite."""
    used = _upload_refs()
    up, th = os.path.join(DATA, "uploads"), os.path.join(DATA, "thumbs")
    n = 0
    for h in set(hashes) - used:
        for d in (up, th):
            if not os.path.isdir(d):
                continue
            for name in os.listdir(d):
                if name.split(".")[0].split("_")[0] == h:
                    try:
                        os.remove(os.path.join(d, name))
                        n += 1
                    except OSError:
                        pass
    return n


ORPHANS_FILE = os.path.join(DATA, "cache_upload_orphans.json")   # photo → heure où plus aucune fiche ne la cite
ORPHAN_GRACE = 2 * 86400


def uploads_gc(min_age=86400):
    """Ménage : photos envoyées mais plus (ou jamais) utilisées, de plus d'un jour (le temps de finir une fiche) ;
    une photo retirée d'une fiche est gardée 2 jours après son retrait."""
    up = os.path.join(DATA, "uploads")
    if not os.path.isdir(up):
        return 0, 0
    return 0, 0   # (20/11 : les photos envoyées restent TOUJOURS sur le serveur — plus aucune suppression automatique)
    used, now, olds, size = _upload_refs(), time.time(), set(), 0
    orph = _load(ORPHANS_FILE, {})
    for name in os.listdir(up):
        h, p = name.split(".")[0], os.path.join(up, name)
        if h in used or now - os.path.getmtime(p) <= min_age or now - orph.get(h, 0) <= ORPHAN_GRACE:
            continue
        olds.add(h)
        size += os.path.getsize(p)
    n = uploads_drop(olds) if olds else 0
    try:   # liste des retirées : sans celles effacées ou de nouveau citées
        keep = {h: t for h, t in orph.items() if h not in olds and h not in used and any(x.startswith(h) for x in os.listdir(up))}
        with open(ORPHANS_FILE + ".tmp", "w", encoding="utf-8") as f:
            json.dump(keep, f)
        os.replace(ORPHANS_FILE + ".tmp", ORPHANS_FILE)
    except Exception:
        pass
    th = os.path.join(DATA, "thumbs")   # miniatures dont la photo n'existe plus
    if os.path.isdir(th):
        have = {name.split(".")[0] for name in os.listdir(up)}
        for name in os.listdir(th):
            if re.fullmatch(r"[0-9a-f]{16,40}_\d+\.\w+", name) and name.split("_")[0] not in have:
                try:
                    os.remove(os.path.join(th, name))
                except OSError:
                    pass
    return len(olds), size


def uploads_keeper():
    """Toutes les 6 heures : le ménage des photos inutilisées."""
    time.sleep(60)
    while True:
        try:
            n, size = uploads_gc()
            if n:
                print(f"Ménage des photos : {n} supprimée(s), {size // 1024} Ko libérés", flush=True)
        except Exception as e:
            print("Ménage des photos impossible :", e, flush=True)
        time.sleep(6 * 3600)


BACKUP_DIR = os.path.join(DATA, "backups")


def backup_db(tag=""):
    """Copie de la collection (filet de sécurité) : data/backups/collection-AAAA-MM-JJ[-tag].json ; les 30 jours les plus récents gardés."""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        name = "collection-" + time.strftime("%Y-%m-%d") + (f"-{tag}-" + time.strftime("%H%M%S") if tag else "") + ".json"
        dst = os.path.join(BACKUP_DIR, name)
        if tag or not os.path.exists(dst):
            shutil.copy(DB_FILE, dst)
        names = sorted(os.listdir(BACKUP_DIR))
        daily = [n for n in names if re.fullmatch(r"collection-\d{4}-\d\d-\d\d\.json", n)]          # une par jour : les 30 dernières
        tagged = [n for n in names if re.fullmatch(r"collection-\d{4}-\d\d-\d\d-.+\.json", n)]     # copies « avant-… » : les 80 dernières
        for old in daily[:-30] + tagged[:-80]:   # (chacune de son côté : les copies ne chassent plus les quotidiennes ; autre nom : jamais effacé)
            os.remove(os.path.join(BACKUP_DIR, old))
    except Exception as e:
        print("Sauvegarde impossible :", e, flush=True)


def backup_keeper():
    while True:
        backup_db()
        time.sleep(6 * 3600)


def load_db():
    db = _load(DB_FILE, None)
    changed = False
    if not db:
        db = {"lists": [{"id": uuid.uuid4().hex[:10], "name": "Ma collection",
                         "created_at": int(time.time())}], "items": []}
        changed = True
    for l in db["lists"]:
        if l.get("kind") not in ("collection", "wishlist", "parts"):
            l["kind"] = "collection"
            changed = True
    if not db.get("wishlist_init"):  # crée une liste de souhaits par défaut, une seule fois
        db["wishlist_init"] = True
        if not any(l["kind"] == "wishlist" for l in db["lists"]):
            db["lists"].append({"id": uuid.uuid4().hex[:10], "name": "Liste de souhaits",
                                "kind": "wishlist", "created_at": int(time.time())})
        changed = True
    parts = [l for l in db["lists"] if l["kind"] == "parts"]
    if parts and not any(l.get("default") for l in parts):   # « À commander » d'origine : protégée
        parts[0]["default"] = True
        changed = True
    if not db.get("parts_init"):  # liste « Pièces à commander », créée une seule fois
        db["parts_init"] = True
        if not any(l["kind"] == "parts" for l in db["lists"]):
            db["lists"].append({"id": uuid.uuid4().hex[:10], "name": "À commander",
                                "kind": "parts", "default": True, "created_at": int(time.time())})
        changed = True
    if changed:
        _save(DB_FILE, db)
    return db


def list_kinds(db=None):
    db = db or _load(DB_FILE, {"lists": []})
    return {l["id"]: l.get("kind", "collection") for l in db["lists"]}


MARKET_TTL = 7 * 86400   # annonces d'un set : relues chaque semaine (en fond, quota du jour)
BL_QUOTA_FILE = os.path.join(DATA, "bl_quota.json")
BL_DAY_MAX = 4800   # BrickLink : 5 000 appels par jour au plus


def _bl_before():
    """Compte les appels à l'API BrickLink du jour ; au-delà de la limite : erreur (BrickOwl prend le relais)."""
    day = time.strftime("%Y-%m-%d")
    with _bl_lock:
        q = _load(BL_QUOTA_FILE, {})
        if q.get("day") != day:
            q = {"day": day, "n": 0}
        if q["n"] >= BL_DAY_MAX:
            raise RuntimeError("Quota BrickLink du jour atteint")
        q["n"] += 1
        _save(BL_QUOTA_FILE, q)


_bl_lock = threading.Lock()
BL_STATE_FILE = os.path.join(DATA, "bl_state.json")   # {"alert": {"msg", "t"}} : BrickLink refuse (adresse IP changée…)
_bl_state = {"alert": (_load(BL_STATE_FILE, {}) or {}).get("alert"), **{k: (_load(BL_STATE_FILE, {}) or {}).get(k) for k in ("last_ok", "fail_since")}}


def _bl_state_save():
    _save(BL_STATE_FILE, {k: _bl_state.get(k) for k in ("alert", "last_ok", "fail_since") if _bl_state.get(k)})


def _bl_fail():
    """BrickLink ne répond pas (maintenance, réseau, refus) : début de la panne retenu (21/11 soir)."""
    if not _bl_state.get("fail_since"):
        _bl_state["fail_since"] = int(time.time())
        _bl_state_save()


def bl_down():
    """BrickLink sans réponse depuis plus de 24 h (et toujours en panne) → BrickOwl prend le relais (fiches consultées, actualisation du jour)."""
    if DEMO or not bl_on() or not _bl_state.get("fail_since"):
        return False
    last = _bl_state.get("last_ok")
    if not last:   # (jamais noté : le plus récent relevé BrickLink gardé)
        try:
            last = max((v.get("t") or 0) for k, v in _parts_cache().items() if k[:3] in ("bm:", "fu:", "bp:") and isinstance(v, dict) and v.get("src") == "BrickLink") or 0
        except ValueError:
            last = 0
        _bl_state["last_ok"] = last or _bl_state["fail_since"]
        _bl_state_save()
    return time.time() - max(last or 0, 0) > 86400


def _bl_error(msg):
    if re.search(r"\bIP\b|IP_|_IP", msg.upper()) or "MISMATCH" in msg.upper():   # l'adresse IP du serveur n'est plus celle du jeton
        _bl_state["alert"] = {"msg": msg[:200], "t": int(time.time())}
        _save(BL_STATE_FILE, {"alert": _bl_state["alert"]})


def _bl_ok():
    now = int(time.time())
    back = bool(_bl_state.get("fail_since"))   # (il était en panne : il revient)
    if _bl_state["alert"] or _bl_state.get("fail_since") or now - (_bl_state.get("last_ok") or 0) > 600:   # (réussite : notée au plus toutes les 10 min)
        _bl_state.update(alert=None, fail_since=None, last_ok=now)
        _bl_state_save()
    if back:   # BrickLink revient : le secours BrickOwl activé à la main se désactive tout seul (21/11 soir)
        def off():
            with lock:
                st = _load(sources.SETTINGS_FILE, {})
                if st.get("ref_site") != "brickowl":
                    return
                st["ref_site"], st["bl_back"] = "bricklink", now
                _save(sources.SETTINGS_FILE, st)
                os.chmod(sources.SETTINGS_FILE, 0o600)
            _ref["t"] = 0
            try:
                markets_reapply()
            except Exception as e:
                print("Retour de BrickLink :", e, flush=True)
        threading.Thread(target=off, daemon=True).start()


sources.bl_hooks.update(before=None if DEMO else _bl_before, error=None if DEMO else _bl_error, ok=None if DEMO else _bl_ok, fail=None if DEMO else _bl_fail)   # la démo n'utilise jamais BrickLink




def bl_today():
    q = _load(BL_QUOTA_FILE, {})
    return q.get("n", 0) if q.get("day") == time.strftime("%Y-%m-%d") else 0


def rb_bl_color(rb_id):
    """N° de couleur Rebrickable → n° BrickLink (le plus petit s'il y en a plusieurs)."""
    best = None
    for blc, rbc in (moc_color_maps().get("blrb") or {}).items():
        if str(rbc) == str(rb_id) and (best is None or int(blc) < int(best)):
            best = blc
    return best


def bo_bl_color(bo_name):
    """Couleur BrickOwl (nom) → n° BrickLink."""
    best = None
    for blc, bo in (moc_color_maps().get("bl") or {}).items():
        if bo == bo_name and (best is None or int(blc) < int(best)):
            best = blc
    return best


_bl_night = threading.local()   # par fil : .on = passe de nuit ; .consult = fiche ouverte ou bouton « Actualiser les prix »
def price_cfg():
    """Réglages › Prix : {"every_h": actualisation automatique toutes les X h, "budget": appels BrickLink par jour pour elle,
    "consult_h": fiche consultée relue si son prix a plus de X h} — 24 h, 2 000 appels, 24 h par défaut."""
    p = _load(sources.SETTINGS_FILE, {}).get("prices") or {}
    num = lambda k, d, lo, hi: max(lo, min(hi, int(p.get(k) or d)))
    return {"every_h": num("every_h", 24, 1, 168), "budget": num("budget", BL_BG_DAY, 100, BL_DAY_MAX), "consult_h": num("consult_h", 24, 1, 168)}


def consult_ttl():
    """Fiche ouverte / bouton : un prix BrickLink plus vieux que ça est relu (Réglages › Prix, 24 h par défaut)."""
    return price_cfg()["consult_h"] * 3600


def bl_keep_known(rec):
    """Vrai si ce relevé BrickLink doit être gardé tel quel (crédits BrickLink économisés) :
    - passe de nuit : jamais gardé (c'est elle qui rafraîchit) ;
    - fiche ouverte / bouton « Actualiser les prix » : gardé s'il a moins de 24 h ;
    - partout ailleurs (listes, recherche, inventaires) : toujours gardé."""
    if not rec or rec.get("src") != "BrickLink" or getattr(_bl_night, "on", False):
        return False
    if getattr(_bl_night, "consult", False):
        return time.time() - rec.get("t", 0) < consult_ttl()
    return True


def bl_part(blpart, blcolor, conds=("U", "N"), max_age=7 * 86400):
    """Annonces BrickLink d'une pièce dans une couleur (gardées) : {"used", "new", "t", "src"} ou None."""
    key = f"bp:{blpart}|{blcolor}"
    c = _parts_cache().get(key)
    have = c and all((("used" if x == "U" else "new") in c) for x in conds)   # (neuf et/ou occasion déjà relevés)
    if have and (bl_keep_known(c) or time.time() - c.get("t", 0) < max_age):
        return c
    out = dict(c or {})
    for x in conds:
        kx = "used" if x == "U" else "new"
        out[kx] = bl_keep_rec(sources.bl_guide("PART", blpart, x, color_id=blcolor), (c or {}).get(kx))   # (moins de 3 ventes : ancien prix gardé)
    out.update(t=int(time.time()), src="BrickLink")
    _parts_cache_put(key, out)
    return out


def bl_zone_of(kind, number):
    """Zone où BrickLink a des annonces pour ce set / cette figurine : « France », « UE », « monde » (ou "" si pas relevé).
    Sert aux liens « BrickLink » des pages publiques : ils ouvrent les annonces de cette zone."""
    rec = _parts_cache().get(("fu:" if kind == "fig" else "bm:") + str(number or "")) or {}
    zones = {rec.get("zone"), (rec.get("used") or {}).get("zone"), (rec.get("new") or {}).get("zone")}   # (figurine : l'occasion est à la racine)
    return next((z for z in sources.bl_zone_order() + ["France", "UE", "monde"] if z in zones), "")   # (la première zone réglée qui a des annonces)


def bl_part_ann(blpart, blcolor, max_age=7 * 86400):
    """Pièce à ACHETER : médiane des annonces BrickLink en cours (neuf, occasion), sinon des ventes ; gardé 7 jours (« bpa: ») — 21/11."""
    key = f"bpa:{blpart}|{blcolor}"
    c = _parts_cache().get(key)
    if c and time.time() - c.get("t", 0) < max_age:
        return c
    out = {"used": sources.bl_guide_ann("PART", blpart, "U", color_id=blcolor), "new": sources.bl_guide_ann("PART", blpart, "N", color_id=blcolor),
           "t": int(time.time()), "src": "BrickLink"}
    _parts_cache_put(key, out)
    return out


def bp_unit(rec):
    """Prix unitaire d'une pièce relevé sur BrickLink : moyenne d'occasion, sinon neuve."""
    if not rec:
        return None
    return ((rec.get("used") or {}).get("unit")) or ((rec.get("new") or {}).get("unit"))


_rbbl = {"m": None, "t": 0}


def rbbl_map():
    if not _rbbl["m"] or time.time() - _rbbl["t"] > 3600:
        m = {}
        for blc, rbc in (moc_color_maps().get("blrb") or {}).items():
            if str(rbc) not in m or int(blc) < int(m[str(rbc)]):
                m[str(rbc)] = blc
        _rbbl.update(m=m, t=time.time())
    return _rbbl["m"]


def bl_on():
    return not DEMO and bool(sources.bricklink_keys())


BRICKSET_FILE = os.path.join(DATA, "cache_brickset.json")   # {n° de set: {"launch", "exit", "t"}} — dates LEGO (Brickset, 21/11 soir)


_bsm = {"m": None, "d": {}}


def bs_rec(number):
    """Fiche Brickset d'un set (cache, relu seulement s'il a changé)."""
    try:
        mt = os.path.getmtime(BRICKSET_FILE)
    except OSError:
        return None
    if mt != _bsm["m"]:
        _bsm.update(m=mt, d=_load(BRICKSET_FILE, {}) or {})
    return _bsm["d"].get(number or "")


def with_bs(info, number):
    """Catalogue d'un set d'après Brickset : prix magasin en € (devant les autres sources), pièces et figurines s'il en manque (21/11 soir)."""
    r = bs_rec(number)
    if not r or not isinstance(info, dict):
        return info
    out = dict(info)
    if r.get("retail"):
        out["retail"] = r["retail"]
    if r.get("pieces") and not out.get("pieces"):
        out["pieces"] = r["pieces"]
    if r.get("minifigs") and not out.get("minifig_count"):
        out["minifig_count"] = r["minifigs"]
    return out


def bs_dates(number):
    r = (_load(BRICKSET_FILE, {}) or {}).get(number or "")
    return {"launch": r.get("launch"), "exit": r.get("exit")} if r and (r.get("launch") or r.get("exit")) else None


def brickset_fill(force=False):
    """Dates de mise en vente / de retrait de mes sets (collection, souhaits) : les nouveaux, et tous les 30 jours."""
    if DEMO or COPIE or not sources.brickset_key():
        return 0
    nums = sorted({i["number"] for i in load_db()["items"] if (i.get("kind") or "set") == "set" and re.fullmatch(r"\d+-\d+", str(i.get("number") or ""))})
    cur, now = _load(BRICKSET_FILE, {}), time.time()
    todo = [n for n in nums if force or n not in cur or now - (cur[n] or {}).get("t", 0) > 30 * 86400]
    if not todo:
        return 0
    try:
        got = sources.brickset_dates(todo)
    except Exception as e:
        print("Brickset :", e, flush=True)
        return 0
    with lock:
        cur = _load(BRICKSET_FILE, {})
        for n in todo:
            cur[n] = {**(got.get(n) or {"launch": None, "exit": None}), "t": int(now)}
        _save(BRICKSET_FILE, cur)
    return len(got)


def brickset_one(number):
    """Un set pas encore relevé (fiche ouverte) : sa fiche Brickset, en fond."""
    try:
        got = sources.brickset_dates([number])
    except Exception as e:
        print("Brickset :", e, flush=True)
        return
    with lock:
        cur = _load(BRICKSET_FILE, {})
        cur[number] = {**(got.get(number) or {"launch": None, "exit": None}), "t": int(time.time())}
        _save(BRICKSET_FILE, cur)


ORDERS_EXTRA_DONE = os.path.join(DATA, "orders_extra_done.json")   # « commandées en plus » traitées (OK, attribuées, vers un inventaire) : {clé: {t, how}} (22/11)
ORDERS_EXTRA = os.path.join(DATA, "orders_extra.json")   # commandées en plus (non attribuées), refait à chaque lecture des commandes (22/11)
ORDERS_FILE = os.path.join(DATA, "orders_seen.json")   # {"BrickOwl:<n°>": {"date", "status", "items": [[éléments, références, couleur, qté, nom]]}}
_ord = {"t": 0, "busy": False}


BL_ORDER_OFF = {"CANCELLED", "PURGED", "NPB", "NPX", "NRS", "NSS"}   # (commandes BrickLink annulées ou abandonnées : écartées)


def orders_bl_read(seen):
    """Mes commandes BrickLink (acheteur) → seen["BrickLink:<n°>"] = {date, status, status_id (8 : annulée), items} ; le détail d'une
    commande n'est lu qu'une fois. items : [[], [référence BrickLink], "", quantité, nom, "Part" | "Minifigure", prix unitaire payé, "couleur BrickLink"]."""
    import datetime as _dt
    for o in sources.bl_get("/orders", {"direction": "out"}) or []:
        oid = str(o.get("order_id") or "")
        if not oid:
            continue
        key = "BrickLink:" + oid
        rec = seen.get(key) or {}
        try:
            t = int(_dt.datetime.fromisoformat(str(o.get("date_ordered") or "").replace("Z", "+00:00")).timestamp())
        except ValueError:
            t = rec.get("date") or int(time.time())
        st = str(o.get("status") or "").upper()
        rec.update(date=t, status=st, status_id=8 if st in BL_ORDER_OFF else 1)
        if "items" not in rec:
            rows = []
            for batch in sources.bl_get(f"/orders/{oid}/items") or []:
                for x in (batch if isinstance(batch, list) else [batch]):
                    it, typ = x.get("item") or {}, str((x.get("item") or {}).get("type") or "").upper()
                    if typ not in ("PART", "MINIFIG"):
                        continue
                    rows.append([[], [str(it.get("no") or "").lower()], "", int(x.get("quantity") or 0), it.get("name") or "",
                                 "Part" if typ == "PART" else "Minifigure", float(x.get("disp_unit_price_final") or x.get("unit_price_final") or 0),
                                 str(x.get("color_id")) if typ == "PART" else None,
                                 f"https://img.bricklink.com/ItemImage/PN/{x.get('color_id')}/{it.get('no')}.png" if typ == "PART" else f"https://img.bricklink.com/ItemImage/MN/0/{it.get('no')}.png"])   # (image — 22/11)
            rec["items"] = rows
        seen[key] = rec


def orders_sync(force=False):
    """Mes commandes BrickOwl (acheteur) → les lignes de « À commander » qu'elles contiennent passent « Commandée » (date, quantité) ;
    jamais « OK » (21/11 soir). Rend {"changed": nb de lignes changées, "orders": nb de commandes, "unmatched": [noms]}."""
    if DEMO or COPIE or not (sources.brickowl_key() or sources.bricklink_keys()) or _ord["busy"] or (not force and time.time() - _ord["t"] < 3600):
        return {"changed": 0}
    _ord["busy"] = True
    try:
        seen = _load(ORDERS_FILE, {})
        if sources.bricklink_keys():   # mes commandes BrickLink (acheteur) — 22/11 ; en panne : rien, nouvel essai au passage suivant
            try:
                orders_bl_read(seen)
            except Exception as e:
                print("Commandes BrickLink :", e, flush=True)
        lst = (sources.bo_api("order/list", {"list_type": "customer", "limit": 200}) or []) if sources.brickowl_key() else []
        for o in lst:
            oid, key = str(o.get("order_id") or ""), "BrickOwl:" + str(o.get("order_id") or "")
            if not oid:
                continue
            rec = seen.get(key) or {}
            rec.update(date=int(o.get("order_date") or 0), status=o.get("status") or "", status_id=int(o.get("status_id") or 0))
            if "items" not in rec or any(len(x) < 9 for x in rec["items"]):   # (le détail : lu une seule fois ; relu une fois pour le prix payé, puis l'image — 22/11)
                items = sources.bo_api("order/items", {"order_id": oid}) or []
                rec["items"] = [[sorted({str(i.get("id")) for i in x.get("ids") or [] if i.get("type") == "item_no"}),
                                 sorted({str(i.get("id")).lower() for i in x.get("ids") or [] if i.get("type") == "design_id"}),
                                 str(x.get("color_name") or "").lower(), int(x.get("ordered_quantity") or 0) - int(x.get("refunded_quantity") or 0),
                                 x.get("name") or "", x.get("type") or "", float(x.get("base_price") or 0), None, x.get("image_small") or ""] for x in items]   # (prix unitaire payé ; image)
            seen[key] = rec
        _save(ORDERS_FILE, seen)
        cmap = {k: str(v).lower() for k, v in (moc_color_maps().get("rb") or {}).items()}
        rbbl = {str(k): str(v) for k, v in rbbl_map().items()}   # (couleur Rebrickable → BrickLink : commandes BrickLink)
        with lock:
            db = load_db()
            kinds = list_kinds(db)
            parts = [i for i in db["items"] if kinds.get(i.get("list_id")) == "parts" and i.get("kind") == "part"]
            # (réserve partagée : pièces identiques de plusieurs inventaires — 21/11 nuit)
            fnorm = lambda nm: " ".join(re.sub(r"[^\w]+", " ", re.sub(r"\b(lego|minifigure|minifig|figurine)\b", " ", str(nm or "").lower())).split())   # (nom d'une figurine, comparable)
            refs_ = lambda nm: {x.strip().lower() for x in ((re.search(r"\(([^()]*)\)\s*$", nm or "") or [None, ""])[1]).split("/") if x.strip()}   # (références du nom)
            oitems = [{"site": key.split(":", 1)[0], "order": key.split(":", 1)[1], "date": int(rec.get("date") or 0), "els": set(els),
                       "des": set(des) | refs_(name), "cn": cn, "left": q, "q": q, "name": name, "price": (rest or [None])[0],
                       "fig": fnorm(name) if typ == "Minifigure" else None, "blc": rest[1] if len(rest) > 1 else None, "img": rest[2] if len(rest) > 2 else ""}
                      for key, rec in seen.items() if rec.get("status_id") != 8   # (annulée : écartée)
                      for els, des, cn, q, name, typ, *rest in rec.get("items") or [] if q > 0 and typ in ("Part", "Minifigure")]
            cons = []   # ce qui peut recevoir une commande : (date, sorte, objet, éléments, références, couleur, quantité, commandes écartées, dès le)
            for p_ in parts:
                cons.append((int(p_.get("added_at") or 0), "part", p_, {str(p_.get("element_id") or "")} - {""},
                             {str(p_.get("bricklink") or "").lower(), str(p_.get("part_num") or "").lower()} - {""}, str(p_.get("color_id")),
                             int(p_.get("quantity") or 1), set(p_.get("o_off") or []), int(p_.get("added_at") or 0)))   # (ajoutée après la commande : surplus → vrac)
            fcache = _load(CACHE_FILE, {})
            for f_ in (i for i in db["items"] if kinds.get(i.get("list_id")) == "parts" and i.get("kind") == "fig"):   # figurines à commander : par leur nom (22/11)
                nm_ = fnorm((fcache.get("fig:" + str(f_.get("number"))) or {}).get("name") or f_.get("display_name") or "")
                fno = str(f_.get("number") or "").lower()
                if nm_ or fno:   # (BrickLink : sa référence ; BrickOwl : son nom)
                    cons.append((int(f_.get("added_at") or 0), "part", f_, set(), {fno, str(sources.bl_fig_no(fno) or "").lower()} - {""}, "fig:" + nm_,
                                 int(f_.get("quantity") or 1), set(f_.get("o_off") or []), int(f_.get("added_at") or 0)))
            linked = {(l.get("inv"), l.get("row")) for i in db["items"] for l in i.get("inv_links") or []}
            names = part_names()
            byid = {i["id"]: i for i in db["items"]}
            for ikey, inv in (db.get("inventories") or {}).items():
                snum = inv.get("set") or (byid.get(ikey) or {}).get("number")
                if not snum:
                    continue
                try:
                    base = {r["key"]: r for r in inventory_rows(snum) or [] if r.get("key")}
                except Exception:
                    base = {}
                sw = {str(k_): str(v_) for k_, v_ in (inv.get("swaps") or {}).items()}   # (règle de couleur de l'inventaire)
                for rk, st in (inv.get("rows") or {}).items():
                    if st.get("o_lock") or not (st.get("s") == "order" or (st.get("s") in ("cmd", "ok") and st.get("o"))) or (ikey, rk) in linked:   # (o_lock : attribuée à la main — 22/11)
                        continue   # (« Commandée » à la main, ou de l'ancienne façon — copiée dans « À commander » — : laissée telle quelle)
                    r = base.get(rk) or {}
                    pn = st.get("p") or r.get("part_num") or rk.split("|")[0]
                    c0 = str(r.get("color_id") if r else rk.split("|")[-1])
                    col = str(st.get("c")) if st.get("c") is not None else sw.get(c0, c0)
                    els = set()
                    if not st.get("p") and st.get("c") is None and c0 not in sw and r.get("element_id"):
                        els.add(str(r["element_id"]))
                    m_ = re.search(r"/elements/(\d+)\.", st.get("ci") or "")
                    if m_:
                        els.add(m_.group(1))
                    ids = {str(pn).lower(), str((names.get(pn) or {}).get("bl") or "").lower(), "" if st.get("p") else str(r.get("bricklink") or "").lower()} - {""}
                    cons.append((int(inv.get("created") or 0), "row", (ikey, inv, st), els, ids, col, int(st.get("q") or r.get("quantity") or 1),
                                 set(st.get("o_off") or []), max(int(inv.get("created") or 0), int(st.get("t") or 0))))   # (inventaire créé / ligne mise à commander après la commande : surplus → vrac)
            cons.sort(key=lambda c: (not ((c[1] == "part" and c[2].get("got")) or (c[1] == "row" and c[2][2].get("s") == "ok")), c[0]))   # (déjà reçues d'abord, puis du plus ancien au plus récent)
            changed = 0
            for t0, kind, obj, els, ids, col, need, off, since in cons:
                take, got_ = [], 0
                for o in oitems:
                    if got_ >= need:
                        break
                    if o["left"] <= 0 or o["order"] in off or (since and o["date"] < since):   # (commande d'avant l'inventaire : jamais)
                        continue
                    if ((o["fig"] is not None and ((col[4:] and o["fig"] == col[4:]) or bool(ids & o["des"]))) if col.startswith("fig:")
                            else (o["fig"] is None and ((els & o["els"]) or ((ids & o["des"]) and ((rbbl.get(col) == o["blc"]) if o["blc"] is not None else cmap.get(col) == o["cn"]))))):
                        n = min(o["left"], need - got_)
                        take.append((o, n))
                        got_ += n
                if got_ >= need:   # toute la quantité est commandée : la réserve est prise
                    al = {}
                    for o, n in take:
                        o["left"] -= n
                        x = al.setdefault(o["order"], {"site": o["site"], "order": o["order"], "date": o["date"], "qty": 0})
                        x["qty"] += n
                        if o.get("price") is not None and x.get("paid", 0) is not None:   # payé : seulement la quantité attribuée à cette ligne
                            x["paid"] = round(x.get("paid", 0) + n * o["price"], 4)
                        else:
                            x["paid"] = None
                    new = sorted(al.values(), key=lambda x: x["date"] or 0)
                else:
                    new = []
                if kind == "part":
                    if (obj.get("ordered") or []) != new:
                        if new:
                            obj["ordered"] = new
                        else:
                            obj.pop("ordered", None)
                        changed += 1
                    continue
                ikey, inv, st = obj
                if st.get("s") == "ok":   # (reçue : son état ne bouge pas, seule la commande retenue suit)
                    if new and st.get("o") != new:
                        st["o"] = new
                        changed += 1
                    continue
                if new and (st.get("s") != "cmd" or st.get("o") != new):
                    st.update(s="cmd", o=new)
                    inv["updated"] = int(time.time())
                    changed += 1
                elif not new and st.get("o"):
                    st["s"] = "order"
                    st.pop("o", None)
                    inv["updated"] = int(time.time())
                    changed += 1
            unmatched = [o["name"] for o in oitems if o["left"] == o["q"]]
            try:   # commandées EN PLUS : ce qui reste une fois tout réparti (surplus, ou rien d'équivalent) — affichées dans « Commandes » (22/11)
                cfr, inv_bo = colors_fr(), {v: k for k, v in cmap.items()}
                done_ = _load(ORDERS_EXTRA_DONE, {})
                blrb = {str(k): str(v) for k, v in (moc_color_maps().get("blrb") or {}).items()}
                ext = []
                for o in oitems:
                    if o["left"] <= 0:
                        continue
                    rbc = blrb.get(str(o["blc"])) if o.get("blc") is not None else inv_bo.get(o.get("cn") or "")
                    nm = re.sub(r"\s*\([^()]*\)\s*$", "", re.sub(r"^LEGO\s+", "", o["name"] or "")).replace(" Minifigure", "").strip()
                    if o.get("cn") and nm.lower().startswith(o["cn"] + " "):   # (la couleur est déjà à côté — 22/11)
                        nm = nm[len(o["cn"]) + 1:]
                    ref = min(o["des"], key=lambda x: (len(x), x)) if o["des"] else ""   # (la plus courte : 3069b plutôt que 113477)
                    img = o.get("img") or (f"https://cdn.rebrickable.com/media/parts/elements/{sorted(o['els'])[0]}.jpg" if o["els"] else "")
                    pn_ = next((d for d in sorted(o["des"], key=lambda x: (len(x), x)) if d in names), ref)   # (référence Rebrickable)
                    key_ = f'{o["site"]}:{o["order"]}:{",".join(sorted(o["des"])) or o.get("fig") or nm}:{rbc}'
                    if key_ in done_:
                        continue
                    ext.append({"key": key_, "part_num": pn_, "bl": (names.get(pn_) or {}).get("bl") or ref, "color_id": int(rbc) if str(rbc or "").lstrip("-").isdigit() else None,
                                "price": o.get("price"), "site": o["site"], "order": o["order"], "date": o["date"], "name": nm, "ref": ref, "qty": o["left"],
                                "fig": o.get("fig") is not None, "color_fr": (cfr.get(str(rbc)) or {}).get("fr") or (o.get("cn") or "").capitalize(),
                                "rgb": (cfr.get(str(rbc)) or {}).get("rgb") or "", "paid": round(o["left"] * o["price"], 2) if o.get("price") else None, "image": img})
                ext.sort(key=lambda x: (-(x["date"] or 0), x["name"]))
                _save(ORDERS_EXTRA, {"t": int(time.time()), "items": ext})
            except Exception as e_:
                print("Commandées en plus :", e_, flush=True)
            if changed:
                _save(DB_FILE, db)
        _ord["t"] = time.time()
        return {"changed": changed, "orders": len(seen), "unmatched": unmatched[:50]}
    except Exception as e:
        print("Commandes BrickOwl :", e, flush=True)
        return {"changed": 0, "error": str(e)}
    finally:
        _ord["busy"] = False


def orders_keeper():
    time.sleep(420)
    while True:
        try:
            orders_sync(True)
        except Exception as e:
            print("Commandes :", e, flush=True)
        time.sleep(86400)


def brickset_keeper():
    time.sleep(300)
    while True:
        try:
            brickset_fill()
        except Exception as e:
            print("Brickset :", e, flush=True)
        time.sleep(86400)


REF_SITES = ("bricklink", "brickowl", "both")
_ref = {"t": 0, "v": "bricklink", "m": None}


def ref_site():
    """Source des prix : « bricklink » (d'office) ou « brickowl » (plan de secours, Réglages — 21/11 soir)."""
    try:
        mt = os.path.getmtime(sources.SETTINGS_FILE)
    except OSError:
        mt = None
    if mt != _ref["m"] or time.time() - _ref["t"] > 30:
        v = str(_load(sources.SETTINGS_FILE, {}).get("ref_site") or "bricklink")
        _ref.update(v=v if v in ("bricklink", "brickowl") else "bricklink", m=mt, t=time.time())   # (« les deux » : plus proposé)
    return "brickowl" if _ref["v"] == "brickowl" or bl_down() else "bricklink"   # (BrickLink muet depuis 24 h : BrickOwl en attendant — 21/11 soir)


def bo_first():
    """BrickOwl passe AVANT BrickLink seulement s'il est choisi dans les Réglages ; en secours automatique (BrickLink muet), les prix
    BrickLink déjà connus restent et BrickOwl ne comble que les manques (22/11)."""
    ref_site()
    return _ref["v"] == "brickowl"


def bo_solid(rec):
    """Relevé BrickOwl (set, figurine) assez fourni pour s'y fier : au moins le minimum de ventes / annonces réglé (3), comme BrickLink (22/11)."""
    try:
        return bool(rec) and bool(rec.get("unit")) and (rec.get("offers") is None or int(rec.get("offers") or 0) >= bl_min_sales())
    except (TypeError, ValueError):
        return False


def part_cond_view(bl_rec, bo_rec):
    """Prix d'une pièce pour chaque état voulu (N neuf, U occasion, X n'importe), selon le site de référence (21/11)."""
    def bl_u(c):
        if not bl_rec:
            return None
        return ((bl_rec.get("new") or {}).get("unit") if c == "N" else (bl_rec.get("used") or {}).get("unit") if c == "U" else bp_unit(bl_rec))

    def bo_u(c):
        r = bo_rec or {}
        return ((r.get("new") or {}).get("unit") if c == "N" else (r.get("used") or {}).get("unit") if c == "U" else r.get("unit"))
    out = {}
    for c in "NUX":
        a, b = bl_u(c), bo_u(c)
        u, fb = ref_mix(a, b)
        out[c] = {"unit": u, **({"fb": fb} if fb else {}), "sites": {"BrickLink": a, "BrickOwl": b}}
    return out


def ref_mix(bl, bo):
    """Prix BrickLink, prix BrickOwl → (prix retenu, site de secours utilisé ou "") selon le réglage (21/11)."""
    bl = bl if isinstance(bl, (int, float)) and bl > 0 else None
    bo = bo if isinstance(bo, (int, float)) and bo > 0 else None
    s = ref_site()
    if s == "both":
        if bl and bo:
            return round((bl + bo) / 2, 3), ""
        return (bl or bo), ("BrickLink" if bl else "BrickOwl" if bo else "")   # (un seul des deux : signalé)
    a, b, other = (bo, bl, "BrickLink") if s == "brickowl" and bo_first() else (bl, bo, "BrickOwl")   # (secours automatique : BrickLink connu d'abord — 22/11)
    return (a, "") if a else (b, other) if b else (None, "")


SITE_LOGO_DIR = os.path.join(DATA, "site_logos")   # (privé : jamais publié)
SITE_LOGO_SRC = {"bricklink": ["https://www.bricklink.com/v2/img/favicon/favicon.ico", "https://www.bricklink.com/favicon.ico"],
                 "brickowl": ["https://img.brickowl.com/sites/default/themes/bs_ss/images/favicon-32x32.png"]}
_slogo = {"t": 0, "v": {}}


def site_logos():
    """Petits logos des deux sites, en data: (pour les marques de prix) ; manquant : récupéré en fond (une fois par jour)."""
    import base64
    if time.time() - _slogo["t"] < 60:
        return _slogo["v"]
    out, miss = {}, []
    for k in SITE_LOGO_SRC:
        f = os.path.join(SITE_LOGO_DIR, k)
        try:
            raw = open(f, "rb").read()
            mime = "image/png" if raw[:4] == b"\x89PNG" else "image/x-icon"
            out[k] = f"data:{mime};base64," + base64.b64encode(raw).decode()
        except OSError:
            miss.append(k)
    if miss and not DEMO:
        def fetch():
            os.makedirs(SITE_LOGO_DIR, exist_ok=True)
            for k in miss:
                for u in SITE_LOGO_SRC[k]:
                    try:
                        raw = sources._get(u, timeout=20)[0]
                    except Exception:
                        continue
                    if raw[:4] in (b"\x89PNG", b"\x00\x00\x01\x00") and len(raw) < 60000:   # (une vraie icône : pas la page « maintenance »)
                        with open(os.path.join(SITE_LOGO_DIR, k), "wb") as fh:
                            fh.write(raw)
                        _slogo["t"] = 0
                        break
        bg_once("site_logos", fetch, 86400)
    _slogo.update(t=time.time(), v=out)
    return out


THIN_KEYS = ("unit", "offers", "qty", "zone", "kind", "min", "max")


_bl_min = {"t": 0, "v": 3}


def bl_min_sales():
    """Minimum de ventes réglé (Réglages › Prix, 3 par défaut) — relu au plus toutes les 30 s."""
    if time.time() - _bl_min["t"] > 30:
        try:
            _bl_min.update(v=sources.bl_zone_cfg()["min"])
        except Exception:
            pass
        _bl_min["t"] = time.time()
    return _bl_min["v"]


def bl_thin(rec):
    """Relevé BrickLink trop mince pour s'y fier : moins de ventes (ou d'annonces) que le minimum réglé (3 par défaut), dans toutes les zones."""
    try:
        return bool(rec) and (bool(rec.get("few")) or int(rec.get("offers") or 0) < bl_min_sales())
    except (TypeError, ValueError):
        return True


def bl_keep_rec(rec, old):
    """Relevé trop mince (demande du 17/11) : l'ancien relevé est gardé s'il était solide ; le mince reste noté dans « thin » (affiché)."""
    if rec and rec.get("unit") and bl_thin(rec) and not rec.get("thin") and old and old.get("unit") and (old.get("thin") or not bl_thin(old)):   # (old « thin » : un prix déjà gardé)
        return {**{k: v for k, v in old.items() if k != "thin"}, "thin": {x: rec.get(x) for x in THIN_KEYS}}
    return rec


def bl_market(itype, no):
    """Annonces BrickLink en vente, neuves et d'occasion (France, sinon Europe, sinon monde)."""
    used = sources.bl_guide(itype, no, "U")
    new = sources.bl_guide(itype, no, "N")
    page = {"SET": "S", "MINIFIG": "M", "PART": "P"}[itype]
    return {"new": new, "used": used, "url": f"https://www.bricklink.com/v2/catalog/catalogitem.page?{page}={urllib.parse.quote(str(sources.bl_fig_no(no)) if itype == 'MINIFIG' else no)}#T=S",
            "t": int(time.time()), "src": "BrickLink"}


BL_BG_DAY = 2000   # appels BrickLink de la passe de nuit (le reste du quota : ce qui n'a encore aucun prix, à l'écran)
BL_BG_HOUR = 3     # la passe quotidienne commence à cette heure (ou au démarrage, si celle du jour n'est pas faite)
BL_NIGHT_FILE = os.path.join(DATA, "bl_nightly.json")   # {"day", "calls", "jobs", "done", "left", "t"} : passe du jour
PART_BL_TTL = 30 * 86400


def apply_market(number):
    """Annonces d'un set relues → sa cote dans le cache des sets."""
    m = market_of(number, force=True)   # appel réseau : hors du verrou
    if not m:
        return
    with lock:
        cache = _load(CACHE_FILE, {})
        if number in cache:
            cache[number] = market_apply(cache[number], m)   # (ne relance pas market_of sous le verrou : c'était le blocage)
            _save(CACHE_FILE, cache)


def bl_queue():
    """Ce qui reste à relever sur BrickLink : sets (7 j), figurines (7 j), puis pièces (30 j)."""
    now = time.time()
    db, cache, pc = load_db(), _load(CACHE_FILE, {}), _parts_cache()
    kinds = list_kinds(db)
    sets = {i["number"] for i in db["items"] if i.get("kind", "set") == "set"}
    figs = {i["number"] for i in db["items"] if i.get("kind") == "fig"} | {
        f["id"] for s in sets for f in (cache.get(s) or {}).get("minifigs") or [] if f.get("id")}
    stale = lambda c, ttl: not c or now - c.get("t", 0) > ttl or c.get("src") != "BrickLink"
    q = [("set", s) for s in sorted(sets) if s in cache and stale(pc.get("bm:" + s), MARKET_TTL)]
    q += [("fig", f) for f in sorted(figs) if not RB_FIG.fullmatch(f) and stale(pc.get("fu:" + f), FIG_USED_TTL)]
    rbbl, names, combos = rbbl_map(), part_names(), set()
    for k in part_prices():   # pièces de la collection (réf. et couleur Rebrickable)
        pn, _, c = k.partition("|")
        if rbbl.get(c) is not None:
            combos.add(((names.get(pn) or {}).get("bl") or pn, rbbl[c]))
    for k in pc:   # pièces des MOC (réf. BrickLink, couleur BrickOwl)
        if k.startswith("mp:"):
            part, _, bo = k[3:].partition("|")
            blc = bo_bl_color(bo)
            if blc is not None:
                combos.add((part, blc))
    for k in pc:   # assemblages montés des sets partiels (ex. le T-Rex trex02)
        if k.startswith("ba:"):
            for a in (pc[k] or {}).get("list") or []:
                combos.add((a["no"], a["color"]))
    for i in db["items"]:   # pièces à commander
        if i.get("kind") == "part" and rbbl.get(str(i.get("color_id"))) is not None:
            combos.add((i.get("bricklink") or i.get("part_num"), rbbl[str(i["color_id"])]))
    q += [("part", p, c) for p, c in sorted(combos) if p and stale(pc.get(f"bp:{p}|{c}"), PART_BL_TTL)]
    old = lambda r: (r or {}).get("src") == "BrickLink" and not ((r or {}).get("kind") or ((r or {}).get("used") or {}).get("kind") or ((r or {}).get("new") or {}).get("kind"))
    have = {(j[0], j[1]) for j in q if j[0] != "part"} | {(j[1], j[2]) for j in q if j[0] == "part"}
    q += [("set", s) for s in sorted(sets) if ("set", s) not in have and old(pc.get("bm:" + s))]   # relevés d'avant (annonces) : à refaire en ventes réelles
    q += [("fig", f) for f in sorted(figs) if ("fig", f) not in have and not RB_FIG.fullmatch(f) and old(pc.get("fu:" + f))]
    def age(job):   # date du dernier relevé BrickLink (0 : jamais relevé → en premier ; 1 : relevé « moyenne » d'avant → juste après)
        rec = pc.get({"set": "bm:", "fig": "fu:"}.get(job[0], "") + job[1] if job[0] != "part" else f"bp:{job[1]}|{job[2]}") or {}
        if rec.get("src") != "BrickLink":
            return 0
        sold = rec.get("sold") or (rec.get("used") or {}).get("kind") or (rec.get("new") or {}).get("kind") or rec.get("kind")
        return rec.get("t", 0) if sold else 1   # (relevé d'avant les ventes réelles : juste après ceux jamais relevés)
    return sorted(q, key=lambda j: (age(j), ("set", "fig", "part").index(j[0])))   # les plus anciens d'abord


def consult_prices(item=None, set_no=None, fig_no=None):
    """Fiche ouverte (prix consultés à l'instant t) : prix BrickLink de cet élément et de ses figurines relus s'ils ont
    plus de 24 h. Rend True si au moins un appel BrickLink a été fait (les prix ont pu changer)."""
    if not DEMO and not COPIE and ref_site() == "brickowl":   # (BrickOwl : forcé, ou BrickLink muet depuis 24 h — la fiche consultée relue si plus de 24 h ; 21/11 soir)
        kind0 = (item or {}).get("kind", "set") if item else ("fig" if fig_no else "set")
        num0 = (item or {}).get("number") or set_no or fig_no
        got = False
        try:
            if kind0 == "set" and num0:
                c = _parts_cache().get("bmo:" + num0)
                if not c or time.time() - c.get("t", 0) > 86400:
                    _market_bo(num0, True)
                    got = True
                for f in (_load(CACHE_FILE, {}).get(num0) or {}).get("minifigs") or []:
                    if f.get("id"):
                        cf = _parts_cache().get("fuo:" + f["id"])
                        if not cf or time.time() - cf.get("t", 0) > 86400:
                            fig_bo_rec(f["id"], fetch=True, max_age=86400)
                            got = True
            elif kind0 == "fig" and num0:
                cf = _parts_cache().get("fuo:" + num0)
                if not cf or time.time() - cf.get("t", 0) > 86400:
                    fig_bo_rec(num0, fetch=True, max_age=86400)
                    got = True
        except Exception as e:
            print("BrickOwl (fiche consultée) :", e, flush=True)
        if got:
            _fu_mem["t"] = 0
            if kind0 == "set" and num0:
                markets_reapply([num0])
        if not bl_on():
            return got
    if DEMO or COPIE or not bl_on():
        return False
    n0 = bl_today()
    _bl_night.consult = True
    try:
        kind = (item or {}).get("kind", "set") if item else ("fig" if fig_no else "set")
        number = (item or {}).get("number") or set_no or fig_no
        if kind == "set" and number:
            apply_market(number)   # annonces du set (gardées si elles ont moins de 24 h)
            for f in (_load(CACHE_FILE, {}).get(number) or {}).get("minifigs") or []:   # et ses figurines
                if f.get("id"):
                    fig_used_fetch(f["id"], max_age=consult_ttl())
        elif kind == "fig" and number:
            fig_used_fetch(number, max_age=consult_ttl())
        elif kind == "part" and item:
            blc = rbbl_map().get(str(item.get("color_id")))
            if blc is not None:
                bl_part(item.get("bricklink") or item.get("part_num"), blc, max_age=consult_ttl())
        if item and item.get("moc_parts"):   # MOC / set estimé par ses pièces : chaque pièce de plus de 24 h relue, puis nouveau chiffrage
            n1 = bl_today()
            for lot in item.get("moc_parts") or []:
                blc = bo_bl_color(lot.get("color"))
                if lot.get("part") and blc is not None:
                    try:
                        bl_part(lot["part"], blc, conds=("U",), max_age=consult_ttl())
                    except Exception as e:
                        if "quota" in str(e).lower():
                            break
            if bl_today() > n1:
                moc_price_start(item["id"], front=True)
    except Exception as e:
        print("BrickLink (fiche ouverte) :", e, flush=True)
    finally:
        _bl_night.consult = False
    return bl_today() > n0


def bl_keeper():
    """Arrière-plan : une passe BrickLink par jour, dès BL_BG_HOUR heures (voir bl_nightly_pass)."""
    time.sleep(90)
    while True:
        try:
            st, cfg = _load(BL_NIGHT_FILE, {}), price_cfg()
            start = st.get("start") or (st.get("t", 0) if st.get("day") == time.strftime("%Y-%m-%d") and st.get("done") else 0)   # (ancien format : une par jour)
            due = time.time() - start >= cfg["every_h"] * 3600 - 300 and (cfg["every_h"] < 24 or time.localtime().tm_hour >= BL_BG_HOUR)
            unfinished = st.get("day") == time.strftime("%Y-%m-%d") and st.get("start") and not st.get("done")   # coupée par un redémarrage : reprise
            if bl_on() and (due or unfinished):
                bl_nightly_pass(resume=bool(unfinished and not due))
        except Exception as e:
            print("BrickLink (passe du jour) :", e, flush=True)
        time.sleep(600)


def bl_nightly_pass(resume=False):
    """Les prix BrickLink les plus anciens d'abord (sets, figurines, pièces) ; toutes les X heures (Réglages › Prix), au plus
    « budget » appels par jour pour l'ensemble des passes du jour. Reprend après un redémarrage (dépense du jour : data/bl_nightly.json)."""
    today = time.strftime("%Y-%m-%d")
    st = _load(BL_NIGHT_FILE, {})
    if st.get("day") != today:
        st = {"day": today, "calls": 0, "jobs": 0}
    if not resume:
        st["start"] = int(time.time())
    st["done"] = False
    budget = price_cfg()["budget"]
    queue = bl_queue()
    _bl_night.on = True   # dans ce fil seulement : les prix connus peuvent être relus
    try:
        k = 0
        for k, job in enumerate(queue):
            if st["calls"] >= budget:
                break
            before = bl_today()
            try:
                if job[0] == "set":
                    apply_market(job[1])
                elif job[0] == "fig":
                    fig_used_fetch(job[1], max_age=0)
                else:
                    bl_part(job[1], job[2], conds=("U",), max_age=0)
            except Exception as e:
                print("BrickLink (passe du jour)", job, e, flush=True)
                if "quota" in str(e).lower():
                    break
            st["calls"] += max(0, bl_today() - before)
            st["jobs"] += 1
            if st["jobs"] % 10 == 0:   # avancement gardé : un redémarrage ne redépense pas le budget
                _save(BL_NIGHT_FILE, {**st, "t": int(time.time())})
            time.sleep(1)
        else:
            k = len(queue)
        st.update(done=True, left=max(0, len(queue) - k), t=int(time.time()))
        _save(BL_NIGHT_FILE, st)
        print(f"BrickLink : passe du jour faite, {st['calls']} appels, {st['left']} prix encore à rafraîchir", flush=True)
    finally:
        _bl_night.on = False


_quick = threading.local()   # .on : fiche ouverte — réponse tout de suite avec ce qui est connu, sans appel réseau
_bg_seen = {}                # clé → heure : tâches de fond déjà lancées


def quick():
    return getattr(_quick, "on", False)


def bg_once(key, fn, every=86400):
    """Lance fn en arrière-plan, au plus une fois par « every » secondes pour cette clé (relectures d'une fiche ouverte)."""
    now = time.time()
    if now - _bg_seen.get(key, 0) < every:
        return
    _bg_seen[key] = now

    def run():
        try:
            fn()
        except Exception as e:
            print("Arrière-plan", key, ":", e, flush=True)
    threading.Thread(target=run, daemon=True).start()


def market_of(number, force=False):
    """Annonces d'un set selon le SITE DE RÉFÉRENCE (21/11) : BrickLink et / ou BrickOwl, combinés (ref_mix) ; « sites » : chacun à part."""
    m = _market_main(number, force)   # (comme avant : BrickLink, ou BrickOwl s'il manque)
    bl = m if m and m.get("src") == "BrickLink" else None
    bo = m if m and m.get("src") != "BrickLink" else None
    if ref_site() == "brickowl":   # (BrickLink choisi : jamais BrickOwl, même en secours — 21/11 soir)
        bo = _market_bo(number, force) or bo
    return market_combine(bl, bo)




def markets_reapply(numbers=None):
    """Cote des sets (cache des sets) recalculée d'après les relevés gardés (BrickLink, BrickOwl) et le site de référence — sans réseau (21/11)."""
    pc = _parts_cache()
    with lock:
        cache = _load(CACHE_FILE, {})
        n_ok = 0
        for n in (numbers if numbers is not None else list(cache)):
            v = cache.get(n)
            if not isinstance(v, dict) or str(n).startswith("fig:"):
                continue
            bm, bmo = pc.get("bm:" + n), pc.get("bmo:" + n)
            bl = bm if bm and bm.get("src") == "BrickLink" else None
            bo = bmo or (bm if bm and bm.get("src") != "BrickLink" else None)
            m = market_combine(bl, bo)
            if m:
                cache[n] = market_apply(v, m)
                n_ok += 1
        if n_ok:
            _save(CACHE_FILE, cache)
    return n_ok

def _market_bo(number, force=False):
    """Annonces BrickOwl d'un set, gardées à part (« bmo: », une semaine) ; fiche ouverte : relevées en fond."""
    c = _parts_cache().get("bmo:" + number)
    if c and time.time() - c.get("t", 0) < MARKET_TTL and not force:
        return c
    if quick() and not force:
        bg_once("bmo:" + number, lambda: _market_bo(number, True), 3600)
        return c
    try:
        m = sources.set_market(number)
    except Exception:
        return c
    m = {**(m or {"new": None, "used": None}), "src": "BrickOwl", "t": int(time.time())}
    _parts_cache_put("bmo:" + number, m)
    if not _bo_fill["on"]:   # (fiche ouverte : sa cote recalculée tout de suite ; la passe complète recalcule tout à la fin)
        markets_reapply([number])
    return m


def market_combine(bl, bo):
    """Deux relevés (BrickLink, BrickOwl) → un relevé selon le réglage ; chaque état : prix retenu, « fb » (site de secours) ; « sites » : les deux."""
    if not bl and not bo:
        return None
    s = ref_site()
    sites = {nm: {"new": ((r or {}).get("new") or {}).get("unit"), "used": ((r or {}).get("used") or {}).get("unit"), "url": (r or {}).get("url")}
             for nm, r in (("BrickLink", bl), ("BrickOwl", bo)) if r}
    if s == "bricklink" and bl and not bo:   # (comme avant)
        return {**bl, "sites": sites}
    base = dict(bl if (not bo_first() and bl) or not bo else bo)
    for k in ("new", "used"):
        a, b = ((bl or {}).get(k) or {}), ((bo or {}).get(k) or {})
        if b.get("unit") and not bo_solid(b):   # (BrickOwl trop mince : pas retenu — 22/11)
            b = {}
        u, fb = ref_mix(a.get("unit"), b.get("unit"))
        if u is None:
            base[k] = a or b or None
            continue
        src_rec = b if fb == "BrickOwl" or (bo_first() and not fb) else a if a.get("unit") else b
        base[k] = {**src_rec, "unit": u, **({"fb": fb} if fb else {}), **({"mix": True} if s == "both" and a.get("unit") and b.get("unit") else {})}
    base["src"] = {"both": "both", "brickowl": "BrickOwl"}.get(s, base.get("src") or "BrickLink")
    base["sites"] = sites
    return base


def _market_main(number, force=False):
    """Annonces d'un set (gardées 24 h) : BrickLink si ses codes sont réglés, sinon BrickOwl. {"new", "used", "url", "t", "src"} ou None."""
    c = _parts_cache().get("bm:" + number)
    want_bl = bl_on()
    if quick() and not force:   # fiche ouverte : tout de suite (BrickLink : relu par /api/consult ; sinon BrickOwl en fond)
        if not want_bl and (not c or time.time() - c.get("t", 0) >= MARKET_TTL):
            bg_once("bm:" + number, lambda: market_of(number), 3600)
        return c
    if want_bl and bl_keep_known(c):   # déjà relevé sur BrickLink : relu seulement par la passe de nuit
        return c
    if c and not force and time.time() - c.get("t", 0) < MARKET_TTL and (c.get("src") == "BrickLink") == want_bl:
        return c
    if want_bl:
        try:
            m = bl_market("SET", number)
            try:
                hist_backfill(number, m)   # (6 mois de ventes, mois par mois — 21/11)
            except Exception:
                pass
            for k in ("used", "new"):   # moins de 3 ventes partout : l'ancien relevé solide est gardé
                m[k] = bl_keep_rec(m.get(k), (c or {}).get(k))
            _parts_cache_put("bm:" + number, m)
            return m
        except Exception as e:
            print("BrickLink", number, e, flush=True)   # injoignable ou quota atteint : BrickOwl
            if c and c.get("src") == "BrickLink":   # déjà relevé sur BrickLink : on garde ce prix-là
                return c
    return c   # (BrickLink seul : plus de relevé BrickOwl ; le dernier prix connu reste jusqu'au retour de BrickLink — 21/11)


def with_market(data, number, force=False):
    """Cote neuve et d'occasion d'un set : celle des annonces (France, sinon Europe, sinon monde)."""
    return market_apply(data, market_of(number, force))


def market_apply(data, m):
    """Reporte des annonces déjà relues (m) dans la fiche d'un set : aucun appel réseau, aucun verrou."""
    if not m:
        return data
    out = dict(data)
    mk = {k: m.get(k) for k in ("new", "used", "url", "src", "sites")}   # (sites : prix de chaque site — 21/11)
    for key, fld in (("used", "used_value"), ("new", "new_value")):
        rec = m.get(key) or {}
        if not rec.get("unit"):
            continue
        pure_bl = not rec.get("mix") and not rec.get("fb") and (m.get("src") or "BrickLink") == "BrickLink"   # (prix BrickLink pur — 21/11)
        if "kept_" + fld not in out and out.get(fld) is not None:
            out["kept_" + fld] = out[fld]   # (le prix connu de la fiche, mis à part : un retour à BrickLink le retrouve)
        kept = out.get("kept_" + fld)
        if bl_thin(rec) and not rec.get("thin") and pure_bl \
                and kept and abs(kept - rec["unit"]) > 0.004 and not (key == "used" and out.get("used_guess")):
            mk[key] = {"unit": kept, "thin": {x: rec.get(x) for x in THIN_KEYS}}   # trop peu de ventes : le prix déjà connu de la fiche est gardé
            out[fld] = kept
        else:
            out[fld] = rec["unit"]
            if pure_bl:
                out["kept_" + fld] = rec["unit"]
            if key == "used":
                out.pop("used_guess", None)
    if not (m.get("used") or {}).get("unit") and not out.get("used_value") and out.get("new_value"):   # aucune annonce d'occasion : repli habituel
        out["used_value"] = round(out["new_value"] * 0.6, 2)
        out["used_guess"] = True
    out["market"] = mk
    out["price_src"] = m.get("src") or "BrickOwl"
    out.pop("pending_prices", None)
    return out


def rb_set_basic(number):
    """Set absent du catalogue des cotes : nom, année, pièces, photo et gamme (Rebrickable)."""
    d = sources.rb(f"lego/sets/{number}/")
    theme = None
    try:
        theme = sources.rb(f"lego/themes/{d.get('theme_id')}/").get("name") if d.get("theme_id") else None
    except Exception:
        pass
    figs = []
    try:   # ses figurines (références Rebrickable fig-…)
        for f in sources.rb(f"lego/sets/{number}/minifigs/?page_size=100").get("results") or []:
            figs.append({"id": f.get("set_num"), "name": f.get("set_name"), "image": f.get("set_img_url"), "qty": f.get("quantity") or 1})
    except Exception:
        pass
    return {"number": number, "name": d.get("name") or number, "year": d.get("year"), "pieces": d.get("num_parts"), "image": d.get("set_img_url"),
            "theme": theme, "minifigs": figs, "minifig_count": sum(f["qty"] for f in figs) or None,
            "source": f"https://rebrickable.com/sets/{number}/", "pending_prices": True}


def get_set(number, force=False, market_force=False):
    """force : catalogue relu ; market_force : annonces relevées tout de suite (sinon gardées 24 h)."""
    cache = _load(CACHE_FILE, {})
    hit = cache.get(number)
    if hit and not force and time.time() - hit.get("fetched_at", 0) < CACHE_TTL:
        return hit
    if hit and not force and quick():   # fiche ouverte : la fiche connue tout de suite, le catalogue relu en fond
        bg_once("set:" + number, lambda: get_set(number))
        return hit
    try:
        data = sources.set_details(number)
    except Exception:   # catalogue des cotes injoignable (BrickEconomy) : la fiche connue, ou Rebrickable ; les prix du marché
        base = hit or rb_set_basic(number)
        data = with_market({**base, "fetched_at": int(time.time())}, number, market_force)
        if data.get("pending_prices") and not hit:
            raise LookupError("Set sans prix connu")
        with lock:
            cache = _load(CACHE_FILE, {})
            cache[number] = data
            _save(CACHE_FILE, cache)
        return data
    data = with_market(data, number, market_force)
    with lock:
        cache = _load(CACHE_FILE, {})
        cache[number] = data
        _save(CACHE_FILE, cache)
    return data


RB_FIG = re.compile(r"fig-\d{3,7}")   # référence Rebrickable d'une minifig (pas de référence BrickLink, donc pas de cote)


def parts_estimable(it):
    """Élément qui peut être estimé par ses pièces quand il n'a pas de cote : set, ou minifig connue de Rebrickable seulement."""
    k = it.get("kind") or "set"
    return k == "set" or (k == "fig" and bool(RB_FIG.fullmatch(str(it.get("number") or ""))))


def get_fig(fid, force=False):
    """Fiche d'une minifig (cache partagé avec les sets, clé « fig:<id> »)."""
    key = "fig:" + fid
    cache = _load(CACHE_FILE, {})
    hit = cache.get(key)
    if RB_FIG.fullmatch(fid):   # minifig Rebrickable : nom, photo et nombre de pièces, sans cote
        if hit and not force:
            return hit
        try:
            d = sources.rb(f"lego/minifigs/{fid}/")
        except Exception:
            if hit:
                return hit
            raise
        data = {"type": "fig", "number": fid, "name": d.get("name") or fid, "image": d.get("set_img_url"), "pieces": d.get("num_parts"),
                "pending_prices": True, "rb": True, "fetched_at": int(time.time())}
        with lock:
            cache = _load(CACHE_FILE, {})
            cache[key] = data
            _save(CACHE_FILE, cache)
        return data
    if hit and not force and time.time() - hit.get("fetched_at", 0) < CACHE_TTL:
        return hit
    if hit and not force and quick():   # fiche ouverte : la fiche connue tout de suite, le catalogue relu en fond
        bg_once("fig:" + fid, lambda: get_fig(fid))
        return hit
    try:
        data = sources.fig_details(fid)
    except Exception:
        if hit:
            return hit
        alt = fig_from_sets(fid, cache)   # catalogue injoignable : ce qu'en disent les sets connus (gardé avec fetched_at 0 : réessayé plus tard)
        if alt:
            with lock:   # gardé pour que les listes aient au moins nom, photo et prix
                cache = _load(CACHE_FILE, {})
                cache.setdefault(key, alt)
                _save(CACHE_FILE, cache)
            return alt
        raise
    with lock:
        cache = _load(CACHE_FILE, {})
        cache[key] = data
        _save(CACHE_FILE, cache)
    return data


def fig_from_sets(fid, cache):
    """Fiche minimale d'une minifig d'après les sets en cache qui la contiennent (nom, photo, prix neuf)."""
    sets = []
    found = None
    for k, v in cache.items():
        if k.startswith("fig:") or not isinstance(v, dict):
            continue
        for f in v.get("minifigs") or []:
            if str(f.get("id", "")).lower() == fid.lower():
                found = found or f
                sets.append(k)   # même format que le catalogue : numéros de sets
    if not found:
        return None
    return {"type": "fig", "number": fid, "name": found.get("name") or fid, "image": found.get("image"), "value": found.get("value"),
            "sets": sets[:20], "fetched_at": 0, "from_sets": True}


def rb_set_lots(num):
    """Inventaire complet (figurines comprises) d'un set Rebrickable → (fiche du set, lots chiffrables)."""
    d = sources.rb(f"lego/sets/{urllib.parse.quote(num)}/")
    rows, url = [], f"lego/sets/{urllib.parse.quote(num)}/parts/?inc_minifig_parts=1&page_size=1000"
    while url:
        r = sources.rb(url)
        rows += [x for x in r.get("results", []) if not x.get("is_spare")]
        nxt = r.get("next")
        url = nxt.split("/api/v3/", 1)[1] if nxt else None
    bo, agg = moc_color_maps()["rb"], {}
    for x in rows:
        pt, col = x["part"], x["color"]
        bl = ((pt.get("external_ids") or {}).get("BrickLink") or [pt["part_num"]])[0]
        c = bo.get(str(col["id"]))
        if not c:
            continue
        k = (bl, c)
        if k in agg:
            agg[k]["qty"] += x["quantity"]
        else:
            el = x.get("element_id")
            agg[k] = {"part": bl, "color": c, "qty": x["quantity"], "color_id": col["id"], "name": pt.get("name") or "",
                      "color_fr": FR_COLORS.get(col.get("name") or "", col.get("name") or ""),
                      "image": (f"https://cdn.rebrickable.com/media/parts/elements/{el}.jpg" if el else None) or pt.get("part_img_url") or ""}
    return d, list(agg.values())


def bl_set_figs(number):
    """Figurines d'un set selon l'inventaire BrickLink (API officielle ; une requête, gardée 30 jours, réessayée le lendemain si vide)
    → [{"id", "name", "image", "qty"}] aux références BrickLink (celles du catalogue des cotes). Sert aux sets absents du catalogue des cotes."""
    if DEMO:
        return []
    key = "blsf:" + str(number)
    c = _parts_cache().get(key) or {}
    if time.time() - c.get("t", 0) < (36500 if c.get("figs") else 1) * 86400:   # (connues : gardées pour toujours ; pas encore : réessai le lendemain)
        return c.get("figs") or []
    figs = []
    try:
        import html as _html
        for g in sources.bl_get(f"/items/SET/{urllib.parse.quote(str(number))}/subsets", {"break_minifigs": "false"}) or []:
            for e in g.get("entries") or []:
                it = e.get("item") or {}
                if it.get("type") == "MINIFIG" and it.get("no"):
                    figs.append({"id": it["no"], "name": _html.unescape(it.get("name") or it["no"]), "qty": int(e.get("quantity") or 1),
                                 "image": f"https://img.bricklink.com/ItemImage/MN/0/{it['no']}.png"})
    except Exception as e:
        print("Figurines du set (BrickLink) :", number, e, flush=True)
        return []   # (rien gardé : réessayé à la prochaine ouverture)
    _parts_cache_put(key, {"figs": figs, "t": time.time()})
    return figs


def owns_set(number):
    """Ce set est-il dans ma collection (au moins un exemplaire) ?"""
    db = load_db()
    kinds = list_kinds(db)
    return any(i.get("kind", "set") == "set" and i.get("number") == number and kinds.get(i.get("list_id")) == "collection" for i in db["items"])


def with_bl_figs(info, number):
    """Fiche d'un set sans figurines connues (ou seulement des références Rebrickable « fig-… ») : celles de BrickLink, si elle en donne."""
    mf = info.get("minifigs") or []
    if mf and not all(str(f.get("id") or "").startswith("fig-") for f in mf):
        return info
    figs = bl_set_figs(number)
    return {**info, "minifigs": figs, "minifig_count": sum(f["qty"] for f in figs)} if figs else info


def placeholder_set(number, name="", strict=False, image="", soon=""):
    """BrickEconomy injoignable : fiche provisoire du set (nom, photo, année, pièces depuis Rebrickable), sans cote.
    fetched_at = 0 : relue chez BrickEconomy dès la prochaine actualisation."""
    info = {"number": number, "name": name or number, "pending_prices": True, "fetched_at": 0, "minifigs": [],
            **({"image": image} if image and IMG_OK.match(image) else {}),
            **({"availability": "Pending", "releasing": soon} if soon else {})}   # nouveauté à venir (lego.com)
    try:
        d = sources.rb(f"lego/sets/{urllib.parse.quote(number)}/")
        info.update(name=d.get("name") or info["name"], year=d.get("year"), pieces=d.get("num_parts"), image=d.get("set_img_url") or info.get("image"))
    except Exception:
        if strict:   # inconnu de Rebrickable aussi : pas de fiche provisoire
            return None
    info = with_bl_figs(info, number)   # ses figurines (BrickLink) : affichées, ouvrables, ajoutables seules
    with lock:
        cache = _load(CACHE_FILE, {})
        if not cache.get(number):
            cache[number] = info
            _save(CACHE_FILE, cache)
    return info


GIFT_LINK = os.path.join(DATA, "gift_link.json")   # {"token"} : lien public secret de la liste « À offrir »


def gift_token():
    return (_load(GIFT_LINK, {}) or {}).get("token") or ""


NOV_FILE = os.path.join(DATA, "cache_novelties.json")
LEGO_PRICES = os.path.join(ROOT, "data", "cache_lego_prices.json")   # n° de set → prix public lego.com, date de sortie (partagé avec la démo)
_legop = {"m": {}, "t": None}


def lego_price(number):
    """Prix public lego.com connu d'un set : {price, when, soon} ou None."""
    try:
        mt = os.path.getmtime(LEGO_PRICES)
    except OSError:
        return None
    if mt != _legop["t"]:
        _legop["m"], _legop["t"] = _load(LEGO_PRICES, {}), mt
    return _legop["m"].get(number)
NOV_HIDDEN = os.path.join(DATA, "novelties_hidden.json")   # sets que je ne veux plus voir dans les nouveautés
NOV_THEMES = os.path.join(DATA, "novelties_themes.json")   # thèmes exclus des nouveautés
NOV_SEEN = os.path.join(DATA, "novelties_seen.json")   # sets déjà vus dans la page Nouveautés (les autres : « nouveaux »)


def novelties_mine():
    """Nouveautés selon mes filtres : sans ce que j'ai, sans les masquées, seulement les thèmes suivis."""
    d = _load(NOV_FILE, {})
    mine = {i.get("number") for i in load_db()["items"] if i.get("kind", "set") == "set"}
    hidden = set(_load(NOV_HIDDEN, []))
    ex_th = {theme_norm(t) for t in _load(NOV_THEMES, [])}
    return [x for x in d.get("items") or [] if x.get("pieces") and x["number"] not in mine and x["number"] not in hidden
            and theme_norm(x.get("theme")) not in ex_th]
_nov = {"busy": False}


THEME_FR = {"christmas": "Noël", "other": "Autre", "minifigures": "Figurines à collectionner", "seasonal": "Saisonnier", "gear": "Accessoires",
            "books": "Livres", "creator": "Creator", "creator 3-in-1": "Creator 3 en 1", "icons": "Icons", "editions": "Editions"}


def theme_norm(t):
    """Nom de gamme uniforme : sans ™ / ®, sans « LEGO », en français pour les plus courants, NINJAGO = Ninjago."""
    t = re.sub(r"[™®©]", "", str(t or "")).strip()
    t = re.sub(r"^LEGO\s+", "", t, flags=re.I).strip()
    if THEME_FR.get(t.lower()):
        return THEME_FR[t.lower()]
    if t.isupper() and len(t) > 3:
        t = t.title()
    return t or "Autre"


def lego_urls():
    """Pages produits LEGO.com connues (relevées avec les nouveautés) : {numéro du set : adresse}. Les autres sets : pas d'adresse sûre."""
    out = {}
    for n, x in (_load(LEGO_PRICES, {}) or {}).items():   # (pages des thèmes lego.com, relevées chaque jour — 21/11)
        u = str((x or {}).get("url") or "")
        if u.startswith("https://www.lego.com/") and (x or {}).get("status") != "gone":
            out[n] = u
    for x in (_load(NOV_FILE, {}) or {}).get("items") or []:
        u = str(x.get("url") or "")
        if x.get("number") and u.startswith("https://www.lego.com/"):
            out[x["number"]] = u
    return out


LEGO_SKIP = {"braille-bricks", "brand-catalogue", "lego-education", "serious-play", "powered-up"}   # (pas des sets à collectionner)


def lego_themes_build():
    """Une fois par jour : les pages des thèmes de lego.com → prix public, page produit, disponibilité de chaque set vendu (21/11)."""
    try:
        slugs = [s for s in sources.lego_theme_slugs() if s not in LEGO_SKIP]
    except Exception as e:
        print("Thèmes lego.com :", e, flush=True)
        return
    now, seen = int(time.time()), set()
    for slug in slugs:
        try:
            prods = sources.lego_category(slug, 12, "themes")
        except Exception as e:
            print("Thème lego.com", slug, e, flush=True)
            time.sleep(20)
            continue
        with lock:
            lp = _load(LEGO_PRICES, {})
            for p in prods:
                n = p["code"] + "-1"
                seen.add(n)
                old = lp.get(n) or {}
                soon = str(p.get("status") or "").startswith(("B_COMING_SOON", "A_PRE_ORDER"))
                lp[n] = {**old, **({"price": p["price"]} if p.get("price") is not None else {}), "when": p.get("when") or old.get("when") or "",
                         "soon": soon, "name": p.get("name") or old.get("name") or "", "url": p.get("url") or old.get("url") or "",
                         "status": p.get("status") or "", "t": now}
            _save(LEGO_PRICES, lp)
        time.sleep(6)   # (une pause entre deux thèmes : lego.com n'est pas pressé)
    with lock:   # plus en vente (absent de tous les thèmes) : le lien direct n'est plus proposé ; le prix public reste
        lp = _load(LEGO_PRICES, {})
        for n, x in lp.items():
            if isinstance(x, dict) and x.get("url") and n not in seen and x.get("t", 0) < now - 3 * 86400:
                x["status"] = "gone"
        _save(LEGO_PRICES, lp)
    print(f"Thèmes lego.com : {len(seen)} sets relevés", flush=True)


def lego_themes_keeper():
    time.sleep(900)
    while True:
        try:
            lego_themes_build()
        except Exception as e:
            print("Thèmes lego.com :", e, flush=True)
        time.sleep(86400)   # (une fois par jour)


def with_lego(info, number):
    """Fiche d'un set : prix public lego.com s'il manque, « en vente » si on n'en sait rien d'autre (pages des thèmes — 21/11)."""
    lp = lego_price(number) or {}
    if not info or not lp:
        return info
    out = dict(info)
    if lp.get("price") and not out.get("retail"):
        out["retail"] = lp["price"]
    if not out.get("availability") and lp.get("status") and lp.get("status") != "gone" and not lp.get("soon"):
        out["availability"] = "Retail"
    return out


def novelties_build():
    """lego.com : « bientôt disponibles » + « nouveautés » ; puis, sur Rebrickable, les minifigs de chaque set et celles
    qu'on ne trouve dans aucun autre set (exclusives aux nouveautés). Gardé dans cache_novelties.json."""
    if _nov["busy"]:
        return
    _nov["busy"] = True
    try:
        items = {}
        for slug, kind in (("coming-soon", "soon"), ("new-sets-and-products", "new")):
            try:
                for p in sources.lego_category(slug):
                    st = "soon" if kind == "soon" or str(p["status"]).startswith(("B_COMING_SOON", "A_PRE_ORDER")) else "new"
                    items.setdefault(p["code"], {**p, "number": p["code"] + "-1", "kind": st, "pos": len(items)})
            except Exception as e:
                print("Nouveautés : lego.com", slug, e, flush=True)
        if not items:
            return
        try:   # prix publics : registre gardé (sets à venir et récents, y compris ceux que j'ai déjà)
            lp = _load(LEGO_PRICES, {})
            for x in items.values():
                if x.get("price") is not None:
                    lp[x["number"]] = {"price": x["price"], "when": x.get("when") or "", "soon": x["kind"] == "soon", "name": x.get("name") or "", "t": int(time.time())}
            _save(LEGO_PRICES, lp)
        except Exception as e:
            print("Prix lego.com :", e, flush=True)
        MOIS = "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre"
        prev = {x["number"]: x for x in (_load(NOV_FILE, {}).get("items") or [])}
        now = int(time.time())
        for x in items.values():
            x["seen"] = (prev.get(x["number"]) or {}).get("seen") or now   # première apparition sur lego.com (départage les sets d'une même année)
            pv = prev.get(x["number"]) or {}
            bo_ = "BACKORDER" in str(x.get("status") or "").upper()   # (réassort : « expédié d'ici le … » n'est PAS une date de sortie — 22/11)
            if "BACKORDER" in str(pv.get("status") or "").upper():
                pv = {**pv, "release": "", "day": ""}   # (date relevée pendant un réassort : oubliée)
            wt = "" if bo_ else (x.get("when") or "")
            m = re.search(rf"(?:\b\d{{1,2}}\s+)?({MOIS})\s+(\d{{4}})", wt, re.I)
            x["release"] = f"{m.group(1).lower()} {m.group(2)}" if m else pv.get("release") or ""   # vue « à venir » avant : son mois reste
            d2 = re.search(rf"\b(\d{{1,2}})\s+({MOIS})\s+(\d{{4}})", wt, re.I)   # (date exacte « 1 janvier 2027 » : retenue — une fois sorti, il reste à son jour)
            x["day"] = f"{d2.group(1)} {d2.group(2).lower()} {d2.group(3)}" if d2 else pv.get("day") or ""
        items = {k: x for k, x in items.items() if x.get("pieces")}   # pas les « goodies » (sacs, trousses, vêtements…) : rien à construire
        _save(NOV_FILE, {"t": int(time.time()), "items": list(items.values()), "figs_done": False})
        nums, pc = {x["number"] for x in items.values()}, _parts_cache()
        for x in items.values():   # Rebrickable : l'année (sortis sans mois connu) et la gamme (lego.com : « Autre » ou rien)
            need_year, need_theme = not x.get("release"), (x.get("theme") or "Autre") == "Autre"
            if not (need_year or need_theme):
                continue
            c = pc.get("nvy:" + x["number"])
            if not (c and time.time() - c.get("t", 0) < 30 * 86400 and "theme_id" in c):
                try:
                    d = sources.rb(f"lego/sets/{urllib.parse.quote(x['number'])}/")
                    c = {"year": d.get("year"), "theme_id": d.get("theme_id"), "t": time.time()}
                except Exception:
                    c = {"year": None, "theme_id": None, "t": time.time()}
                _parts_cache_put("nvy:" + x["number"], c)
            if need_year:
                x["release"] = str(c.get("year") or "")
            if need_theme and c.get("theme_id"):
                th = pc.get(f"rbth:{c['theme_id']}")
                if not th:
                    try:
                        t = sources.rb(f"lego/themes/{c['theme_id']}/")
                        th = {"name": t.get("name") or ""}
                        _parts_cache_put(f"rbth:{c['theme_id']}", th)
                    except Exception:
                        th = {}
                if th.get("name") and "fr" not in th:   # nom de la gamme en français (traduit une fois)
                    try:
                        th = {**th, "fr": sources.mt_fr(th["name"]) or th["name"]}
                    except Exception:
                        th = {**th}
                    if "fr" in th:
                        _parts_cache_put(f"rbth:{c['theme_id']}", th)
                if th.get("name"):
                    x["theme"] = th.get("fr") or th["name"]
        for x in items.values():   # minifigs de chaque set (Rebrickable ; un set pas encore connu : aucune)
            c = pc.get("nvs:" + x["number"])
            fresh = 6 * 3600 if c and any(not f.get("image") for f in c.get("figs") or []) else 7 * 86400   # une figurine sans photo : relue toutes les 6 h
            if c and time.time() - c.get("t", 0) < fresh:
                x["figs"] = c["figs"]
                continue
            try:
                r = sources.rb(f"lego/sets/{urllib.parse.quote(x['number'])}/minifigs/?page_size=100").get("results", [])
                x["figs"] = [{"fig": m["set_num"], "name": m.get("set_name") or m["set_num"], "image": m.get("set_img_url") or "", "qty": m.get("quantity", 1)} for m in r if m.get("set_num")]
            except Exception:
                x["figs"] = []
            _parts_cache_put("nvs:" + x["number"], {"figs": x["figs"], "t": time.time()})
        for x in items.values():   # figurine encore sans photo chez Rebrickable : en attendant, l'image de son torse imprimé (photo provisoire)
            x["figs"] = [dict(f) for f in x.get("figs") or []]   # (copie : la photo provisoire n'entre pas dans le cache « nvs: », relu toutes les 6 h)
            for f in x["figs"]:
                if f.get("image"):
                    continue
                t = pc.get("nvt:" + f["fig"])
                if not (t and time.time() - t.get("t", 0) < 3 * 86400):
                    try:
                        ps = sources.rb(f"lego/minifigs/{urllib.parse.quote(f['fig'])}/parts/?page_size=100").get("results", [])
                        tor = next((q["part"] for q in ps if re.search(r"torso", (q.get("part") or {}).get("name") or "", re.I) and (q.get("part") or {}).get("part_img_url")), None)
                        t = {"img": (tor or {}).get("part_img_url") or "", "t": time.time()}
                    except Exception:
                        t = {"img": "", "t": time.time() - 3 * 86400 + 6 * 3600}   # (Rebrickable indisponible : réessai dans 6 h)
                    _parts_cache_put("nvt:" + f["fig"], t)
                if t.get("img"):
                    f["image"], f["image_tmp"] = t["img"], True
        for x in items.values():   # exclusive : dans aucun set hors des nouveautés
            for f in x.get("figs") or []:
                c = pc.get("nvf:" + f["fig"])
                if not (c and time.time() - c.get("t", 0) < 7 * 86400):
                    try:
                        sets = [s["set_num"] for s in sources.rb(f"lego/minifigs/{urllib.parse.quote(f['fig'])}/sets/?page_size=100").get("results", [])]
                    except Exception:
                        sets = None
                    c = {"sets": sets, "t": time.time()}
                    if sets is not None:
                        _parts_cache_put("nvf:" + f["fig"], c)
                f["exclusive"] = c.get("sets") is not None and all(s in nums for s in c["sets"])
        _save(NOV_FILE, {"t": int(time.time()), "items": list(items.values()), "figs_done": True})
        print(f"Nouveautés : {len(items)} sets", flush=True)
    finally:
        _nov["busy"] = False




_bo_fill = {"on": False}


def bo_fill_start():
    """Prix BrickOwl de ce que j'ai (sets, figurines) et de mes souhaits, en fond, une page toutes les 2 s (réglage BrickOwl / les deux — 21/11)."""
    if _bo_fill["on"]:
        return
    _bo_fill["on"] = True

    def run():
        try:
            db, kinds = load_db(), list_kinds()
            sets, figs, done = [], [], []
            for it in db["items"]:
                if kinds.get(it.get("list_id")) not in ("collection", "wishlist"):
                    continue
                if it.get("kind", "set") == "set" and it.get("number") and it["number"] != "custom":
                    sets.append(it["number"])
                elif it.get("kind") == "fig" and it.get("number"):
                    figs.append(it["number"])
            for n in dict.fromkeys(sets):
                if ref_site() == "bricklink":
                    return
                c = _parts_cache().get("bmo:" + n)
                if not c or time.time() - c.get("t", 0) >= 86400:   # (une fois par jour — 21/11 soir)
                    _market_bo(n, True)
                    done.append(n)
                    if len(done) % 20 == 0:
                        markets_reapply(done[-20:])
                    time.sleep(2)
            for f in dict.fromkeys(figs):
                if ref_site() == "bricklink":
                    return
                c = _parts_cache().get("fuo:" + f)
                if not c or time.time() - c.get("t", 0) >= 86400:   # (une fois par jour — 21/11 soir)
                    fig_bo_rec(f, fetch=True, max_age=86400)
                    time.sleep(2)
            _fu_mem["t"] = 0
            markets_reapply()
        except Exception as e:
            print("BrickOwl (site de référence) :", e, flush=True)
        finally:
            _bo_fill["on"] = False
    threading.Thread(target=run, daemon=True).start()


def bo_keeper():
    time.sleep(600)
    while True:
        if ref_site() != "bricklink":
            bo_fill_start()
        time.sleep(3600)   # (vérifie chaque heure ; chaque fiche est relue au plus une fois par jour — 21/11 soir)

def novelties_keeper():
    time.sleep(150)
    while True:
        try:
            novelties_build()
        except Exception as e:
            print("Nouveautés :", e, flush=True)
        time.sleep(3600)   # (toutes les heures : deux pages de lego.com ; les figurines d'un set ne sont cherchées qu'une fois)


def bl_fig_info(fid):
    """Fiche d'une minifig dans le catalogue officiel de BrickLink (API) : {name, image, year}, ou None."""
    import html as _html
    try:
        d = sources.bl_get(f"/items/MINIFIG/{urllib.parse.quote(fid)}") or {}
    except Exception:
        return None
    img = f"https://img.bricklink.com/ItemImage/MN/0/{urllib.parse.quote(str(sources.bl_fig_no(fid)))}.png"   # l'image standard des minifigs BrickLink (adresse autorisée)
    return {"name": _html.unescape(d.get("name") or ""), "image": img, "year": d.get("year_released")} if d.get("name") else None


def fig_sets_of(fid):
    """Sets du catalogue qui contiennent cette minifig : ceux de sa fiche, sinon BrickLink (« supersets », API officielle).
    Le résultat BrickLink est gardé dans sa fiche (sets, sets_t) ; vide : nouvel essai après 7 jours. Rend une liste de n° de sets."""
    with lock:
        info = _load(CACHE_FILE, {}).get("fig:" + fid) or {}
    if info.get("sets"):
        return list(info["sets"])
    if time.time() - (info.get("sets_t") or 0) < 7 * 86400 or not bl_on():
        return []
    try:   # (appel réseau : hors du verrou)
        d = sources.bl_get(f"/items/MINIFIG/{urllib.parse.quote(fid)}/supersets") or []
    except Exception:
        return []
    sets = []
    for g in d if isinstance(d, list) else []:
        for e in g.get("entries") or []:
            it = e.get("item") or {}
            if it.get("type") == "SET" and it.get("no") and it["no"] not in sets:
                sets.append(it["no"])
    with lock:
        cache = _load(CACHE_FILE, {})
        rec = cache.get("fig:" + fid)
        if isinstance(rec, dict) and not rec.get("sets"):
            rec.update(sets=sets, sets_t=int(time.time()), **({"sets_src": "BrickLink"} if sets else {}))
            _save(CACHE_FILE, cache)
    return sets


def placeholder_fig(fid, name="", image=""):
    """BrickEconomy injoignable : fiche provisoire d'une minifig (nom et photo de la reconnaissance), sans cote.
    pending_prices : relue chez BrickEconomy par le gardien horaire jusqu'à obtenir sa fiche complète."""
    if not (isinstance(image, str) and IMG_OK.match(image)):   # pas d'image : celle du catalogue de reconnaissance (Brickognize), si elle existe
        image = f"https://storage.googleapis.com/brickognize-static/thumbnails/v4.0/fig/{urllib.parse.quote(fid)}/0.webp"
        try:
            cache_image(image)
        except Exception:
            image = ""
    info = {"type": "fig", "number": fid, "name": name or fid, "pending_prices": True, "fetched_at": 0, **({"image": image} if image else {})}
    with lock:
        cache = _load(CACHE_FILE, {})
        if not cache.get("fig:" + fid):
            cache["fig:" + fid] = info
            _save(CACHE_FILE, cache)
    return info


def parts_estimate_start(item_id):
    """Set sans cote : son inventaire (Rebrickable) puis le prix de ses pièces, en arrière-plan.
    Rebrickable injoignable : rien n'est perdu, le gardien horaire réessaiera. Rend True si lancé."""
    it = next((i for i in load_db()["items"] if i["id"] == item_id), None)
    if not it or not parts_estimable(it) or it.get("moc_parts") or it.get("no_parts_est"):
        return False
    try:
        if it.get("kind") == "fig":
            lots = [dict(x) for x in rb_fig_parts(it["number"])]
        else:
            _, lots = rb_set_lots(norm_set(it["number"]) or it["number"])
    except Exception as e:
        print("Estimation par les pièces reportée", it["number"], e, flush=True)
        return False
    if not lots:
        return False
    with lock:   # pas de « updated_at » : ce n'est pas une modification de l'utilisateur
        db = load_db()
        cur = next((i for i in db["items"] if i["id"] == item_id), None)
        if not cur or cur.get("moc_parts") or cur.get("no_parts_est"):
            return False
        cur.update(moc_parts=lots, moc_file=f"Inventaire Rebrickable {it['number']}",
                   moc_price={"total": 0, "priced": 0, "missing": 0, "lots": len(lots), "done": False, "t": int(time.time())})
        _save(DB_FILE, db)
    moc_price_start(item_id, front=True)
    return True


def pending_prices_keeper():
    """Sets ajoutés sans cote, toutes les heures (et peu après le démarrage) : on retente BrickEconomy jusqu'à obtenir
    leur fiche complète ; en attendant, leur estimation par les pièces est lancée d'office (reprise si Rebrickable ne répondait pas)."""
    time.sleep(90)
    while True:
        try:
            cache = _load(CACHE_FILE, {})
            for num, v in list(cache.items()):
                if isinstance(v, dict) and v.get("pending_prices") and not num.startswith("fig:"):
                    get_set(num, force=True)   # injoignable : la fiche provisoire est gardée telle quelle
                    time.sleep(2)
                elif isinstance(v, dict) and v.get("pending_prices") and num.startswith("fig:") and not v.get("rb"):   # minifig ajoutée sans cote
                    try:
                        get_fig(num[4:], force=True)
                    except Exception:
                        pass
                    time.sleep(2)
            cache = _load(CACHE_FILE, {})
            for it in load_db()["items"]:
                if parts_estimable(it) and not it.get("moc_parts") and not it.get("no_parts_est") \
                        and (cache.get(cache_key(it)) or {}).get("pending_prices"):
                    parts_estimate_start(it["id"])
                    time.sleep(2)
        except Exception as e:
            print("Cotes en attente :", e, flush=True)
        time.sleep(3600)


_fig_info = {"on": False, "tried": {}}


def fig_info_fill(nums):
    """Arrière-plan : la fiche catalogue (nom, photo, cote) des minifigs qui n'en ont pas encore (réessai après 6 h)."""
    now = time.time()
    todo = [n for n in dict.fromkeys(nums) if now - _fig_info["tried"].get(n, 0) > 6 * 3600]
    if not todo or _fig_info["on"]:
        return
    _fig_info["on"] = True
    for n in todo:
        _fig_info["tried"][n] = now

    def run():
        try:
            for n in todo:
                try:
                    get_fig(n)
                except Exception:
                    pass
        finally:
            _fig_info["on"] = False
    threading.Thread(target=run, daemon=True).start()


def cache_key(item):
    return ("fig:" + item["number"]) if item.get("kind") == "fig" else item["number"]


# ---------------------------------------------------------------- noms français (LEGO.com)
NAMES_FILE = os.path.join(DATA, "cache_names_fr.json")
_names = {"data": None}
_names_busy = set()
NAME_RETRY = 30 * 86400   # set inconnu de LEGO.com : on réessaie au bout de 30 jours


def _names_db():
    if _names["data"] is None:
        _names["data"] = _load(NAMES_FILE, {})
    return _names["data"]


def fr_name(number, fetch=False):
    """Nom français connu d'un set (None sinon). Avec fetch=True, interroge LEGO.com si besoin."""
    if not number:
        return None
    hit = _names_db().get(number)
    if hit is not None and (hit.get("fr") or time.time() - hit.get("t", 0) < NAME_RETRY):
        return hit.get("fr")
    if not fetch or number in _names_busy:
        return None
    _names_busy.add(number)
    try:
        name = sources.lego_fr_name(number)
    except Exception:
        return None   # LEGO.com injoignable : on réessaiera
    finally:
        _names_busy.discard(number)
    with lock:
        db = _names_db()
        db[number] = {"fr": name, "t": int(time.time())}
        _save(NAMES_FILE, db)
    return name


def fill_fr_names(numbers):
    """Récupère en arrière-plan les noms français encore inconnus (un par un, sans bloquer l'application)."""
    todo = [n for n in dict.fromkeys(numbers) if n and n not in _names_db() and n not in _names_busy]
    if not todo:
        return
    _worker("sets", todo, lambda n: fr_name(n, fetch=True), 0.5)


_workers = {}   # une seule tâche de fond par type ; les numéros demandés entre-temps s'ajoutent à sa file


def _worker(kind, todo, fn, pause):
    with lock:
        w = _workers.get(kind)
        if w is not None:
            w.extend(x for x in todo if x not in w)
            return
        q = _workers[kind] = list(todo)
    def run():
        try:
            while True:
                with lock:
                    if not q:
                        _workers.pop(kind, None)
                        return
                    n = q.pop(0)
                if kind == "figs" and time.time() < _fig_pause[0]:
                    continue
                fn(n)
                time.sleep(pause)
        except Exception:
            _workers.pop(kind, None)
    threading.Thread(target=run, daemon=True).start()


_fig_pause = [0.0]   # quota de traduction atteint : pause jusqu'à cet horodatage


def fr_fig(name, fetch=False):
    """Nom français (traduit) d'une minifig, mis en cache pour toujours. None si pas encore connu."""
    if not name:
        return None
    key = "fig:" + name
    hit = _names_db().get(key)
    if hit is not None:
        return hit.get("fr")
    if not fetch or key in _names_busy or time.time() < _fig_pause[0]:
        return None
    _names_busy.add(key)
    try:
        fr = sources.fig_fr_name(name)
    except sources.QuotaError:
        _fig_pause[0] = time.time() + 6 * 3600
        return None
    except Exception:
        return None
    finally:
        _names_busy.discard(key)
    with lock:
        db = _names_db()
        db[key] = {"fr": fr, "t": int(time.time())}
        _save(NAMES_FILE, db)
    return fr


def fill_fig_names(names):
    todo = [n for n in dict.fromkeys(names) if n and ("fig:" + n) not in _names_db() and ("fig:" + n) not in _names_busy]
    if not todo or time.time() < _fig_pause[0]:
        return
    _worker("figs", todo, lambda n: fr_fig(n, fetch=True), 0.4)


def with_fr_fig(f):
    """Copie d'une minifig (fiche, résultat ou figurine d'un set) avec son nom français.
    Minifig à collectionner : pas de renvoi vers son « set » (sachet ou boîte de la série)."""
    if f and f.get("theme") in CMF_THEMES and f.get("sets"):
        f = {**f, "sets": []}
    if not f or not f.get("name"):
        return f
    en = f.get("name_en") or f["name"]
    fr = fr_fig(en)
    if not fr or fr.strip().lower() == en.strip().lower():
        return f
    return {**f, "name": fr, "name_en": en}


def _norm(t):
    import unicodedata
    t = unicodedata.normalize("NFD", str(t or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").replace("’", "'")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def fr_matches(query, limit=10):
    """Sets et minifigs dont le nom français (déjà connu) contient tous les mots cherchés."""
    words = [w for w in _norm(query).split() if w not in ("le", "la", "les", "de", "du", "des", "et", "un", "une")]
    if not words:
        return []
    out = []
    figs_by_name = None
    for key, v in list(_names_db().items()):
        fr = v.get("fr")
        toks = _norm(fr).split() if fr else []
        if not fr or not all(w in toks or (len(w) > 2 and any(x.startswith(w) for x in toks)) for w in words):
            continue
        if key.startswith("fig:"):   # minifig : retrouver sa référence d'après le nom anglais
            if figs_by_name is None:
                cache = _load(CACHE_FILE, {})
                figs_by_name = {}
                for k, c in cache.items():
                    if k.startswith("fig:") and c.get("name"):
                        figs_by_name.setdefault(c["name"], c.get("number") or k[4:])
                    for f in (c.get("minifigs") or []) if not k.startswith("fig:") else []:
                        figs_by_name.setdefault(f.get("name"), f.get("id"))
            fid = figs_by_name.get(key[4:])
            if fid:
                out.append(("fig", fid, fr))
        else:
            out.append(("set", key, fr))
        if len(out) >= limit:
            break
    return out


def with_fr(info, number=None):
    """Copie de la fiche avec le nom français (et l'anglais dans name_en) quand il existe."""
    fr = fr_name(number or info.get("number"))
    if not fr or not info.get("name") or fr.strip().lower() == str(info["name"]).strip().lower():
        return info
    return {**info, "name": fr, "name_en": info.get("name_en") or info["name"]}


MODELS_FILE = os.path.join(DATA, "cache_models.json")


def get_models(number):
    """Sous-modèles proposés pour un set (ex. les 2 voitures d'un Speed Champions)."""
    cache = _load(MODELS_FILE, {})
    if number in cache and "images" in cache[number]:
        return cache[number]
    name = None
    if sources.rebrickable_key():
        try:
            name = sources.rb(f"lego/sets/{number}/").get("name")   # (par le frein Rebrickable)
        except Exception:
            pass
    if not name:
        try:
            name = sources.full_name(number)
        except Exception:
            pass
    if not name:
        name = (_load(CACHE_FILE, {}).get(number) or {}).get("name")
    models = sources.split_models(name)
    images = [sources.submodel_image(number, k + 1) for k in range(len(models))] if models else []
    res = {"full_name": name, "models": models, "images": images}
    with lock:
        cache = _load(MODELS_FILE, {})
        cache[number] = res
        _save(MODELS_FILE, cache)
    return res


def norm_set(v):
    v = (v or "").strip()
    if not re.fullmatch(r"\d{1,7}(-\d{1,3})?", v):
        return None
    return v if "-" in v else v + "-1"


# ---------------------------------------------------------------- pièces
PARTS_CACHE = os.path.join(DATA, "cache_parts.json")
FR_COLORS = {
    "Black": "Noir", "White": "Blanc", "Red": "Rouge", "Blue": "Bleu", "Yellow": "Jaune", "Green": "Vert",
    "Dark Bluish Gray": "Gris foncé", "Light Bluish Gray": "Gris clair", "Tan": "Beige", "Dark Tan": "Beige foncé",
    "Reddish Brown": "Brun rougeâtre", "Dark Brown": "Brun foncé", "Brown": "Marron", "Orange": "Orange",
    "Dark Red": "Rouge foncé", "Dark Blue": "Bleu foncé", "Dark Green": "Vert foncé", "Lime": "Vert citron",
    "Bright Green": "Vert vif", "Medium Blue": "Bleu moyen", "Dark Azure": "Azur foncé", "Medium Azure": "Azur moyen",
    "Light Gray": "Gris clair (ancien)", "Dark Gray": "Gris foncé (ancien)", "Pearl Gold": "Or nacré",
    "Flat Silver": "Argent mat", "Metallic Silver": "Argent métallisé", "Chrome Silver": "Argent chromé",
    "Trans-Clear": "Transparent", "Trans-Red": "Rouge transparent", "Trans-Light Blue": "Bleu clair transparent",
    "Trans-Dark Blue": "Bleu foncé transparent", "Trans-Yellow": "Jaune transparent", "Trans-Orange": "Orange transparent",
    "Trans-Green": "Vert transparent", "Trans-Black": "Noir transparent", "Trans-Neon Green": "Vert fluo transparent",
    "Bright Pink": "Rose vif", "Dark Pink": "Rose foncé", "Magenta": "Magenta", "Medium Lavender": "Lavande moyen",
    "Lavender": "Lavande", "Dark Purple": "Violet foncé", "Sand Blue": "Bleu sable", "Sand Green": "Vert sable",
    "Olive Green": "Vert olive", "Nougat": "Nougat", "Medium Nougat": "Nougat moyen", "Dark Orange": "Orange foncé",
    "Bright Light Orange": "Orange clair vif", "Bright Light Yellow": "Jaune clair vif", "Coral": "Corail",
    "Dark Turquoise": "Turquoise foncé", "Light Aqua": "Aqua clair", "Yellowish Green": "Vert jaunâtre",
    "Light Nougat": "Nougat clair", "Pearl Dark Gray": "Gris foncé nacré", "Dark Bluish Grey": "Gris foncé",
}


_pcm = {"m": None, "data": None}   # cache des pièces gardé en mémoire (2,9 Mo) : relu seulement si le fichier a changé


def _parts_cache():
    """Cache des pièces (lecture seule pour les appelants ; écriture : _parts_cache_put)."""
    try:
        m = os.path.getmtime(PARTS_CACHE)
    except OSError:
        m = None
    if _pcm["data"] is None or _pcm["m"] != m:
        _pcm["data"], _pcm["m"] = _load(PARTS_CACHE, {}), m
    return _pcm["data"]


def _parts_cache_put(key, value):
    with lock:
        c = _parts_cache()
        if isinstance(value, dict) and key.startswith(("bp:", "mp:", "fu:")):   # prix d'une pièce ou d'une figurine : celui du relevé d'avant est gardé (« prev » → sa variation)
            old = c.get(key) if isinstance(c.get(key), dict) else None
            ou = (bp_unit(old) if key.startswith("bp:") else old.get("unit")) if old else None
            if ou:
                value = {**value, "prev": {"unit": ou, "t": old.get("t")}}
            elif old and old.get("prev"):
                value = {**value, "prev": old["prev"]}
        c[key] = value
        _save(PARTS_CACHE, c)
        try:
            _pcm["m"] = os.path.getmtime(PARTS_CACHE)
        except OSError:
            _pcm["m"] = None


def cached_part_from_bricklink(bl):
    key = "bl:" + bl
    c = _parts_cache()
    if key in c:
        return c[key]
    try:
        v = sources.part_from_bricklink(bl)
    except Exception:
        return None
    _parts_cache_put(key, v)
    return v


def part_detail(part_num):
    """Fiche Rebrickable d'une pièce (gardée 30 jours)."""
    key = "pd:" + part_num
    c = _parts_cache().get(key)
    if c is None or time.time() - c.get("_t", 0) > 36500 * 86400:   # (une pièce ne change pas : gardée pour toujours)
        d = sources.rb(f"lego/parts/{urllib.parse.quote(part_num)}/")
        c = {"part_num": d.get("part_num"), "name": d.get("name"), "print_of": d.get("print_of"),
             "molds": d.get("molds") or [], "alternates": d.get("alternates") or [], "_t": time.time()}
        _parts_cache_put(key, c)
    return c


def part_sets(part, part_num="", color_id=None):
    """Fiche d'une pièce (Rebrickable) et sets où elle apparaît dans cette couleur (gardée 7 jours).
    part : référence BrickLink ou Rebrickable ; part_num : référence Rebrickable si connue."""
    pn = part_num or ""
    if not pn:
        found = cached_part_from_bricklink(part) or {}
        pn = found.get("part_num") or part
    key = f"ps:{pn}|{color_id if color_id is not None else ''}"
    c = _parts_cache().get(key)
    if c and time.time() - c.get("_t", 0) < 180 * 86400:   # (relue tous les 6 mois : nouveaux sets)
        return c
    d = sources.rb(f"lego/parts/{urllib.parse.quote(pn)}/")
    ext = d.get("external_ids") or {}
    out = {"part_num": pn, "name": d.get("name"), "image": d.get("part_img_url"), "url": d.get("part_url"),
           "bricklink": (ext.get("BrickLink") or [part])[0], "year_from": d.get("year_from"), "year_to": d.get("year_to"),
           "color_id": color_id, "sets": [], "count": 0, "colors": []}
    cols = part_colors(pn)["colors"]
    out["colors"] = [{"color_id": x["color_id"], "color_fr": x["color_fr"], "rgb": x.get("rgb"), "num_sets": x.get("num_sets")} for x in cols]
    if color_id is not None:
        hit = next((x for x in cols if x["color_id"] == color_id), None)
        if hit:
            out.update(image=hit.get("image") or out["image"], elements=hit.get("elements") or [], num_sets=hit.get("num_sets"))
            r = sources.rb(f"lego/parts/{urllib.parse.quote(pn)}/colors/{color_id}/sets/?page_size=200&ordering=-year")
            out["count"] = r.get("count") or 0
            out["sets"] = [{"set_num": x["set_num"], "name": x.get("name"), "year": x.get("year"), "pieces": x.get("num_parts"),
                            "image": x.get("set_img_url"), "url": x.get("set_url")} for x in r.get("results", [])]
        else:
            out["no_color"] = True   # la pièce n'existe pas dans cette couleur chez LEGO
    out["_t"] = time.time()
    _parts_cache_put(key, out)
    return out


# ---------------------------------------------------------------- pièces des sets possédés (recherche « mes sets qui ont cette pièce »)
OWNED_PARTS_FILE = os.path.join(DATA, "cache_owned_parts.json")   # {set: [[part_num, color_id, qty], ...]} (un inventaire ne change pas)
_op = {"mem": None, "busy": False}


def _owned_parts():
    if _op["mem"] is None:
        _op["mem"] = _load(OWNED_PARTS_FILE, {})
    return _op["mem"]


def owned_set_numbers():
    db = load_db()
    kinds = list_kinds(db)
    return list(dict.fromkeys(norm_set(i["number"]) or i["number"] for i in db["items"]
                              if i.get("kind", "set") == "set" and kinds.get(i["list_id"]) == "collection"))


def owned_parts_fill():
    """Arrière-plan : inventaire (figurines comprises) de chaque set possédé pas encore connu."""
    with lock:
        if _op["busy"]:
            return
        _op["busy"] = True

    def run():
        try:
            for num in owned_set_numbers():
                if num in _owned_parts():
                    continue
                rows = None
                for attempt in range(4):
                    try:
                        rows = sources.set_parts(num)
                        break
                    except Exception as e:
                        if "404" in str(e):   # set inconnu de Rebrickable : on ne le redemande pas
                            rows = []
                            break
                        print(f"Inventaire de {num} indisponible ({e}), nouvel essai…", flush=True)
                        time.sleep(5 * (attempt + 1))   # limite de débit Rebrickable : on patiente
                if rows is None:
                    continue
                agg = {}
                for r in rows:
                    if r.get("spare"):
                        continue
                    k = (r["part_num"], r["color_id"])
                    agg[k] = agg.get(k, 0) + r["quantity"]
                with lock:
                    _owned_parts()[num] = [[pn, c, q] for (pn, c), q in agg.items()]
                    _save(OWNED_PARTS_FILE, _owned_parts())
        finally:
            _op["busy"] = False
    threading.Thread(target=run, daemon=True).start()


# ---------------------------------------------------------------- toutes les pièces de la collection (par pièce, couleurs réunies)
PART_NAMES_FILE = os.path.join(DATA, "cache_part_names.json")   # {part_num: {name, image, cat}} — un nom de pièce ne change pas
_pn = {"mem": None, "busy": False}


def part_names():
    if _pn["mem"] is None:
        _pn["mem"] = _load(PART_NAMES_FILE, {})
    return _pn["mem"]


def part_names_fill(pns):
    """Arrière-plan : nom, photo et catégorie des pièces inconnues, par paquets de 100 (Rebrickable)."""
    with lock:
        if _pn["busy"]:
            return
        _pn["busy"] = True

    def run():
        try:
            todo = [x for x in dict.fromkeys(pns) if x not in part_names()]
            for k in range(0, len(todo), 100):
                chunk = todo[k:k + 100]
                r = None
                for attempt in range(4):   # erreur passagère (limite de débit) : on réessaie un peu plus tard
                    try:
                        r = sources.rb("lego/parts/?page_size=100&part_nums=" + urllib.parse.quote(",".join(chunk)))
                        break
                    except Exception:
                        time.sleep(5 * (attempt + 1))
                if r is None:
                    continue
                got = {x["part_num"]: {"name": x.get("name"), "image": x.get("part_img_url"), "cat": x.get("part_cat_id"),
                                       "bl": ((x.get("external_ids") or {}).get("BrickLink") or [None])[0]}
                       for x in r.get("results", [])}
                for x in chunk:
                    got.setdefault(x, {"name": None, "image": None, "cat": None})
                with lock:
                    part_names().update(got)
                    _save(PART_NAMES_FILE, part_names())
        finally:
            _pn["busy"] = False
    threading.Thread(target=run, daemon=True).start()


CAT_FR = {
    "Animal / Creature Accessories": "Animaux : accessoires", "Animal / Creature Body Parts": "Animaux : parties du corps",
    "Animals / Creatures": "Animaux", "Bars, Ladders and Fences": "Barres, échelles et barrières", "Baseplates": "Plaques de base",
    "Bricks": "Briques", "Bricks Curved": "Briques courbes", "Bricks Round and Cones": "Briques rondes et cônes",
    "Bricks Sloped": "Briques inclinées", "Bricks Special": "Briques spéciales", "Bricks Wedged": "Briques biseautées",
    "Containers": "Conteneurs", "Electronics": "Électronique", "Energy Effects": "Effets d'énergie",
    "Flags, Banners and Signs": "Drapeaux, bannières et panneaux", "Gear Parts": "Pièces d'engrenage",
    "Hinges, Arms and Turntables": "Charnières, bras et plateaux tournants", "Large Buildable Figures": "Grandes figurines à construire",
    "Magnets and Holders": "Aimants et supports", "Mechanical": "Mécanique", "Minidoll Heads": "Mini-poupées : têtes",
    "Minidoll Lower Body": "Mini-poupées : bas du corps", "Minidoll Upper Body": "Mini-poupées : haut du corps",
    "Minifig Accessories": "Figurine : accessoires", "Minifig Heads": "Figurine : têtes", "Minifig Headwear": "Figurine : coiffes",
    "Minifig Headwear Accessories": "Figurine : accessoires de coiffe", "Minifig Hipwear": "Figurine : accessoires de taille",
    "Minifig Lower Body": "Figurine : jambes", "Minifig Neckwear": "Figurine : accessoires de cou",
    "Minifig Shields, Weapons, & Tools": "Figurine : boucliers, armes et outils", "Minifig Upper Body": "Figurine : torses",
    "Minifigs": "Figurines", "Non-Buildable Figures (Duplo, Fabuland, etc)": "Figurines non constructibles",
    "Non-System Parts": "Pièces hors système", "Other": "Autres", "Panels": "Panneaux", "Plants & Trees": "Plantes et arbres",
    "Plates": "Plaques", "Plates Round Curved and Dishes": "Plaques rondes, courbes et paraboles", "Plates Special": "Plaques spéciales",
    "Plates Wedged": "Plaques biseautées", "Pneumatics": "Pneumatique", "Projectiles / Launchers": "Projectiles et lanceurs",
    "Rock": "Roches", "Stickers": "Autocollants", "String, Bands and Reels": "Ficelles, élastiques et bobines",
    "Supports, Girders and Cranes": "Supports, poutres et grues", "Technic Axles": "Technic : axes", "Technic Beams": "Technic : poutres",
    "Technic Beams Special": "Technic : poutres spéciales", "Technic Bricks": "Technic : briques", "Technic Bushes": "Technic : bagues",
    "Technic Connectors": "Technic : connecteurs", "Technic Gears": "Technic : engrenages", "Technic Panels": "Technic : panneaux",
    "Technic Pins": "Technic : goupilles", "Technic Special": "Technic : spéciales",
    "Technic Steering, Suspension and Engine": "Technic : direction, suspension et moteur", "Tiles": "Tuiles",
    "Tiles Round and Curved": "Tuiles rondes et courbes", "Tiles Special": "Tuiles spéciales", "Tools": "Outils",
    "Transportation - Land": "Transport terrestre", "Transportation - Sea and Air": "Transport maritime et aérien",
    "Tubes and Hoses": "Tubes et tuyaux", "Wheels and Tyres": "Roues et pneus", "Windows and Doors": "Fenêtres et portes",
    "Windscreens and Fuselage": "Pare-brise et fuselages",
}


def part_categories():
    """Catégories Rebrickable (Briques, Plaques, Tuiles…), gardées 30 jours."""
    c = _parts_cache().get("pcats")
    if not c or time.time() - c.get("_t", 0) > 365 * 86400:
        try:
            d = sources.rb("lego/part_categories/?page_size=200")
            c = {"cats": {str(x["id"]): x["name"] for x in d.get("results", [])}, "_t": time.time()}
            _parts_cache_put("pcats", c)
        except Exception:
            return {k: CAT_FR.get(v, v) for k, v in ((c or {}).get("cats") or {}).items()}
    return {k: CAT_FR.get(v, v) for k, v in c["cats"].items()}   # en français quand on connaît la traduction


PART_PRICES_FILE = os.path.join(DATA, "cache_part_prices.json")   # {"réf|couleur rb": {"unit", "t"}} : prix des pièces de la collection
PART_PRICE_TTL = 30 * 86400
_pp = {"mem": None, "busy": False}


def part_prices():
    if _pp["mem"] is None:
        _pp["mem"] = _load(PART_PRICES_FILE, {})
    return _pp["mem"]


def part_unit(pn, color_id, rbmap, pc):
    """Prix unitaire connu (BrickOwl) d'une pièce dans une couleur Rebrickable, sinon None (caches passés une fois pour toutes)."""
    blc = rbbl_map().get(str(color_id))
    if blc is not None:   # BrickLink d'abord (moyenne des annonces)
        u = bp_unit(pc.get(f"bp:{(part_names().get(pn) or {}).get('bl') or pn}|{blc}"))
        if u:
            return u
    e = part_prices().get(f"{pn}|{color_id}")
    if e:
        return e.get("unit")
    bo = rbmap.get(str(color_id))
    hit = pc.get(f"mp:{pn}|{bo}") if bo else None   # déjà chiffrée pour un MOC
    return (hit or {}).get("unit")


_ppg = {"done": 0, "total": 0}


# ---------------------------------------------------------------- prix approché d'une pièce sans prix
# Pièce introuvable sur BrickOwl : prix calqué sur les pièces qui lui ressemblent le plus et qui ont un prix,
# dans cet ordre : la même pièce dans d'autres couleurs ; le même moule (versions imprimées entre elles, sinon
# toutes) ; les pièces de même nom de base (« Plate 1 x 2 », « Tile 2 x 2 »…) ; sinon la médiane de sa catégorie.
_sim = {"t": 0, "key": None, "idx": None}
_PRINT = re.compile(r"^(.+?)(?:pb|pr|pat|px|ps|pt|pat)\d+.*$")


def _base_mold(pn):
    m = _PRINT.match(str(pn))
    return (m.group(1), True) if m else (str(pn), False)


def _name_stem(name):
    n = (name or "").lower()
    n = re.split(r" with | - |, | \[| \(| print| pattern| decorated| sticker", n)[0]
    return n.strip()


def _median(v):
    v = sorted(v)
    return (v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2) if v else None


def _sim_index():
    """Index des prix connus (réf. Rebrickable + couleur), reconstruit au plus toutes les 10 minutes."""
    pp, pc = part_prices(), _parts_cache()
    key = (len(pp), _pcm["m"])
    if _sim["idx"] is not None and (key == _sim["key"] or time.time() - _sim["t"] < 600):
        return _sim["idx"]
    bo_rb = {}
    for k, v in (moc_color_maps().get("rb") or {}).items():
        bo_rb.setdefault(v, int(k))
    known = {}
    for k, e in list(pp.items()):
        if e.get("unit"):
            pn, _, c = k.partition("|")
            known[(pn, int(c) if c.lstrip("-").isdigit() else c)] = e["unit"]
    for k, e in list(pc.items()):
        if k.startswith("mp:") and (e or {}).get("unit"):   # pièces chiffrées pour un MOC (réf. BrickLink + couleur BrickOwl)
            bl, _, bo = k[3:].partition("|")
            pn = (pc.get("bl:" + bl) or {}).get("part_num") or bl
            c = bo_rb.get(bo)
            if c is not None:
                known.setdefault((pn, c), e["unit"])
    names = part_names()
    idx = {"part": {}, "mold": {}, "stem": {}, "cat": {}}
    for (pn, c), u in known.items():
        idx["part"].setdefault(pn, {})[c] = u
        base, printed = _base_mold(pn)
        idx["mold"].setdefault(base, []).append((pn, c, u, printed))
        nm = names.get(pn) or {}
        st = _name_stem(nm.get("name"))
        if st:
            idx["stem"].setdefault(st, []).append(u)
        if nm.get("cat") is not None:
            idx["cat"].setdefault(nm["cat"], []).append(u)
    _sim.update(t=time.time(), key=key, idx=idx)
    return idx


def similar_unit(pn, color_id):
    """Prix approché d'une pièce sans prix (voir plus haut), ou None si rien de comparable."""
    idx = _sim_index()
    other = [u for c, u in (idx["part"].get(pn) or {}).items() if c != color_id]
    if other:
        return round(_median(other), 3)
    base, printed = _base_mold(pn)
    mold = [x for x in idx["mold"].get(base) or [] if x[0] != pn]
    if mold:
        same = [x for x in mold if x[3] == printed] or mold
        col = [x[2] for x in same if x[1] == color_id]
        return round(_median(col or [x[2] for x in same]), 3)
    nm = part_names().get(pn) or {}
    st = _name_stem(nm.get("name"))
    if st and idx["stem"].get(st):
        return round(_median(idx["stem"][st]), 3)
    cat = idx["cat"].get(nm.get("cat")) if nm.get("cat") is not None else None
    if cat and len(cat) >= 3:
        return round(_median(cat), 3)
    return None


def bl_price_known(part, color=None, color_id=None):
    """Le prix de cette pièce vient-il d'un relevé BrickLink (fiable : ventes réelles / annonces) ? part : réf. BrickLink ou
    Rebrickable ; color : couleur BrickOwl (nom) ou color_id : couleur Rebrickable."""
    blc = bo_bl_color(color) if color is not None else rbbl_map().get(str(color_id)) if color_id is not None else None
    if blc is None:
        return False
    pc = _parts_cache()
    for ref in {part, (part_names().get(part) or {}).get("bl") or part}:
        if bp_unit(pc.get(f"bp:{ref}|{blc}")):
            return True
    return False


def sane_unit(pn, color_id, u, offers=None, trusted=False):
    """(trusted : prix BrickLink — jamais remplacé.)"""
    if trusted:
        return u, False
    return _sane_unit(pn, color_id, u, offers)


def _sane_unit(pn, color_id, u, offers=None):
    """Prix BrickOwl invraisemblable (marché très mince : quelques vendeurs hors de prix) → prix des pièces semblables.
    Rend (prix, estimé ?). Une pièce unie ne coûte pas 30 fois plus dans une couleur que dans les autres ;
    une offre isolée (moins de 3) ne vaut pas 10 fois plus que les pièces qui lui ressemblent."""
    if u is None or u <= 2:
        return u, False
    other = [v for c, v in (_sim_index()["part"].get(pn) or {}).items() if c != color_id]
    if len(other) >= 1 and u > 30 * _median(other):
        return round(_median(other), 3), True
    if offers is not None and offers < 3:
        s = similar_unit(pn, color_id)
        if s and u > 10 * s:
            return s, True
    return u, False


MANUAL_FILE = os.path.join(DATA, "manual_prices.json")   # {"rb:<n° Rebrickable>|<n° couleur>": {"unit", "t"}, "bl:<réf. BrickLink>|<couleur BrickOwl>": …}


def manual_price(part_num=None, color_id=None, part=None, color=None):
    """Prix saisi à la main pour une pièce introuvable (servi seulement à défaut de prix BrickOwl ou d'estimation)."""
    mp = _load(MANUAL_FILE, {})
    if not mp:
        return None
    keys = []
    if part_num and color_id is not None:
        keys.append(f"rb:{part_num}|{color_id}")
    if part and color:
        keys.append(f"bl:{part}|{color}")
        pn = (_parts_cache().get("bl:" + part) or {}).get("part_num")   # même pièce vue par l'autre catalogue
        cid = next((k for k, v in (moc_color_maps().get("rb") or {}).items() if v == color), None) if pn else None
        if pn and cid is not None:
            keys.append(f"rb:{pn}|{cid}")
    if part_num and color_id is not None:
        bo = (moc_color_maps().get("rb") or {}).get(str(color_id))
        if bo:
            keys.append(f"bl:{part_num}|{bo}")
    for k in keys:
        if (mp.get(k) or {}).get("unit") is not None:
            return mp[k]["unit"]
    return None


def similar_unit_bl(bl, bo_color):
    """Même chose pour une pièce de MOC (réf. BrickLink + couleur BrickOwl)."""
    pn = (_parts_cache().get("bl:" + bl) or {}).get("part_num") or bl
    c = next((int(k) for k, v in (moc_color_maps().get("rb") or {}).items() if v == bo_color), None)
    return similar_unit(pn, c)


def part_prices_fill(combos, on_done=None, max_age=PART_PRICE_TTL):
    """Arrière-plan : prix BrickOwl de chaque pièce + couleur, les plus nombreuses d'abord ; sauvegarde par paquets."""
    with lock:
        if _pp["busy"]:
            return
        _pp["busy"] = True

    def run():
        try:
            rbmap = moc_color_maps().get("rb") or {}
            names = part_names()
            done = 0
            _ppg.update(done=0, total=len(combos))
            for pn, c in combos:
                _ppg["done"] += 1
                k = f"{pn}|{c}"
                e = part_prices().get(k)
                if e and time.time() - e.get("t", 0) < max_age:
                    continue
                bo = rbmap.get(str(c))
                if not bo:
                    continue
                try:
                    r = sources.moc_part_price((names.get(pn) or {}).get("bl") or pn, bo)
                except Exception:
                    time.sleep(10)   # BrickOwl ne répond pas : on ralentit
                    continue
                part_prices()[k] = {"unit": (r or {}).get("unit"), "offers": (r or {}).get("offers"), "t": int(time.time())}
                done += 1
                if done % 25 == 0:
                    with lock:
                        _save(PART_PRICES_FILE, part_prices())
                time.sleep(1.0)   # rythme raisonnable pour BrickOwl
            with lock:
                _save(PART_PRICES_FILE, part_prices())
            if on_done:
                on_done()
        finally:
            _pp["busy"] = False
    threading.Thread(target=run, daemon=True).start()


WEEK = 7 * 86400


TODO_CATS = ["Photo", "Pièces", "Accessoires", "Autres"]   # catégories de tâches de base ; les autres sont dans les réglages


NOTES_FILE = os.path.join(DATA, "notes.json")


def free_todos():
    return _load(NOTES_FILE, {}).get("todos") or []


TODO_OTHER = "Autres"   # catégorie de repli : ni supprimée ni renommée (les tâches d'une catégorie supprimée y vont)
TODO_ICON_BASE = {"Photo": "📷", "Pièces": "🧱", "Accessoires": "🎒", "Autres": "📝"}   # icônes des catégories de base (même table que l'interface)


def todo_cats():
    """Catégories de tâches, dans l'ordre : la liste gérée par l'utilisateur (réglage « todo_cat_list ») ; avant toute gestion,
    les catégories de base + celles ajoutées (ancien réglage « todo_cats »). « Autres » est toujours là."""
    st = _load(sources.SETTINGS_FILE, {})
    lst = st.get("todo_cat_list")
    if not isinstance(lst, list):
        lst = TODO_CATS + [c for c in st.get("todo_cats") or [] if isinstance(c, str) and c and c not in TODO_CATS]
    out = []
    for c in lst:
        if isinstance(c, str) and c and c not in out:
            out.append(c)
    if TODO_OTHER not in out:
        out.append(TODO_OTHER)
    return out


def todo_icons():
    """Icônes des catégories renommées {nom : icône} (une catégorie de base renommée garde la sienne)."""
    ic = _load(sources.SETTINGS_FILE, {}).get("todo_icons") or {}
    return {k: v for k, v in ic.items() if isinstance(k, str) and isinstance(v, str)} if isinstance(ic, dict) else {}


def todo_cat_change(op, old, new=""):
    """Renomme (op « rename ») ou supprime (op « delete ») une catégorie de tâches : les tâches des fiches et les notes libres suivent
    (supprimée : elles vont dans « Autres »). La date de modification des fiches ne bouge pas (une tâche n'est pas une modification).
    Rend le nombre de tâches déplacées ; lève ValueError avec un message lisible."""
    cats = todo_cats()
    if old == TODO_OTHER:
        raise ValueError("« Autres » ne peut être ni supprimée ni renommée : c'est là que vont les tâches sans catégorie.")
    if op == "rename":
        if not new:
            raise ValueError("Nom vide")
        if any(c.lower() == new.lower() and c != old for c in cats):
            raise ValueError(f"La catégorie « {new} » existe déjà")
        dest = new
    elif op == "delete":
        dest = TODO_OTHER
    else:
        raise ValueError("Opération inconnue")
    moved = 0
    with lock:
        db = load_db()
        for it in db["items"]:
            for t in it.get("todos") if isinstance(it.get("todos"), list) else []:
                if isinstance(t, dict) and t.get("cat") == old:
                    t["cat"] = dest
                    moved += 1
        if moved:
            _save(DB_FILE, db)
        notes = _load(NOTES_FILE, {})
        nf = 0
        for t in notes.get("todos") or []:
            if isinstance(t, dict) and t.get("cat") == old:
                t["cat"] = dest
                nf += 1
        if nf:
            _save(NOTES_FILE, notes)
        if old not in cats and not (moved + nf):   # (une catégorie peut n'exister que par ses tâches : elle se gère aussi)
            raise ValueError("Catégorie introuvable")
        st = _load(sources.SETTINGS_FILE, {})
        icons = todo_icons()
        if op == "rename":
            lst = [dest if c == old else c for c in cats] if old in cats else [c for c in cats if c != TODO_OTHER] + [dest, TODO_OTHER]
            ic = icons.pop(old, None) or TODO_ICON_BASE.get(old)
            if ic:
                icons[dest] = ic   # l'icône suit le nom
        else:
            lst = [c for c in cats if c != old]
            icons.pop(old, None)
        st.update(todo_cat_list=lst, todo_icons=icons)
        _save(sources.SETTINGS_FILE, st)
        os.chmod(sources.SETTINGS_FILE, 0o600)
    return moved + nf


def clean_todos(b):
    """Tâches d'une fiche : [{cat, note}]. Ancien format (todo + todo_note) : une tâche « Autres »."""
    raw = b.get("todos")
    if not isinstance(raw, list):
        return [{"cat": "Autres", "note": str(b.get("todo_note") or "").strip()[:500]}] if b.get("todo") else []
    out = []
    for t in raw[:12]:
        if isinstance(t, dict):
            fig = str(t.get("fig") or "")
            out.append({"cat": " ".join(str(t.get("cat") or "").split())[:30] or "Autres", "note": str(t.get("note") or "").strip()[:500],
                        **({"fig": fig, "fig_name": " ".join(str(t.get("fig_name") or "").split())[:80]} if re.fullmatch(r"[\w.-]{1,40}", fig) else {}),   # figurine du set
                        **({"rule": str(t["rule"])} if re.fullmatch(r"[\w-]{1,48}", str(t.get("rule") or "")) else {})})   # tâche posée par une règle du back office
    return out


UI_THEMES = ("moderne", "classique", "verre", "brique", "minimal", "neon", "bd", "pastel", "technique", "nuit")   # thèmes de l'application (style.css : html[data-ui=…])


def ui_theme():
    """Thème de l'application (Réglages → Apparence) : « moderne » d'office."""
    t = _load(sources.SETTINGS_FILE, {}).get("ui_theme")
    return t if t in UI_THEMES else "moderne"


def _settings_update(**kw):
    with lock:
        st = _load(sources.SETTINGS_FILE, {})
        st.update(kw)
        _save(sources.SETTINGS_FILE, st)
        os.chmod(sources.SETTINGS_FILE, 0o600)


def start_parts_pricing(max_age=PART_PRICE_TTL):
    """Chiffre les pièces de la collection sans prix ou dont le prix a plus de max_age secondes.
    Mémorisé dans les réglages : repris automatiquement après un redémarrage, jusqu'à la fin."""
    if _pp["busy"]:
        return {"started": False, "running": True, **_ppg}
    collection_parts()
    pp, now = part_prices(), time.time()
    stale = [(pn, c) for pn, cc in _owned_combos() for c in cc
             if f"{pn}|{c}" in pp and now - pp[f"{pn}|{c}"].get("t", 0) > max_age]
    todo = list(dict.fromkeys((getattr(collection_parts, "todo", None) or []) + stale))
    if not todo:
        _settings_update(parts_pricing=None, parts_priced_at=int(time.time()))
        return {"started": False, "running": False, "done": 0, "total": 0}
    _settings_update(parts_pricing={"max_age": max_age, "since": int(time.time())})

    def done():   # tout chiffré : on l'oublie, et la mise à jour hebdomadaire prend le relais
        _settings_update(parts_pricing=None, parts_priced_at=int(time.time()))
        print("Chiffrage des pièces terminé", flush=True)
    part_prices_fill(todo, on_done=done, max_age=max_age)
    return {"started": True, "running": True, "done": 0, "total": len(todo)}


def parts_pricing_keeper():
    """Au démarrage : reprend un chiffrage interrompu. Ensuite : une fois tout chiffré, mise à jour chaque semaine."""
    time.sleep(20)
    while True:
        try:
            st = _load(sources.SETTINGS_FILE, {})
            if not _pp["busy"]:
                if st.get("parts_pricing"):   # chiffrage commencé et pas fini (redémarrage) : on reprend
                    r = start_parts_pricing(st["parts_pricing"].get("max_age", PART_PRICE_TTL))
                    if r.get("started"):
                        print(f"Chiffrage des pièces repris : {r['total']} restants", flush=True)
                elif st.get("parts_priced_at") and time.time() - st["parts_priced_at"] > WEEK:   # hebdomadaire
                    r = start_parts_pricing(WEEK)
                    if r.get("started"):
                        print(f"Mise à jour hebdomadaire des prix des pièces : {r['total']}", flush=True)
        except Exception as e:
            print("Chiffrage des pièces :", e, flush=True)
        time.sleep(3 * 3600)


def _owned_combos():
    """(réf., couleurs) des pièces des sets de la collection."""
    agg = {}
    kinds, owned = list_kinds(), _owned_parts()
    for it in load_db()["items"]:
        if it.get("kind", "set") == "set" and kinds.get(it["list_id"]) == "collection":
            for pn, c, _ in owned.get(norm_set(it["number"]) or it["number"]) or []:
                agg.setdefault(pn, set()).add(c)
    return agg.items()


# ---------------------------------------------------------------- pièces d'un set : hors figurines + chaque figurine
SPLIT_FILE = os.path.join(DATA, "cache_set_split.json")   # {set: {"nofig": [[pn, c, n]], "figs": [{"rb", "name", "qty", "parts": [[pn, c, n]]}]}}
_split = {"mem": None, "busy": False}


def set_splits():
    if _split["mem"] is None:
        _split["mem"] = _load(SPLIT_FILE, {})
    return _split["mem"]


def set_split_fill(nums):
    """Arrière-plan (Rebrickable, 1 requête/s) : pièces d'un set sans ses figurines, et pièces de chacune de ses figurines."""
    with lock:
        if _split["busy"]:
            return
        _split["busy"] = True

    def run():
        try:
            for num in nums:
                if num in set_splits():
                    continue
                try:
                    nofig = {}
                    for r in inventory_rows(num):
                        k = (r["part_num"], r["color_id"])
                        nofig[k] = nofig.get(k, 0) + r["quantity"]
                    figs = []
                    for m in sources.rb(f"lego/sets/{urllib.parse.quote(num)}/minifigs/?page_size=100").get("results", []):
                        parts = {}
                        for p in rb_fig_parts(m["set_num"]):
                            k = (p["part_num"], p["color_id"])
                            parts[k] = parts.get(k, 0) + (p.get("qty") or 1)
                        figs.append({"rb": m["set_num"], "name": m.get("set_name") or "", "qty": m.get("quantity", 1),
                                     "parts": [[pn, c, n] for (pn, c), n in parts.items()]})
                except Exception as e:
                    if "404" in str(e):
                        set_splits()[num] = {"nofig": None, "figs": []}
                    else:
                        print("Pièces par figurine", num, e, flush=True)
                        time.sleep(5)
                    continue
                with lock:
                    set_splits()[num] = {"nofig": [[pn, c, n] for (pn, c), n in nofig.items()], "figs": figs}
                    _save(SPLIT_FILE, set_splits())
        finally:
            _split["busy"] = False
    threading.Thread(target=run, daemon=True).start()


def _fig_match(be_figs, rb_figs):
    """Figurines BrickEconomy (sw0001…) → figurines Rebrickable du set (fig-000123), par les mots de leur nom."""
    words = lambda t: {w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if len(w) > 2}
    out, free = {}, list(range(len(rb_figs)))
    pairs = sorted(((len(words(f.get("name_en") or f.get("name")) & words(r["name"])), i, j)
                    for i, f in enumerate(be_figs) for j, r in enumerate(rb_figs)), reverse=True)
    for score, i, j in pairs:
        if score and be_figs[i]["id"] not in out and j in free:
            out[be_figs[i]["id"]] = rb_figs[j]; free.remove(j)
    left = [f for f in be_figs if f["id"] not in out]
    if len(left) == 1 and len(free) == 1:   # la dernière restante
        out[left[0]["id"]] = rb_figs[free[0]]
    return out


def owned_set_rows(it, info, rows):
    """Pièces vraiment possédées d'un set : parties possédées (au prorata) hors figurines, plus les figurines présentes.
    None tant que le détail par figurine n'est pas connu (on garde alors le calcul simple)."""
    q = max(1, int(it.get("quantity", 1) or 1))
    por = it.get("portion", 100)
    mfs = info.get("minifigs") or []
    with_figs = it.get("with_minifigs", True)
    have = fig_have(it, mfs, q) if with_figs else {f["id"]: 0 for f in mfs}
    full = all(have.get(f["id"], 0) >= f.get("qty", 1) * q for f in mfs) and with_figs
    if por >= 100 and full:
        return None   # tout est là : l'inventaire complet
    num = norm_set(it["number"]) or it["number"]
    sp = set_splits().get(num)
    if sp is None:
        return False   # détail à récupérer
    if sp.get("nofig") is None:
        return None
    out = {}
    add = lambda pn, c, n: out.__setitem__((pn, c), out.get((pn, c), 0) + n) if n > 0 else None
    for pn, c, n in sp["nofig"]:
        add(pn, c, round(n * q * por / 100) if por < 100 else n * q)
    match = _fig_match(mfs, sp["figs"])
    for f in mfs:
        r, h = match.get(f["id"]), have.get(f["id"], 0)
        if r and h:
            for pn, c, n in r["parts"]:
                add(pn, c, n * h)
    return [[pn, c, n] for (pn, c), n in out.items()]


def collection_parts(list_id="", with_prices=True):
    """Pièces des sets de la collection (ou d'une liste et ses sous-listes), regroupées par pièce, couleurs réunies."""
    db, kinds = load_db(), list_kinds()
    scope = None
    if list_id:
        scope, grow = {list_id}, True
        while grow:
            grow = False
            for l in db["lists"]:
                if l.get("parent_id") in scope and l["id"] not in scope:
                    scope.add(l["id"]); grow = True
    owned, agg, pending = _owned_parts(), {}, 0
    sets_info, split_todo = _load(CACHE_FILE, {}), []
    pc, bo_rb, miss_bl = _parts_cache(), {}, []
    for k, v in (moc_color_maps().get("rb") or {}).items():
        bo_rb.setdefault(v, int(k))   # couleur BrickOwl → n° Rebrickable
    add = lambda pn, c, n: agg.setdefault(pn, {}).__setitem__(c, agg.get(pn, {}).get(c, 0) + n) if n > 0 else None
    for it in db["items"]:
        if kinds.get(it["list_id"]) != "collection" or (scope and it["list_id"] not in scope):
            continue
        q = max(1, int(it.get("quantity", 1) or 1))
        if it.get("kind") == "custom" and it.get("custom_type") != "fig":   # MOC : sa liste de pièces (comme la case « Pièces »)
            for x in it.get("moc_parts") or []:
                bl = x.get("part")
                if not bl:
                    continue
                if "bl:" + bl not in pc:
                    miss_bl.append(bl)
                pn = (pc.get("bl:" + bl) or {}).get("part_num") or bl
                c = x.get("color_id") if x.get("color_id") is not None else bo_rb.get(x.get("color"))
                if c is not None:
                    add(pn, c, int(x.get("qty", 1) or 1) * q)
            continue
        if it.get("kind", "set") != "set":
            continue
        rows = owned.get(norm_set(it["number"]) or it["number"])
        if rows is None:
            pending += 1
            continue
        # ce que je n'ai pas est exclu : figurines absentes, parties d'un set divisé non possédées (hors figurines, au prorata)
        mine = owned_set_rows(it, sets_info.get(it["number"]) or {}, rows)
        if mine:
            for pn, c, n in mine:
                add(pn, c, n)
            continue
        if mine is False:
            split_todo.append(norm_set(it["number"]) or it["number"])
        por = it.get("portion", 100)   # en attendant le détail : au prorata de la partie possédée
        for pn, c, n in rows:
            add(pn, c, round(n * q * por / 100) if por < 100 else n * q)
    if split_todo:
        set_split_fill(list(dict.fromkeys(split_todo)))
    if pending:
        owned_parts_fill()
    if miss_bl:
        moc_names_fill(list(dict.fromkeys(miss_bl)))
    names = part_names()
    need = [x for x in agg if x not in names]
    if need:
        part_names_fill(need)
    cols, cats = colors_fr(), part_categories()
    rbmap, pcache = moc_color_maps().get("rb") or {}, _parts_cache()
    out, todo, tq, pq, tv, aq = [], [], 0, 0, 0.0, 0
    for pn, cc in agg.items():
        info = names.get(pn) or {}
        colors, value, priced, approx = [], 0.0, 0, 0
        cimg = {x.get("color_id"): x.get("image") for x in (pcache.get("pc:" + pn) or []) if isinstance(x, dict) and x.get("image")}   # photo par couleur, si connue
        for c, n in cc.items():
            u = part_unit(pn, c, rbmap, pcache)
            tried = u is not None or f"{pn}|{c}" in part_prices()   # tried sans prix : introuvable sur BrickOwl
            u, ap = sane_unit(pn, c, u, (part_prices().get(f"{pn}|{c}") or {}).get("offers"), bl_price_known(pn, color_id=c))
            manual = False
            if u is None:
                todo.append((n, pn, c))
                u = manual_price(pn, c)   # mon prix d'abord, sinon calqué sur les pièces qui lui ressemblent
                manual = u is not None
                if u is None:
                    u = similar_unit(pn, c)
                    ap = u is not None
            if u is not None:
                value += u * n; priced += n
                approx += n if ap else 0
            colors.append({"color_id": c, "color_fr": (cols.get(str(c)) or {}).get("fr", str(c)), "rgb": (cols.get(str(c)) or {}).get("rgb"),
                           "trans": (cols.get(str(c)) or {}).get("trans"), "qty": n, "unit": u, "tried": tried, **({"approx": True} if ap else {}), **({"manual": True} if manual else {}),
                           **({"image": cimg[c]} if cimg.get(c) else {})})
        total = sum(cc.values())
        tq += total; pq += priced; tv += value; aq += approx
        out.append({"part_num": pn, "name": info.get("name") or pn, "image": info.get("image"),
                    "cat": cats.get(str(info.get("cat")), "") if info.get("cat") is not None else "",
                    "total": total, "value": round(value, 2), "priced": priced, **({"approx": approx} if approx else {}),
                    "colors": sorted(colors, key=lambda x: -x["qty"])})
    out.sort(key=lambda x: -x["total"])
    if not with_prices:   # page publique : aucun prix
        for x in out:
            x.pop("value", None); x.pop("priced", None); x.pop("approx", None)
            for c in x["colors"]:
                c.pop("unit", None); c.pop("tried", None); c.pop("approx", None)
        return {"parts": out, "pending_sets": pending, "pending_names": len(need)}
    collection_parts.todo = [(pn, c) for _, pn, c in sorted(todo, reverse=True)]   # repris par le chiffrage de nuit
    return {"parts": out, "pending_sets": pending, "pending_names": len(need),
            "value": round(tv, 2), "priced_share": round((pq - aq) / tq * 100, 1) if tq else 0,   # chiffrées pour de vrai (BrickOwl)
            "approx_share": round(aq / tq * 100, 1) if tq else 0,
            "pricing": _pp["busy"], "to_price": len(todo)}


def item_parts_refresh(item_id):
    """Après un ajout ou une modification : inventaire du set (s'il manque), puis nom, photo et prix de SES pièces,
    tout de suite et en arrière-plan (les autres attendent la nuit)."""
    def run():
        try:
            db = load_db()
            it = next((i for i in db["items"] if i["id"] == item_id), None)
            if it and it.get("kind", "set") == "set" and any(l["id"] == it["list_id"] and l.get("gift") for l in db["lists"]):
                extras_start(it["number"])   # « À surveiller » : prix de la boîte et du plan seuls
            if not it or list_kinds().get(it["list_id"]) != "collection":
                return
            if cmf_fig_of(it):   # minifig à collectionner ajoutée comme set : minifig seule
                convert_cmf_sets()
                return
            if it.get("kind", "set") == "set":
                extras_start(it["number"])
            combos = []
            if it.get("kind", "set") == "set":
                num = norm_set(it["number"]) or it["number"]
                if num not in _owned_parts():   # nouveau set : son inventaire maintenant
                    for attempt in range(3):
                        try:
                            rows = sources.set_parts(num)
                            break
                        except Exception as e:
                            rows = [] if "404" in str(e) else None
                            if rows is not None:
                                break
                            time.sleep(5)
                    if rows is None:
                        return
                    agg = {}
                    for r in rows:
                        if not r.get("spare"):
                            agg[(r["part_num"], r["color_id"])] = agg.get((r["part_num"], r["color_id"]), 0) + r["quantity"]
                    with lock:
                        _owned_parts()[num] = [[pn, c, q] for (pn, c), q in agg.items()]
                        _save(OWNED_PARTS_FILE, _owned_parts())
                combos = [(pn, c) for pn, c, _ in _owned_parts().get(num) or []]
            elif it.get("kind") == "custom" and it.get("moc_parts"):
                pc, bo_rb = _parts_cache(), {}
                for k, v in (moc_color_maps().get("rb") or {}).items():
                    bo_rb.setdefault(v, int(k))
                for x in it["moc_parts"]:
                    pn = (pc.get("bl:" + x["part"]) or {}).get("part_num") or x["part"]
                    c = x.get("color_id") if x.get("color_id") is not None else bo_rb.get(x.get("color"))
                    if c is not None:
                        combos.append((pn, c))
            if not combos:
                return
            new_names = [pn for pn, _ in combos if pn not in part_names()]
            if new_names:
                part_names_fill(new_names)
            todo = [(pn, c) for pn, c in dict.fromkeys(combos) if part_unit(pn, c, moc_color_maps().get("rb") or {}, _parts_cache()) is None
                    and f"{pn}|{c}" not in part_prices()]
            if todo:
                part_prices_fill(todo)   # seulement ses pièces pas encore chiffrées (si le chiffrage de nuit tourne, il les prendra)
        except Exception as e:
            print("Mise à jour des pièces impossible :", e, flush=True)
    threading.Thread(target=run, daemon=True).start()


def owned_sets_with_part(part_num):
    """Sets de ma collection qui contiennent la pièce (toutes couleurs), avec quantité et couleurs."""
    nums = owned_set_numbers()
    known = _owned_parts()
    missing = [n for n in nums if n not in known]
    if missing:
        owned_parts_fill()
    cols = colors_fr()
    out = []
    for n in nums:
        hits = [(c, q) for pn, c, q in known.get(n) or [] if pn == part_num]
        if hits:
            out.append({"set": n, "qty": sum(q for _, q in hits),
                        "colors": [{"color_id": c, "color_fr": (cols.get(str(c)) or {}).get("fr", str(c)),
                                    "rgb": (cols.get(str(c)) or {}).get("rgb"), "qty": q} for c, q in hits]})
    return {"sets": out, "pending": len(missing), "total": len(nums)}


def part_figs(part_num, color_id, budget=20):
    """Minifigs (Rebrickable) qui portent cette pièce dans cette couleur, en parcourant les sets où elle apparaît.
    Listes de minifigs des sets et pièces des minifigs gardées en cache (elles ne changent pas)."""
    key = f"pf:{part_num}|{color_id}"
    c = _parts_cache().get(key)
    if c and time.time() - c.get("_t", 0) < 180 * 86400:   # (relue tous les 6 mois : nouvelles figurines)
        return c
    sets = part_sets(part_num, part_num, color_id).get("sets") or []
    t0, figs, seen, partial = time.time(), [], set(), False
    for st in sets[:30]:
        if time.time() - t0 > budget:
            partial = True
            break
        sk = "sm:" + st["set_num"]
        sm = _parts_cache().get(sk)
        if sm is None:
            try:
                d = sources.rb(f"lego/sets/{urllib.parse.quote(st['set_num'])}/minifigs/?page_size=100")
            except Exception:
                continue
            sm = [{"fig": x["set_num"], "name": x.get("set_name"), "image": x.get("set_img_url")} for x in d.get("results", [])]
            _parts_cache_put(sk, sm)
        for f in sm:
            if f["fig"] in seen:
                continue
            if time.time() - t0 > budget:
                partial = True
                break
            fk = "fp:" + f["fig"]
            fp = _parts_cache().get(fk)
            if fp is None:
                try:
                    d = sources.rb(f"lego/minifigs/{urllib.parse.quote(f['fig'])}/parts/?page_size=100")
                except Exception:
                    continue
                fp = [[r["part"]["part_num"], r["color"]["id"]] for r in d.get("results", [])]
                _parts_cache_put(fk, fp)
            seen.add(f["fig"])
            if any(pn == part_num and col == color_id for pn, col in fp):
                figs.append({**f, "sets": [{"set_num": st["set_num"], "name": st.get("name")}]})
    # même minifig dans plusieurs sets : une seule ligne
    out = {}
    for f in figs:
        out.setdefault(f["fig"], {**f, "sets": []})["sets"] += f["sets"]
    res = {"figs": list(out.values()), "partial": partial, "_t": time.time()}
    if not partial:
        _parts_cache_put(key, res)
    return res


def part_equivalents(pn):
    """Pièces qui peuvent en remplacer une autre, de la plus proche à la plus lointaine (gardé 30 jours)."""
    key = "eq:" + pn
    c = _parts_cache().get(key)
    if c and time.time() - c.get("_t", 0) < 30 * 86400:
        return c
    d = part_detail(pn)
    base = d.get("print_of") or pn
    try:
        bd = part_detail(base) if base != pn else d
    except Exception:   # pièce de base absente de Rebrickable (ex. pare-brise 7304 : n'existe qu'imprimé) : on garde ses autres impressions
        bd = {"name": d.get("name"), "molds": [], "alternates": []}
    rel = [(pn, "Même pièce, autre couleur")]
    if base != pn:
        rel.append((base, "Sans impression"))
    rel += [(x, "Moule équivalent") for x in (d.get("molds") or []) + (bd.get("molds") or [])]
    rel += [(x, "Pièce équivalente") for x in (d.get("alternates") or []) + (bd.get("alternates") or [])]
    try:
        rel += [(x, "Même forme") for x in shape_search(bd.get("name") or "")]
    except Exception:
        pass
    fam = {base, *(bd.get("molds") or [])}   # autres impressions (tampo) de la même pièce de base ou de ses moules
    prints = []
    for b0 in [base] + [x for x in (bd.get("molds") or []) if x != base][:2]:   # la pièce de base d'abord
        if len(prints) >= 400:
            break
        try:
            r = sources.rb(f"lego/parts/?page_size=1000&inc_part_details=1&search={urllib.parse.quote(b0 + 'pr')}")
            seen_p = {x["part_num"] for x in prints}
            prints += [x for x in r.get("results", []) if x.get("print_of") in fam and x["part_num"] != pn and x["part_num"] not in seen_p]
        except Exception:
            pass
    rel += [(x["part_num"], "Autre impression") for x in prints[:400]]
    pinfo = {x["part_num"]: sources._part(x) for x in prints[:400]}
    seen, order = set(), []
    for num, why in rel:
        if num not in seen:
            seen.add(num)
            order.append((num, why))
    info = dict(pinfo)
    rest = [n for n, _ in order if n not in info]
    for k in range(0, len(rest), 50):   # détails des autres pièces en quelques appels
        chunk = rest[k:k + 50]
        try:
            r = sources.rb(f"lego/parts/?page_size=100&inc_part_details=1&part_nums={urllib.parse.quote(','.join(chunk))}")
            for x in r.get("results", []):
                info[x["part_num"]] = sources._part(x)
        except Exception:
            pass
    out = {"base": base, "parts": [{**info[n], "relation": why} for n, why in order if n in info], "_t": time.time()}
    _parts_cache_put(key, out)
    return out


PRINT_RE = re.compile(r"pr\d|print|sticker|pattern|decorat", re.I)


def shape_name(name):
    """Nom de la forme, sans la décoration : « … No Studs with … Print » → « … No Studs »."""
    return re.sub(r"\s+(with|w/)\s+.*$", "", name or "", flags=re.I).strip(" ,")


def shape_search(name):
    """Pièces sans impression dont le nom commence par la même forme (recherche Rebrickable, gardée 30 jours)."""
    base = shape_name(name)
    if not base or base == name.strip() and not PRINT_RE.search(name):
        return []
    key = "ns:" + base.lower()
    c = _parts_cache().get(key)
    if c is None or time.time() - c.get("_t", 0) > 180 * 86400:
        d = sources.rb("lego/parts/?page_size=50&search=" + urllib.parse.quote(base))
        found = [p["part_num"] for p in d.get("results", [])
                 if p["name"].lower().startswith(base.lower()) and not PRINT_RE.search(p["part_num"] + " " + p["name"])]
        c = {"parts": found[:4], "_t": time.time()}
        _parts_cache_put(key, c)
    return c["parts"]


def replacement_for(part_num, color_id):
    """Première pièce de même forme qui existe dans la couleur demandée (ou None)."""
    for s in similar_parts(part_num)["similar"]:
        hit = next((c for c in s["colors"] if c["color_id"] == color_id), None)
        if hit:
            return {"part_num": s["part_num"], "name": s["name"], "relation": s["relation"],
                    "image": hit.get("image"), "color_id": color_id}
    return None


def similar_parts(part_num):
    """Pièces de même forme que part_num, chacune avec ses couleurs disponibles."""
    d = part_detail(part_num)
    cands = []
    if d.get("print_of"):
        cands.append((d["print_of"], "sans impression"))
    cands += [(x, "moule équivalent") for x in d.get("molds", [])]
    cands += [(x, "pièce équivalente") for x in d.get("alternates", [])]
    cands += [(x, "même forme") for x in shape_search(d.get("name") or "")]   # ex. « Brick Curved 2 x 4 x 2/3 No Studs »
    if d.get("print_of"):   # pièce imprimée : ses autres impressions (ex. pare-brise 7304pr0001 → 7304pr0002…, sans version unie)
        try:
            cands += [(x["part_num"], "autre impression") for x in part_equivalents(part_num)["parts"] if x.get("relation") == "Autre impression"]
        except Exception:
            pass
    out, seen = [], {part_num}
    for num, rel in cands[:14]:
        if num in seen:
            continue
        seen.add(num)
        try:
            info = part_detail(num)
            out.append({"part_num": num, "name": info.get("name") or num, "relation": rel,
                        "colors": part_colors(num)["colors"]})
        except Exception:
            continue
    return {"part_num": part_num, "similar": out}


def colors_fr():
    """Toutes les couleurs LEGO (Rebrickable) avec leur nom français quand il est connu."""
    cols = _parts_cache().get("colors")
    if not cols:
        try:
            cols = sources.all_colors()
            _parts_cache_put("colors", cols)
        except Exception:
            cols = {}
    return {k: {"name": v["name"], "fr": FR_COLORS.get(v["name"], v["name"]), "rgb": v.get("rgb"), "trans": v.get("trans")}
            for k, v in cols.items() if int(k) >= 0}


def inventory_rows(set_num):
    """Lignes d'inventaire d'un set (gardées en cache : un inventaire ne change pas)."""
    key = "inv:" + set_num
    rows = _parts_cache().get(key)
    if rows is None:
        rows = sources.set_inventory(set_num)
        _parts_cache_put(key, rows)
    # même pièce + même couleur sur plusieurs lignes (ex. éléments différents) : on regroupe
    merged = {}
    for r in rows:
        k = f"{r['part_num']}|{r['color_id']}"
        if k in merged:
            merged[k]["quantity"] += r["quantity"]
        else:
            merged[k] = {**r, "key": k, "color_fr": FR_COLORS.get(r.get("color_name") or "", r.get("color_name"))}
    return sorted(merged.values(), key=lambda r: (r.get("color_fr") or "", r.get("name") or ""))


def part_colors(part_num, set_num=""):
    """Couleurs existantes d'une pièce, avec teinte, photo, n° d'élément, et quantité dans un set donné."""
    c = _parts_cache()
    colors = c.get("colors")
    if not colors:
        colors = sources.all_colors()
        _parts_cache_put("colors", colors)
    key = "pc:" + part_num
    pcs = c.get(key)
    if pcs is None or time.time() - c.get(key + ":t", 0) > 180 * 86400:
        pcs = sources.part_colors(part_num)
        _parts_cache_put(key, pcs)
        _parts_cache_put(key + ":t", time.time())
    in_set = {}
    if set_num:
        sn = norm_set(set_num) or set_num
        skey = "sp:" + sn
        sp = _parts_cache().get(skey)
        if sp is None:
            try:
                sp = sources.set_parts(sn)
                _parts_cache_put(skey, sp)
            except Exception:
                sp = []
        for r in sp:
            if r["part_num"] == part_num and not r.get("spare"):
                e = in_set.setdefault(r["color_id"], {"qty": 0, "element": r.get("element_id")})
                e["qty"] += r["quantity"]
    out = []
    for pc in pcs:
        col = colors.get(str(pc["color_id"]), {})
        hit = in_set.get(pc["color_id"])
        out.append({**pc, "rgb": col.get("rgb"), "trans": col.get("trans"),
                    "color_fr": FR_COLORS.get(pc["color_name"], pc["color_name"]),
                    "in_set": hit["qty"] if hit else 0,
                    "set_element": hit["element"] if hit else None})
    out.sort(key=lambda x: (-x["in_set"], -(x.get("num_sets") or 0)))
    return {"colors": out, "set": set_num, "set_found": bool(in_set) if set_num else None}


# ---------------------------------------------------------------- prix d'occasion des minifigs
# BrickEconomy ne donne que le prix neuve/détachée : le prix d'occasion est celui relevé sur BrickOwl
# (offres « Used »), jamais une décote du neuf. Inconnu (aucune offre) → None.
FIG_USED_TTL = 7 * 86400
_fu_mem = {"t": 0, "c": {}}


def _fu_cache():
    if time.time() - _fu_mem["t"] > 5:
        _fu_mem["c"] = {k[3:]: v for k, v in _parts_cache().items() if k.startswith("fu:")}
        _fu_mem["t"] = time.time()
    return _fu_mem["c"]


def fig_used(fid):
    """Prix d'occasion relevé (cache seulement, sans requête) ou None — selon le site de référence (21/11)."""
    bo = fig_bo_rec(fid)
    return ref_mix((fig_bl_rec(fid) or {}).get("unit"), bo.get("unit") if bo_solid(bo) else None)[0]   # (BrickOwl trop mince : pas retenu — 22/11)


def fig_bl_rec(fid):
    c = _fu_cache().get(fid)
    return c if c and c.get("src") == "BrickLink" else None


def fig_bo_rec(fid, fetch=False, max_age=None):
    """Prix d'occasion BrickOwl d'une minifig, gardé à part (« fuo: ») ; l'ancien relevé BrickOwl (« fu: ») sert en attendant."""
    c = _parts_cache().get("fuo:" + fid)
    if fetch and not RB_FIG.fullmatch(fid or "") and (not c or time.time() - c.get("t", 0) >= (max_age or FIG_USED_TTL)):
        try:
            r = sources.fig_used_price(fid) or {"unit": None}
            r.update(t=int(time.time()), src="BrickOwl")
            _parts_cache_put("fuo:" + fid, r)
            c = r
        except Exception:
            pass
    if c:
        return c
    leg = _fu_cache().get(fid)
    return leg if leg and leg.get("src") != "BrickLink" else None


def fig_used_fetch(fid, max_age=FIG_USED_TTL):
    if RB_FIG.fullmatch(fid or ""):   # minifig Rebrickable : pas de référence BrickLink, donc pas de prix d'occasion
        return None
    c = _fu_cache().get(fid)
    want_bl = bl_on()
    if want_bl and bl_keep_known(c):   # déjà relevée sur BrickLink : relue seulement par la passe de nuit
        return c.get("unit")
    if c and time.time() - c.get("t", 0) < max_age and (c.get("src") == "BrickLink") == want_bl:
        return c.get("unit")
    r = None
    if want_bl:   # BrickLink d'abord : annonces d'occasion (prix retenu) et neuves
        try:
            m = bl_market("MINIFIG", fid)
            try:
                hist_backfill("fig:" + fid, m)   # (6 mois de ventes, mois par mois — 21/11)
            except Exception:
                pass
            u = bl_keep_rec(m.get("used"), c if c and c.get("src") == "BrickLink" else None) or {}   # moins de 3 ventes partout : l'ancien prix solide est gardé
            m["new"] = bl_keep_rec(m.get("new"), (c or {}).get("new"))
            r = {**u, "unit": u.get("unit"), "new": m.get("new"), "url": m["url"], "src": "BrickLink", "name": (c or {}).get("name")}
        except Exception as e:
            print("BrickLink", fid, e, flush=True)
            if c and c.get("src") == "BrickLink":   # déjà relevée sur BrickLink : on garde ce prix-là
                return c.get("unit")
    if not r:   # (BrickLink muet : le dernier prix connu reste ; plan de secours BrickOwl : son relevé — 21/11 soir)
        if ref_site() == "brickowl":
            fig_bo_rec(fid, fetch=True)
            _fu_mem["t"] = 0
            return fig_used(fid)
        return c.get("unit") if c else None
    r["t"] = int(time.time())
    _parts_cache_put("fu:" + fid, r)
    _fu_mem["t"] = 0
    if ref_site() != "bricklink" and r.get("src") == "BrickLink":   # (site de référence BrickOwl / les deux : BrickOwl aussi — 21/11)
        fig_bo_rec(fid, fetch=True)
    return fig_used(fid)


def fig_used_stats(fid):
    """Annonces d'occasion relevées : {min, max, avg, offers, zone} ou None — du site de référence (secours : l'autre ; les deux : la moyenne).
    « sites » : le prix de chaque site ; « fb » : site de secours (21/11)."""
    bl, bo = fig_bl_rec(fid), fig_bo_rec(fid)
    u, fb = ref_mix((bl or {}).get("unit"), (bo or {}).get("unit") if bo_solid(bo) else None)   # (BrickOwl trop mince : pas retenu — 22/11)
    s = ref_site()
    r = dict((bo if (fb == "BrickOwl" or (bo_first() and bo_solid(bo))) else bl or bo) or {})
    if u is not None:
        r.update(unit=u, **({"fb": fb} if fb else {}), **({"mix": True} if s == "both" and not fb else {}))
    r["sites"] = {nm: {"used": (x or {}).get("unit"), "url": (x or {}).get("url")} for nm, x in (("BrickLink", bl), ("BrickOwl", bo)) if x}
    if r.get("min") is None and u is not None:
        r["min"] = r["max"] = u
    if r.get("min") is not None:
        return {**{k: r.get(k) for k in ("min", "max", "avg", "offers", "zone", "fr", "src", "unit", "kind", "sold", "qty", "thin", "few", "fb", "mix")}, "sites": r["sites"]}
    r = {}
    return {k: r.get(k) for k in ("min", "max", "avg", "offers", "zone", "fr", "src", "unit", "kind", "sold", "qty", "thin", "few")} if r.get("min") is not None else None   # (unit, kind : drapeau et « ventes / annonces »)


def fig_used_many(ids):
    """Prix d'occasion de plusieurs minifigs tout de suite (requêtes en parallèle)."""
    from concurrent.futures import ThreadPoolExecutor
    ids = [i for i in dict.fromkeys(ids) if i]
    want_bl = bl_on()
    todo = [i for i in ids if not (_fu_cache().get(i) and time.time() - _fu_cache()[i].get("t", 0) < FIG_USED_TTL
                                   and (_fu_cache()[i].get("src") == "BrickLink") == want_bl)]   # BrickLink branché : l'ancien relevé BrickOwl est relu
    if todo and quick():   # fiche ouverte : les prix connus tout de suite (BrickLink : relus par /api/consult ; sinon en fond)
        if not want_bl:
            bg_once("fu:" + ",".join(todo)[:300], lambda: fig_used_many(todo), 3600)
        todo = []
    if todo:
        with ThreadPoolExecutor(4) as ex:
            list(ex.map(fig_used_fetch, todo))
    return {i: fig_used(i) for i in ids}


_fu_busy = [False]


def fig_used_fill():
    """Arrière-plan : prix d'occasion de toutes les minifigs de la collection (seules et dans les sets)."""
    with lock:
        if _fu_busy[0]:
            return
        _fu_busy[0] = True

    def run():
        try:
            db, cache = load_db(), _load(CACHE_FILE, {})
            ids = []
            for it in db["items"]:
                if it.get("kind") == "fig":
                    ids.append(it["number"])
                elif it.get("kind", "set") == "set":
                    ids += [f["id"] for f in (cache.get(cache_key(it)) or {}).get("minifigs") or []]
            for fid in dict.fromkeys(ids):
                c = _fu_cache().get(fid)
                if c and time.time() - c.get("t", 0) < FIG_USED_TTL:
                    continue
                fig_used_fetch(fid)
                time.sleep(0.5)
        finally:
            _fu_busy[0] = False
    threading.Thread(target=run, daemon=True).start()


def with_used_figs(info):
    """Ajoute à chaque minifig d'un set son prix d'occasion relevé (« used »)."""
    if not info or not info.get("minifigs"):
        return info
    fu = _fu_cache()
    mfs = [{**f, "used": fig_used(f["id"]), "used_zone": (fu.get(f["id"]) or {}).get("zone")} for f in info["minifigs"]]   # used_zone : drapeau du prix
    return {**info, "minifigs": mfs}


def price_zones(kind, number, info):
    """Zone (France / UE / monde) des prix neuf et d'occasion affichés, quand ils viennent bien d'un relevé (même montant) :
    {"new", "used"} (None sinon). Sert au drapeau à côté du prix sur les pages publiques."""
    ok = lambda rec, v: rec.get("zone") if isinstance(rec, dict) and v is not None and rec.get("unit") is not None and abs(rec["unit"] - v) < 0.005 else None
    if kind == "fig":
        r = _fu_cache().get(number) or {}
        return {"new": ok(r.get("new"), info.get("value")), "used": ok(r, info.get("used") if info.get("used") is not None else r.get("unit"))}
    m = info.get("market") or {}
    return {"new": ok(m.get("new"), info.get("new_value")), "used": None if info.get("used_guess") else ok(m.get("used"), info.get("used_value"))}


def lot_zones(lots):
    """Zone du prix BrickLink de chaque pièce {"pièce|couleur": {"zone", "unit"}} — cache seulement, aucune requête (drapeau des tuiles)."""
    out, pc = {}, _parts_cache()
    for l in lots[:400]:
        part, color = str(l.get("part") or "")[:40], str(l.get("color") or "")[:60]
        blc = bo_bl_color(color) if part else None
        rec = pc.get(f"bp:{part}|{blc}") if blc is not None else None
        if not rec:
            continue
        s = rec.get("used") if (rec.get("used") or {}).get("unit") else rec.get("new")   # (même choix que bp_unit)
        if s and s.get("unit") and s.get("zone"):
            out[f"{part}|{color}"] = {"zone": s["zone"], "unit": s["unit"]}
    return out


# ---------------------------------------------------------------- estimation


_md = {"t": 0, "v": 5.0}


def mod_discount():
    """Décote (en %) d'un set ou d'une minifig modifié(e) : un exemplaire dénaturé se revend moins bien."""
    if time.time() - _md["t"] > 5:
        try:
            _md["v"] = max(0.0, min(90.0, float(_load(sources.SETTINGS_FILE, {}).get("mod_discount", 5))))
        except (TypeError, ValueError):
            _md["v"] = 5.0
        _md["t"] = time.time()
    return _md["v"]


_bb = {"t": 0, "v": 6.0}


def box_bonus():
    """Plus-value (en %) d'un set d'occasion avec sa boîte, par rapport à la cote d'occasion (sans boîte garantie)."""
    if time.time() - _bb["t"] > 5:
        try:
            _bb["v"] = max(0.0, min(100.0, float(_load(sources.SETTINGS_FILE, {}).get("box_bonus", 6))))
        except (TypeError, ValueError):
            _bb["v"] = 6.0
        _bb["t"] = time.time()
    return _bb["v"]


CMF_THEMES = ("Minifigure Series", "Collectible Minifigures")
CMF_STANDS = {"88646"}   # socle noir 3 x 4 avec 4 tenons fourni avec chaque minifig à collectionner


def cmf_stand_removed(info, sw):
    """Minifig à collectionner : retirer le socle noir n'est ni une modification ni une perte de valeur."""
    o = sw.get("orig") or {}
    return (sw.get("new") is None and (info or {}).get("theme") in CMF_THEMES and o.get("color_id") == 0
            and (str(o.get("part") or "") in CMF_STANDS or str(o.get("part_num") or "") in CMF_STANDS))


def _real_swaps(swaps):
    return [x for x in swaps or [] if not x.get("free") and not x.get("fix")]   # (fix : pièce d'origine corrigée — pas une modification)


_pc = {"t": 0, "v": 5.0}


def plan_cut():
    """Plus-value (en %) d'un set d'occasion avec son livret de plans, quand BrickOwl n'en donne pas le prix."""
    if time.time() - _pc["t"] > 5:
        try:
            _pc["v"] = max(0.0, min(90.0, float(_load(sources.SETTINGS_FILE, {}).get("plan_bonus", 5))))
        except (TypeError, ValueError):
            _pc["v"] = 5.0
        _pc["t"] = time.time()
    return _pc["v"]


EXTRAS_FILE = os.path.join(DATA, "cache_extras.json")
EXTRAS_TTL = 30 * 86400
_extras_busy = set()


_extras_mem = {"m": None, "d": {}}


def set_extras(number):
    """Prix relevés (BrickOwl) des plans seuls et de la boîte vide d'un set : {"plan": {...}, "box": {...}, "t": …}."""
    try:
        mt = os.path.getmtime(EXTRAS_FILE)
    except OSError:
        return {}
    if _extras_mem["m"] != mt:   # relu seulement quand le fichier change
        _extras_mem.update(m=mt, d=_load(EXTRAS_FILE, {}))
    return _extras_mem["d"].get(number) or {}


def extras_fetch(number):
    if number in _extras_busy:
        return
    _extras_busy.add(number)
    try:
        out = {"t": int(time.time())}
        for key, what in (("plan", "instructions"), ("box", "packaging")):
            try:
                r = sources.set_extra_price(number, what)
                out[key] = {"unit": r.get("unit"), "url": r.get("url"), "offers": r.get("offers"), "zone": r.get("zone")}
            except Exception as e:
                print("Prix plans/boîte", number, e, flush=True)
                return   # erreur réseau : on réessaiera
            time.sleep(1)
        with lock:
            c = _load(EXTRAS_FILE, {})
            c[number] = out
            _save(EXTRAS_FILE, c)
    finally:
        _extras_busy.discard(number)


def extras_start(number):
    if number and number not in _extras_busy and not set_extras(number):
        threading.Thread(target=extras_fetch, args=(number,), daemon=True).start()


def extras_keeper():
    """Prix des plans et boîtes vides de chaque set de la collection : relevés au démarrage, puis tous les 30 jours."""
    time.sleep(60)
    while True:
        try:
            kinds = list_kinds()
            db = load_db()
            watch = {l["id"] for l in db["lists"] if l.get("gift")}   # « À surveiller » : boîte / plan comptent dans son prix
            nums = dict.fromkeys(i["number"] for i in db["items"]
                                 if i.get("kind", "set") == "set" and (kinds.get(i.get("list_id")) == "collection" or i.get("list_id") in watch))
            for num in nums:
                if time.time() - (set_extras(num).get("t") or 0) > EXTRAS_TTL:
                    extras_fetch(num)
                    time.sleep(3)
        except Exception as e:
            print("Prix plans/boîtes :", e, flush=True)
        time.sleep(6 * 3600)


def extra_unit(number, key):
    u = (set_extras(number).get(key) or {}).get("unit")
    return u if u else None


def cmf_fig_of(item, cache=None):
    """Minifig à collectionner enregistrée comme « set » (ex. 71048-2) : l'id de sa minifig (ex. col450), sinon None."""
    if item.get("kind", "set") != "set":
        return None
    info = (cache if cache is not None else _load(CACHE_FILE, {})).get(item["number"]) or {}
    mfs = info.get("minifigs") or []
    if info.get("theme") in CMF_THEMES and len(mfs) == 1 and mfs[0].get("qty", 1) == 1 and mfs[0].get("id"):
        return mfs[0]["id"]
    return None


def convert_cmf_sets():
    """Les minifigs à collectionner deviennent des minifigs seules : pas de notion de set, ni boîte ni plan.
    Pièces échangées : reprises sur la minifig (le socle retiré est oublié). Appelé au démarrage et après un ajout."""
    cache = _load(CACHE_FILE, {})
    todo = [(i["id"], cmf_fig_of(i, cache)) for i in load_db()["items"]]
    todo = [(iid, fid) for iid, fid in todo if fid]
    if not todo:
        return 0
    with lock:   # fiche de chaque minifig tirée de celle du set si BrickEconomy ne l'a pas encore donnée (relue plus tard)
        cache = _load(CACHE_FILE, {})
        for iid, fid in todo:
            it = next((i for i in load_db()["items"] if i["id"] == iid), None)
            info = (cache.get(it["number"]) or {}) if it else {}
            f = (info.get("minifigs") or [{}])[0]
            if info and "fig:" + fid not in cache:
                cache["fig:" + fid] = {"type": "fig", "number": fid, "name": f.get("name") or info.get("name"), "theme": info.get("theme"),
                                       "subtheme": info.get("subtheme"), "years": str(info.get("year") or ""), "availability": info.get("availability"),
                                       "value": f.get("value"), "image": (f.get("image") or "").replace("_thumb.png", "_medium.jpg") or info.get("image"),
                                       "sets": [it["number"]], "source": f"https://www.brickeconomy.com/minifig/{fid}/", "fetched_at": 0}
        _save(CACHE_FILE, cache)
    rb_of, parts_of, wait = {}, {}, set()
    for iid, fid in todo:   # réseau hors verrou : version Rebrickable seulement si des pièces ont été échangées
        it = next((i for i in load_db()["items"] if i["id"] == iid), None)
        if it and _real_swaps((it.get("set_mod") or {}).get("fig_swaps")):
            try:
                c = rb_fig_candidates(fid)
                if c:
                    rb_of[fid] = c[0]["fig_num"]
                    parts_of[fid] = rb_fig_parts(rb_of[fid])
            except Exception as e:
                print("Minifig à collectionner", fid, e, flush=True)
            if fid not in rb_of:
                wait.add(iid)   # pièces échangées à reprendre : on réessaiera plus tard plutôt que de les perdre
    n = 0
    with lock:
        db, cache = load_db(), _load(CACHE_FILE, {})
        hist = _load(HISTORY_FILE, {})
        for iid, fid in todo:
            it = next((i for i in db["items"] if i["id"] == iid), None)
            if not it or iid in wait or cmf_fig_of(it, cache) != fid:
                continue
            swaps = []
            for x in _real_swaps((it.get("set_mod") or {}).get("fig_swaps")):
                if x.get("orig") is None:   # pièce ajoutée
                    swaps.append({"k": min([-1] + [s["k"] - 1 for s in swaps if s["k"] < 0]), "orig": x["orig"], "new": x["new"]})
                    continue
                o = x["orig"]   # pièce d'origine : retrouvée dans la minifig Rebrickable
                k = next((j for j, p in enumerate(parts_of.get(fid) or []) if p.get("part_num") == o.get("part_num") and p.get("color_id") == o.get("color_id")), None)
                if k is not None and k not in [s["k"] for s in swaps]:
                    swaps.append({"k": k, "orig": o, "new": x["new"]})
            old_num = it["number"]
            for key in ("set_mod", "fig_mods", "fig_counts", "has_box", "no_plan", "display_name"):
                it.pop(key, None)
            it.update(kind="fig", number=fid, cmf_set=old_num, with_minifigs=True, missing_minifigs=[], updated_at=int(time.time()))
            if swaps and rb_of.get(fid):
                it.update(rb_fig=rb_of[fid], fig_swaps=swaps, swap_price={"delta": 0, "done": False})
            h = hist.get("items") or {}
            if old_num in h and "fig:" + fid not in h:   # courbe de valeur gardée
                h["fig:" + fid] = h.pop(old_num)
            n += 1
            print(f"Minifig à collectionner {old_num} → minifig {fid}", flush=True)
        _save(HISTORY_FILE, hist)
        _save(DB_FILE, db)
    for iid, fid in todo:
        try:
            fig_used_fetch(fid)   # prix d'occasion de la minifig (BrickOwl)
        except Exception:
            pass
        it = next((i for i in load_db()["items"] if i["id"] == iid), None)
        if it and it.get("fig_swaps"):
            moc_price_start(iid)
    return n


def _removals(swaps):
    """Pièces d'origine retirées ou remplacées (une pièce seulement ajoutée ne dénature pas l'exemplaire ;
    un accessoire retiré non plus : seul son prix est déduit)."""
    return [x for x in _real_swaps(swaps) if x.get("orig") and not (x.get("acc") and x.get("new") is None)]


def cmf_set_of(item):
    """Minifig à collectionner seule : le « set » d'où elle vient (pour ses accessoires), sinon None."""
    if item.get("kind") != "fig":
        return None
    if item.get("cmf_set"):
        return item["cmf_set"]
    cache = _load(CACHE_FILE, {})
    info = cache.get("fig:" + item["number"]) or {}
    if info.get("theme") not in CMF_THEMES:
        return None
    sets = [s for s in info.get("sets") or [] if re.fullmatch(r"\w+-\d+", s)]
    one = [s for s in sets if [f.get("id") for f in (cache.get(s) or {}).get("minifigs") or []] == [item["number"]]]
    return (one or sets or [None])[0]


def cmf_accessories(item):
    """Accessoires d'une minifig à collectionner : pièces de son set hors figurine, sans le socle noir."""
    sn = cmf_set_of(item)
    if not sn:
        return []
    bo = moc_color_maps()["rb"]
    out = []
    for r in inventory_rows(sn):
        if r["part_num"] in CMF_STANDS and r["color_id"] == 0:
            continue
        out.append({"part_num": r["part_num"], "part": r.get("bricklink") or r["part_num"], "name": r.get("name") or "",
                    "color_id": r["color_id"], "color": bo.get(str(r["color_id"]), r.get("color_name")), "color_fr": r.get("color_fr") or "",
                    "qty": r.get("quantity", 1), "color_name": r.get("color_name") or "", "rgb": r.get("rgb") or "",
                    "element_id": r.get("element_id") or "", "image": r.get("image") or "", "acc": True})
    return out


def is_modified(item, mfs=None):
    """Décote « modifié » : seulement si des pièces d'origine ont été retirées (ou remplacées), sur le set lui-même,
    une de ses figurines D'ORIGINE, ou la minifig seule. Ajouter des pièces ne compte pas ; le socle d'une minifig à collectionner non plus ;
    une figurine ajoutée en plus (même référence) et modifiée non plus (exemplaires modifiés ≤ exemplaires en plus)."""
    if _removals((item.get("set_mod") or {}).get("fig_swaps")) or _removals(item.get("fig_swaps")):
        return True
    mods = [(fid, m) for fid, m in (item.get("fig_mods") or {}).items() if isinstance(m, dict) and _removals(m.get("fig_swaps"))]
    if not mods:
        return False
    if mfs is None:
        mfs = (_load(CACHE_FILE, {}).get(item.get("number") or "") or {}).get("minifigs") or []
    q = max(1, int(item.get("quantity", 1) or 1))
    have = {} if item.get("with_minifigs") is False else fig_have(item, mfs, q)
    for fid, m in mods:
        f = next((x for x in mfs if x.get("id") == fid), None)
        if not f:
            return True
        n = have.get(fid, 0)
        if n <= 0:   # plus aucun exemplaire dans le set : ses anciennes pièces échangées ne comptent plus (= figModOnOrig)
            continue
        if mod_copies(m.get("fig_swaps"), max(1, n)) > max(0, n - (f.get("qty", 1) or 1) * q):
            return True
    return False


def ia_page(txt, title, dl, back, back_t):
    """Page « 🤖 Condensé pour IA » d'un guide : le texte, « 📋 Tout copier », « ⬇ Télécharger (.txt) », retour au guide."""
    e = __import__("html").escape
    return ("""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Condensé pour IA — """ + e(title) + """</title><link rel="icon" href="/icon.svg"><style>
body{margin:0;font:15px/1.45 system-ui,sans-serif;background:#111317;color:#e8eaed}header{position:sticky;top:0;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 14px;background:#1b1e24;border-bottom:1px solid #2c313a}
h1{font-size:17px;margin:0 auto 0 0}a,button{font:600 14px system-ui,sans-serif;color:#e8eaed;background:#262a31;border:1px solid #3a404a;border-radius:10px;padding:8px 12px;text-decoration:none;cursor:pointer}
button.main{background:#d01012;border-color:#d01012;color:#fff}p{margin:10px 14px;color:#9aa0a8;font-size:13.5px}textarea{box-sizing:border-box;width:calc(100% - 28px);height:calc(100vh - 150px);margin:0 14px 14px;background:#0b0d10;color:#e8eaed;border:1px solid #2c313a;border-radius:10px;padding:10px;font:12.5px/1.4 ui-monospace,monospace}
</style></head><body><header><h1>🤖 Condensé pour IA — """ + e(title) + """</h1><button type="button" class="main" id="cp">📋 Tout copier</button><a href="""" + dl + """">⬇ Télécharger (.txt)</a><a href="""" + back + """">← """ + e(back_t) + """</a></header>
<p>Copiez tout, collez-le au début d'une conversation avec une IA, puis posez votre question (« comment je fais pour… ») : elle répondra d'après ce guide.</p>
<textarea id="t" readonly spellcheck="false">""" + e(txt) + """</textarea>
<script>document.getElementById("cp").onclick = async () => { const t = document.getElementById("t"), b = document.getElementById("cp");
  try { await navigator.clipboard.writeText(t.value); } catch { t.focus(); t.select(); document.execCommand("copy"); }
  b.textContent = "✔ Copié"; setTimeout(() => b.textContent = "📋 Tout copier", 2000); };</script></body></html>""").encode("utf-8")


def estimate(item, info):
    """Valeur estimée d'un exemplaire selon état et figurines présentes (une case par exemplaire de figurine)."""
    base = info.get("new_value") if item["condition"] == "neuf" else info.get("used_value")
    base = base or info.get("retail") or 0
    neuf = item["condition"] == "neuf"
    n = max(1, int(item.get("quantity", 1) or 1))   # calcul sur tous les exemplaires, ramené à l'unité
    mfs = info.get("minifigs", [])
    # figurines : prix neuf pour un set neuf, sinon prix d'occasion relevé (inconnu → 0, rien n'est déduit)
    # (pas encore de prix d'occasion relevé, ex. minifig récente → prix neuf)
    figs = {f["id"]: (f.get("value") or 0) if neuf else (fig_used(f["id"]) if fig_used(f["id"]) is not None else f.get("value") or 0) for f in mfs}
    qty = {f["id"]: f.get("qty", 1) * n for f in mfs}
    total_figs = sum(figs[i] * f_qty for i, f_qty in ((f["id"], f.get("qty", 1)) for f in mfs)) * n if mfs \
        else ((info.get("minifig_value") or 0) * n if neuf else 0)
    base = base * n
    extra = 0.0
    if item.get("with_minifigs", True):
        have = fig_have(item, mfs, n)
        deduct = sum(max(0, qty[i] - have[i]) * figs[i] for i in figs)   # figurines en moins
        extra = sum(max(0, have[i] - qty[i]) * figs[i] for i in figs)    # figurines en plus (ex. 6 au lieu de 3)
        extra += fig_mods_delta(item, have)   # figurines dont des pièces ont été remplacées
    else:
        deduct = total_figs
    if (item.get("set_mod") or {}).get("fig_swaps"):   # pièces du set remplacées ou retirées (sur un exemplaire)
        extra += (item["set_mod"].get("swap_price") or {}).get("delta") or 0
    # Un set sans figurines se revend en général sous la valeur des figurines seules
    unit = max(base - deduct, base * 0.25 if base else 0) + extra
    if item.get("has_box") and not neuf:   # set d'occasion avec sa boîte : + prix d'une boîte vide (sinon un pourcentage)
        bp = extra_unit(item["number"], "box")
        unit = unit + bp * n if bp else unit * (1 + box_bonus() / 100)
    # livret de plans : n'entre pas dans l'estimation
    if is_modified({**item, "set_mod": None, "fig_swaps": None}, mfs):   # décote : seulement une figurine ORIGINALE modifiée (pas les pièces du set, pas les ajoutées)
        unit *= 1 - mod_discount() / 100
    return round(unit / n, 4)


def fig_have(item, mfs, n=None):
    """Nombre de chaque figurine possédé pour cet élément (quantité choisie, sinon fournie par le set moins les manquantes)."""
    n = n or max(1, int(item.get("quantity", 1) or 1))
    counts = item.get("fig_counts") or {}
    miss = {}
    for m in item.get("missing_minifigs") or []:
        miss[m] = miss.get(m, 0) + 1
    out = {}
    for f in mfs:
        default = f.get("qty", 1) * n
        out[f["id"]] = max(0, int(counts[f["id"]])) if f["id"] in counts else max(0, default - miss.get(f["id"], 0))
    return out


def is_retired(info):
    return (info.get("availability") or "").lower() == "retired"


def owner_name():
    """Nom du propriétaire affiché sur les pages publiques (« Collection de … ») ; vide = « La collection »."""
    return str(_load(sources.SETTINGS_FILE, {}).get("owner_name") or "")[:60]


def novelties_public():
    """Nouveautés pour la page publique /nouveautes : tout, sans rien de privé (ni ma collection, ni mes masqués, ni mes thèmes)."""
    d = _load(NOV_FILE, {})
    noimg = lambda u: not u or "/assets/?" in u
    keep = ("number", "name", "pieces", "price", "release", "kind", "when", "day", "pos", "seen", "images", "url")
    items = [{**{k: x.get(k) for k in keep}, "theme": theme_norm(x.get("theme")), "image": (x.get("images") or [RB_IMG.format(x["number"])])[0] if noimg(x.get("image")) else x.get("image"),
              "figs": [{"fig": f.get("fig"), "name": f.get("name"), "image": f.get("image")} for f in x.get("figs") or [] if f.get("exclusive")]}
             for x in d.get("items") or [] if x.get("pieces")]
    return {"items": items, "t": d.get("t"), "figs_done": d.get("figs_done", False)}


def part_img_fix(x):
    """Pièce sans n° d'élément (couleur changée, pièce remplacée) : la photo de la pièce dans SA couleur, si connue."""
    if x.get("element_id"):
        return {}
    try:
        for c in _parts_cache().get("pc:" + str(x.get("part_num"))) or []:
            if isinstance(c, dict) and str(c.get("color_id")) == str(x.get("color_id")) and c.get("image"):
                return {"image": c["image"]}
    except Exception:
        pass
    return {}


def bl_to_send(it, full=False):
    """Pièces à exporter vers BrickLink : la quantité pas encore exportée (tout, si full)."""
    q = max(1, int(it.get("quantity") or 1))
    return q if full else max(0, q - int(it.get("bl_qty") or 0))


def bl_wanted_xml(items, full=False):
    """Pièces → wanted list BrickLink (format XML officiel, sans déclaration ni WANTEDLISTID : liste principale).
    Seulement ce qui n'a pas encore été exporté (sauf full). Même pièce + même couleur + même état : une ligne, quantités additionnées.
    Rend (xml, lignes, ignorées)."""
    rbbl = {}
    for blc, rbc in (moc_color_maps().get("blrb") or {}).items():   # n° de couleur Rebrickable → n° BrickLink
        if str(rbc) not in rbbl or int(blc) < int(rbbl[str(rbc)]):
            rbbl[str(rbc)] = blc
    names = part_names()
    esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    rows, skipped = {}, []
    for it in items:
        add = bl_to_send(it, full)
        if not add:
            continue
        if it.get("kind") == "fig":   # figurine à commander : une minifig BrickLink (type M), sans couleur
            cond = it.get("bl_cond") if it.get("bl_cond") in ("N", "U", "X") else "N"   # état voulu (neuf par défaut)
            r = rows.setdefault(("M", it["number"], None, cond), {"type": "M", "pid": sources.bl_fig_no(it["number"]), "col": None, "cond": cond, "qty": 0, "ids": [], "sets": set()})   # (pid : sa référence BrickLink)
            r["qty"] += add
            r["ids"].append(it["id"])
            continue
        pid = it.get("bricklink") or (names.get(it.get("part_num")) or {}).get("bl") or it.get("part_num")
        col = rbbl.get(str(it.get("color_id"))) if it.get("color_id") is not None else None
        label = f"{it.get('part_num')} {it.get('part_name') or ''}".strip()
        if not pid:
            skipped.append({"id": it["id"], "name": label, "why": "référence BrickLink inconnue"})
            continue
        if it.get("color_id") is not None and col is None:
            skipped.append({"id": it["id"], "name": label, "why": f"couleur {it.get('color_name') or it.get('color_id')} inconnue de BrickLink"})
            continue
        cond = it.get("bl_cond") if it.get("bl_cond") in ("N", "U", "X") else "N"   # état voulu : N neuf (défaut), U occasion, X n'importe
        k = (pid, col, cond)   # même pièce, même couleur, même état : une ligne
        r = rows.setdefault(k, {"type": "P", "pid": pid, "col": col, "cond": cond, "qty": 0, "ids": [], "sets": set()})
        r["qty"] += add
        r["ids"].append(it["id"])
        if it.get("set_number"):
            r["sets"].add(it["set_number"])
    xml = "<INVENTORY>\n" + "".join(
        "  <ITEM>\n    <ITEMTYPE>" + r.get("type", "P") + "</ITEMTYPE>\n    <ITEMID>" + esc(r["pid"]) + "</ITEMID>\n"
        + (f"    <COLOR>{r['col']}</COLOR>\n" if r["col"] is not None else "")
        + f"    <MINQTY>{r['qty']}</MINQTY>\n"
        + f"    <CONDITION>{r.get('cond') or 'N'}</CONDITION>\n"   # N neuf, U occasion, X n'importe (format officiel)
        + ("    <REMARKS>Briquothèque · " + esc(", ".join(sorted(r["sets"]))) + "</REMARKS>\n" if r["sets"] else "    <REMARKS>Briquothèque</REMARKS>\n")
        + "  </ITEM>\n" for r in rows.values()) + "</INVENTORY>\n"
    return xml, list(rows.values()), skipped


def wish_prices(item, info):
    """Souhait cherché neuf ET d'occasion : {"neuf", "occasion"} (prix unitaires), sinon None."""
    if not (item.get("also_used") and item.get("condition") == "neuf"):
        return None
    return {"neuf": estimate_wish({**item, "also_used": False}, info),
            "occasion": estimate_wish({**item, "also_used": False, "condition": "occasion"}, info)}


def wish_lines(item, info):
    """Détail d'un souhait (set) : pour chaque état cherché (neuf, occasion, ou les deux) son prix avec figurines, et sans figurines
    quand on les cherche sans (« sf »). [{"c": "neuf" | "occasion", "v": prix, "sf": prix ou None}] (prix unitaires)."""
    if (item.get("kind") or "set") != "set" or not info:
        return []
    conds = ["neuf", "occasion"] if item.get("also_used") and item.get("condition") == "neuf" else [item.get("condition") or "occasion"]
    no_figs = item.get("with_minifigs", True) is False and bool(info.get("minifig_count") or info.get("minifigs"))
    out = []
    for c in conds:
        base = {**item, "also_used": False, "condition": c}
        out.append({"c": c, "v": round(estimate_wish({**base, "with_minifigs": True}, info), 2),
                    "sf": round(estimate_wish({**base, "with_minifigs": False}, info), 2) if no_figs else None})
    return out


def sf_prices(number, info):
    """Set : ses prix SANS figurines {"neuf", "occasion"} (même calcul que la liste de souhaits) ; None s'il n'a pas de figurines."""
    if not info or not (info.get("minifigs") or info.get("minifig_count")):
        return None
    base = {"kind": "set", "number": number, "quantity": 1, "with_minifigs": False, "has_box": False, "no_plan": False}
    try:
        return {"neuf": estimate_wish({**base, "condition": "neuf"}, info), "occasion": estimate_wish({**base, "condition": "occasion"}, info)}
    except Exception:
        return None


def estimate_wish(item, info):
    """Liste de souhaits, selon l'état choisi : neuf → prix magasin tant qu'il est en vente, sinon sa valeur neuve ;
    occasion → valeur d'occasion, avec ou sans figurines comme renseigné. Neuf ou occasion : le moins cher des deux.
    Boîte et plan : jamais cherchés dans un souhait (15/11) → ignorés."""
    item = {**item, "has_box": False, "no_plan": False}
    wp = wish_prices(item, info)
    if wp:
        return min(wp.values())
    if item.get("condition") == "neuf":
        on_sale = not is_retired(info)
        v = (info.get("retail") if on_sale else None) or info.get("new_value") or info.get("retail") or 0
        if item.get("with_minifigs", True) is False:   # neuf sans ses figurines : leur valeur neuve en moins
            mfs = info.get("minifigs") or []
            figs = sum((f.get("value") or 0) * f.get("qty", 1) for f in mfs) if mfs else info.get("minifig_value") or 0
            v = max(v - figs, v * 0.25) if figs else v
        return round(v, 2)
    unit = estimate({**item, "condition": "occasion", "missing_minifigs": [], "fig_counts": {}, "portion": 100}, info)
    if item.get("no_plan") and item.get("kind", "set") == "set":   # occasion sans plan : le prix relevé du livret seul en moins
        unit = max(0.0, unit - (extra_unit(item["number"], "plan") or 0))
    return round(unit, 4)


# ---------------------------------------------------------------- MOC : liste de pièces importée → estimation
def moc_color_maps():
    """Couleurs : n° BrickLink et n° Rebrickable → nom BrickOwl (pour chercher le prix). Gardé 30 jours."""
    c = _parts_cache().get("moc_colors")
    if not c or "blrb" not in c or time.time() - c.get("_t", 0) > 365 * 86400:
        d = sources.rb("lego/colors/?page_size=500")
        bl, rbm, blrb = {}, {}, {}
        for col in d.get("results", []):
            ext = col.get("external_ids") or {}
            bo = ((ext.get("BrickOwl") or {}).get("ext_descrs") or [[col["name"]]])[0][0] or col["name"]
            rbm[str(col["id"])] = bo
            for k in (ext.get("BrickLink") or {}).get("ext_ids") or []:
                if k is not None:
                    bl[str(k)] = bo
                    blrb.setdefault(str(k), col["id"])   # n° BrickLink → n° Rebrickable
        c = {"bl": bl, "rb": rbm, "blrb": blrb, "_t": time.time()}
        _parts_cache_put("moc_colors", c)
    return c


_mocnames = {"busy": False}


def moc_names_fill(parts):
    """Arrière-plan : nom et référence Rebrickable des pièces (n° BrickLink), gardés en cache."""
    with lock:
        if _mocnames["busy"]:
            return
        _mocnames["busy"] = True

    def run():
        try:
            for bl in parts:
                try:
                    cached_part_from_bricklink(bl)
                except Exception:   # (sans clé / sans internet : la suivante ; réessayé à la prochaine ouverture — 22/11)
                    continue
        finally:
            _mocnames["busy"] = False
    threading.Thread(target=run, daemon=True).start()


def offline_pack():
    """Paquet hors ligne : ce que les fiches demandent au serveur, pour TOUTES les fiches (même jamais ouvertes), construit depuis les caches
    seulement — aucun appel extérieur, aucune tâche de fond (le serveur n'a qu'un processeur). Mêmes réponses que les routes :
    "sets" = /api/set/<n> (sets, sets partiels, et sets cités par les figurines), "figs" = /api/fig/<n>, "moc_lots" = /api/items/<id>/moc-lots."""
    db = load_db()
    cache = _load(CACHE_FILE, {})
    hist = _load(HISTORY_FILE, {}).get("items") or {}
    fu = _fu_cache()
    set_nums, fig_nums = set(), set()
    for it in db["items"]:
        k = it.get("kind", "set")
        if k == "set" or (k == "custom" and it.get("partial_set")) and it.get("number"):
            set_nums.add(it["number"])
        elif k == "fig":
            fig_nums.add(it["number"])
    for n in list(set_nums):   # figurines de ces sets
        for f in (cache.get(n) or {}).get("minifigs") or []:
            if f.get("id"):
                fig_nums.add(f["id"])
    figs = {}
    for n in fig_nums:
        f = cache.get("fig:" + n)
        if not f:
            continue
        rec = fu.get(n) or {}
        figs[n] = {**with_fr_fig(f), **({"value": rec["new"]["unit"]} if (rec.get("new") or {}).get("unit") else {}),
                   "market": {"used": fig_used_stats(n), "new": rec.get("new"), "src": rec.get("src") or "BrickOwl"},
                   "used": fig_used(n), "used_stats": fig_used_stats(n), "own_hist": hist.get("fig:" + n) or []}
        sts = f.get("sets") or []
        for st in (re.findall(r"[\w.]+-\d+", sts) if isinstance(sts, str) else sts):   # sets où elle se trouve (rubrique de sa fiche)
            if isinstance(st, str) and st in cache:
                set_nums.add(st)
    sets = {}
    for n in set_nums:
        info = cache.get(n)
        if not info or n.startswith("fig:"):
            continue
        if info.get("pending_prices"):
            sets[n] = {**info, "own_hist": [], "minifig_used": None, "minifig_used_missing": 0}
            continue
        info = with_used_figs(with_fr(info, n))
        mu = [f.get("used") for f in info.get("minifigs") or []]
        sets[n] = {**info, "extras": set_extras(info.get("number") or n), "own_hist": hist.get(n) or [], "minifigs": [with_fr_fig(f) for f in info.get("minifigs") or []],
                   "minifig_used": round(sum((f["used"] if f.get("used") is not None else f.get("value") or 0) * f.get("qty", 1) for f in info.get("minifigs") or []), 2) if mu else None,
                   "minifig_used_missing": sum(1 for u in mu if u is None)}
    lots = {}
    for it in db["items"]:
        if it.get("kind") == "custom" and it.get("moc_parts"):
            try:
                lots[it["id"]] = moc_lots_detail(it)
            except Exception:
                pass
    return {"t": int(time.time()), "sets": sets, "figs": figs, "moc_lots": lots}


def moc_lots_detail(item):
    """Liste de pièces d'un MOC pour l'affichage : nom, couleur (n° Rebrickable et BrickLink), photo, prix relevé."""
    lots = item.get("moc_parts") or []
    cm = moc_color_maps()
    cols = colors_fr()
    bo_rb = {}
    for k, v in cm.get("rb", {}).items():
        bo_rb.setdefault(v, int(k))
    pc = _parts_cache()
    units = (item.get("moc_price") or {}).get("units") or []
    in_asm = {k: a for a in (item.get("moc_price") or {}).get("asm") or [] for k in a.get("lots") or []}   # n° de lot → assemblage monté
    out, missing = [], []
    for k, x in enumerate(lots):
        bl = x["part"]
        found = pc.get("bl:" + bl)
        if "bl:" + bl not in pc:
            missing.append(bl)
        cid = x.get("color_id") if x.get("color_id") is not None else bo_rb.get(x.get("color"))
        col = cols.get(str(cid)) or {}
        unit = units[k] if k < len(units) else (pc.get("mp:" + f"{bl}|{x.get('color')}") or {}).get("unit")
        out.append({"part": bl, "part_num": (found or {}).get("part_num") or "", "name": x.get("name") or (found or {}).get("name") or "",
                    "color": x.get("color"), "color_id": cid, "color_fr": x.get("color_fr") or col.get("fr") or x.get("color"),
                    "rgb": col.get("rgb"), "trans": col.get("trans"), "qty": x.get("qty", 1), "unit": unit,
                    "image": x.get("image") or (found or {}).get("image"),
                    **({"asm": {"no": in_asm[k]["no"], "name": in_asm[k]["name"]}} if k in in_asm else {})})
    if missing:
        moc_names_fill(list(dict.fromkeys(missing)))
    return {"lots": out, "pending": len(set(missing))}


def parse_moc_parts(text):
    """Fichier XML BrickLink / Studio, ou CSV Rebrickable → [{part, color, qty}] (couleur = nom BrickOwl)."""
    import csv, io
    import xml.etree.ElementTree as ET
    maps = moc_color_maps()
    by_name = {v.lower(): v for v in list(maps["bl"].values()) + list(maps["rb"].values())}

    def color_of(v, kind):   # n° de couleur (BrickLink ou Rebrickable) ou nom écrit en toutes lettres
        v = (v or "").strip()
        return maps[kind].get(v) if v.lstrip("-").isdigit() else by_name.get(v.lower())
    lots, skipped = {}, 0
    t = text.lstrip("\ufeff").strip()
    if t.startswith("<"):
        root = ET.fromstring(t)
        for it in root.iter("ITEM"):
            g = lambda k: (it.findtext(k) or "").strip()
            if g("ITEMTYPE") not in ("", "P"):
                skipped += 1
                continue
            part, col = g("ITEMID"), color_of(g("COLOR"), "bl")
            try:
                qty = int(float(g("MINQTY") or g("QTY") or 1))
            except ValueError:
                qty = 1
            if not part or not col:
                skipped += 1
                continue
            lots[(part, col)] = lots.get((part, col), 0) + max(1, qty)
    else:
        rows = list(csv.reader(io.StringIO(t)))
        head = [h.strip().lower() for h in rows[0]] if rows else []
        ix = lambda *names: next((head.index(n) for n in names if n in head), None)
        ip, ic, iq, isp = ix("part", "part_num"), ix("color", "color_id"), ix("quantity", "qty"), ix("is spare", "is_spare")
        if ip is None or ic is None:
            raise ValueError("Fichier non reconnu : il faut un export XML BrickLink ou CSV Rebrickable (Part, Color, Quantity)")
        for r in rows[1:]:
            if len(r) <= max(ip, ic):
                continue
            if isp is not None and len(r) > isp and r[isp].strip().lower() in ("true", "1", "yes"):
                continue
            part, col = r[ip].strip(), color_of(r[ic].strip(), "rb")
            try:
                qty = int(float(r[iq])) if iq is not None and len(r) > iq and r[iq].strip() else 1
            except ValueError:
                qty = 1
            if not part or not col:
                skipped += 1
                continue
            lots[(part, col)] = lots.get((part, col), 0) + max(1, qty)
    if not lots:
        raise ValueError("Aucune pièce trouvée dans ce fichier")
    out = [{"part": p_[:40], "color": c_[:60], "qty": q_} for (p_, c_), q_ in list(lots.items())[:2000]]
    return out, skipped


def acc_clean(a):
    """Un accessoire (mini-construction) : nom, photo, et sa liste de pièces facultative (parts : [{part, color, qty}], file : nom de la liste)."""
    out = {"name": str(a.get("name") or "").strip()[:100] or "Accessoire",
           "photo": a["photo"] if re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", str(a.get("photo") or "")) else ""}
    try:   # combien de cet accessoire (ses pièces et sa valeur sont multipliées)
        _q = max(1, min(999, int(a.get("qty") or 1)))
    except (TypeError, ValueError):
        _q = 1
    if _q > 1:
        out["qty"] = _q
    lots = []
    for x in (a.get("parts") if isinstance(a.get("parts"), list) else [])[:500]:
        if not isinstance(x, dict) or not x.get("part") or not x.get("color"):
            continue
        try:
            q = max(1, min(9999, int(x.get("qty") or 1)))
        except (TypeError, ValueError):
            q = 1
        lots.append({"part": str(x["part"])[:40], "color": str(x["color"])[:60], "qty": q})
    if lots:
        out["parts"], out["file"] = lots, str(a.get("file") or "")[:120]
    return out


def acc_price(a):
    """Valeur d'un accessoire qui a une liste de pièces : prix connus (les autres sont cherchés en arrière-plan)."""
    lots = a.get("parts") or []
    if not lots:
        return None
    r = lot_prices_cached(lots)
    pr, val, priced = r["prices"], 0.0, 0
    for x in lots:
        u = pr.get(f"{x['part']}|{x['color']}")
        if u:
            val += u * x["qty"]
            priced += 1
    n = max(1, int(a.get("qty") or 1))   # (plusieurs fois le même accessoire : pièces et valeur multipliées)
    return {"value": round(round(val, 2) * n, 2), "unit": round(val, 2), "priced": priced, "lots": len(lots), "pieces": sum(x["qty"] for x in lots) * n, "pending": r["pending"]}


def acc_annotate(out, item):
    """Fiche prête à afficher : chaque accessoire avec une liste de pièces reçoit son prix (price) ; rend leur somme
    (accessoires de la fiche + ceux des figurines d'un set)."""
    total = 0.0
    if item.get("accessories"):
        out["accessories"] = [dict(a) for a in item["accessories"]]
        for a in out["accessories"]:
            p = acc_price(a)
            if p:
                a["price"] = p
                total += p["value"]
    if isinstance(item.get("fig_mods"), dict) and any((m or {}).get("accessories") for m in item["fig_mods"].values()):
        fm = {k: dict(v) for k, v in item["fig_mods"].items()}
        for m in fm.values():
            if m.get("accessories"):
                m["accessories"] = [dict(a) for a in m["accessories"]]
                for a in m["accessories"]:
                    p = acc_price(a)
                    if p:
                        a["price"] = p
                        total += p["value"]
        out["fig_mods"] = fm
    return round(total, 2)


_rb_theme_names = {}


def fallback_search(query):
    """Recherche sans le catalogue des prix : sets (Rebrickable, la recherche et sa traduction anglaise), minifigs (celles connues de l'appli
    et de Rebrickable : offline_fig_search), et une référence de minifig BrickLink exacte (sw0002…) par le catalogue BrickLink — 22/11.
    Les demandes à Rebrickable partent EN MÊME TEMPS (une seule attente)."""
    import concurrent.futures as cf
    out, seen = [], set()
    q = query.strip()
    if sources.FIG_RE.match(q):   # référence exacte de minifig : en tête
        f = (_load(CACHE_FILE, {}).get("fig:" + q.lower()) or {})
        bl = None if f.get("name") else bl_fig_info(q.lower())
        if f.get("name") or bl:
            out.append({"type": "fig", "number": q.lower(), "name": f.get("name") or bl["name"], "image": f.get("image") or bl.get("image"),
                        "value": f.get("value"), "years": f.get("years") or ([bl["year"]] if bl and bl.get("year") else None), "sets": (f.get("sets") or [])[:4]})
            seen.add(("fig", q.lower()))
    en = None
    try:
        en = sources.translate_fr(q)
    except Exception:
        pass
    qs = [q] + ([en] if en and en.lower() != q.lower() else [])
    def sets_of(qq):
        if not sources.rebrickable_key():
            return []
        try:
            return sources.rb("lego/sets/?page_size=30&ordering=-year&search=" + urllib.parse.quote(qq)).get("results") or []
        except Exception:
            return []
    def themes():
        if not _rb_theme_names and sources.rebrickable_key():
            try:
                _rb_theme_names.update({t["id"]: t.get("name") or "" for t in sources.rb("lego/themes/?page_size=1000").get("results") or []})
            except Exception:
                pass
    def figs_of(qq):
        try:
            return offline_fig_search(qq)
        except Exception:
            return []
    ex = cf.ThreadPoolExecutor(6)
    fs = [ex.submit(sets_of, qq) for qq in qs], [ex.submit(figs_of, qq) for qq in qs], ex.submit(themes)
    cf.wait(fs[0] + fs[1] + [fs[2]], timeout=20)
    ex.shutdown(wait=False)
    for fu in fs[0]:
        for x in (fu.result() if fu.done() else []):
            n = x.get("set_num") or ""
            if n and ("set", n) not in seen:
                out.append({"type": "set", "number": n, "name": x.get("name") or n, "image": x.get("set_img_url"), "year": x.get("year"),
                            "theme": _rb_theme_names.get(x.get("theme_id"), ""), "pieces": x.get("num_parts")})
                seen.add(("set", n))
    for fu in fs[1]:
        for r in (fu.result() if fu.done() else []):
            if ("fig", r.get("number")) not in seen:
                out.append(r); seen.add(("fig", r.get("number")))
    return out


def offline_fig_search(query, limit=40):
    """Catalogue des prix injoignable : minifigs dont le nom ou la référence contient la recherche —
    celles déjà connues de l'appli (fiches en cache, figurines des sets en cache), puis celles de Rebrickable (sans cote)."""
    words = re.findall(r"[^\W_]+", query.lower())
    if not words:
        return []
    cache = _load(CACHE_FILE, {})
    out, seen = [], set()

    def match(*texts):
        hay = " ".join(str(t or "") for t in texts).lower()
        return all(w in hay for w in words)
    for k, v in cache.items():
        if len(out) >= limit:
            break
        if not isinstance(v, dict) or not k.startswith("fig:") or v.get("pending_prices"):
            continue
        num = v.get("number") or k[4:]
        if num not in seen and match(num, v.get("name"), fr_fig(v.get("name") or "")):
            seen.add(num)
            sets = v.get("sets") if isinstance(v.get("sets"), list) else []
            out.append(with_fr_fig({"type": "fig", "number": num, "name": v.get("name") or num, "image": v.get("image"),
                                    "value": v.get("value"), "years": v.get("years"), "sets": sets[:4]}))
    for k, v in cache.items():
        if len(out) >= limit:
            break
        if not isinstance(v, dict) or k.startswith("fig:"):
            continue
        for f in v.get("minifigs") or []:
            num = f.get("id")
            if num and num not in seen and match(num, f.get("name"), fr_fig(f.get("name") or "")):
                seen.add(num)
                out.append(with_fr_fig({"type": "fig", "number": num, "name": f.get("name") or num, "image": f.get("image"),
                                        "value": f.get("value"), "sets": [k]}))
    if sources.rebrickable_key():
        try:
            r = sources.rb("lego/minifigs/?page_size=30&search=" + urllib.parse.quote(query))
            out += [{"type": "fig", "number": x["set_num"], "name": x.get("name") or x["set_num"], "image": x.get("set_img_url"),
                     "pieces": x.get("num_parts"), "rb": True} for x in r.get("results", []) if x.get("set_num")]
        except Exception:
            pass
    return out


def with_avail(results):
    """Résultats de recherche : disponibilité des sets déjà connus (retiré, retrait prévu), pour la voir d'un coup d'œil."""
    cache = _load(CACHE_FILE, {})
    for r in results:
        if r.get("type") in ("set", "rbset"):
            c = cache.get(r.get("number")) or {}
            for k in ("availability", "retirement"):
                if c.get(k) and not r.get(k):
                    r[k] = c[k]
    return results


def rb_fig_candidates(fid):
    """Minifigs Rebrickable qui peuvent correspondre à une minifig BrickEconomy : celles de ses sets, puis par nom."""
    try:
        info = get_fig(fid)
    except Exception:   # (catalogue des cotes injoignable : sa fiche gardée, sinon rien que son n°)
        info = _load(CACHE_FILE, {}).get("fig:" + fid) or {"name": fid}
    if RB_FIG.fullmatch(fid):
        return [{"fig_num": fid, "name": info.get("name") or fid, "image": info.get("image"), "num_parts": info.get("pieces"), "from": fid, "score": 1, "sure": True}]
    out, seen = [], set()

    def add(m, src):
        if m.get("set_num") and m["set_num"] not in seen:
            seen.add(m["set_num"])
            out.append({"fig_num": m["set_num"], "name": m.get("name") or m.get("set_name") or "", "image": m.get("set_img_url"),
                        "num_parts": m.get("num_parts"), "from": src})
    sets = info.get("sets") or []
    if isinstance(sets, str):
        sets = re.findall(r"[\w.]+-\d+", sets)
    for st in sets[:3]:
        try:
            for m in sources.rb(f"lego/sets/{urllib.parse.quote(st)}/minifigs/?page_size=100").get("results", []):
                add(m, st)
        except Exception:
            pass
    name = (info.get("name_en") or info.get("name") or "").split(" - ")[0].strip()
    if name:
        try:
            for m in sources.rb("lego/minifigs/?page_size=24&search=" + urllib.parse.quote(name)).get("results", []):
                add(m, "nom")
        except Exception:
            pass
    words = {w for w in re.findall(r"[a-z0-9]+", name.lower()) if len(w) > 2}
    for m in out:
        m["score"] = len(words & set(re.findall(r"[a-z0-9]+", m["name"].lower())))
    out.sort(key=lambda m: (-m["score"], m["from"] == "nom"))
    # choix sûr : la minifig de ses sets dont le nom correspond nettement le mieux (ou la seule du set)
    in_sets = [m for m in out if m["from"] != "nom"]
    by_set = {}
    for m in in_sets:
        by_set.setdefault(m["from"], []).append(m)
    alone = {ms[0]["fig_num"] for ms in by_set.values() if len(ms) == 1}
    if in_sets:
        best = in_sets[0]["score"]
        tops = list({m["fig_num"]: m for m in in_sets if m["score"] == best}.values())
        if best > 0 and len(tops) == 1:
            tops[0]["sure"] = True   # nom qui correspond nettement le mieux
        elif best > 0 and len([m for m in tops if m["fig_num"] in alone]) == 1:
            next(m for m in tops if m["fig_num"] in alone)["sure"] = True   # à égalité : celle qui est seule dans son set
        elif best == 0 and len({m["fig_num"] for m in in_sets}) == 1:
            in_sets[0]["sure"] = True   # noms différents, mais une seule minifig dans ses sets
    out.sort(key=lambda m: not m.get("sure"))
    return out[:30]


def rb_fig_parts(fig_num, refresh=False):
    """Pièces d'une minifig Rebrickable ; couleur en nom BrickOwl pour les prix. Gardées pour toujours
    (une figurine ne change pas) — l'ouverture d'une fiche n'attend jamais Rebrickable."""
    key = "mf2:" + fig_num
    c = _parts_cache().get(key)
    if c and isinstance(c.get("parts"), list) and not refresh:
        return c["parts"]   # (une figurine ne change pas : gardée pour toujours)
    d = sources.rb(f"lego/minifigs/{urllib.parse.quote(fig_num)}/parts/?page_size=100")
    bo = moc_color_maps()["rb"]
    parts = []
    for r in d.get("results", []):
        pt, col = r["part"], r["color"]
        el = r.get("element_id")
        parts.append({"part_num": pt["part_num"], "part": ((pt.get("external_ids") or {}).get("BrickLink") or [pt["part_num"]])[0],
                      "name": pt.get("name") or "", "color_id": col["id"], "color": bo.get(str(col["id"]), col.get("name")),
                      "color_fr": FR_COLORS.get(col.get("name") or "", col.get("name") or ""), "qty": r.get("quantity", 1),
                      "color_name": col.get("name") or "", "rgb": col.get("rgb") or "", "element_id": el or "",
                      "image": (f"https://cdn.rebrickable.com/media/parts/elements/{el}.jpg" if el else None) or pt.get("part_img_url") or ""})
    _parts_cache_put(key, {"parts": parts, "_t": time.time()})
    return parts


_bg_run = set()   # relectures en fond en cours (une seule à la fois par clé)


def _bg_once(key, fn):
    """Relecture en fond (une seule à la fois pour une même clé) : la réponse d'avant est rendue sans attendre."""
    if DEMO or key in _bg_run:
        return
    _bg_run.add(key)

    def go():
        try:
            fn()
        except Exception:
            pass
        finally:
            _bg_run.discard(key)
    threading.Thread(target=go, daemon=True).start()


SFA_STOP = {"with", "and", "the", "minifigure", "minifig", "lego", "of", "in", "figure", "head", "print", "torso", "legs", "hips"}


def _sfa_words(name):
    """Mots qui distinguent une figurine (couleurs BrickLink → Rebrickable : Flesh = Nougat, Grey = Gray)."""
    t = (name or "").lower().replace("grey", "gray").replace("medium dark flesh", "medium nougat").replace("light flesh", "light nougat").replace("flesh", "nougat")
    return {w for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2 and w not in SFA_STOP}


def bo_fig_name(fid):
    """Nom BrickOwl d'une minifig (réf. BrickLink), lu sur SA page (le n° y figure) ; gardé pour toujours (« bon: »). "" si rien de sûr."""
    import html as _html
    c = _parts_cache().get("bon:" + fid)
    if isinstance(c, dict) and "n" in c:
        return c["n"]
    name = ""
    page = sources._get_en("https://www.brickowl.com/search/catalog?query=" + urllib.parse.quote(fid))
    for l in [x for x in dict.fromkeys(re.findall(r'href="(/catalog/lego-[^"]+)"', page)) if "-set-" not in x][:3]:
        pg = sources._get_en("https://www.brickowl.com" + l)
        if re.search(r"(?<![\w-])" + re.escape(fid) + r"(?![\w-])", pg, re.I):
            t = re.search(r"<h1[^>]*>(.*?)</h1>", pg, re.S)
            name = _html.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip() if t else ""
            break
    _parts_cache_put("bon:" + fid, {"n": name, "_t": time.time()})
    return name


def _sfa_assign(fs, ms, names):
    """Associe figurines du catalogue (fs) et minifigs Rebrickable du set (ms) sans ambiguïté : quantités, noms (meilleur dans les deux
    sens), élimination ; recommence tant que ça avance. Rend {n° catalogue: fig-… Rebrickable}."""
    out, lf, lm = {}, list(fs), list(ms)
    same_size = len(fs) == len(ms)   # (« la dernière de chaque côté » : seulement si les deux listes ont autant de figurines)
    sc = lambda f, m: len(_sfa_words(names(f)) & _sfa_words(m.get("set_name") or m.get("name")))
    def take(f, m):
        out[f["id"]] = m["set_num"]; lf.remove(f); lm.remove(m)
    while lf and lm:
        moved = False
        for f in list(lf):   # quantité > 1 qui n'existe qu'une fois de chaque côté
            q = int(f.get("qty") or 1)
            if q > 1 and sum(1 for g in lf if int(g.get("qty") or 1) == q) == 1:
                same = [m for m in lm if int(m.get("quantity") or 1) == q]
                if len(same) == 1:
                    take(f, same[0]); moved = True
        for f in list(lf):   # nom : le meilleur pour elle, et elle la meilleure pour lui (à égalité : rien)
            if f not in lf or not lm:
                continue
            ss = sorted(lm, key=lambda m: -sc(f, m))
            if sc(f, ss[0]) == 0 or (len(ss) > 1 and sc(f, ss[0]) == sc(f, ss[1])):
                continue
            back = sorted(lf, key=lambda g: -sc(g, ss[0]))
            if back[0] is f and (len(back) == 1 or sc(back[0], ss[0]) > sc(back[1], ss[0])):
                take(f, ss[0]); moved = True
        if same_size and len(lf) == 1 and len(lm) == 1:   # la dernière de chaque côté
            take(lf[0], lm[0]); moved = True
        if not moved:
            break
    return out


def bl_fig_refs(fid):
    """Références BrickLink des pièces d'une minifig (API officielle BrickLink, « subsets ») ; gardées pour toujours. None : BrickLink indisponible."""
    c = _parts_cache().get("bls:" + fid)
    if isinstance(c, dict) and isinstance(c.get("r"), list):
        return set(c["r"])
    if not bl_on():
        return None
    try:
        d = sources.bl_get(f"/items/MINIFIG/{urllib.parse.quote(str(sources.bl_fig_no(fid)))}/subsets") or []
    except Exception:
        return None   # (maintenance, quota… : nouvel essai plus tard)
    refs = set()
    for g in d if isinstance(d, list) else []:
        for e in g.get("entries") or []:
            it = e.get("item") or {}
            if it.get("type") == "PART" and it.get("no"):
                refs.add(str(it["no"]).lower())
    if refs:
        _parts_cache_put("bls:" + fid, {"r": sorted(refs), "_t": time.time()})
    return refs or None


def fig_pick_by_refs(fid, cands):
    """Parmi les versions Rebrickable candidates, celle dont les références de pièces sont celles de la minifig BrickLink (fid). None sinon."""
    refs = bl_fig_refs(fid)
    if not refs:
        return None
    scored = []
    for m in cands[:12]:
        fn = m.get("fig_num") or m.get("set_num")
        if not fn:
            continue
        try:
            got = {str(r.get("part") or r.get("part_num") or "").lower() for r in rb_fig_parts(fn)}
        except sources.RebrickableBusy:
            raise
        except Exception:
            continue
        got.discard("")
        if got:
            scored.append((len(refs & got) / len(refs | got), got == refs, fn, m))
    exact = [x for x in scored if x[1]]
    if len(exact) == 1:
        return exact[0][3]
    scored.sort(key=lambda x: -x[0])
    if scored and scored[0][0] >= .8 and (len(scored) == 1 or scored[0][0] - scored[1][0] >= .2):
        return scored[0][3]
    return None


def set_figs_rb(number, mfs):
    """Figurines d'un set → leur minifig Rebrickable (inventaire Rebrickable du même set) ; gardé (« sfa:<set> »)."""
    key = "sfa:" + number
    c = _parts_cache().get(key)
    if isinstance(c, dict) and isinstance(c.get("m"), dict) and not (c.get("partial") and bl_on()):
        return c["m"]
    ms = [m for m in sources.rb(f"lego/sets/{urllib.parse.quote(number)}/minifigs/?page_size=100").get("results", []) if m.get("set_num")]
    fs = [f for f in mfs if isinstance(f, dict) and f.get("id")]
    out = _sfa_assign(fs, ms, lambda f: f.get("name"))
    left = [f for f in fs if f["id"] not in out]
    if left and len(ms) > len(out):   # encore ambigu : les noms BrickOwl (plus précis : couleur de la tête…) pour celles-là
        bo = {}
        for f in left:
            try:
                bo[f["id"]] = bo_fig_name(sources.bl_fig_no(f["id"]))
            except Exception:
                bo[f["id"]] = ""
        used = set(out.values())
        more = _sfa_assign(left, [m for m in ms if m["set_num"] not in used], lambda f: (f.get("name") or "") + " " + bo.get(f["id"], ""))
        out.update(more)
    left = [f for f in fs if f["id"] not in out]
    for f in left:   # toujours ambiguës : leurs références BrickLink comparées à celles des minifigs Rebrickable du set qui restent
        used = set(out.values())
        try:
            pick = fig_pick_by_refs(f["id"], [m for m in ms if m["set_num"] not in used])
        except sources.RebrickableBusy:
            raise
        if pick:
            out[f["id"]] = pick["set_num"]
    if left and any(f["id"] not in out for f in left) and not bl_on():
        _parts_cache_put(key, {"m": out, "_t": time.time(), "partial": True})   # (BrickLink absent : complété plus tard)
        return out
    _parts_cache_put(key, {"m": out, "_t": time.time()})
    return out


def set_figs_apply(it, mfs):
    """Les versions déduites du set deviennent celles de ses figurines (« fc: »), sauf si une version est déjà connue."""
    m = set_figs_rb(norm_set(it.get("number") or "") or it.get("number"), mfs)
    for fid, rb in m.items():
        c = _parts_cache().get("fc:" + fid)
        if not (isinstance(c, dict) and c.get("rb")):
            _parts_cache_put("fc:" + fid, {"rb": rb, "_t": time.time(), "src": "set"})
    return m


def rb_fig_match(fid, refresh=False):
    """Minifigs Rebrickable candidates d'une figurine (rb_fig_candidates), GARDÉES pour toujours :
    rendues tout de suite. Une liste vide (Rebrickable injoignable ?) n'est pas gardée."""
    key = "rbm:" + fid
    c = _parts_cache().get(key)
    if c and isinstance(c.get("l"), list) and not refresh:
        return c["l"]   # (gardées pour toujours)
    lst = rb_fig_candidates(fid)
    if lst:
        _parts_cache_put(key, {"l": lst, "_t": time.time()})
    return lst


def rb_fig_match_known(fid):
    """Comme rb_fig_match, mais une version déjà connue (déduite de son set, ou choisie) passe en tête, marquée sûre : plus de question."""
    rb = (_parts_cache().get("fc:" + fid) or {}).get("rb") if isinstance(_parts_cache().get("fc:" + fid), dict) else None
    if not rb:   # figurine d'un de mes sets : sa version se déduit du set
        db, cache = load_db(), _load(CACHE_FILE, {})
        for it in db["items"]:
            mfs = (cache.get(cache_key(it)) or {}).get("minifigs") if (it.get("kind") or "set") == "set" else None
            if mfs and any(isinstance(f, dict) and f.get("id") == fid for f in mfs):
                try:
                    rb = set_figs_apply(it, mfs).get(fid)
                except Exception:
                    rb = None
                if rb:
                    break
    try:
        lst = [dict(x) for x in rb_fig_match(fid)]
    except Exception:
        lst = []
    if not rb and lst and not lst[0].get("sure"):   # plusieurs versions possibles : ses références BrickLink tranchent (si BrickLink répond)
        try:
            pick = fig_pick_by_refs(fid, lst)
        except Exception:
            pick = None
        if pick:
            rb = pick.get("fig_num")
            _parts_cache_put("fc:" + fid, {"rb": rb, "_t": time.time(), "src": "refs"})
    if rb:
        for x in lst:
            x.pop("sure", None)
        hit = next((x for x in lst if x.get("fig_num") == rb), None) or {"fig_num": rb, "name": rb, "image": RB_IMG.format(rb), "from": "set"}
        lst = [dict(hit, sure=True)] + [x for x in lst if x.get("fig_num") != rb]
    return lst


def fig_rb_cached(n, known=None):
    """Référence Rebrickable d'une figurine, SANS réseau : choisie sur la fiche, déjà une « fig-… », ou correspondance sûre gardée."""
    if known:
        return known
    if RB_FIG.fullmatch(n):
        return n
    c = _parts_cache()
    fc = c.get("fc:" + n)
    if isinstance(fc, dict) and fc.get("rb"):
        return fc["rb"]
    lst = (c.get("rbm:" + n) or {}).get("l") or []
    return lst[0]["fig_num"] if lst and lst[0].get("sure") else None


def offline_figs():
    """Figurines de la collection et des listes : seules (avec leur version choisie) et celles de chaque set → {numéro: réf. choisie ou None}."""
    db, cache, out = load_db(), _load(CACHE_FILE, {}), {}
    for it in db["items"]:
        if it.get("kind") == "fig" and it.get("number") and it["number"] != "custom":
            out[it["number"]] = it.get("rb_fig") or out.get(it["number"])
        for f in (cache.get(cache_key(it)) or {}).get("minifigs") or []:
            if isinstance(f, dict) and f.get("id"):
                out.setdefault(f["id"], None)
    return out


def _cmf_items():
    """Minifigs à collectionner seules (celles qui ont des accessoires) — catalogue lu UNE fois (cmf_set_of le relit à chaque appel)."""
    cache = _load(CACHE_FILE, {})
    return [it for it in load_db()["items"] if it.get("kind") == "fig" and (it.get("cmf_set") or (cache.get("fig:" + (it.get("number") or "")) or {}).get("theme") in CMF_THEMES)]


def offline_warm():
    """Prépare tout ce qu'une fiche demande, pour qu'elle s'ouvre sans attendre et hors connexion : correspondance et pièces de
    chaque figurine, inventaire de chaque set. Seulement ce qui manque ; freiné (Rebrickable : une requête à la fois)."""
    if DEMO or COPIE or not sources.rebrickable_key():
        return
    done = 0
    _cache = _load(CACHE_FILE, {})
    for it in [i for i in load_db()["items"] if (i.get("kind") or "set") == "set"]:   # versions des figurines d'origine : déduites de leur set
        mfs = (_cache.get(cache_key(it)) or {}).get("minifigs") or []
        _c = _parts_cache().get("sfa:" + (norm_set(it.get("number") or "") or it.get("number")))
        if mfs and (not _c or (isinstance(_c, dict) and _c.get("partial") and bl_on())):   # (pas encore fait, ou fait sans BrickLink et BrickLink revenu)
            try:
                set_figs_apply(it, mfs)
            except (sources.RebrickableBusy, PermissionError):
                return
            except Exception:
                continue
    for n, known in sorted(offline_figs().items()):
        try:
            rb = fig_rb_cached(n, known)
            if not rb and "rbm:" + n not in _parts_cache():
                lst = rb_fig_match(n)
                rb = lst[0]["fig_num"] if lst and lst[0].get("sure") else None
            if rb and "mf2:" + rb not in _parts_cache():
                rb_fig_parts(rb); done += 1
            if not rb and bl_on() and "rbm:" + n in _parts_cache():   # plusieurs versions possibles : ses références BrickLink tranchent
                pick = fig_pick_by_refs(n, (_parts_cache().get("rbm:" + n) or {}).get("l") or [])
                if pick:
                    rb = pick["fig_num"]; _parts_cache_put("fc:" + n, {"rb": rb, "_t": time.time(), "src": "refs"})
                    if "mf2:" + rb not in _parts_cache():
                        rb_fig_parts(rb); done += 1
            if not rb:   # plusieurs versions possibles (choix demandé une fois) : les pièces des candidates de ses sets, prêtes d'avance — 20/11
                for m in [x for x in (_parts_cache().get("rbm:" + n) or {}).get("l") or [] if x.get("from") and x.get("from") != "nom"][:8]:
                    if m.get("fig_num") and "mf2:" + m["fig_num"] not in _parts_cache():
                        rb_fig_parts(m["fig_num"]); done += 1
        except (sources.RebrickableBusy, PermissionError):
            return
        except Exception:
            continue
    for it in [i for i in load_db()["items"] if i.get("kind", "set") in ("set", "custom")] + _cmf_items():
        try:
            sn = cmf_set_of(it) if it.get("kind") == "fig" else norm_set(it.get("number") or "")
            if sn and "inv:" + sn not in _parts_cache():
                inventory_rows(sn); done += 1
        except (sources.RebrickableBusy, PermissionError):
            return
        except Exception:
            continue
    if done:
        print(f"Hors ligne : {done} liste(s) de pièces préparée(s)", flush=True)


def offline_loop():
    time.sleep(150)   # (après le démarrage)
    while True:
        try:
            offline_warm()
        except Exception as e:
            print("Hors ligne :", e, flush=True)
        time.sleep(6 * 3600)


def offline_pack():
    """Toutes les listes de pièces des figurines de la collection, depuis le cache (aucun appel réseau) :
    {fig: {numéro: réf. Rebrickable}, parts: {réf.: pièces}, acc: {fiche: accessoires d'une minifig à collectionner}}."""
    c, fig, parts, acc = _parts_cache(), {}, {}, {}
    for n, known in offline_figs().items():
        rb = fig_rb_cached(n, known)
        ps = (c.get("mf2:" + rb) or {}).get("parts") if rb else None
        if isinstance(ps, list):
            fig[n], parts[rb] = rb, ps
    for it in _cmf_items():
        try:
            sn = cmf_set_of(it)
            if sn and "inv:" + sn in c:
                a = cmf_accessories(it)
                if a:
                    acc[it["id"]] = a
        except Exception:
            continue
    return {"fig": fig, "parts": parts, "acc": acc, "t": int(time.time())}


FIG_BODY = re.compile(r"(Minifig\s+)?(Head|Hips|Legs?|Torso|Arms?|Hands?|Animal Body|Hair|Helmet|Hat|Hood|Headwear|Cap)\b", re.I)   # le corps (et la coiffe)


def fig_objects(parts, swaps=None):
    """Objets d'une minifig (armes, outils…) : ses pièces sans celles du corps, après mes remplacements."""
    parts = [dict(p) for p in parts or []]
    for s in swaps or []:
        new, k = s.get("new"), s.get("k")
        if not s.get("orig"):   # pièce ajoutée
            if new:
                parts.append(dict(new))
        elif isinstance(k, int) and 0 <= k < len(parts) and (s.get("orig") or {}).get("part_num", parts[k].get("part_num")) == parts[k].get("part_num"):
            parts[k] = dict(new) if new else {}
    return [{"name": p.get("name") or "", "part": p.get("part") or p.get("part_num") or "", "color": p.get("color_fr") or p.get("color") or "",
             "image": p.get("image") or "", "qty": p.get("qty", 1)} for p in parts if p.get("name") and not FIG_BODY.match(p["name"])]


def fig_rb_known(it):
    """Référence Rebrickable d'une minifig sans appel réseau (None : inconnue, "" : aucune sûre)."""
    n = it.get("number") or ""
    if it.get("rb_fig"):
        return it["rb_fig"]
    if RB_FIG.fullmatch(n):
        return n
    c = _parts_cache().get("fc:" + n)
    return c.get("rb") or "" if c and time.time() - c.get("_t", 0) < 36500 * 86400 else None


def guest_fig_objs(it):
    """Objets d'une minifig seule pour la page publique, depuis le cache (None : pas encore connus)."""
    rb = fig_rb_known(it)
    if rb == "":
        return []
    c = _parts_cache().get("mf2:" + rb) if rb else None
    return fig_objects(c["parts"], it.get("fig_swaps")) if c else None


def fig_objs_resolve(it):
    """Comme guest_fig_objs, en interrogeant Rebrickable si besoin (gardé en cache)."""
    rb = fig_rb_known(it)
    if rb is None:
        c = rb_fig_candidates(it["number"])
        rb = c[0]["fig_num"] if c and c[0].get("sure") else ""
        _parts_cache_put("fc:" + it["number"], {"rb": rb, "_t": time.time()})
    return fig_objects(rb_fig_parts(rb), it.get("fig_swaps")) if rb else []


_fig_warm = {"on": False, "tried": {}}   # tried : n° → heure du dernier essai raté (pas de nouvel essai avant 6 h)


def warm_fig_objs(figs):
    """En arrière-plan, une seule fois à la fois : les objets des minifigs pas encore connus (page publique)."""
    if _fig_warm["on"]:
        return
    now = time.time()
    todo = [f for f in figs if guest_fig_objs(f) is None and now - _fig_warm["tried"].get(f.get("number"), 0) > 6 * 3600]
    if not todo:
        return
    _fig_warm["on"] = True

    def run():
        try:
            for f in todo:
                try:
                    fig_objs_resolve(f)
                except sources.RebrickableBusy:
                    break   # Rebrickable demande de ralentir : on arrête là (repris plus tard)
                except Exception:
                    _fig_warm["tried"][f.get("number")] = time.time()   # raté : pas avant 6 h
        finally:
            _fig_warm["on"] = False
    threading.Thread(target=run, daemon=True).start()


def part_chg(part, color, pc=None):
    """Variation (%) du prix d'une pièce depuis le relevé d'avant, dans le même ordre que lot_price() (BrickLink, sinon BrickOwl) ; None si inconnue."""
    pc = pc if pc is not None else _parts_cache()
    blc = bo_bl_color(color)
    order = ((pc.get(f"bp:{part}|{blc}") if blc is not None else None, bp_unit), (pc.get("mp:" + f"{part}|{color}"), lambda r: (r or {}).get("unit")))
    for rec, unit in (order if ref_site() != "brickowl" else order[::-1]):   # (le site de référence d'abord — 21/11)
        u = unit(rec) if isinstance(rec, dict) else None
        if u:
            prev = (rec.get("prev") or {}).get("unit")
            return round((u - prev) / prev * 100, 1) if prev else None
    return None


def lot_price(part, color):
    """Prix unitaire d'une pièce dans une couleur, selon le site de référence (BrickLink, BrickOwl, les deux : moyenne — 21/11), ou None."""
    blc = bo_bl_color(color)
    u = bp_unit(_parts_cache().get(f"bp:{part}|{blc}")) if blc is not None else None
    if u and ref_site() == "bricklink":   # relevé BrickLink (moyenne des annonces)
        return u
    bl_u = u
    key = "mp:" + f"{part}|{color}"
    c = _parts_cache().get(key)
    if not c or time.time() - c.get("t", 0) > 7 * 86400:
        try:
            c = sources.moc_part_price(part, color) or {"unit": None}
        except Exception:
            c = {"unit": None}
        c["t"] = int(time.time())
        _parts_cache_put(key, c)
        time.sleep(0.4)
    return ref_mix(bl_u, c.get("unit"))[0]


_lp = {"todo": [], "on": False}
_lp_lock = threading.Lock()


_lp_bl_tried = {}   # "pièce|couleur BrickLink" → heure du dernier essai BrickLink raté (pas de nouvel essai avant 6 h)


def lot_prices_cached(lots):
    """Prix connus des pièces {"pièce|couleur": prix ou None} ; les autres sont cherchés en arrière-plan.
    Même ordre que lot_price() et le détail de la pièce : le relevé BrickLink d'abord, BrickOwl sinon."""
    out, miss, pc, now, man = {}, [], _parts_cache(), time.time(), []
    for l in lots[:300]:
        part, color = str(l.get("part") or "")[:40], str(l.get("color") or "")[:60]
        if not part:
            continue
        blc = bo_bl_color(color)   # couleur BrickOwl (nom) → n° BrickLink
        bpr = pc.get(f"bp:{part}|{blc}") if blc is not None else None
        c = pc.get("mp:" + f"{part}|{color}")
        if bp_unit(bpr) and (ref_site() == "bricklink" or (c and now - c.get("t", 0) <= 7 * 86400)):   # relevé BrickLink (et BrickOwl si le réglage s'en sert)
            out[f"{part}|{color}"] = ref_mix(bp_unit(bpr), (c or {}).get("unit"))[0] if ref_site() != "bricklink" else bp_unit(bpr)
            continue
        if bp_unit(bpr):   # BrickOwl pas encore relevé : BrickLink en attendant, BrickOwl cherché
            out[f"{part}|{color}"] = bp_unit(bpr)
            miss.append((part, color))
            continue
        bl_done = blc is None or bpr is not None or now - _lp_bl_tried.get(f"{part}|{blc}", 0) < 6 * 3600   # BrickLink déjà interrogé (ou impossible)
        if c and now - c.get("t", 0) <= 7 * 86400 and (c.get("unit") is not None or bl_done):   # BrickOwl connu, ou introuvable partout
            out[f"{part}|{color}"] = c.get("unit")
            if c.get("unit") is None:   # introuvable : mon prix, s'il y en a un (signalé comme saisi)
                mu = manual_price(l.get("part_num"), l.get("color_id"), part, color)
                if mu is not None:
                    out[f"{part}|{color}"] = mu
                    man.append(f"{part}|{color}")
        else:
            miss.append((part, color))
    if miss:
        with _lp_lock:
            for m in miss:
                if m not in _lp["todo"]:
                    _lp["todo"].append(m)
            start = not _lp["on"]
            _lp["on"] = True
        if start:
            threading.Thread(target=_lp_run, daemon=True).start()
    return {"prices": out, "pending": len(miss), "manual": man}


def _lp_run():
    while True:
        with _lp_lock:
            if not _lp["todo"]:
                _lp["on"] = False
                return
            part, color = _lp["todo"].pop(0)
        try:
            u = lot_price(part, color)   # BrickLink s'il est en cache, sinon BrickOwl
        except Exception:
            u = None
        blc = bo_bl_color(color)
        if u is None and blc is not None and not _parts_cache().get(f"bp:{part}|{blc}"):   # aucun prix : BrickLink (prix manquant à l'écran)
            try:
                bl_part(part, blc)   # gardé dans « bp: » (même sans annonce : pas de nouvel appel)
            except Exception:   # pas de codes BrickLink, quota du jour, réseau : pas de nouvel essai avant 6 h
                _lp_bl_tried[f"{part}|{blc}"] = time.time()


def _swap_targets(it):
    """Où sont rangés les remplacements : la minifig seule elle-même, ou chaque figurine modifiée d'un set."""
    if not it:
        return []
    if it.get("kind") == "fig":
        return [("", it)]
    out = [(fid, m) for fid, m in (it.get("fig_mods") or {}).items() if isinstance(m, dict)]
    if isinstance(it.get("set_mod"), dict):
        out.append(("#set", it["set_mod"]))
    return out


def _swap_price_item(iid):
    """Pièces remplacées (minifig du catalogue, seule ou dans un set) : écart de prix (nouvelles − d'origine)."""
    it = next((i for i in load_db()["items"] if i["id"] == iid), None)
    for fid, tgt in _swap_targets(it):
        swaps = tgt.get("fig_swaps") or []
        if not swaps or (tgt.get("swap_price") or {}).get("done"):
            continue
        priced = []

        def lp(x):   # prix BrickOwl, sinon calqué sur les pièces qui lui ressemblent (marqué approx)
            u = lot_price(x["part"], x["color"])
            if u:
                u2, bad = sane_unit(x.get("part_num") or x["part"], x.get("color_id"), u, (_parts_cache().get(f"mp:{x['part']}|{x['color']}") or {}).get("offers"), bl_price_known(x["part"], x["color"]))
                return {**x, "unit": u2, "approx": bad}
            mu = manual_price(x.get("part_num"), x.get("color_id"), x.get("part"), x.get("color"))   # mon prix d'abord
            if mu is not None:
                return {**x, "unit": mu, "approx": False, "manual": True}
            a = similar_unit(x.get("part_num") or x["part"], x.get("color_id"))
            return {**x, "unit": a, "approx": a is not None}
        for sw in swaps:
            o, n = sw["orig"], sw["new"]
            priced.append({**sw, "orig": lp(o) if o else None, "new": lp(n) if n else None})
        with lock:
            db = load_db()
            cur_it = next((i for i in db["items"] if i["id"] == iid), None)
            cur = dict(_swap_targets(cur_it)).get(fid)
            key = lambda lst: [(x["k"], (x["new"] or {}).get("part"), (x["new"] or {}).get("color")) for x in lst]
            if not cur or key(cur.get("fig_swaps") or []) != key(swaps):
                continue   # modifié entre-temps : un autre chiffrage suivra
            ok = lambda x: (x["orig"] is None or x["orig"]["unit"] is not None) and (x["new"] is None or x["new"]["unit"] is not None)
            delta = sum(((x["new"]["unit"] * x["new"]["qty"]) if x["new"] else 0) - ((x["orig"]["unit"] * x["orig"]["qty"]) if x["orig"] else 0)
                        for x in priced if ok(x) and not x.get("free") and not x.get("fix"))   # (correction : sans effet sur l'estimation)
            cur["fig_swaps"] = priced
            cur["swap_price"] = {"delta": round(delta, 2), "done": True, "unpriced": sum(1 for x in priced if not ok(x) and not x.get("free") and not x.get("fix")),
                                 "approx": any((x.get(s) or {}).get("approx") for x in priced if ok(x) and not x.get("free") for s in ("orig", "new"))}
            _save(DB_FILE, db)


def mod_copies(swaps, q):
    """Figurines modifiées d'un lot (décote sur elles seules) : la pièce d'origine la plus retirée, en figurines (orig.per = pièces par figurine)."""
    r = [-(-int(x["orig"].get("qty") or 1) // max(1, int(x["orig"].get("per") or 1))) for x in swaps or [] if isinstance(x, dict) and x.get("orig")]
    return max(1, min(q, max(r) if r else 1))


PHOTO_TODO = "Photo à faire : aucune image disponible pour cette figurine"


def bo_behav(key):
    """Réglage « Comportements » publié dans le back office (noMerge : figurines identiques non regroupées — les pages publiques suivent)."""
    try:
        return (backoffice.published().get("behav") or {}).get(key) is True
    except Exception:
        return False


def lot_swaps_migrate():
    """Une fois par collection : les pièces échangées d'une figurine seule en plusieurs exemplaires passent au comptage « lot entier »
    (avant le 16/11/2026 : notées pour UNE figurine et appliquées à toutes). Même valeur. La marque « lot_swaps » de la collection évite de
    recommencer ; une ancienne sauvegarde restaurée ne la porte pas : elle est convertie à son tour. Rend le nombre de fiches converties."""
    with lock:
        db = load_db()
        if db.get("lot_swaps"):
            return 0
        n = 0
        for it in db["items"]:
            try:
                q = int(it.get("quantity", 1) or 1)
            except (TypeError, ValueError):
                q = 1
            if it.get("kind") != "fig" or not it.get("fig_swaps") or q < 2:
                continue
            for sw in it["fig_swaps"]:
                for side in ("orig", "new"):
                    x = sw.get(side) if isinstance(sw, dict) else None
                    if isinstance(x, dict):
                        one = max(1, int(x.get("qty") or 1))
                        if side == "orig":
                            x["per"] = one
                        x["qty"] = one * q
            sp = it.get("swap_price")
            if isinstance(sp, dict) and "delta" in sp:
                sp["delta"] = round((sp.get("delta") or 0) * q, 2)
            n += 1
        if n:
            backup_db("avant-pieces-sur-le-lot")
        db["lot_swaps"] = True
        _save(DB_FILE, db)
        return n


def fig_mods_delta(item, have):
    """Set : écart de valeur des figurines modifiées — une fois (l'exemplaire modifié), même si le set en a plusieurs."""
    return sum(((m.get("swap_price") or {}).get("delta") or 0) * min(1, have.get(fid, 0))
               for fid, m in (item.get("fig_mods") or {}).items() if isinstance(m, dict) and m.get("fig_swaps"))


# ---------------------------------------------------------------- validation des minifigs MOC (page temporaire)
REVIEW_FILE = os.path.join(DATA, "moc_review.json")
REVIEW_SLOTS = [   # (clé, libellé, zones lues, mots-clés du nom de pièce, choix par défaut si rien)
    ("coiffe", "Cheveux / couvre-chef", ("coiffe", "tete"), r"hair|headgear|helmet|hat\b|cap\b|hood|crown|tiara|headdress|bandana|beanie|turban", "notfound"),
    ("tete", "Tête", ("tete", "coiffe"), r"^(minifigure, )?head\b(?!gear)|\bhead (mask|alien|modified)", "notfound"),
    ("torse", "Torse", ("torse", "dos"), r"torso", "notfound"),
    ("jambes", "Jambes", ("jambes", "taille"), r"legs|hips", "notfound"),
    ("dos", "Accessoire dos / cou", ("dos", "torse"), r"cape|neck|backpack|jet ?pack|quiver|wing|armor|shoulder|container|scabbard|cloak|shawl|collar|pauldron|bracket|tank", "none"),
    ("taille", "Accessoire taille", ("taille", "jambes"), r"belt|skirt|holster|sash|pouch|loincloth|apron|kilt|hip accessory|tasset", "none"),
]
# zones d'une minifig, en fraction de la hauteur de la figurine (centrée sur son axe)
SCAN_ZONES = {
    "coiffe": (-0.30, 0.00, 0.30, 0.27), "tete": (-0.17, 0.12, 0.17, 0.34), "torse": (-0.30, 0.30, 0.30, 0.62),
    "jambes": (-0.22, 0.58, 0.22, 1.00), "main_g": (-0.42, 0.45, -0.12, 0.68), "main_d": (0.12, 0.45, 0.42, 0.68),
    "bras_g": (-0.36, 0.32, -0.16, 0.55), "bras_d": (0.16, 0.32, 0.36, 0.55),
    "dos": (-0.45, 0.20, 0.45, 0.70), "taille": (-0.30, 0.52, 0.30, 0.72),
}


def _col_rb(blrb, cf, c):
    rb = blrb.get(str(c.get("bl")))
    return None if rb is None else {"color_id": rb, "color_fr": (cf.get(str(rb)) or {}).get("fr") or c.get("name"), "score": c.get("score", 0), "bl_name": c.get("name")}


def review_slots(raw):
    """Propositions par emplacement (+ bras / mains si différents du torse, + autres pièces repérées)."""
    blrb = moc_color_maps()["blrb"]
    cf = colors_fr()
    pc = _parts_cache()
    zones = raw.get("zones") or {}
    image_of = lambda pid, fb: (pc.get("bl:" + pid) or {}).get("image") or (pc.get("bl:" + pid + "c01") or {}).get("image") or fb
    zone_cols = lambda z: [c for c in (_col_rb(blrb, cf, x) for x in (zones.get(z) or {}).get("colors") or []) if c]

    def cimg_of(pid):   # photo de la pièce dans chaque couleur (Rebrickable, si connue) : l'image proposée suit la couleur reconnue
        rbn = (pc.get("bl:" + pid) or {}).get("part_num") or pid
        got = pc.get("pc:" + rbn)   # (seulement si déjà connues : aucune requête Rebrickable ici — limite de l'API)
        return {str(x["color_id"]): x["image"] for x in got or [] if isinstance(x, dict) and x.get("image")}
    if raw.get("mode") == "exploded":   # toutes les pièces repérées sur la photo, sans les ranger par type
        rows = []
        for n, (z, zd) in enumerate(sorted(zones.items(), key=lambda kv: int(re.sub(r"\D", "", kv[0]) or 0))):
            cands = [{"part": it["id"], "name": it.get("name") or it["id"], "image": image_of(it["id"], it.get("img") or ""), "cimg": cimg_of(it["id"]), "score": it.get("score", 0)}
                     for it in (zd.get("items") or [])[:3]]
            rows.append({"key": z, "label": f"Pièce {n + 1}", "cands": cands, "colors": zone_cols(z)[:3], "thumb": zd.get("thumb", ""),
                         "default": "cand" if cands else "notfound", "low": bool(cands) and cands[0]["score"] < 55, "qty": 1})
        return rows, []
    out, used = [], set()
    for key, label, zs, pat, dflt in REVIEW_SLOTS:
        cands, seen = [], set()
        for z in zs:
            for it in (zones.get(z) or {}).get("items") or []:
                nm = (it.get("name") or "").lower()
                if it["id"] in seen or not (pat and re.search(pat, nm)):
                    continue
                if key == "coiffe" and it["id"].startswith("3626"):
                    continue
                if key in ("dos", "taille") and (re.match(r"(973|970|3626|76382)", it["id"]) or re.search(r"torso|legs|^(minifigure, )?head\b", nm)):
                    continue   # accessoires : jamais un torse, des jambes ou une tête
                seen.add(it["id"])
                cands.append({"part": it["id"], "name": it.get("name") or it["id"], "image": image_of(it["id"], it.get("img") or ""), "cimg": cimg_of(it["id"]), "score": it.get("score", 0)})
        cands.sort(key=lambda c: -c["score"])
        used |= {c["part"] for c in cands[:3]}
        cols = []
        for c in zone_cols(zs[0]):
            if c["color_id"] not in [x["color_id"] for x in cols]:
                cols.append(c)
        if not cands and dflt != "notfound":
            continue   # accessoire non repéré : pas de ligne vide
        out.append({"key": key, "label": label, "cands": cands[:3], "colors": cols[:3],
                    "default": "cand" if cands else dflt, "low": bool(cands) and cands[0]["score"] < 55, "qty": 1})
    # autres pièces repérées (hors emplacements) : à ajouter si besoin
    others, seen = [], set(used)
    for z, zd in zones.items():
        for it in zd.get("items") or []:
            if it["id"] in seen or it.get("score", 0) < (20 if z.startswith("objet") else 40) or re.match(r"(973|970|3626)", it["id"]):
                continue
            if z.startswith("objet") and any(o.get("zone") == z for o in others):
                continue   # un objet séparé = une pièce : sa meilleure proposition seulement
            seen.add(it["id"])
            cc = zone_cols(z)
            others.append({"part": it["id"], "name": it.get("name") or it["id"], "image": image_of(it["id"], it.get("img") or ""), "cimg": cimg_of(it["id"]),
                           "score": it.get("score", 0), "colors": cc[:2], "zone": z})
    others.sort(key=lambda c: -c["score"])
    for n, row in enumerate(out):   # une pièce est une pièce : « Pièce 1, 2… », sans « tête / jambes / mains »
        row["label"] = f"Pièce {n + 1}"
    return out, others[:10]


# ---------------------------------------------------------------- scan d'une minifig MOC (serveur, en tâche de fond)
def _fig_box(im):
    """Cadre de la figurine sur fond clair (calculé sur une miniature)."""
    k = 300 / max(im.size)
    sm = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))))
    px = sm.load()
    x0, y0, x1, y1 = sm.width, sm.height, 0, 0
    for y in range(sm.height):
        for x in range(sm.width):
            r, g, b = px[x, y][:3]
            if r + g + b < 3 * 225 or max(r, g, b) - min(r, g, b) > 30:
                x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
    if x1 <= x0:
        return 0, 0, im.width - 1, im.height - 1
    return int(x0 / k), int(y0 / k), int(x1 / k), int(y1 / k)


def _jpeg(im):
    import io
    b = io.BytesIO()
    im.save(b, "JPEG", quality=92)
    return b.getvalue()


def _scan_one(data, zones_wanted=True):
    """Une photo → {zone: {items, colors}} (+ « entier » : la photo entière)."""
    import io
    from concurrent.futures import ThreadPoolExecutor
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    jobs = {}
    if zones_wanted:
        x0, y0, x1, y1 = _fig_box(im)
        fh, cx = y1 - y0 + 1, (x0 + x1) / 2
        for z, (a, t, c, u) in SCAN_ZONES.items():
            l, tp = max(0, round(cx + a * fh)), max(0, round(y0 + t * fh))
            r, bt = min(im.width, round(cx + c * fh)), min(im.height, round(y0 + u * fh))
            if r - l < 6 or bt - tp < 6:
                continue
            crop = im.crop((l, tp, r, bt))
            k = min(400 / crop.width, 400 / crop.height)
            crop = crop.resize((max(1, round(crop.width * k)), max(1, round(crop.height * k))), Image.LANCZOS)
            canvas = Image.new("RGB", (400, 400), "white")
            canvas.paste(crop, ((400 - crop.width) // 2, (400 - crop.height) // 2))
            jobs[z] = _jpeg(canvas)
    whole = im.copy()
    whole.thumbnail((800, 800))
    jobs["entier"] = _jpeg(whole)

    def ask(item):
        z, data_ = item
        for _ in range(3):
            try:
                found, cols = sources.recognize_part_colors(data_, "image/jpeg", top=5)
                return z, {"items": [{"id": f["number"], "name": f["name"], "img": f["image"], "score": f["score"]} for f in found],
                           "colors": cols}
            except Exception:
                time.sleep(1.5)
        return z, {"items": [], "colors": []}
    with ThreadPoolExecutor(6) as ex:
        return dict(ex.map(ask, jobs.items()))


def scan_fig(main, extras=()):
    """Photo principale (zones) + photos supplémentaires (zones et photo entière), fusionnées par zone."""
    zones = _scan_one(main)
    for k, data in enumerate(extras):
        ez = _scan_one(data)
        for z, zd in ez.items():
            if z == "entier":
                zones[f"extra{k + 1}"] = zd
                continue
            cur = zones.setdefault(z, {"items": [], "colors": []})
            have = {i["id"] for i in cur["items"]}
            cur["items"] = sorted(cur["items"] + [i for i in zd["items"] if i["id"] not in have], key=lambda i: -i["score"])
            if not cur["colors"]:
                cur["colors"] = zd["colors"]
    return zones


def _objects(im, max_objects=16):
    """Pièces posées séparément sur un fond uni : cadres des objets (composantes connexes), du plus grand au plus petit."""
    k = 360 / max(im.size)
    sm = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))))
    W, H = sm.size
    px = sm.load()
    border = [px[x, 0][:3] for x in range(W)] + [px[x, H - 1][:3] for x in range(W)] + [px[0, y][:3] for y in range(H)] + [px[W - 1, y][:3] for y in range(H)]
    bg = tuple(sorted(c[i] for c in border)[len(border) // 2] for i in range(3))   # couleur du fond : médiane des bords
    mask = bytearray(W * H)
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y][:3]
            if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > 60 or max(r, g, b) - min(r, g, b) > 45:
                mask[y * W + x] = 1
    # léger épaississement : une pièce à deux tons ou avec un reflet reste d'un seul tenant
    grown = bytearray(mask)
    for y in range(H):
        for x in range(W):
            if mask[y * W + x]:
                for dy in (-2, -1, 0, 1, 2):
                    for dx in (-2, -1, 0, 1, 2):
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < W and 0 <= yy < H:
                            grown[yy * W + xx] = 1
    seen = bytearray(W * H)
    boxes = []
    for start in range(W * H):
        if not grown[start] or seen[start]:
            continue
        stack, area = [start], 0
        seen[start] = 1
        x0, y0, x1, y1 = W, H, 0, 0
        while stack:
            i = stack.pop()
            x, y = i % W, i // W
            area += 1
            x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
            for j in (i - 1 if x > 0 else -1, i + 1 if x < W - 1 else -1, i - W if y > 0 else -1, i + W if y < H - 1 else -1):
                if j >= 0 and grown[j] and not seen[j]:
                    seen[j] = 1
                    stack.append(j)
        if area >= W * H * 0.002:
            boxes.append((area, x0, y0, x1, y1))
    boxes.sort(reverse=True)
    return [(int(x0 / k), int(y0 / k), int((x1 + 1) / k), int((y1 + 1) / k)) for _, x0, y0, x1, y1 in boxes[:max_objects]]


def scan_exploded(images):
    """Photos des pièces séparées : chaque objet repéré est reconnu seul → liste de toutes les pièces (avec un aperçu)."""
    import base64
    import io
    from concurrent.futures import ThreadPoolExecutor
    from PIL import Image, ImageOps
    crops, thumbs = [], []
    for data in images:
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
        for (x0, y0, x1, y1) in _objects(im):
            m = int(max(x1 - x0, y1 - y0) * 0.08) + 4
            c = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
            kk = min(400 / c.width, 400 / c.height)
            c = c.resize((max(1, round(c.width * kk)), max(1, round(c.height * kk))), Image.LANCZOS)
            canvas = Image.new("RGB", (400, 400), "white")
            canvas.paste(c, ((400 - c.width) // 2, (400 - c.height) // 2))
            crops.append(_jpeg(canvas))
            t = canvas.copy(); t.thumbnail((160, 160))
            thumbs.append("data:image/jpeg;base64," + base64.b64encode(_jpeg(t)).decode())

    def ask(data_):
        for _ in range(3):
            try:
                found, cols = sources.recognize_part_colors(data_, "image/jpeg", top=5)
                return {"items": [{"id": f["number"], "name": f["name"], "img": f["image"], "score": f["score"]} for f in found], "colors": cols}
            except Exception:
                time.sleep(1.5)
        return {"items": [], "colors": []}
    with ThreadPoolExecutor(6) as ex:
        results = list(ex.map(ask, crops))
    return {f"objet{n + 1}": {**r, "thumb": thumbs[n]} for n, r in enumerate(results)}


def _item_photo(it):
    im = str(it.get("image") or "")
    m = re.fullmatch(r"/api/upload/([0-9a-f]{16,40})", im)
    if m:
        for ext in (".jpg", ".png", ".webp"):
            pth = os.path.join(UPLOAD_DIR, m.group(1) + ext)
            if os.path.isfile(pth):
                return open(pth, "rb").read()
    if im.startswith("https://"):
        try:
            return sources.fetch_image(im)[0]
        except Exception:
            return None
    return None


SCAN_TODO_CHECK = "Pièces du scan à valider"   # tâche posée quand un scan est fini mais pas encore validé
SCAN_TODO_MANUAL = "Pièces à ajouter à la main (scan impossible)"   # …quand le scan échoue à chaque fois
SCAN_MAX_FAIL = 3   # essais automatiques (toutes les 3 h) avant de passer la main


def scan_todo(it, note, on):
    """Pose (on) ou retire une tâche « Pièces » du scan sur la fiche d'un MOC (sans toucher à sa date de modification)."""
    ts = [t for t in (it.get("todos") or []) if not (isinstance(t, dict) and t.get("note") == note)]
    if on:
        ts.append({"cat": "Pièces", "note": note})
    it["todos"] = ts
    it["todo"] = bool(ts)
    it["todo_note"] = ts[0]["note"] if ts else ""


def _set_scan_status(iid, status):
    with lock:
        db = load_db()
        it = next((i for i in db["items"] if i["id"] == iid), None)
        if it:
            it["moc_scan"] = status
            if status == "done":   # fini : à valider dans « MOC à valider » (pas de tâche) ; plus d'échec compté
                it.pop("moc_scan_fail", None)
            elif status == "error":   # échec : nouvel essai automatique plus tard (SCAN_MAX_FAIL au plus)
                it["moc_scan_fail"] = int(it.get("moc_scan_fail") or 0) + 1
            _save(DB_FILE, db)


_tmp_scans = {}   # jeton → (heure, zones) : scan de la photo d'une figurine MOC pas encore enregistrée (gardé 2 h)


NOCOLOR_RE = re.compile(r"^Pièce (\S+) : couleur à valider$")


def nocolor_keeper():
    """Une fois par jour : pièces ajoutées sans couleur (tâche « Pièce <réf> : couleur à valider ») — si leurs couleurs sont de
    nouveau connues (Rebrickable), la tâche devient « couleurs disponibles, choisissez-la »."""
    time.sleep(900)
    while True:
        try:
            refs = {m.group(1) for it in load_db()["items"] for t in it.get("todos") or [] if isinstance(t, dict)
                    for m in [NOCOLOR_RE.match(str(t.get("note") or ""))] if m}
            ok = set()
            for pn in sorted(refs)[:60]:
                try:
                    if part_colors(pn):
                        ok.add(pn)
                except Exception:
                    pass
            if ok:
                with lock:
                    db = load_db()
                    for it in db["items"]:
                        for t in it.get("todos") or []:
                            m = NOCOLOR_RE.match(str(t.get("note") or "")) if isinstance(t, dict) else None
                            if m and m.group(1) in ok:
                                t["note"] = f"Pièce {m.group(1)} : couleurs de nouveau disponibles, choisissez la bonne"
                    _save(DB_FILE, db)
        except Exception as e:
            print("Couleurs à valider :", e, flush=True)
        time.sleep(86400)


def moc_scan_retry_keeper():
    """Arrière-plan : les scans de figurines MOC en échec sont relancés toutes les 3 h (SCAN_MAX_FAIL essais au plus)."""
    while True:
        time.sleep(3 * 3600)
        try:
            for it in load_db()["items"]:
                if it.get("kind") == "custom" and it.get("custom_type") == "fig" and it.get("moc_scan") == "error" \
                        and int(it.get("moc_scan_fail") or 0) < SCAN_MAX_FAIL and not it.get("moc_reviewed"):
                    moc_scan_start(it["id"])
        except Exception as e:
            print("Relance des scans :", e, flush=True)


def moc_scan_item(iid, extras=(), mode="assembled", append=False):
    """Scanne la photo d'une minifig MOC (+ photos supplémentaires, non gardées) et garde les propositions."""
    it = next((i for i in load_db()["items"] if i["id"] == iid), None)
    if not it or it.get("kind") != "custom":
        return False
    if it.get("custom_type") != "fig" and not extras:
        return False   # set MOC : seulement des photos de pièces séparées
    if it.get("custom_type") != "fig":
        mode = "exploded"
    stored = _item_photo(it)
    if not stored and not extras:
        _set_scan_status(iid, "nophoto")
        return False
    # photos données pour le scan : la première sert de base (souvent en HD) ; la photo du MOC complète, sans être remplacée
    main, others = (extras[0], list(extras[1:]) + ([stored] if stored else [])) if extras else (stored, [])
    _set_scan_status(iid, "running")
    try:
        zones = scan_exploded(list(extras)) if extras and mode == "exploded" else scan_fig(main, others)
        prev = (_load(REVIEW_FILE, {}).get(iid) or {})
        if append and mode == "exploded" and prev.get("mode") == "exploded":   # nouvelles photos : pièces ajoutées à la suite
            start = len(prev.get("zones") or {})
            zones = {**prev["zones"], **{f"objet{start + n + 1}": z for n, z in enumerate(zones.values())}}
    except Exception as e:
        print("Scan MOC impossible :", e, flush=True)
        _set_scan_status(iid, "error")
        return False
    cur = next((i for i in load_db()["items"] if i["id"] == iid), None)
    if not cur or cur.get("moc_scan") == "cancelled":   # annulé entre-temps
        return False
    with lock:
        raw = _load(REVIEW_FILE, {})
        raw[iid] = {"zones": zones, "t": int(time.time()), "extras": len(extras), "image": it.get("image"), "mode": mode if extras else "assembled"}
        _save(REVIEW_FILE, raw)
    _set_scan_status(iid, "done")
    return True


_scan_queue, _scan_busy = [], [False]


def moc_scan_start(iid):
    """Scan en tâche de fond (une file)."""
    with lock:
        if iid not in _scan_queue:
            _scan_queue.append(iid)
        if _scan_busy[0]:
            return
        _scan_busy[0] = True

    def run():
        try:
            while True:
                with lock:
                    if not _scan_queue:
                        _scan_busy[0] = False
                        return
                    i = _scan_queue.pop(0)
                moc_scan_item(i)
        finally:
            _scan_busy[0] = False
    threading.Thread(target=run, daemon=True).start()


_rv_img_busy = [False]


def review_images_fill(figs):
    """Arrière-plan : image Rebrickable de chaque pièce proposée (une requête par seconde, gardée en cache)."""
    ids = list(dict.fromkeys([c["part"] for f in figs for sl in f["slots"] for c in sl["cands"]] + [o["part"] for f in figs for o in f.get("others") or []]))
    pc = _parts_cache()
    todo = [i for i in ids if "bl:" + i not in pc]
    todo += [i + "c01" for i in ids if re.fullmatch(r"973pb\d+", i) and pc.get("bl:" + i) is None and "bl:" + i + "c01" not in pc]
    if not todo or _rv_img_busy[0]:
        return
    _rv_img_busy[0] = True

    def run():
        try:
            for i in todo:
                cached_part_from_bricklink(i)
        finally:
            _rv_img_busy[0] = False
    threading.Thread(target=run, daemon=True).start()


def review_fig(it, raw, names=None):
    r = raw.get(it["id"]) or {}
    slots, others = review_slots(r) if r else ([], [])
    return {"id": it["id"], "name": it.get("custom_name") or "Sans nom", "image": it.get("image") or "", "list": (names or {}).get(it["list_id"], ""),
            "analysed": bool(r), "t": r.get("t", 0), "scan": it.get("moc_scan") or ("done" if r else ""), "mode": r.get("mode", "assembled"),
            "type": "fig" if it.get("custom_type") == "fig" else "set",
            "slots": slots, "others": others}


def review_pending():
    db = load_db()
    raw = _load(REVIEW_FILE, {})
    kinds = list_kinds(db)
    names = {l["id"]: l["name"] for l in db["lists"]}
    return [review_fig(it, raw, names) for it in db["items"]
            if it.get("kind") == "custom" and kinds.get(it["list_id"]) == "collection"
            and (it.get("moc_scan") in ("done", "running") or (it.get("custom_type") == "fig" and not it.get("moc_parts") and not it.get("moc_reviewed")))]


_moc_queue, _moc_busy = [], [False]


def fig_swaps_scale(swaps, n, m):
    """Pièces échangées d'un lot de n figurines → pour un lot de m (chaque figurine pareille). None si le lot n'est pas uniforme."""
    out = []
    for x in swaps or []:
        y = json.loads(json.dumps(x))
        for side in ("orig", "new"):
            if y.get(side):
                q = int(y[side].get("qty") or 1)
                if q % max(1, n):
                    return None
                y[side]["qty"] = q // max(1, n) * max(1, m)
        out.append(y)
    return out


def fig_swaps_sig(swaps, n):
    """Signature des pièces échangées d'un lot de n figurines, ramenée à UNE figurine (pour comparer deux lots)."""
    n = max(1, int(n or 1))
    k = lambda x: (x.get("part"), x.get("color_id"), round(int(x.get("qty") or 1) / n, 4)) if x else None
    return sorted(json.dumps([k(x.get("orig")), k(x.get("new"))]) for x in swaps or [] if not x.get("free"))



def fig_absorb(db, it):
    """Figurine seule « it » : si une AUTRE fiche seule identique existe dans la même liste, it la rejoint (quantités additionnées, pièces
    échangées ramenées au nouveau total) et disparaît. Rend la fiche qui reste. Ne fusionne jamais une fiche qui a quelque chose à elle."""
    if not it or it.get("kind") != "fig" or it.get("attached_to") or it.get("set_orig"):
        return it
    plain = lambda x: not (x.get("notes") or x.get("todos") or x.get("accessories") or x.get("alt_photos") or x.get("indiv") or x.get("as_set") or x.get("dup_pending"))
    q = lambda x: max(1, int(x.get("quantity", 1) or 1))
    key = lambda x: (x.get("number"), x.get("list_id"), x.get("display_name") or "", x.get("photo_url") or "", x.get("condition") or "", json.dumps(fig_swaps_sig(x.get("fig_swaps"), q(x))))
    if not plain(it):
        return it
    twin = next((x for x in db["items"] if x is not it and x.get("kind") == "fig" and not x.get("attached_to") and not x.get("set_orig") and plain(x) and key(x) == key(it)), None)
    if not twin:
        return it
    tot = q(twin) + q(it)
    if twin.get("fig_swaps"):
        sw = fig_swaps_scale(twin["fig_swaps"], q(twin), tot)
        if sw is None:   # (lot non uniforme : on ne mélange pas)
            return it
        twin["fig_swaps"], twin["swap_price"] = sw, {"delta": 0, "done": False}
    twin["quantity"], twin["updated_at"] = tot, int(time.time())
    db["items"] = [x for x in db["items"] if x is not it]
    return twin


def fig_msig(it, host=None):
    """Signature courte des modifications d'une figurine (page publique : regrouper les exemplaires identiques, comme mergeFigs de l'appli).
    Figurine d'origine : ses modifications sont sur le set (fig_mods). Variante (indiv) : une signature à elle seule."""
    if it.get("indiv"):
        return "v:" + it["id"]
    m = ((host or {}).get("fig_mods") or {}).get(it.get("number")) or {} if it.get("set_orig") else it
    raw = json.dumps([fig_swaps_sig(m.get("fig_swaps"), it.get("quantity", 1)), len(m.get("accessories") or [])])
    return hashlib.sha1(raw.encode()).hexdigest()[:10]


def fig_share_swaps(db, src_id, fid, swaps, rb, prev=None):
    """Modifications partagées (17/11) : les pièces échangées d'une figurine (src_id ; fid : figurine d'un set) recopiées sur tous ses autres
    exemplaires de la collection — même référence, même nom, pas une variante (indiv). Rend les fiches touchées (à rechiffrer)."""
    cache = _load(CACHE_FILE, {})
    kinds = list_kinds(db)
    src = next((i for i in db["items"] if i["id"] == src_id), None)
    if not src:
        return []
    if fid:
        ref, name = fid, str(((src.get("fig_mods") or {}).get(fid) or {}).get("name") or "")
        mfs = (cache.get(src.get("number")) or {}).get("minifigs") or []
        n = (fig_have(src, mfs) if src.get("with_minifigs") is not False else {}).get(fid, 0)
    else:
        if src.get("indiv"):
            return []   # (variante : ses modifications restent à elle)
        ref, name, n = src.get("number"), str(src.get("display_name") or ""), max(1, int(src.get("quantity", 1) or 1))
    if not ref or n < 1 or (swaps and fig_swaps_scale(swaps, n, n) is None):
        return []
    before = fig_swaps_sig(prev, n)   # (seuls les exemplaires qui avaient exactement ces modifications suivent : rien d'autre n'est écrasé)
    touched = []
    for t in db["items"]:
        if t["id"] == src_id or kinds.get(t.get("list_id")) != "collection":
            continue
        if t.get("kind", "set") == "set":
            mfs = (cache.get(t.get("number")) or {}).get("minifigs") or []
            if t.get("with_minifigs") is False or not any(f.get("id") == ref for f in mfs):
                continue
            c = fig_have(t, mfs).get(ref, 0)
            mo = (t.get("fig_mods") or {}).get(ref) or {}
            if c < 1 or str(mo.get("name") or "") != name or fig_swaps_sig(mo.get("fig_swaps"), c) != before:
                continue
            new = fig_swaps_scale(swaps, n, c) if swaps else []
            if new is None:
                continue
            mo = t.setdefault("fig_mods", {}).setdefault(ref, {})
            if new:
                mo["fig_swaps"], mo["swap_price"] = new, {"delta": 0, "done": False}
            else:
                mo.pop("fig_swaps", None); mo.pop("swap_price", None)
            if rb:
                mo["rb_fig"] = rb
            t["fig_mods"] = {k: v for k, v in t["fig_mods"].items() if v}
            if not t["fig_mods"]:
                t.pop("fig_mods", None)
            touched.append(t["id"])
        elif t.get("kind") == "fig" and t.get("number") == ref and not t.get("set_orig") and not t.get("indiv") and str(t.get("display_name") or "") == name:
            m_ = max(1, int(t.get("quantity", 1) or 1))
            if fig_swaps_sig(t.get("fig_swaps"), m_) != before:   # modifiée autrement : on n'y touche pas
                continue
            new = fig_swaps_scale(swaps, n, m_) if swaps else []
            if new is None:
                continue
            if new:
                t["fig_swaps"], t["swap_price"] = new, {"delta": 0, "done": False}
            else:
                t.pop("fig_swaps", None); t.pop("swap_price", None)
            if rb:
                t["rb_fig"] = rb
            t["updated_at"] = int(time.time())
            touched.append(t["id"])
    return touched


def moc_price_start(item_id, front=False):
    """Chiffre les pièces d'un MOC en arrière-plan (une file, une requête BrickOwl à la fois)."""
    with lock:
        if item_id not in _moc_queue:   # petites listes (minifigs) en tête de file
            _moc_queue.insert(0, item_id) if front else _moc_queue.append(item_id)
        if _moc_busy[0]:
            return
        _moc_busy[0] = True

    def run():
        try:
            while True:
                with lock:
                    if not _moc_queue:
                        _moc_busy[0] = False
                        return
                    iid = _moc_queue.pop(0)
                try:
                    _moc_price_item(iid)
                    _swap_price_item(iid)
                except Exception as e:
                    print("Chiffrage MOC impossible :", e, flush=True)
        finally:
            _moc_busy[0] = False
    threading.Thread(target=run, daemon=True).start()


MOC_REPRICE = 7 * 86400   # un MOC est rechiffré chaque semaine : sa courbe se construit au fil du temps


def moc_hist_add(it, total, day=None):
    """Historique de la valeur d'un MOC (prix de ses pièces) : [[date, total], …], un point par jour."""
    day = day or time.strftime("%Y-%m-%d")
    h = [x for x in (it.get("value_hist") or []) if x[0] != day]
    h.append([day, total])
    it["value_hist"] = sorted(h)[-400:]


def moc_reprice_loop():
    """Arrière-plan : chaque jour, rechiffre les MOC dont le dernier chiffrage date d'une semaine.
    Au démarrage : les sets partiels chiffrés avant la reconnaissance des assemblages montés (pas de clé « asm »)."""
    try:
        for it in load_db()["items"]:
            if it.get("partial_set") and it.get("moc_parts") and "asm" not in (it.get("moc_price") or {}):
                moc_price_start(it["id"])
    except Exception as e:
        print("Rechiffrage des sets partiels impossible :", e, flush=True)
    while True:
        try:
            for it in load_db()["items"]:
                mp = it.get("moc_price") or {}
                if it.get("moc_parts") and mp.get("done") and time.time() - (mp.get("t") or 0) > MOC_REPRICE:
                    moc_price_start(it["id"])
        except Exception as e:
            print("Rechiffrage des MOC impossible :", e, flush=True)
        time.sleep(86400)


def touch_for_fig(host, fid=None):
    """Une figurine rangée dans ce set vient d'être modifiée (nom, photo, pièces, accessoires, rattachement) :
    la version du set change (updated_at : détection des conflits d'enregistrement), mais pas sa place dans
    « Dernière modification » — seule la figurine remonte (fig_at[figurine] = maintenant).
    own_at = la dernière modification du set lui-même ; fig_touch = celle d'une de ses figurines (= updated_at tant que
    rien d'autre n'a touché le set ; le tri lit alors own_at)."""
    now = int(time.time())
    if not host.get("fig_touch") or host["fig_touch"] != host.get("updated_at"):   # la dernière date était celle du set lui-même : on la garde
        host["own_at"] = host.get("updated_at") or host.get("added_at") or 0
    host["updated_at"] = host["fig_touch"] = now
    if fid and fid != "#set":
        host["fig_at"] = {**(host.get("fig_at") or {}), str(fid)[:40]: now}


def move_linked(db, lead_ids, target, quiet_fig=None, touch_lead=True, prev=None):   # prev : {id: liste d'avant} (fiche déjà changée par un PUT)
    """Déplacement vers la liste « target » : les fiches reliées suivent — le set qui contient une fiche rangée
    (attached_to), et tout ce qui est rangé dans un set déplacé (figurines, MOC rattachés).
    lead_ids : les fiches déplacées par l'utilisateur (elles remontent dans « Dernière modification ») ;
    les autres suivent sans remonter. quiet_fig : figurine d'un set (sans fiche à elle) à l'origine du déplacement :
    son set suit sans remonter, seule elle remonte. touch_lead=False : la date de la fiche est déjà à jour (PUT).
    Rend le nombre de fiches déplacées."""
    by_id = {i["id"]: i for i in db["items"]}
    grp = {x for x in lead_ids if x in by_id}
    _kd = list_kinds(db)
    for x in list(grp):   # fiche RANGÉE déplacée seule vers une autre sorte de liste que son set (collection ↔ souhaits) : elle quitte son set
        _h = by_id.get(by_id[x].get("attached_to"))
        if _h and _h["id"] not in grp and _kd.get(_h.get("list_id"), "collection") != _kd.get(target, "collection"):
            if by_id[x].get("set_orig"):
                orig_fig_leaves(db, by_id[x])   # (figurine d'origine : déduite de son set, ses personnalisations la suivent)
            by_id[x].pop("attached_to", None)
    lists0 = {x: (prev or {}).get(x, by_id[x].get("list_id")) for x in grp}   # (listes avant le déplacement)
    att = {i["id"] for i in db["items"] if i.get("attached_to") in lists0 and i.get("list_id") == lists0[i["attached_to"]]}   # un set déplacé emmène ses figurines… de la même liste seulement
    if list_kinds(db).get(target, "collection") != "collection":   # set parti en souhaits / à commander : les figurines ajoutées que je possède restent dans ma collection, sorties du set
        for x in list(att):
            if not by_id[x].get("set_orig") and x not in lead_ids:
                by_id[x].pop("attached_to", None)
                by_id[x]["updated_at"] = int(time.time())
                att.discard(x)
    grp |= att
    n = 0
    for x in grp:
        it, lead = by_id[x], x in lead_ids
        if not lead and it.get("list_id") == target:
            continue
        it["list_id"] = target
        n += 1
        if lead and quiet_fig:
            touch_for_fig(it, quiet_fig)
        elif lead:
            if touch_lead:
                it["updated_at"] = int(time.time())
        else:
            touch_for_fig(it)   # suit : garde sa place dans « Dernière modification »
    return n


FIG_CUSTOM = ("display_name", "photo_url", "fig_swaps", "swap_price", "accessories", "alt_photos", "alt_names", "alt_hidden", "main_name", "rb_fig")   # personnalisations d'une figurine


def orig_figs_sync(db, host, cache=None):
    """Les figurines d'origine d'un set converti (fig_items) = autant de fiches (kind fig, attached_to, set_orig) qu'il y en a
    dans le set (fig_have : fig_counts / manquantes / « sans figurines »). Créées, mises à jour (quantité, liste, état) ou
    retirées. Leurs personnalisations restent dans le set (fig_mods) : rien n'est perdu quand une figurine disparaît du set."""
    if host.get("kind", "set") != "set" or not host.get("fig_items"):
        return
    origs = [i for i in db["items"] if i.get("attached_to") == host["id"] and i.get("set_orig")]
    if list_kinds(db).get(host.get("list_id")) != "collection":   # (liste de souhaits : pas de figurines possédées)
        for o in origs:
            db["items"].remove(o)
        return
    cache = cache if cache is not None else _load(CACHE_FILE, {})
    mfs = (cache.get(host["number"]) or {}).get("minifigs") or []
    have = fig_have(host, mfs) if host.get("with_minifigs", True) else {}
    by = {}
    for o in origs:
        by.setdefault(o["number"], []).append(o)
    now = int(time.time())
    for f in mfs:
        q, lst = have.get(f["id"], 0), by.pop(f["id"], [])
        if q > 0 and lst:
            lst[0].update(quantity=q, condition=host.get("condition") or "occasion")   # (sa liste à elle : elle peut différer de celle du set)
            for extra in lst[1:]:
                db["items"].remove(extra)
        elif q > 0:
            it = Handler.clean_item({"kind": "fig", "number": f["id"], "list_id": host["list_id"], "quantity": q, "attached_to": host["id"],
                                     "set_orig": True, "condition": host.get("condition") or "occasion"})
            it.update(id=uuid.uuid4().hex[:12], added_at=host.get("added_at") or now,
                      updated_at=(host.get("fig_at") or {}).get(f["id"]) or host.get("added_at") or now)
            db["items"].append(it)
        else:
            for o in lst:
                db["items"].remove(o)
    for lst in by.values():   # plus dans la liste des figurines du set
        for o in lst:
            db["items"].remove(o)


def set_figs_sheets(db, host, cache=None):
    """Un set de la collection a les fiches de ses figurines d'origine (créées au besoin, comme à son ajout) ; hors de la collection
    (liste de souhaits) il n'en a pas. À appeler quand un set change de liste, de numéro ou de type — sans attendre le redémarrage."""
    if host.get("kind", "set") != "set":
        return
    cache = cache if cache is not None else _load(CACHE_FILE, {})
    if not host.get("fig_items") and list_kinds(db).get(host.get("list_id")) == "collection" and (cache.get(host.get("number")) or {}).get("minifigs"):
        host["fig_items"] = True
    orig_figs_sync(db, host, cache)


def swaps_split(swaps, price, n, tot):
    """Pièces échangées d'un lot de « tot » figurines (quantités pour le lot entier) : la part de « n » d'entre elles, et ce qui reste.
    → (part, reste, prix_part, prix_reste). Un échange qui tombe à 0 disparaît."""
    import copy as _c
    take, rest = [], []
    for s in swaps or []:
        q = int(((s.get("orig") or s.get("new") or {}).get("qty")) or 1)
        a = min(q, max(0, round(q * n / tot)))
        for lst, qq in ((take, a), (rest, q - a)):
            if qq > 0:
                x = _c.deepcopy(s)
                for side in ("orig", "new"):
                    if isinstance(x.get(side), dict) and x[side].get("qty") is not None:
                        x[side]["qty"] = qq
                lst.append(x)
    p1 = p2 = None
    if isinstance(price, dict):
        d = float(price.get("delta") or 0)
        p1, p2 = {**price, "delta": round(d * n / tot, 2)}, {**price, "delta": round(d - d * n / tot, 2)}
    return take, rest, p1, p2


INDIV_KEYS = ("fig_swaps", "photo_url", "display_name", "accessories", "alt_photos", "todos")   # ce qui distingue une figurine mise à part


def indiv_rejoin(db, it):
    """« Dupliquer puis modifier » : la fiche à part enregistrée SANS rien de différent (ni pièces, ni photo, nom, accessoires, apparences) rejoint
    les autres — une fiche ajoutée identique du même set, sinon le compte du set (fig_counts). Rend True si elle a rejoint (fiche retirée)."""
    if not it.get("indiv") or it.get("kind") != "fig" or not it.get("attached_to"):
        return False
    if it.get("indiv_copy") is not None:   # copie d'une ORIGINALE (« Dupliquer puis modifier ») : pas modifiée → elle disparaît (le set n'a pas changé)
        if {k: it[k] for k in INDIV_KEYS if it.get(k)} == it["indiv_copy"]:
            db["items"].remove(it)
            return True
        it.pop("indiv_copy", None)   # modifiée : une figurine ajoutée à part entière
        return False
    if any(it.get(k) for k in INDIV_KEYS):
        return False   # elle diffère : séparée
    host = next((i for i in db["items"] if i["id"] == it["attached_to"]), None)
    if not host:
        return False
    q = int(it.get("quantity", 1) or 1)
    same = next((x for x in db["items"] if x is not it and x.get("attached_to") == host["id"] and x.get("kind") == "fig" and not x.get("set_orig")
                 and x.get("number") == it.get("number") and x.get("list_id") == it.get("list_id") and not x.get("dup_pending")
                 and not any(x.get(k) for k in ("fig_swaps", "photo_url", "display_name", "accessories", "alt_photos"))), None)
    if same:
        same["quantity"] = int(same.get("quantity", 1) or 1) + q
    elif host.get("kind", "set") == "set":
        cache = _load(CACHE_FILE, {})
        mfs = (cache.get(host["number"]) or {}).get("minifigs") or []
        if not any(f["id"] == it.get("number") for f in mfs):
            return False
        have = fig_have(host, mfs)
        have[it["number"]] = have.get(it["number"], 0) + q
        host["fig_counts"], host["missing_minifigs"] = have, []
        db["items"].remove(it)
        orig_figs_sync(db, host, cache)
        return True
    else:
        return False
    db["items"].remove(it)
    return True


def orig_fig_free(host, fig):
    """Figurine d'origine qui redevient une fiche ordinaire parce que son set change de nature (set MOC, set partiel) : la marque
    « d'origine » est retirée et ses personnalisations, gardées dans le set (fig_mods), sont copiées sur elle."""
    fig.pop("set_orig", None)
    m = ((host or {}).get("fig_mods") or {}).get(fig.get("number")) or {}
    for k in FIG_CUSTOM:
        v = m.get("name" if k == "display_name" else k)
        if v and not fig.get(k):
            fig[k] = v


def orig_fig_leaves(db, fig, to_set=None):
    """Une figurine d'origine quitte son set (sortie, ou rattachée à un autre set) : elle devient indépendante — ses
    personnalisations sont copiées sur elle — et le set la déduit (fig_counts)."""
    host = next((i for i in db["items"] if i["id"] == fig.get("attached_to")), None)
    fig.pop("set_orig", None)
    if not host:
        return
    m = (host.get("fig_mods") or {}).get(fig["number"]) or {}
    for k, v in (("display_name", m.get("name")), ("photo_url", m.get("photo_url")), ("fig_swaps", m.get("fig_swaps")),
                 ("swap_price", m.get("swap_price")), ("accessories", m.get("accessories")), ("alt_photos", m.get("alt_photos")),
                 ("alt_names", m.get("alt_names")), ("alt_hidden", m.get("alt_hidden")), ("main_name", m.get("main_name")), ("rb_fig", m.get("rb_fig"))):
        if v and not fig.get(k):
            fig[k] = v
    mfs = (_load(CACHE_FILE, {}).get(host["number"]) or {}).get("minifigs") or []
    have = fig_have(host, mfs)
    have[fig["number"]] = max(0, have.get(fig["number"], 0) - int(fig.get("quantity", 1) or 1))
    host["fig_counts"], host["missing_minifigs"] = have, []
    if not have[fig["number"]]:
        (host.get("fig_mods") or {}).pop(fig["number"], None)
    host["updated_at"] = int(time.time())


def items_removed(db, ids):
    """Fiches retirées. Un set retiré ne touche JAMAIS à ses figurines (20/11) : celles d'origine deviennent des fiches indépendantes,
    avec ce que le set gardait pour elles (photo, nom, pièces échangées…) ; celles ajoutées restent, seules. Une figurine d'origine
    retirée seule est déduite de son set (« je ne l'ai pas »)."""
    ids = set(ids)
    for f in [i for i in db["items"] if i.get("set_orig") and i.get("attached_to") in ids and i["id"] not in ids]:
        orig_fig_leaves(db, f)   # (ses personnalisations copiées sur elle ; plus « d'origine »)
        f.pop("attached_to", None)
        f["updated_at"] = int(time.time())
    for f in [i for i in db["items"] if i["id"] in ids and i.get("set_orig") and i.get("attached_to") not in ids]:
        host = next((i for i in db["items"] if i["id"] == f.get("attached_to")), None)
        if host:
            mfs = (_load(CACHE_FILE, {}).get(host["number"]) or {}).get("minifigs") or []
            have = fig_have(host, mfs)
            have[f["number"]] = max(0, have.get(f["number"], 0) - int(f.get("quantity", 1) or 1))
            host["fig_counts"], host["missing_minifigs"] = have, []
    for x in db["items"]:   # figurines AJOUTÉES dans un set retiré : elles restent, seules (jamais de lien vers une fiche disparue)
        if x.get("attached_to") in ids and x["id"] not in ids:
            x.pop("attached_to", None)
            x["updated_at"] = int(time.time())
    db["items"] = [i for i in db["items"] if i["id"] not in ids]


def orig_figs_convert_all():
    """Au démarrage : les figurines des sets deviennent des fiches (sets pas encore convertis, figurines connues), et les sets
    déjà convertis sont resynchronisés (ex. la démo, copiée sans les fiches de figurines). Sauvegarde avant, s'il y a un changement."""
    with lock:
        db = load_db()
        before = json.dumps(db["items"], sort_keys=True)
        kinds, cache = list_kinds(db), _load(CACHE_FILE, {})
        n = 0
        for host in [i for i in db["items"] if i.get("kind", "set") == "set" and kinds.get(i.get("list_id")) == "collection"]:
            if not host.get("fig_items"):
                if not (cache.get(host["number"]) or {}).get("minifigs"):
                    continue
                host["fig_items"] = True
                n += 1
            orig_figs_sync(db, host, cache)
        if json.dumps(db["items"], sort_keys=True) == before:
            return 0
        backup_db("avant-figurines-fiches")
        _save(DB_FILE, db)
        return n or 1


def bl_set_assemblies(set_no):
    """Assemblages d'un set selon son inventaire BrickLink (« counterparts » : un animal, un dinosaure… vendu monté,
    ex. trex02, le T-Rex du set 5886) → [{"no", "color", "name", "parts": {pièce BrickLink: quantité}}].
    Gardé 30 jours (1 appel pour le set + 1 par assemblage ; API officielle)."""
    import html as _html
    key = "ba:" + set_no
    c = _parts_cache().get(key)
    if c and time.time() - c.get("t", 0) < 36500 * 86400:   # (un set ne change pas)
        return c["list"]
    out = []
    for g in sources.bl_get(f"/items/SET/{urllib.parse.quote(set_no)}/subsets", {"break_minifigs": "false"}) or []:
        for e in g.get("entries") or []:
            itm = e.get("item") or {}
            if not e.get("is_counterpart") or itm.get("type") != "PART" or not itm.get("no"):
                continue
            comp = {}   # ses pièces (inventaire BrickLink de l'assemblage)
            for g2 in sources.bl_get(f"/items/PART/{urllib.parse.quote(itm['no'])}/subsets") or []:
                for e2 in g2.get("entries") or []:
                    n = (e2.get("item") or {}).get("no")
                    if n:
                        comp[n] = comp.get(n, 0) + int(e2.get("quantity") or 1)
            if comp:
                out.append({"no": itm["no"], "color": str(e.get("color_id") or 0), "name": _html.unescape(itm.get("name") or itm["no"]), "parts": comp})
    _parts_cache_put(key, {"list": out, "t": int(time.time())})
    return out


def moc_assemblies(set_no, lots):
    """Pièces d'un set partiel qui forment un assemblage complet (ex. les 8 pièces du T-Rex) : chiffrées au prix de
    l'assemblage monté sur BrickLink (moyenne des annonces d'occasion), réparti entre elles — au prorata du prix connu
    de chaque pièce seule, sinon à parts égales. Les pièces sont reconnues par leur référence (la couleur peut différer
    entre Rebrickable et BrickLink : le corps du T-Rex est « rouge foncé » chez l'un, « orange foncé » chez l'autre).
    Rend ({n° de lot: {"qty": pièces comptées, "value": valeur}}, [{"no", "name", "n", "unit", "lots"}])."""
    by_part, pc = {}, _parts_cache()
    for k, l in enumerate(lots):
        by_part.setdefault(str(l.get("part") or ""), []).append(k)
    out, found = {}, []
    for a in bl_set_assemblies(set_no):
        need = a["parts"]
        free = {p: sum(lots[k].get("qty", 1) - out.get(k, {}).get("qty", 0) for k in by_part.get(p, [])) for p in need}
        n = min(free[p] // q for p, q in need.items())   # nombre d'assemblages complets
        if n < 1:
            continue
        try:
            u = bp_unit(bl_part(a["no"], a["color"]))   # gardé dans « bp: » (relu par la passe de nuit)
        except Exception:   # pas de codes BrickLink, quota, réseau : le dernier relevé s'il y en a un
            u = bp_unit(pc.get(f"bp:{a['no']}|{a['color']}"))
        if not u:
            continue
        w = {}
        for p, q in need.items():   # poids : prix connu de la pièce seule
            l0 = lots[by_part[p][0]]
            blc = bo_bl_color(l0.get("color"))
            w[p] = (bp_unit(pc.get(f"bp:{p}|{blc}")) or (pc.get(f"mp:{p}|{l0.get('color')}") or {}).get("unit") or 0) * q
        if not all(w.values()):   # un prix manque : parts égales (par pièce)
            w = dict(need)
        tot, ks = sum(w.values()), []
        for p, q in need.items():
            left, val = q * n, u * n * w[p] / tot
            for k in by_part[p]:
                take = min(lots[k].get("qty", 1) - out.get(k, {}).get("qty", 0), left)
                if take <= 0:
                    continue
                e = out.setdefault(k, {"qty": 0, "value": 0.0})
                e["qty"] += take
                e["value"] += val * take / (q * n)
                left -= take
                ks.append(k)
                if left <= 0:
                    break
        found.append({"no": a["no"], "name": a["name"], "n": n, "unit": u, "lots": sorted(set(ks))})
    return out, found


def _moc_price_item(iid):
    it = next((i for i in load_db()["items"] if i["id"] == iid), None)
    lots = (it or {}).get("moc_parts") or []
    if not lots:
        return
    total, priced, missing, approx = 0.0, 0, 0, []
    units = []
    asm, asm_found = {}, []   # set partiel : pièces d'un assemblage monté (T-Rex…) → prix de l'assemblage
    if (it or {}).get("partial_set") and it.get("number"):
        try:
            asm, asm_found = moc_assemblies(it["number"], lots)
        except Exception as e:   # pas de codes BrickLink, quota, réseau : chiffrage pièce par pièce
            print("Assemblages BrickLink indisponibles :", e, flush=True)

    def store(done):
        with lock:
            db = load_db()
            cur = next((i for i in db["items"] if i["id"] == iid), None)
            if not cur or cur.get("moc_parts") != lots:   # supprimé ou liste remplacée entre-temps
                return False
            cur["moc_price"] = {"total": round(total, 2), "priced": priced, "missing": missing, "lots": len(lots), "approx": approx,
                                "done": done, "t": int(time.time()), **({"units": units} if len(lots) <= 80 else {}),
                                **({"asm": [{**x, "unit": round(x["unit"], 2)} for x in asm_found]} if cur.get("partial_set") else {})}
            if done and priced:
                moc_hist_add(cur, round(total, 2))
            _save(DB_FILE, db)
        return True

    def single(lot):   # prix d'une pièce seule : relevé (BrickLink, BrickOwl), sinon mon prix, sinon pièces semblables → (prix, estimé ?)
        u, ap = lot_price(lot["part"], lot["color"]), False
        if u:   # prix invraisemblable (marché mince) : celui des pièces semblables
            pn = (_parts_cache().get("bl:" + lot["part"]) or {}).get("part_num") or lot["part"]
            u2, bad = sane_unit(pn, lot.get("color_id"), u, (_parts_cache().get(f"mp:{lot['part']}|{lot['color']}") or {}).get("offers"), bl_price_known(lot["part"], lot["color"]))
            if bad:
                u, ap = u2, True
        if not u:   # introuvable : mon prix, si j'en ai mis un, sinon calqué sur les pièces qui lui ressemblent
            u = manual_price(None, lot.get("color_id"), lot["part"], lot["color"])
        if not u:
            u = similar_unit_bl(lot["part"], lot["color"])
            ap = bool(u)
        return u, ap

    for k, lot in enumerate(lots):
        a, q = asm.get(k), lot.get("qty", 1)
        if a and a["qty"] >= q:   # toute la ligne est dans un assemblage monté
            u = a["value"] / q
        else:
            u, ap = single(lot)
            if a:   # pièces en plus de l'assemblage : au prix d'une pièce seule
                u = (a["value"] + (u or 0) * (q - a["qty"])) / q
            if ap:
                approx.append(k)
        units.append(u)
        if u:
            total += u * lot["qty"]
            priced += 1
        else:
            missing += 1
        if k % 10 == 9 and not store(False):
            return
    store(True)


def enrich(item, cache=None, kinds=None):
    """Fiche prête à afficher (valeur, infos du catalogue). Figurine d'origine d'un set : son prix est affiché (own_total),
    mais compté dans la cote du set (total_value 0 : jamais deux fois)."""
    out = _enrich(item, cache, kinds)
    try:   # accessoires avec une liste de pièces : leur valeur s'ajoute à celle de la fiche (une fois)
        av = acc_annotate(out, item)
        if av:
            out["acc_value"] = av
            out["total_value"] = round((out.get("total_value") or 0) + av, 2)
            out.pop("no_estimate", None)
    except Exception as e:
        print("Prix des accessoires :", e, flush=True)
    if item.get("set_orig") and item.get("attached_to"):
        out["own_total"] = out.get("total_value") or 0
        out["own_unit"] = out.get("unit_value") or 0
        out["total_value"] = 0
        out["in_set"] = True
    return out


def _enrich(item, cache=None, kinds=None):
    if cache is None:
        cache = _load(CACHE_FILE, {})
    if kinds is None:
        kinds = list_kinds()
    if item.get("kind") == "part":   # pièce à commander : pas d'estimation
        out = dict(item)
        out.update(unit_value=0, total_value=0, no_estimate=True,
                   info={"name": item.get("part_name") or item.get("part_num"), "image": item.get("image")},
                   color_fr=FR_COLORS.get(item.get("color_name") or "", item.get("color_name")))
        return out
    if item.get("kind") == "custom":   # MOC : estimé par ses pièces si une liste a été importée, sinon pas d'estimation
        out = dict(item)
        out.pop("moc_parts", None)   # liste complète inutile côté interface
        mp = item.get("moc_price") or {}
        lots = item.get("moc_parts") or []
        out["moc_info"] = {"lots": len(lots), "pieces": sum(x.get("qty", 1) for x in lots), **mp} if lots else None
        if out["moc_info"]:
            out["moc_info"].pop("units", None)
        if item.get("custom_type") == "fig":   # minifig MOC : ses pièces, avec leur prix
            un, ap = mp.get("units") or [], set(mp.get("approx") or [])
            out["moc_lots"] = [{**x, "unit": un[k] if k < len(un) else None, **({"approx": True} if k in ap else {})} for k, x in enumerate(lots)]
        if out["moc_info"]:
            out["moc_info"]["approx"] = len(mp.get("approx") or [])
            out["approx"] = bool(mp.get("approx") or mp.get("missing"))   # MOC pas chiffré à 100 % : « ~ » devant son prix
        unit = mp.get("total") if lots and mp.get("priced") else None   # set ou minifig MOC
        out.update(unit_value=round(unit or 0, 2), total_value=round((unit or 0) * item.get("quantity", 1), 2), no_estimate=unit is None,
                   info={"name": item.get("custom_name") or "Sans nom", "image": item.get("image"),
                         "pieces": sum(x.get("qty", 1) for x in lots) if lots else None,
                         **({"year": item.get("year")} if item.get("catalog_set") else {}),
                         **({"set_minifigs": [m.get("id") for m in (cache.get(item.get("number") or "") or {}).get("minifigs") or [] if m.get("id")]}
                            if item.get("partial_set") else {})})
        return out
    info = backoffice_outils.fix(cache.get(cache_key(item)) or {}, cache_key(item))   # corrections faites dans le back office
    if item.get("kind") == "fig" and not info.get("theme"):   # figurine sans gamme (fiche venue d'un set) : la gamme et l'année de son set
        src = next((cache.get(n) for n in info.get("sets") or [] if (cache.get(n) or {}).get("theme")), None)
        if src:
            info = {**info, "theme": src["theme"], "subtheme": info.get("subtheme") or src.get("subtheme"),
                    "years": info.get("years") or info.get("year") or src.get("year"), "theme_from_set": True}
    wish = kinds.get(item.get("list_id")) == "wishlist"
    out_noest = False
    lp = lego_price(item.get("number")) if item.get("kind", "set") == "set" else None
    if lp and info and not info.get("availability") and lp.get("status") and lp.get("status") != "gone" and not lp.get("soon"):
        info = {**info, "availability": "Retail"}   # (vendu sur lego.com d'après la page de son thème — 21/11)
    if lp and lp.get("price") and info and not info.get("retail"):   # prix public lego.com (sets à venir / récents) quand le catalogue n'en a pas
        dm = re.search(r"\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}", lp.get("when") or "", re.I)
        info = {**info, "retail": lp["price"], **({"availability": "Pending", "releasing": ("Disponible le " + dm.group(0)) if dm else lp.get("when") or ""}
                                                  if lp.get("soon") and not info.get("availability") else {})}
    if item.get("kind", "set") == "set" and info:
        info = with_bs(info, item.get("number"))   # (catalogue Brickset : prix magasin en €… — 21/11 soir)
    if info.get("pending_prices"):   # ajouté sans cote : estimation par ses pièces si demandée, sinon en attente
        mp = item.get("moc_price") or {}
        if item.get("moc_parts") and mp.get("priced"):
            unit = mp.get("total") or 0
        elif wish and info.get("retail"):   # souhait sans cote : son prix public (lego.com)
            unit = estimate_wish(item, info)
        elif item.get("kind") == "fig" and fig_used(item["number"]) is not None:   # minifig sans cote : son prix d'occasion relevé
            unit = fig_used(item["number"])
        else:
            unit, out_noest = 0, True
    elif not info:
        unit = item.get("unit_value", 0)
    elif item.get("kind") == "fig":
        used = fig_used(item["number"])   # minifig d'occasion : prix relevé, sinon prix neuf (ex. minifig récente)
        unit = used if used is not None else info.get("value")
        if unit is None:
            out_noest, unit = True, 0
        if item.get("fig_swaps"):   # pièces remplacées : on retire l'origine, on ajoute le remplacement, puis la décote « modifiée »
            q = max(1, int(item.get("quantity", 1) or 1))   # pièces du LOT entier : prix × q + écart, décote sur les seules figurines modifiées
            d = (item.get("swap_price") or {}).get("delta", 0) or 0
            mk = mod_discount() / 100 if is_modified(item) else 0
            mc = mod_copies(item.get("fig_swaps"), q) if mk else 0
            unit = max(0, round((unit * q + d - mk * (unit * mc + d)) / q, 4))
    else:
        unit = estimate_wish(item, info) if wish else estimate(item, info)
    box_add = 0.0
    if not wish and item.get("has_box") and item.get("condition") != "neuf" and (item.get("kind") or "set") == "set" and info:   # part de la boîte dans l'estimation
        try:
            box_add = round((unit - estimate({**item, "has_box": False}, info)) * max(1, int(item.get("quantity", 1) or 1)), 2)
        except Exception:
            box_add = 0.0
    out = dict(item)
    if box_add:
        out["box_add"] = box_add   # (vignettes : la boîte seule ne fait pas apparaître la ligne « réel »)
    if wish and info and (item.get("kind") or "set") == "set":   # détail lisible sur la carte (états cherchés, sans figurines)
        try:
            out["wish_lines"] = wish_lines(item, info)
        except Exception:
            pass
    if wish and info and item.get("also_used"):   # cherché neuf ou d'occasion : les deux prix
        wp = wish_prices(item, info)
        if wp:
            out["wish_prices"] = {k: round(v, 2) for k, v in wp.items()}
    out["unit_value"] = unit
    out["total_value"] = round(unit * item.get("quantity", 1), 2)
    out["unit_value"] = round(unit, 2)
    if out_noest:   # minifig sans aucun prix
        out["no_estimate"] = True
    if parts_estimable(item) and item.get("moc_parts"):   # set (ou minifig Rebrickable) estimé par ses pièces (cote indisponible)
        mp = item.get("moc_price") or {}
        out.pop("moc_parts", None)
        out["moc_info"] = {"lots": len(item["moc_parts"]), "pieces": sum(x.get("qty", 1) for x in item["moc_parts"]),
                           **{k: v for k, v in mp.items() if k != "units"}, "approx": len(mp.get("approx") or [])}
        if info.get("pending_prices") and (mp.get("approx") or mp.get("missing")):
            out["approx"] = True
    out["info"] = {k: info.get(k) for k in (
        "name", "theme", "year", "pieces", "image", "retail", "new_value",
        "used_value", "minifig_count", "minifig_value", "minifigs",
        "availability", "source", "fetched_at", "value", "years", "sets", "subtheme", "retirement", "releasing", "pending_prices", "market", "price_src")}
    if item.get("kind", "set") == "set" and info:
        out["info"] = with_fr(out["info"], item["number"])
        out["info"]["extras"] = set_extras(item["number"])
        _sf = sf_prices(item["number"], info)
        if _sf:
            out["info"]["sf"] = _sf   # (prix sans figurines : neuf, occasion — bulles de la fiche, 21/11)
        if out["info"].get("minifigs"):
            out["info"]["minifigs"] = [with_fr_fig(f) for f in with_used_figs(out["info"])["minifigs"]]
            names = {fid: m["name"] for fid, m in (item.get("fig_mods") or {}).items() if isinstance(m, dict) and m.get("name")}
            if names:   # figurine renommée dans ce set : son nom partout (listes, recherche, page publique)
                out["info"]["minifigs"] = [{**f, "name": names[f.get("id")], "orig_name": f.get("name")} if f.get("id") in names else f
                                           for f in out["info"]["minifigs"]]
    elif item.get("kind") == "fig" and info:
        rec = _fu_cache().get(item["number"]) or {}
        nv = (rec.get("new") or {}).get("unit")   # neuve : annonces (France, sinon Europe, sinon monde)
        out["info"] = {**with_fr_fig(out["info"]), "used": fig_used(item["number"]), **({"value": nv} if nv else {}),
                       **({"market": {"used": fig_used_stats(item["number"]), "new": rec.get("new"), "src": rec.get("src") or "BrickOwl"}} if rec else {})}
    if info:   # images du catalogue : la version HD quand elle est prête
        out["info"]["image"] = hd_img(out["info"].get("image"))
        if out["info"].get("minifigs"):
            out["info"]["minifigs"] = [{**f, "image": hd_img(f.get("image"))} for f in out["info"]["minifigs"]]
    out["info"] = backoffice_outils.fix(out["info"], cache_key(item))   # corrections du back office, une 2e fois : par-dessus le nom français et l'image HD
    return out


VISITS_FILE = os.path.join(DATA, "visits.json")


def record_visit(page, ip):
    """Compte une visite de la page publique (/wishlist ou /collection) : une par personne et par jour, visiteurs distincts, dernière visite."""
    day = time.strftime("%Y-%m-%d")
    h = hashlib.sha256(("bq-visite|" + ip).encode()).hexdigest()[:16]   # adresse jamais stockée en clair
    with lock:
        v = _load(VISITS_FILE, {})
        e = v.setdefault(page, {"views": 0, "visitors": [], "days": {}, "last": None})
        if h not in e["visitors"]:
            e["visitors"] = (e["visitors"] + [h])[-5000:]
        d = e["days"].setdefault(day, {"views": 0, "ips": []})
        if h in d["ips"]:   # au plus une visite par personne et par jour (recharger, revenir : ne compte pas)
            return
        d["ips"].append(h)
        d["views"] += 1
        e["views"] += 1
        e["days"] = dict(sorted(e["days"].items())[-90:])   # 90 derniers jours
        e["last"] = int(time.time())
        _save(VISITS_FILE, v)


def visit_stats():
    day = time.strftime("%Y-%m-%d")
    week = time.strftime("%Y-%m-%d", time.localtime(time.time() - 6 * 86400))
    out = {}
    for page, e in _load(VISITS_FILE, {}).items():
        days = e.get("days") or {}
        out[page] = {"views": e.get("views", 0), "visitors": len(e.get("visitors") or []), "last": e.get("last"),
                     "today": (days.get(day) or {}).get("views", 0),
                     "week": sum(d.get("views", 0) for k, d in days.items() if k >= week)}
    return out


REFRESH_MIN_GAP = 10 * 60   # au rechargement : pas plus d'une actualisation complète toutes les 10 min
_refresh = {"running": False, "done": 0, "total": 0, "errors": [], "finished": None}


def refresh_status():
    st = _load(sources.SETTINGS_FILE, {})
    return {"running": _refresh["running"], "done": _refresh["done"], "total": _refresh["total"],
            "erreurs": _refresh["errors"], "actualises": _refresh["done"] - len(_refresh["errors"]),
            "finished": _refresh["finished"], "last_refresh": st.get("last_refresh")}


def refresh_start(force=False):
    """Actualise les prix de tous les sets et minifigs, dans un fil séparé (un seul à la fois)."""
    if COPIE and not force:   # copie de travail : jamais d'actualisation automatique (seulement demandée à la main)
        return {**refresh_status(), "started": False}
    with lock:
        last = _load(sources.SETTINGS_FILE, {}).get("last_refresh") or 0
        if _refresh["running"] or (not force and time.time() - last < REFRESH_MIN_GAP):
            return {**refresh_status(), "started": False}
        db = load_db()
        cache, kinds = _load(CACHE_FILE, {}), list_kinds(db)
        # travaux : ("set", n) · ("fig", n) figurine seule · ("sfig", n) figurine d'un set · ("est", id) estimé par ses pièces
        jobs = sorted({("fig" if i.get("kind") == "fig" else "set", i["number"]) for i in db["items"] if i.get("kind") not in ("custom", "part")})
        if force:
            own = {n for k, n in jobs if k == "fig"}
            jobs += sorted({("sfig", f["id"]) for k, n in jobs if k == "set" for f in (cache.get(n) or {}).get("minifigs") or []
                            if f.get("id") and f["id"] not in own and not RB_FIG.fullmatch(f["id"])})
            jobs += [("est", i["id"]) for i in db["items"] if i.get("moc_parts") and kinds.get(i["list_id"]) == "collection"]
        numbers = jobs
        _refresh.update(running=True, done=0, total=len(numbers), errors=[])

    def one(arg):
        kind, n = arg
        _bl_night.consult = force   # bouton : les prix BrickLink de plus de 24 h sont relus (sinon : gardés)
        try:
            if kind in ("fig", "sfig"):   # annonces d'occasion et neuves
                fig_used_fetch(n, max_age=consult_ttl() if force else FIG_USED_TTL)
                if kind == "fig":
                    get_fig(n, force=True)
            elif kind == "est":   # MOC / set estimé par ses pièces : chaque pièce relue, puis nouveau chiffrage
                it = next((i for i in load_db()["items"] if i["id"] == n), None)
                for lot in (it or {}).get("moc_parts") or []:
                    blc = bo_bl_color(lot.get("color"))
                    if lot.get("part") and blc is not None:
                        try:
                            bl_part(lot["part"], blc, conds=("U",), max_age=consult_ttl())
                        except Exception as e:
                            if "quota" in str(e).lower():
                                raise
                if it:
                    moc_price_start(n)
            else:
                get_set(n, force=True, market_force=force)
        except Exception:
            _refresh["errors"].append(n)
        finally:
            _bl_night.consult = False
        _refresh["done"] += 1

    def run():
        import concurrent.futures as cf
        try:
            with cf.ThreadPoolExecutor(3) as ex:
                list(ex.map(one, numbers))
            with lock:
                st = _load(sources.SETTINGS_FILE, {})
                st["last_refresh"] = int(time.time())
                _save(sources.SETTINGS_FILE, st)
                os.chmod(sources.SETTINGS_FILE, 0o600)
            fig_used_fill()   # prix d'occasion des minifigs (BrickOwl), à la suite
        finally:
            _refresh["running"] = False
            _refresh["finished"] = int(time.time())
    threading.Thread(target=run, daemon=True).start()
    return {**refresh_status(), "started": True}


# ---------------------------------------------------------------- réseaux sociaux (Réglages › Réseaux sociaux)


def ig_public_user():
    """Compte Instagram indiqué dans Réglages › Réseaux sociaux (champ libre) : affiché SEULEMENT sur les pages publiques
    (logo + lien vers le compte) ; "" s'il n'y en a pas."""
    u = str((_load(sources.SETTINGS_FILE, {}).get("social") or {}).get("instagram") or "").strip().lstrip("@")
    return u if re.fullmatch(r"[\w.]{1,30}", u) else ""


# ---------------------------------------------------------------- évolution de la valeur dans le temps
HISTORY_FILE = os.path.join(DATA, "history.json")   # relevés quotidiens de la valeur de la collection


def record_day(items, kinds):
    """Une fois par jour : valeur de la collection et de la liste de souhaits (relevé réel, pas une estimation)."""
    day = time.strftime("%Y-%m-%d")
    h = _load(HISTORY_FILE, {})
    if (h.get("collection") or {}).get(day) and h.get("items_day") == day:
        return
    col = sum(i.get("total_value") or 0 for i in items if kinds.get(i.get("list_id")) == "collection")
    wish = sum(i.get("total_value") or 0 for i in items if kinds.get(i.get("list_id")) == "wishlist")
    with lock:
        h = _load(HISTORY_FILE, {})
        h.setdefault("collection", {})[day] = {"value": round(col, 2), "wishlist": round(wish, 2),
                                               "count": sum(1 for i in items if kinds.get(i.get("list_id")) == "collection")}
        cache, ih = _load(CACHE_FILE, {}), h.setdefault("items", {})
        for i in items:
            if i.get("kind") not in ("set", "fig", None):
                continue
            key = cache_key(i)
            info = cache.get(key) or {}
            nv = info.get("value") if i.get("kind") == "fig" else info.get("new_value")
            uv = fig_used(i["number"]) if i.get("kind") == "fig" else info.get("used_value")
            if nv is None and uv is None:
                continue
            rows = ih.setdefault(key, [])
            if not rows or rows[-1][1:] != [nv, uv]:
                rows.append([day, nv, uv])
        absent = set()   # (figurines absentes de mes sets : leur prix aussi, chaque jour — courbe « Le set » d'un set sans figurines, 21/11 soir)
        for i in items:
            if (i.get("kind") or "set") == "set" and (i.get("with_minifigs") is False or i.get("missing_minifigs")):
                if i.get("with_minifigs") is False:
                    absent |= {f["id"] for f in ((cache.get(cache_key(i)) or {}).get("minifigs") or []) if f.get("id")}
                else:
                    absent |= {(x.get("id") if isinstance(x, dict) else x) for x in i.get("missing_minifigs") or []}
        for fid in absent - {None, ""}:
            nv, uv = (cache.get("fig:" + fid) or {}).get("value"), fig_used(fid)
            if nv is None and uv is None:
                continue
            rows = ih.setdefault("fig:" + fid, [])
            if not rows or rows[-1][1:] != [nv, uv]:
                rows.append([day, nv, uv])
        h["items_day"] = day
        _save(HISTORY_FILE, h)


VALUE_LOG_FILE = os.path.join(DATA, "value_log.json")   # journal des valeurs par fiche (« Comprendre les variations »)


def _eur(v):
    return f"{v:,.2f}".replace(",", "\u202f").replace(".", ",") + " €"


def _vl_state(raw_items, enriched, cache, kinds):
    """État du moment de chaque fiche de la collection : {id: {"n", "num", "k", "row": [valeur, quantité, liste, cote de base, {figurine: [prix, nombre en plus (+) ou en moins (−)]}]}}.
    Figurine d'origine d'un set : comptée dans son set (pas de ligne). Les figurines citées sont celles qui pèsent sur l'estimation du set."""
    by = {e["id"]: e for e in enriched}
    out = {}
    for it in raw_items:
        if kinds.get(it.get("list_id")) != "collection" or it.get("kind") == "part":
            continue
        e = by.get(it["id"]) or {}
        orig = bool(it.get("set_orig") and it.get("attached_to"))   # figurine d'origine d'un set : suivie (sa flèche), jamais comptée dans les totaux
        q = max(1, int(it.get("quantity", 1) or 1))
        v = round((e.get("own_total") if orig else e.get("total_value")) or 0, 2)
        base, figs = None, {}
        if it.get("kind", "set") in ("set", None):
            info = cache.get(cache_key(it)) or {}
            neuf = it.get("condition") == "neuf"
            base = round((info.get("new_value") if neuf else info.get("used_value")) or info.get("retail") or 0, 2)
            mfs = info.get("minifigs") or []
            have = fig_have(it, mfs, q) if it.get("with_minifigs", True) else {f["id"]: 0 for f in mfs}
            for f in mfs:
                c = have.get(f["id"], 0) - f.get("qty", 1) * q
                if c:
                    fu = fig_used(f["id"])
                    figs[f["id"]] = [round((f.get("value") or 0) if neuf else (fu if fu is not None else f.get("value") or 0), 2), c]
        elif v:
            base = round(v / q, 4)
        name = it.get("display_name") or it.get("custom_name") or (e.get("info") or {}).get("name") or it.get("number") or ""
        out[it["id"]] = {"n": str(name)[:120], "num": "" if it.get("number") in (None, "custom") else it["number"], "k": it.get("kind") or "set",
                         "row": [v, q, it["list_id"], base, figs] + ([1] if orig else [])}
    return out


def _vl_counted(row):
    """Ligne du journal (sans le jour) comptée dans les totaux ? (pas une figurine d'origine, déjà dans la cote de son set)"""
    return not (len(row) > 5 and row[5])


def _vl_backfill(log, st, raw_items, cache):
    """Premier lancement : les jours déjà relevés (history.json, celui d'aujourd'hui compris : l'état du matin) sont reconstitués d'après
    les cotes relevées de chaque fiche et sa date d'ajout (approximation : les fiches supprimées ou modifiées avant ne sont pas connues).
    Rend True si le relevé du matin d'aujourd'hui a été reconstitué (on n'y ajoute alors pas l'état du moment)."""
    h = _load(HISTORY_FILE, {})
    today = time.strftime("%Y-%m-%d")
    days = [d for d in sorted(h.get("collection") or {}) if d <= today]
    ih = h.get("items") or {}

    def cote(key, day, col):
        v = None
        for p in ih.get(key) or []:
            if p[0] <= day and p[col] is not None:
                v = p[col]
        return v
    raw = {i["id"]: i for i in raw_items}
    items = log.setdefault("items", {})
    for day in days:
        for iid, s in st.items():
            it = raw[iid]
            added = time.strftime("%Y-%m-%d", time.localtime(it.get("added_at") or 0))
            if added > day or (added == day and day == today):
                continue   # pas encore dans la collection ce jour-là (aujourd'hui : relevé du matin)
            v, q, lid, base, figs = s["row"][:5]
            neuf = it.get("condition") == "neuf"
            col = 1 if neuf else 2
            v0, b0, f0 = v, base, {}
            if it.get("kind") in ("set", "fig", None):
                info = cache.get(cache_key(it)) or {}
                cur = (info.get("value") if neuf else fig_used(it["number"])) if it.get("kind") == "fig" else (info.get("new_value") if neuf else info.get("used_value"))
                c0 = cote(cache_key(it), day, col)
                if c0 is not None and cur is not None and base is not None:
                    b0 = round(base + (c0 - cur), 4)
                    v0 += (c0 - cur) * q
            for fid, (p, c) in figs.items():
                p0 = cote("fig:" + fid, day, col)
                p0 = round(p0, 2) if p0 is not None else p
                f0[fid] = [p0, c]
                v0 += (p0 - p) * c
            row = [day, round(max(0, v0), 2), q, lid, b0, f0] + s["row"][5:]
            r = items.setdefault(iid, {"rows": []})
            r.update(n=s["n"], num=s["num"], k=s["k"])
            if not r["rows"] or r["rows"][-1][1:] != row[1:]:
                r["rows"].append(row)
    import datetime as _dt
    log["exact_from"] = (_dt.date.today() + _dt.timedelta(days=1)).isoformat() if today in days else today
    if days:
        log["first"] = days[0]
    return today in days


def vl_record(raw_items, enriched, cache, kinds):
    """Une fois par jour (premier chargement) : une ligne par fiche dont la valeur, la quantité, la liste, la cote ou les figurines ont changé."""
    day = time.strftime("%Y-%m-%d")
    fresh = lambda g: g.get("day") == day and g.get("ver", 1) >= 2
    if fresh(_load(VALUE_LOG_FILE, {})):
        return
    st = _vl_state(raw_items, enriched, cache, kinds)
    with lock:
        log = _load(VALUE_LOG_FILE, {})
        if fresh(log):
            return
        if log.get("ver", 1) < 2 and (log.get("exact_from") or "") > day:   # journal d'avant les figurines d'origine, encore tout reconstitué : refait
            log = {}
        morning = False
        if not log.get("items"):
            morning = _vl_backfill(log, st, raw_items, cache)
        log["ver"] = 2
        items = log.setdefault("items", {})
        _pend = lambda x: bool(x.get("fig_swaps")) and not (x.get("swap_price") or {}).get("done")   # pièces échangées pas encore chiffrées
        pending = {i["id"] for i in raw_items if isinstance(i, dict) and (_pend(i) or _pend(i.get("set_mod") or {})
                   or any(isinstance(m, dict) and _pend(m) for m in (i.get("fig_mods") or {}).values()))}
        for iid, s in st.items():
            if morning:
                continue   # (le relevé du matin vient d'être reconstitué : l'état du moment n'est pas « ce matin »)
            if iid in pending and (items.get(iid) or {}).get("rows"):
                continue   # (chiffrage en cours : valeur provisoire — le relevé d'avant reste la référence, 20/11)
            r = items.setdefault(iid, {"rows": []})
            r.update(n=s["n"], num=s["num"], k=s["k"])
            r.pop("gone", None)
            if not r["rows"] or r["rows"][-1][1:] != s["row"]:
                r["rows"].append([day] + s["row"])
        for iid, r in items.items():
            if iid not in st and not r.get("gone"):
                r["gone"] = day
            if len(r["rows"]) > 500:
                r["rows"] = r["rows"][-500:]
        if not morning:   # heure du relevé du jour (« par rapport à 08:05 ») ; le matin reconstitué n'en a pas
            log.setdefault("times", {})[day] = int(time.time())
        log["day"] = day
        log.setdefault("first", day)
        log.setdefault("exact_from", day)
        _save(VALUE_LOG_FILE, log)


TREND_DAYS = (1, 7, 15, 30, 90, 180, 365)   # crans du curseur « Comparer les variations à » (Réglages) ; 30 / 90 / 180 / 365 : même jour, 1 / 3 / 6 / 12 mois avant
TREND_OLD = {"veille": 1, "mois": 30, "annee": 365}   # (anciens choix de la liste)


def trend_until():
    """Date (AAAA-MM-JJ) avant laquelle on cherche le relevé de comparaison des variations, selon la période choisie (Réglages)."""
    import datetime
    import calendar
    n, d = int(trend_cfg().get("period") or 1), datetime.date.today()
    months = {30: 1, 90: 3, 180: 6, 365: 12}.get(n)
    if months:   # glissant : le même jour, 1 / 3 / 6 / 12 mois avant (jour inexistant : le dernier du mois), relevés jusqu'à ce jour-là compris
        y, m = d.year, d.month - months
        while m < 1:
            y, m = y - 1, m + 12
        ref = datetime.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))
    else:   # 1 / 7 / 15 : ce nombre de jours avant (1 = la veille)
        ref = d - datetime.timedelta(days=max(1, n))
    return (ref + datetime.timedelta(days=1)).isoformat()


_tep = {"t": 0, "v": ""}


_lists_c = {"k": None, "t": 0, "v": None}
_LISTS_SELF = {"history.json", "value_log.json", "visits.json", "bans.json", "auth.json", "backoffice_auth.json", "bl_quota.json", "bl_nightly.json",
               "claude-notes.json", "recette.json", "push_subs.json"}   # (écrits par le calcul lui-même, ou sans rapport)


_lists_build = threading.Lock()
_lists_warm = {"t": None}


def lists_warm(delay=1.5, force=False):
    """Après un enregistrement : la collection recalculée en coulisse (une seule fois pour une rafale d'enregistrements)."""
    if _lists_warm["t"] and _lists_warm["t"].is_alive():
        _lists_warm["again"] = True   # (déjà en cours : refait juste après, rien n'est perdu)
        return
    def run():
        try:   # (pour l'écran : priorité normale, n'attend jamais que l'écran soit calme)
            _prio_tl.fg = True
            os.setpriority(os.PRIO_PROCESS, threading.get_native_id(), 0)
        except Exception:
            pass
        time.sleep(delay)
        f = force
        while True:
            _lists_warm["again"] = False
            try:
                lists_payload(force=f)
            except Exception as e:
                print("Préchauffage de la collection :", e, flush=True)
            if not _lists_warm.get("again"):
                break
            f = False   # (relancé : seulement si l'état a changé depuis)
    _lists_warm["t"] = threading.Thread(target=run, daemon=True)
    _lists_warm["t"].start()


def lists_payload(force=False):
    """Toute la collection pour l'appli (« /api/lists ») : gardée en mémoire, recalculée une seule fois à la fois (22/11)."""
    if not force and _lists_c["v"] is not None and lists_cache_key() == _lists_c["k"]:
        if time.time() - _lists_c["t"] >= 120:
            lists_warm(0, force=True)   # (plus de 2 min : servie tout de suite, la version à jour se calcule en coulisse)
        return _lists_c["v"]
    with _lists_build:
        _lk = lists_cache_key()   # (gardé en mémoire tant que rien n'a changé — 22/11)
        if not force and _lk == _lists_c["k"] and _lists_c["v"] is not None:
            return _lists_c["v"]
        db = load_db()
        cache = _load(CACHE_FILE, {})
        kinds = list_kinds(db)
        fig_info_fill([i["number"] for i in db["items"] if i.get("kind") == "fig" and not (cache.get("fig:" + i["number"]) or {}).get("name")])
        items = [enrich(i, cache, kinds) for i in db["items"]]
        trend_lists = {}
        try:
            record_day(items, kinds)
            vl_record(db["items"], items, cache, kinds)   # journal des valeurs par fiche (« Comprendre les variations »)
        except Exception as e:
            print("Relevé du jour impossible :", e, flush=True)
        try:   # (à part : un relevé du jour raté n'empêche pas les flèches)
            trend_lists = vl_trends(items, kinds, cache)   # flèches de variation (chg de chaque fiche, totaux par liste)
            cote_trends(items, cache)   # … et variation de chaque cote (détail des prix d'une fiche)
        except Exception as e:
            print("Variations impossibles :", e, flush=True)
        fill_fr_names([i["number"] for i in db["items"] if i.get("kind", "set") == "set"]
                      + [(inv.get("set") or "") for inv in (db.get("inventories") or {}).values()])
        fill_fig_names([n for i in items for n in
                        ([i["info"].get("name_en") or i["info"].get("name")] if i.get("kind") == "fig" and i.get("info") else
                         [f.get("name_en") or f.get("name") for f in ((i.get("info") or {}).get("minifigs") or [])])])
        return (_lists_keep(_lk, {"lists": db["lists"], "items": items, "mod_discount": mod_discount(), "box_bonus": box_bonus(), "plan_cut": plan_cut(),
                               "ref_site": ref_site(), "bl_down": bl_down(), "bl_back": _load(sources.SETTINGS_FILE, {}).get("bl_back"), "site_logos": site_logos(), "trend": trend_cfg(), "trend_lists": trend_lists, "trend_ref": vl_ref(),   # flèches de variation à côté des prix (et le relevé comparé)
                               "app_color": _load(sources.SETTINGS_FILE, {}).get("app_color") or "",   # thème de l'application (Réglages)
                               **(perso.payload() if perso else {}),   # (extensions locales)
                               "bl_zones": {**sources.bl_zone_cfg(), "order": sources.bl_zone_order()},   # zones BrickLink réglées (drapeaux, liens)
                               "todo_cats": todo_cats(), "todo_icons": todo_icons(), "help_on": _load(sources.SETTINGS_FILE, {}).get("help_on", True) is not False, "free_todos": free_todos(), "bl_alert": None if DEMO else _bl_state["alert"],
                               "keys_missing": [] if DEMO else [k for k, ok in (("rebrickable", sources.rebrickable_key()), ("bricklink", bl_on())) if not ok],
                               "side_pub_hide": _load(sources.SETTINGS_FILE, {}).get("side_pub_hide") or [],   # (liens publics masqués dans le menu latéral)
                               "sort_def": _load(sources.SETTINGS_FILE, {}).get("sort_def"),   # (tri par défaut, le même sur tous les appareils — 22/11)
                               "demo_on": DEMO_SITE, "lego_urls": lego_urls()}))   # fiches : lien direct vers la page LEGO.com quand elle est connue


_gz_cache = {}   # (fichiers texte compressés, par version — 22/11)


def lists_cache_key():
    """Clé de « /api/lists » gardé en mémoire : le jour + la dernière modification de MA collection et des réglages (les relevés de prix
    écrits en fond ne comptent pas : ils arrivent par le recalcul en coulisse, toutes les 2 minutes au plus) — 22/11."""
    mt = 0.0   # (tout fichier de données compte — notes libres, nouveautés masquées… — sauf les relevés de fond et les sauvegardes — 22/11)
    try:
        for e in os.scandir(DATA):
            nm = e.name
            if nm.endswith(".json") and not nm.startswith("cache") and ".avant" not in nm and nm not in _LISTS_SELF:
                mt = max(mt, e.stat().st_mtime)
    except OSError:
        return None
    return (time.strftime("%Y-%m-%d"), mt)


def _lists_keep(k, v):
    if k is not None:
        _lists_c.update(k=k, t=time.time(), v=v)   # (rangée sous l'état d'AVANT le calcul : un enregistrement pendant le calcul la rend périmée — 22/11)
    return v


def trend_epoch():
    """Date de départ des variations (réglage « trend_epoch », AAAA-MM-JJ) : les relevés d'avant ne servent jamais de comparaison (22/11)."""
    if time.time() - _tep["t"] > 30:
        _tep.update(v=str(_load(sources.SETTINGS_FILE, {}).get("trend_epoch") or ""), t=time.time())
    return _tep["v"]


def trend_ref_row(rows, today, until, ok=lambda x: True, unit=None):
    """Relevé de comparaison : le dernier d'avant « until » ; sinon (fiche plus récente que la période) le tout premier d'avant aujourd'hui.
    unit (valeur à l'unité d'un relevé) : un relevé qui vaut moins du quart d'un des deux suivants (prix pas encore connu à l'ajout…)
    n'est jamais pris — c'est le relevé fiable suivant qui sert (20/11)."""
    ep = trend_epoch()
    rows = [x for x in rows or [] if ok(x) and (not ep or x[0] >= ep)]   # (rien d'avant la date de départ des variations — 22/11)
    if unit:
        def sure(k):
            u = unit(rows[k])
            nxt = [unit(y) for y in rows[k + 1:k + 3]]
            return not any(v and v > 0.004 and (u or 0) < v / 4 for v in nxt)
        rows = [x for k, x in enumerate(rows) if sure(k)]
    ref = None
    for x in rows:
        if x[0] < until:
            ref = x
    if ref is None:
        ref = next((x for x in rows if x[0] < today), None)
    return ref


def trend_cfg():
    """Réglages → Estimations : flèches de variation à côté des prix {"on", "up" %, "down" %, "stable" (afficher ~), "pct" (afficher le %)}."""
    t = dict(_load(sources.SETTINGS_FILE, {}).get("trend") or {})   # les valeurs choisies par le propriétaire (base)…
    try:   # … modifiées dans le back office (Comportements → Prix et variations, une fois publié)
        o = (backoffice.published().get("behav") or {}).get("trend")
        if isinstance(o, dict):
            t.update({k: v for k, v in o.items() if k in ("on", "stable", "pct", "size")})   # (les seuils : Réglages de l'appli seulement)
    except Exception:
        pass

    def num(k, d):
        try:
            return max(0.0, min(100.0, float(t.get(k, d))))
        except (TypeError, ValueError):
            return d
    try:
        size = int(max(50, min(250, float(t.get("size", 100)))))   # taille des flèches, en % (curseur des Réglages)
    except (TypeError, ValueError):
        size = 100
    return {"on": t.get("on", True) is not False, "up": num("up", 3.0), "down": num("down", 3.0),
            "stable": t.get("stable", True) is not False, "pct": bool(t.get("pct")), "size": size,
            "period": (lambda v: v if v in TREND_DAYS else 1)(TREND_OLD.get(t.get("period")) or (int(t["period"]) if str(t.get("period") or "").isdigit() else 1))}   # (curseur : jours, Réglages)


def vl_ref():
    """Relevé auquel les variations sont comparées : le dernier d'avant aujourd'hui → {"day": "AAAA-MM-JJ", "t": heure (epoch) ou None}."""
    log, today, until = _load(VALUE_LOG_FILE, {}), time.strftime("%Y-%m-%d"), trend_until()
    times = log.get("times") or {}
    ep = trend_epoch()
    days = [d for d in times if ep <= d < today] + [d for d in (_load(HISTORY_FILE, {}).get("collection") or {}) if ep <= d < today]   # (date de départ des variations — 22/11)
    if not days:
        return None
    d = max([x for x in days if x < until] or [min(days)])   # (période choisie ; sinon le premier relevé)
    return {"day": d, "t": times.get(d)}


def comp_chg(e, cache, ih, today):
    """Variation (%) d'une fiche SANS relevé d'avant (ajoutée ou copiée depuis), d'après ses composantes : la cote du set ou de la figurine
    (dernier point d'avant aujourd'hui dans history.json) et, pour une figurine aux pièces échangées, le prix d'avant de ses pièces
    (cache des pièces, « prev ») ; MOC / set partiel : ses propres relevés (value_hist). None si rien n'est connu."""
    def last(pts, col):
        ref = None
        for p_ in pts or []:
            if trend_epoch() <= p_[0] < today and p_[col] is not None:   # (date de départ des variations — 22/11)
                ref = p_[col]
        return ref
    q = max(1, int(e.get("quantity", 1) or 1))
    v = (e.get("own_total") if e.get("set_orig") and e.get("attached_to") else e.get("total_value")) or 0
    if v <= 0.004 or e.get("no_estimate"):
        return None
    kind = e.get("kind") or "set"
    if kind == "custom":
        vh = [x for x in (e.get("value_hist") or []) if trend_epoch() <= x[0] < today]   # (date de départ des variations — 22/11)
        u0 = vh[-1][1] if vh else None
        return round((v / q - u0) / u0 * 100, 1) if u0 else None
    if kind not in ("set", "fig"):
        return None
    info = cache.get(cache_key(e)) or {}
    neuf = e.get("condition") == "neuf"
    if kind == "fig":
        fu = fig_used(e["number"])
        cur, col = (info.get("value"), 1) if neuf or fu is None else (fu, 2)
    else:
        cur, col = (info.get("new_value"), 1) if neuf else (info.get("used_value"), 2)
    ref, eff, known = last(ih.get(cache_key(e)), col), 0.0, False
    if ref is None and cur is not None and col == 2:   # pas d'historique : le dernier relevé de la cote (figurine « fu: », set « bm: »)
        rec = (_fu_cache().get(e["number"]) if kind == "fig" else (_parts_cache().get("bm:" + e["number"]) or {}).get("used")) or {}
        t_ = (_fu_cache().get(e["number"]) or {}).get("t") if kind == "fig" else (_parts_cache().get("bm:" + e["number"]) or {}).get("t")
        pv = (rec.get("prev") or {}).get("unit") if kind == "fig" else None
        if pv:
            ref = pv   # son prix d'avant
        elif t_ and time.strftime("%Y-%m-%d", time.localtime(t_)) < today:
            ref = cur   # relevé avant aujourd'hui, pas relu depuis : inchangé (stable)
    if cur is not None and ref is not None:
        eff += (cur - ref) * q
        known = True
    for sw in (e.get("fig_swaps") or []) if kind == "fig" else []:   # pièces échangées : l'écart de prix de chacune depuis son relevé d'avant
        for side, sign in (("new", 1), ("orig", -1)):
            p_ = sw.get(side) if isinstance(sw, dict) else None
            if not isinstance(p_, dict) or p_.get("unit") is None or not p_.get("part"):
                continue
            c = part_chg(p_["part"], p_.get("color") or "")
            if c is not None and c > -99:
                eff += sign * p_["unit"] * (p_.get("qty") or 1) * c / (100 + c)
                known = True
    prev = v - eff
    return round((v - prev) / prev * 100, 1) if known and prev > 0.004 else None


def hist_backfill(key, m):
    """Historique réel (history.json) : les médianes mensuelles des ventes BrickLink (6 mois) ajoutées AVANT le premier relevé de l'appli
    — [« AAAA-MM-15 », neuf, occasion] (21/11)."""
    nm, um = ((m or {}).get("new") or {}).get("months") or {}, ((m or {}).get("used") or {}).get("months") or {}
    if not nm and not um:
        return
    with lock:
        h = _load(HISTORY_FILE, {})
        rows = (h.setdefault("items", {})).get(key) or []
        first = rows[0][0] if rows else time.strftime("%Y-%m-%d")
        add = [[mo + "-15", nm.get(mo), um.get(mo)] for mo in sorted(set(nm) | set(um)) if mo + "-15" < first]
        if not add:
            return
        h["items"][key] = add + rows
        _save(HISTORY_FILE, h)


def mkt_pair(e, cache, ih, today, until):
    """(prix du marché aujourd'hui, prix du marché au jour de comparaison) d'une fiche, sur l'historique réel — même état que mon exemplaire ; None."""
    kind = e.get("kind") or "set"
    if kind not in ("set", "fig") or not e.get("number"):
        return None
    key = cache_key(e)
    pts = ih.get(key)
    if not pts:
        return None
    info = cache.get(key) or {}
    neuf = e.get("condition") == "neuf"
    col = 1 if neuf else 2
    cur = (info.get("value") if neuf else fig_used(e["number"])) if kind == "fig" else (info.get("new_value") if neuf else info.get("used_value"))
    r = trend_ref_row(pts, today, until, lambda x: len(x) > col and x[col] is not None)
    ref = r[col] if r else None
    return (cur, ref) if cur and ref and ref > 0.004 else None


def mkt_chg(e, cache, ih, today, until):
    """Variation du MARCHÉ seul (sans mes ajouts) d'une fiche, sur l'historique réel du set / de la figurine (21/11) ; None si inconnue."""
    kind = e.get("kind") or "set"
    if kind not in ("set", "fig") or not e.get("number"):
        return None
    key = cache_key(e)
    pts = ih.get(key)
    if not pts:
        return None
    info = cache.get(key) or {}
    neuf = e.get("condition") == "neuf"
    col = 1 if neuf else 2
    cur = (info.get("value") if neuf else fig_used(e["number"])) if kind == "fig" else (info.get("new_value") if neuf else info.get("used_value"))
    r = trend_ref_row(pts, today, until, lambda x: len(x) > col and x[col] is not None)
    ref = r[col] if r else None
    return round((cur - ref) / ref * 100, 1) if cur and ref and ref > 0.004 else None


def vl_trends(enriched, kinds, cache=None):
    """Pose e["chg"] sur chaque fiche de la collection : l'écart en % entre son prix (à l'unité) du moment et celui du dernier relevé d'avant
    aujourd'hui (rien si elle n'était pas relevée). Rend, par liste, [valeur au dernier relevé, valeur du moment] (fiches comptées)."""
    items = _load(VALUE_LOG_FILE, {}).get("items") or {}
    today, until = time.strftime("%Y-%m-%d"), trend_until()   # (période choisie dans les Réglages)

    def ref_of(r):
        return trend_ref_row((r or {}).get("rows"), today, until, unit=lambda x: x[1] / max(1, x[2]))   # (relevés douteux écartés)
    lists, seen = {}, set()
    cache, ih = cache if cache is not None else _load(CACHE_FILE, {}), _load(HISTORY_FILE, {}).get("items") or {}   # (fiches sans relevé d'avant : comp_chg)
    for e in enriched:
        if kinds.get(e.get("list_id")) != "collection" or e.get("kind") == "part":
            continue
        seen.add(e["id"])
        orig = bool(e.get("set_orig") and e.get("attached_to"))
        q = max(1, int(e.get("quantity", 1) or 1))
        v = (e.get("own_total") if orig else e.get("total_value")) or 0
        if not orig:
            lists.setdefault(e["list_id"], [0.0, 0.0])[1] += v
        mp = mkt_pair(e, cache, ih, today, until)   # (MON EXEMPLAIRE sur l'historique réel du marché — 21/11 soir)
        if mp and v > 0 and not e.get("no_estimate"):
            unit = v / q
            r0 = mp[1] + (unit - mp[0]) if unit >= mp[0] else unit * mp[1] / mp[0]   # (ce jour-là : le marché + mes ajouts ; exemplaire incomplet / décoté : en proportion)
            if r0 > 0.004:
                e["_chg_mine"] = round((unit - r0) / r0 * 100, 1)
        ref = ref_of(items.get(e["id"]))
        if not ref:   # pas de relevé d'avant (fiche ajoutée ou copiée depuis) : d'après ses composantes
            c = comp_chg(e, cache, ih, until)
            if c is not None:
                e["chg"] = c
            continue
        if _vl_counted(ref[1:]):
            lists.setdefault(ref[3], [0.0, 0.0])[0] += ref[1]
        u0 = ref[1] / max(1, ref[2])
        if u0 > 0.004 and not e.get("no_estimate"):
            e["chg"] = round((v / q - u0) / u0 * 100, 1)
    for e in enriched:   # (variation de mon exemplaire sur l'historique réel : elle l'emporte sur celle des seuls relevés de ma fiche — 21/11 soir)
        if "_chg_mine" in e:
            e["chg"] = e.pop("_chg_mine")
    for iid, r in items.items():   # fiches parties depuis le dernier relevé : dans la valeur d'avant
        if iid in seen or (r.get("gone") and r["gone"] < today):
            continue
        ref = ref_of(r)
        if ref and _vl_counted(ref[1:]):
            lists.setdefault(ref[3], [0.0, 0.0])[0] += ref[1]
    return {k: [round(a, 2), round(b, 2)] for k, (a, b) in lists.items()}


def cote_trends(enriched, cache):
    """Fiche : variation de chaque COTE (neuve, d'occasion) depuis le dernier relevé d'avant aujourd'hui (history.json) →
    info["cote_chg"] = {"new": %, "used": %} (sur une copie de « info » : le cache n'est pas touché)."""
    ih = _load(HISTORY_FILE, {}).get("items") or {}
    today, until = time.strftime("%Y-%m-%d"), trend_until()

    def ref_of(pts, col):   # relevé de comparaison (période des Réglages ; sinon le premier connu)
        r = trend_ref_row(pts, today, until, lambda x: len(x) > col and x[col] is not None)
        return r[col] if r else None
    for e in enriched:
        if e.get("kind") not in ("set", "fig", None) or not isinstance(e.get("info"), dict):
            continue
        mfs = e["info"].get("minifigs")
        if (e.get("kind") or "set") == "set" and isinstance(mfs, list) and mfs:   # ses figurines : la variation du prix affiché sur leur vignette
            out_f = []
            for f in mfs:
                f = dict(f) if isinstance(f, dict) else f
                if isinstance(f, dict) and f.get("id"):
                    cur, col = (f["used"], 2) if f.get("used") is not None else (f.get("value"), 1)
                    ref = ref_of(ih.get("fig:" + str(f["id"])), col)
                    if ref and cur is not None and ref > 0.004:
                        f["chg"] = round((cur - ref) / ref * 100, 1)
                out_f.append(f)
            e["info"] = {**e["info"], "minifigs": out_f}
        key = cache_key(e)
        pts = ih.get(key)
        if not pts:
            continue
        info = cache.get(key) or {}
        fig = e.get("kind") == "fig"
        out = {}
        for name, col, cur in (("new", 1, info.get("value") if fig else info.get("new_value")), ("used", 2, fig_used(e["number"]) if fig else info.get("used_value"))):
            ref = None
            for p_ in pts:
                if p_[0] < today and p_[col] is not None:
                    ref = p_[col]
            if ref and cur is not None and ref > 0.004:
                out[name] = round((cur - ref) / ref * 100, 1)
        if out:
            e["info"] = {**e["info"], "cote_chg": out}


def variations(list_param="", since=""):
    """« Comprendre les variations » : ce qui a fait bouger la valeur de la liste affichée entre un jour passé (relevé du matin) et maintenant.
    Rend {"from", "to", "v0", "v1", "total", "lines": [{"d": écart, "t": type, "txt", "id", "num"}], "approx", "first", "sums"}."""
    db, cache = load_db(), _load(CACHE_FILE, {})
    kinds = list_kinds(db)
    enriched = [enrich(i, cache, kinds) for i in db["items"]]
    try:
        vl_record(db["items"], enriched, cache, kinds)   # (le relevé du jour, s'il n'est pas encore fait)
    except Exception as e:
        print("Journal des valeurs :", e, flush=True)
    st = _vl_state(db["items"], enriched, cache, kinds)
    log = _load(VALUE_LOG_FILE, {})
    today = time.strftime("%Y-%m-%d")
    first = log.get("first") or today
    d0 = since if re.fullmatch(r"\d{4}-\d\d-\d\d", since or "") else today
    d0 = min(max(d0, first), today)
    col_lists = {l["id"] for l in db["lists"] if kinds.get(l["id"]) == "collection"}
    direct = list_param.startswith("direct:")
    lid = list_param[7:] if direct else list_param
    whole = not lid or lid not in col_lists
    if whole:
        scope = col_lists
    elif direct:
        scope = {lid}
    else:
        scope, grow = {lid}, True
        while grow:
            grow = False
            for l in db["lists"]:
                if l.get("parent_id") in scope and l["id"] not in scope and l["id"] in col_lists:
                    scope.add(l["id"]); grow = True
    ids_now = {i["id"] for i in db["items"]}

    def past(iid):
        r = (log.get("items") or {}).get(iid)
        if not r or (r.get("gone") and r["gone"] <= d0):
            return None
        row = None
        for x in r["rows"]:
            if x[0] <= d0:
                row = x
        return row[1:] if row else None
    fname = {}
    for k, info in cache.items():
        if isinstance(info, dict):
            for f in info.get("minifigs") or []:
                fname.setdefault(f["id"], f.get("name") or f["id"])
    q_ = lambda s: "« " + s + " »"
    lines, v0, v1 = [], 0.0, 0.0
    for iid in set(st) | set(log.get("items") or {}):
        a, s = past(iid), st.get(iid)
        b = s["row"] if s else None
        meta = s or (log.get("items") or {}).get(iid) or {}
        nm = q_(meta.get("n") or meta.get("num") or "?") + (f" ({meta['num']})" if meta.get("num") and meta.get("num") != meta.get("n") else "")
        in0, in1 = bool(a) and _vl_counted(a) and a[2] in scope, bool(b) and _vl_counted(b) and b[2] in scope
        if not in0 and not in1:
            continue
        if in0:
            v0 += a[0]
        if in1:
            v1 += b[0]
        ln = lambda d, t, txt: abs(d) >= 0.005 and lines.append({"d": round(d, 2), "t": t, "txt": txt, "id": iid if iid in ids_now else "", "num": meta.get("num") or ""})
        if in1 and not in0:
            ln(b[0], "add", ("Sortie de son set : " if a and not _vl_counted(a) else "Arrivée dans la liste : " if a else "Ajout de ") + nm)
        elif in0 and not in1:
            ln(-a[0], "del", ("Rangée dans un set (comptée avec lui) : " if b and not _vl_counted(b) else "Sortie de la liste : " if b else "Retrait de ") + nm)
        elif in0 and in1:
            d = b[0] - a[0]
            if abs(d) < 0.005:
                continue
            if a[1] != b[1]:
                ln(d, "mod", f"Quantité de {nm} : {a[1]} → {b[1]}")
                continue
            eff = []
            if a[3] is not None and b[3] is not None and abs(b[3] - a[3]) >= 0.005:
                what = "du prix des pièces de" if meta.get("k") == "custom" else "de la cote de"
                eff.append([(b[3] - a[3]) * b[1], "cote", f"{'Hausse' if b[3] > a[3] else 'Baisse'} {what} {nm} ({_eur(a[3])} → {_eur(b[3])})"])
            fa, fb = a[4] or {}, b[4] or {}
            for fid in set(fa) | set(fb):
                p0, c0 = fa.get(fid) or [None, 0]
                p1, c1 = fb.get(fid) or [None, 0]
                fn = q_(fname.get(fid, fid)) + f" ({fid})"
                if c0 == c1 and p0 is not None and p1 is not None:
                    if abs(p1 - p0) >= 0.005:   # la figurine qui pèse sur le set : c'est elle qu'on cite
                        role = "manquante" if c1 < 0 else "en plus"
                        eff.append([(p1 - p0) * c1, "cote", f"{'Hausse' if p1 > p0 else 'Baisse'} de la cote de la figurine {fn} ({_eur(p0)} → {_eur(p1)}), {role} dans {nm}"])
                else:
                    e_ = (p1 or 0) * c1 - (p0 or 0) * c0
                    eff.append([e_, "mod", f"Figurine {fn} {'ajoutée à' if c1 > c0 else 'retirée de'} {nm}"])
            rest = d - sum(x[0] for x in eff)
            tot = sum(abs(x[0]) for x in eff)
            if eff and tot and abs(rest) <= max(0.05, 0.15 * abs(d)):   # (plancher, décote… : réparti sur les causes trouvées)
                for x in eff:
                    x[0] += rest * abs(x[0]) / tot
                rest = 0
            for x in eff:
                ln(*x)
            if abs(rest) >= 0.005:
                ln(rest, "mod", f"Fiche modifiée : {nm} (figurines, pièces, état, boîte…)")
    approx = d0 < (log.get("exact_from") or today)
    if whole and approx:   # avant le journal : l'écart avec le relevé réel du jour (fiches supprimées ou modifiées depuis)
        h0 = ((_load(HISTORY_FILE, {}).get("collection") or {}).get(d0) or {}).get("value")
        if h0 is not None and abs(h0 - v0) >= 0.5:
            lines.append({"d": round(v0 - h0, 2), "t": "other", "txt": "Autres changements non détaillés (fiches supprimées, déplacées ou modifiées avant le début du journal)", "id": "", "num": ""})
            v0 = h0
    lines.sort(key=lambda x: -abs(x["d"]))
    sums = {}
    for x in lines:
        sums[x["t"]] = round(sums.get(x["t"], 0) + x["d"], 2)
    return {"from": d0, "to": today, "v0": round(v0, 2), "v1": round(v1, 2), "total": round(v1 - v0, 2), "lines": lines[:400], "more": max(0, len(lines) - 400),
            "approx": approx, "first": first, "exact_from": log.get("exact_from") or today, "sums": sums}


def _at(points, day):
    """Valeur d'une courbe [[date, valeur], …] à une date (interpolation linéaire), None avant le premier point."""
    if not points or day < points[0][0]:
        return None
    if day >= points[-1][0]:
        return points[-1][1]
    import datetime as dt
    for (d0, v0), (d1, v1) in zip(points, points[1:]):
        if d0 <= day <= d1:
            a, b, x = (dt.date.fromisoformat(z) for z in (d0, d1, day))
            span = (b - a).days or 1
            return v0 + (v1 - v0) * (x - a).days / span
    return points[-1][1]


def collection_history(list_id=""):
    """Valeur de la collection actuelle dans le temps : chaque set / minifig suit l'évolution de sa valeur BrickEconomy,
    ramenée à son estimation d'aujourd'hui (occasion, figurines…). Mois par mois, avec la prévision."""
    import datetime as dt
    db, cache, kinds = load_db(), _load(CACHE_FILE, {}), list_kinds()
    scope = None
    if list_id:   # une liste et toutes ses sous-listes
        scope, grow = {list_id}, True
        while grow:
            grow = False
            for l in db["lists"]:
                if l.get("parent_id") in scope and l["id"] not in scope:
                    scope.add(l["id"]); grow = True
    today = dt.date.today()
    months = []
    y, m = today.year - 4, today.month
    while (y, m) <= (today.year + 3, today.month):
        months.append(f"{y:04d}-{m:02d}-01")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    now = today.isoformat()
    past = [d for d in months if d <= now] + [now]
    future = [d for d in months if d > now]
    tot_past, tot_fut, tot_new = [0.0] * len(past), [0.0] * len(future), [0.0] * len(past)
    with_hist = without = 0
    for it in db["items"]:
        if kinds.get(it["list_id"]) != "collection" or it.get("kind") == "part" or (scope and it["list_id"] not in scope):
            continue
        e = enrich(it, cache, kinds)
        val = e.get("total_value") or 0
        info = cache.get(cache_key(it)) or {}
        hist, fc = info.get("history") or [], info.get("forecast") or []
        if it.get("kind") == "custom" and len(it.get("value_hist") or []) >= 2:   # MOC : ses propres relevés (avant : premier relevé)
            vh, q = it["value_hist"], it.get("quantity", 1) or 1
            for k, d in enumerate(past):
                v = (_at(vh, d) if d >= vh[0][0] else vh[0][1]) * q
                tot_past[k] += v
                tot_new[k] += v
            for k in range(len(future)):
                tot_fut[k] += val
            continue
        cur = _at(hist, now) if hist else None
        if not cur:   # pas d'historique (MOC, set pas encore relu…) : valeur constante
            without += 1 if it.get("kind") != "custom" else 0
            for k in range(len(past)):
                tot_past[k] += val
                tot_new[k] += val
            for k in range(len(future)):
                tot_fut[k] += val
            continue
        with_hist += 1
        ratio = val / cur
        allp = hist + fc
        qn = it.get("quantity", 1) or 1
        for k, d in enumerate(past):
            v = _at(hist, d)
            tot_past[k] += (v or 0) * ratio   # pas encore sorti à cette date : rien
            tot_new[k] += (v or 0) * qn       # valeur neuve réelle (BrickEconomy)
        for k, d in enumerate(future):
            v = _at(allp, d)
            tot_fut[k] += (v if v is not None else cur) * ratio
    snaps = sorted(((d, x["value"]) for d, x in (_load(HISTORY_FILE, {}).get("collection") or {}).items()))
    return {"estimated": [[d, round(v, 2)] for d, v in zip(past, tot_past)],
            "new": [[d, round(v, 2)] for d, v in zip(past, tot_new)],
            "forecast": [[now, round(tot_past[-1], 2)]] + [[d, round(v, 2)] for d, v in zip(future, tot_fut)],
            "snapshots": [] if scope else [[d, v] for d, v in snaps], "with_history": with_hist, "without_history": without}


BOX_CODES_FILE = os.path.join(DATA, "box_codes.json")   # code à 7 chiffres sous la boîte → figurine (tables publiées + codes appris)


def box_code_lookup(code):
    """Figurine d'une boîte de minifigs à collectionner, d'après son code ; avec les minifigs du catalogue qui correspondent."""
    e = _load(BOX_CODES_FILE, {}).get(code)
    if not e:
        return {"code": code, "found": False}
    figs = []
    if e.get("fig"):   # code appris : la minifig exacte
        try:
            f = get_fig(e["fig"])
            figs = [{"type": "fig", "number": f["number"], "name": f.get("name"), "image": f.get("image"), "value": f.get("value")}]
        except Exception:
            pass
    if not figs:   # table publiée : on cherche la minifig par son nom (et sa série)
        try:
            res, _ = sources.search_page(e["name"], 1)
            figs = [r for r in res if r.get("type") == "fig"][:6]
        except Exception:
            figs = []
    return {"code": code, "found": True, **e, "figs": figs}


EAN_FILE = os.path.join(DATA, "cache_ean.json")   # code-barres d'une boîte → n° de set (gardé pour toujours)


def ean_to_set(code):
    """Numéro de set d'après le code-barres de la boîte : catalogue BrickOwl (cherche aussi par code-barres),
    sinon base publique UPCitemdb. Mis en cache ; un échec est retenté après 7 jours."""
    c = _load(EAN_FILE, {})
    if code in c and (c[code].get("number") or time.time() - c[code].get("t", 0) < 7 * 86400):
        return c[code]
    num, title = None, ""
    try:   # (Brickset d'abord : mes sets connus, puis sa recherche — le code doit correspondre ; 21/11 soir)
        num = next((n for n, r in (_load(BRICKSET_FILE, {}) or {}).items() if str((r or {}).get("ean") or "").lstrip("0") == str(code).lstrip("0")), None) \
            or (sources.brickset_by_ean(code) if sources.brickset_key() and not DEMO else None)
    except Exception:
        num = None
    try:
        if num:
            raise StopIteration   # (trouvé par Brickset)
        page = sources._get_en("https://www.brickowl.com/search/catalog?query=" + code, timeout=20)
        for l in dict.fromkeys(re.findall(r'href="(/catalog/lego-[^"]+)"', page)):
            m = re.search(r"-set-(\d{3,7}(?:-\d+)?)$", l)
            if m:
                num = m.group(1) if "-" in m.group(1) else m.group(1) + "-1"
                title = l.rsplit("/", 1)[-1].replace("lego-", "").replace("-", " ").rsplit(" set ", 1)[0].title()
                break
    except Exception:
        pass
    if not num:
        try:
            req = urllib.request.Request("https://api.upcitemdb.com/prod/trial/lookup?upc=" + code,
                                         headers={"User-Agent": "Briquotheque/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                titles = [i.get("title") or "" for i in json.loads(r.read()).get("items", [])]
            for t in titles:
                m = re.search(r"(?<!\d)(\d{4,7})(?!\d)", t.replace(code, ""))
                if m:
                    num, title = m.group(1) + "-1", t
                    break
        except Exception:
            pass
    res = {"number": num, "title": title, "t": int(time.time())}
    with lock:
        c = _load(EAN_FILE, {}); c[code] = res; _save(EAN_FILE, c)
    return res


def guest_moc_lots(it):
    """Page publique : pièces d'un MOC (nom, couleur, quantité, photo), sans aucun prix."""
    pc, names, out = _parts_cache(), part_names(), []
    for x in it.get("moc_parts") or []:
        pn = (pc.get("bl:" + str(x.get("part"))) or {}).get("part_num") or x.get("part")
        nm = names.get(pn) or {}
        out.append({"name": x.get("name") or nm.get("name") or x.get("part"), "part": x.get("part"),
                    "color": x.get("color_fr") or FR_COLORS.get(x.get("color") or "", x.get("color") or ""),
                    "qty": x.get("qty", 1), "image": x.get("image") or nm.get("image") or ""})
    return out


def has_added_parts(item):
    """Pièces en plus (sans pièce d'origine) sur le set, la minifig seule ou une figurine du set — comme hasAddedParts (app.js)."""
    lists = [(item.get("set_mod") or {}).get("fig_swaps"), item.get("fig_swaps")] + \
        [m.get("fig_swaps") for m in (item.get("fig_mods") or {}).values() if isinstance(m, dict)]
    return any(not x.get("orig") for l in lists for x in _real_swaps(l))


def orig_fill(it, mfs, q, have, att):
    """Originales manquantes d'un set comblées par les figurines rangées dedans (même référence), les non modifiées d'abord — = origFill (app.js).
    → (have avec les comblées, {id: exemplaires qui comblent}, une originale qui comble est modifiée)."""
    fk = lambda n: (lambda m: m.group(1) + m.group(2) + m.group(3) if m else str(n or "").lower())(re.fullmatch(r"([a-z]+)0*(\d+)([a-z]?)", str(n or "").lower()))
    have, used, mod, mu = dict(have or {}), {}, False, {}
    if it.get("with_minifigs") is False:
        have = {f["id"]: 0 for f in mfs}
    figs = [a for a in att if not a.get("set_orig") and a.get("kind") == "fig"]
    for f in mfs:
        need = (f.get("qty", 1) or 1) * q - have.get(f["id"], 0)
        for a in sorted((a for a in figs if fk(a.get("number")) == fk(f["id"])), key=lambda a: 1 if _removals(a.get("fig_swaps")) else 0):
            if need <= 0:
                break
            t = min(int(a.get("quantity", 1) or 1) - used.get(a["id"], 0), need)
            if t <= 0:
                continue
            if _removals(a.get("fig_swaps")):   # modifiée : reste une ajoutée (« Amélioré »), l'originale ne compte pas « remplacée »
                mu[a["id"]] = mu.get(a["id"], 0) + t
            else:
                used[a["id"]] = used.get(a["id"], 0) + t
            need -= t
            have[f["id"]] = have.get(f["id"], 0) + t
            mod = mod or bool(_removals(a.get("fig_swaps")))
    return have, used, mu


def _swaps_only(item, keep):
    """Copie de la fiche avec seulement certaines pièces échangées (remplacements ou retraits) : sur le set, la figurine, ses figurines d'origine."""
    f = lambda l: [x for x in (l or []) if keep(x, l)]
    out = dict(item)
    if isinstance(item.get("set_mod"), dict):
        out["set_mod"] = {**item["set_mod"], "fig_swaps": f(item["set_mod"].get("fig_swaps"))}
    out["fig_swaps"] = f(item.get("fig_swaps"))
    out["fig_mods"] = {k: ({**m, "fig_swaps": f(m.get("fig_swaps"))} if isinstance(m, dict) else m) for k, m in (item.get("fig_mods") or {}).items()}
    return out


_is_rem = lambda x, l=None: bool(x.get("orig") and not x.get("new") and not x.get("acc"))
_is_rep = lambda x, l=None: bool(x.get("orig") and x.get("new")) or (_is_rem(x) and any(not y.get("orig") and y.get("new") for y in l or []))   # (retirée + une ajoutée dans la même liste : un remplacement, 17/11)


def guest_status(it, info, att):
    """Page publique : l'état d'une fiche, calculé comme itemStatus (app.js) — figurines rangées dans le set (att) comprises.
    → {mod, add_parts, fig_rep, fig_add, extra} ; la page en tire les mêmes étiquettes que la page privée."""
    kind = it.get("kind", "set")
    set_or_fig = kind in ("set", "fig")
    extra = [a for a in att if not a.get("set_orig")]
    if kind == "custom" and it.get("partial_set"):   # set partiel : les figurines de son set sont les siennes
        fk = lambda n: (lambda m: m.group(1) + m.group(2) + m.group(3) if m else str(n or "").lower())(re.fullmatch(r"([a-z]+)0*(\d+)([a-z]?)", str(n or "").lower()))   # = figKey (app.js)
        own = {fk(x) for x in (info.get("set_minifigs") or [])}
        extra = [a for a in extra if not (a.get("kind") == "fig" and fk(a.get("number")) in own)]
    fig_rep = fig_add = 0
    mfs = info.get("minifigs") or [] if kind == "set" else []
    q = max(1, int(it.get("quantity", 1) or 1))
    have = ({} if it.get("with_minifigs") is False else fig_have(it, mfs, q)) if mfs else {}
    have, used, fill_mod = orig_fill(it, mfs, q, have, extra)   # rangées qui comblent une originale manquante : des originales (= origFill, app.js)
    more = sum(max(0, have.get(f["id"], 0) - (f.get("qty", 1) or 1) * q) for f in mfs)   # figurines d'origine en plus (« comme celle du set ») : ajoutées aussi
    n = sum((a.get("quantity", 1) or 1) - used.get(a.get("id"), 0) - fill_mod.get(a.get("id"), 0) for a in extra) + more
    if n:
        miss = sum(max(0, (f.get("qty", 1) or 1) * q - have.get(f["id"], 0)) for f in mfs)
        fig_rep = min(miss, n)
        fig_add = n - fig_rep
    miss_all = sum(max(0, (f.get("qty", 1) or 1) * q - have.get(f["id"], 0)) for f in mfs)
    inc = False   # (« Incomplet » supprimé le 17/11, demande du propriétaire)
    fig_add += sum(fill_mod.values())   # ajoutées modifiées de même référence qu'une originale manquante : « Amélioré »
    return {"mod": set_or_fig and is_modified(_swaps_only(it, _is_rep), info.get("minifigs") or []), "inc": inc, "add_parts": set_or_fig and has_added_parts(it), "fig_rep": fig_rep, "fig_add": fig_add,
            "extra": len(extra)}


def guest_figs(it, info, wish, prices=False):
    """Minifigs montrées sur la page publique : celles que je possède vraiment (pas les manquantes,
    rien pour un set « sans figurines »), avec leur nombre. Liste de souhaits : celles du set."""
    mfs = info.get("minifigs") or []
    row = lambda f, q: {"id": f["id"], "name": f["name"], "image": f.get("image"), "qty": q,
                        **({"used": f.get("used") if f.get("used") is not None else f.get("value")} if prices else {})}   # prix : seulement si l'option est cochée
    if wish:
        return [row(f, f.get("qty", 1)) for f in mfs]
    if it.get("kind", "set") != "set" or not it.get("with_minifigs", True):
        return []
    have = fig_have(it, mfs)
    mods = it.get("fig_mods") or {}   # photo choisie pour une figurine du set : à la place de celle du catalogue
    return [{**row(f, have.get(f["id"], 0)), "image": (mods.get(f["id"]) or {}).get("photo_url") or f.get("image"),
             "mod": bool(_real_swaps((mods.get(f["id"]) or {}).get("fig_swaps"))),
             "base": (f.get("qty", 1) or 1) * max(1, int(it.get("quantity", 1) or 1))}   # nombre fourni par le set : au-delà, « ajoutées » (comme la page privée)   # figurine retouchée : « Modifiée » (comme la page privée)
            for f in mfs if have.get(f["id"], 0) > 0]


def inv_row_status(db, key, row, s):
    """Change l'état d'une ligne d'inventaire (sa couleur, sa pièce de remplacement et sa quantité restent)."""
    inv = (db.get("inventories") or {}).get(key)
    if not inv:
        return
    cur = inv.setdefault("rows", {}).get(row) or {}
    inv["rows"][row] = {**cur, "s": s}
    inv["updated"] = int(time.time())


def unlink_order(db, key, row):
    """La ligne n'est plus « commandée » (reçue, ou remise à commander) : la pièce quitte la liste À commander (ou sa quantité baisse)."""
    for it in list(db["items"]):
        links = it.get("inv_links") or []
        ln = next((x for x in links if x.get("inv") == key and x.get("row") == row), None)
        if not ln:
            continue
        it["inv_links"] = [x for x in links if x is not ln]
        it["quantity"] = (it.get("quantity", 1) or 1) - (ln.get("q") or 0)
        if it["quantity"] <= 0:
            db["items"].remove(it)
        else:
            it["updated_at"] = int(time.time())


def inv_mark_ok(db, key, part_num, color_id, qty):
    """Coche une pièce (reçue, ou prise ailleurs) dans l'inventaire d'un set ; renvoie le nom de l'inventaire, ou None."""
    hit = next((x for x in inventories_with_part(db, part_num, color_id) if x["key"] == key), None)
    if not hit:
        return None
    inv = db.setdefault("inventories", {}).setdefault(key, {"rows": {}, "created": int(time.time())})   # (created : une commande d'avant ne le valide jamais)
    try:
        q = max(1, min(9999, int(qty or 1)))
    except (TypeError, ValueError):
        q = 1
    row = {**(inv.setdefault("rows", {}).get(hit["row"]) or {}), "s": "ok", "q": q}
    if not hit["same_color"]:   # autre couleur que celle du set : la couleur retenue pour cette ligne
        row["c"] = int(color_id)
    inv["rows"][hit["row"]] = row
    inv["updated"] = int(time.time())
    return hit["name"]


def inventories_with_part(db, part_num, color_id):
    """Inventaires de sets dont la liste contient cette pièce (même couleur d'abord)."""
    pc, out = _parts_cache(), []
    for key, inv in (db.get("inventories") or {}).items():
        it = next((i for i in db["items"] if i["id"] == key), None)
        num = it["number"] if it else inv.get("set")
        if not num:   # inventaire d'un élément supprimé : ignoré
            continue
        rows = [r for r in (pc.get("inv:" + num) or []) + (inv.get("extra") or []) if r.get("part_num") == part_num]   # (lignes ajoutées comprises — 22/11)
        if not rows:
            continue
        sw, stt = {str(k): str(v) for k, v in (inv.get("swaps") or {}).items()}, inv.get("rows") or {}
        eff = lambda r: str((stt.get(f"{part_num}|{r['color_id']}") or {}).get("c")) if (stt.get(f"{part_num}|{r['color_id']}") or {}).get("c") is not None else sw.get(str(r["color_id"]), str(r["color_id"]))   # (couleur effective — 22/11)
        same = next((r for r in rows if eff(r) == str(color_id)), None)
        out.append({"key": key, "set": num, "name": inv.get("label") or fr_name(num) or inv.get("name") or num,
                    "row": f"{part_num}|{(same or rows[0])['color_id']}", "same_color": bool(same)})
    out.sort(key=lambda x: (not x["same_color"], x["name"]))
    return out


# ---------------------------------------------------------------- partage d'une fiche (lien secret, lecture seule, sans mot de passe)
SHARES_FILE = os.path.join(DATA, "shares.json")   # {jeton: {"item": id, "at": horodatage}}
_share_memo = {}   # jeton → (heure, contenu) : la page charge ses images sans tout recalculer


def hostable(i):
    """Élément auquel on peut rattacher des minifigs : un set, un set partiel ou un MOC (pas une figurine MOC)."""
    return i.get("kind", "set") == "set" or (i.get("kind") == "custom" and i.get("custom_type") != "fig") or (i.get("kind") == "fig" and bool(i.get("as_set")))


def view_hidden(i):
    """Fiche sans carte dans la vue générale : coche « Afficher dans la vue générale » décochée (hide_view) ; par défaut, une copie
    « Dupliquer puis modifier » (indiv) est masquée."""
    return bool(i["hide_view"]) if i.get("hide_view") is not None else bool(i.get("indiv"))


def childable(i):
    """Fiche qui peut être rangée dans un set (enfant) : une figurine du catalogue ou une figurine MOC — jamais un set, un set partiel,
    un set MOC, une pièce, ni une figurine « vue comme un set »."""
    return (i.get("kind") == "fig" and not i.get("as_set")) or (i.get("kind") == "custom" and i.get("custom_type") == "fig")


def links_fix(db):
    """Liens parent / enfant toujours cohérents — appelé à CHAQUE enregistrement de la collection (_save) ; ne supprime JAMAIS de fiche :
    - enfant = figurine ou figurine MOC ; parent = set, set partiel ou set MOC qui existe, qui n'est pas la fiche elle-même, et qui est
      dans la même sorte de liste (collection / liste de souhaits) ; sinon la fiche redevient seule (attached_to retiré) ;
    - marque « d'origine » (set_orig) seulement dans un vrai set du catalogue dont les figurines ont leurs fiches ; sinon retirée
      (la fiche compte alors pour elle-même : elle n'est plus dans la cote d'un set).
    Une fiche a un seul parent (attached_to) : 1 exemplaire = 1 fiche parent ; X exemplaires se partagent en lots (voir /attach).
    Rend le nombre de corrections."""
    items = db.get("items") or []
    by, kinds, n, cat = {i.get("id"): i for i in items}, list_kinds(db), 0, None
    for i in items:
        a = i.get("attached_to")
        if a:
            h = by.get(a)
            if not (childable(i) and h is not None and h is not i and hostable(h) and not childable(h)
                    and kinds.get(i.get("list_id"), "collection") == kinds.get(h.get("list_id"), "collection")):
                i.pop("attached_to", None)
                n += 1
        if i.get("indiv") and not i.get("attached_to"):   # exemplaire « à part » sorti de son set : une figurine ordinaire (avec sa carte)
            i.pop("indiv", None)
            n += 1
        if i.get("set_orig"):
            h = by.get(i.get("attached_to")) if i.get("attached_to") else None
            if h is None or h.get("kind", "set") != "set" or not h.get("fig_items"):
                i.pop("set_orig", None)
                n += 1
            else:   # (20/11) sa référence officielle doit être une figurine de ce set au catalogue ; sinon : figurine ajoutée (comptée pour son prix)
                if cat is None:
                    cat = _load(CACHE_FILE, {})
                mf = (cat.get(h.get("number") or "") or {}).get("minifigs")
                if mf and not any(isinstance(f, dict) and figkey_srv(f.get("id")) == figkey_srv(i.get("number")) for f in mf):
                    i.pop("set_orig", None)
                    n += 1
    return n


def figkey_srv(n):
    """Référence officielle d'une figurine, comparable (casse et zéros de tête du numéro ignorés : sw0001 = sw001 = SW1)."""
    m = re.fullmatch(r"([a-z]+)0*(\d+)([a-z]?)", str(n or "").strip().lower())
    return (m.group(1) + m.group(2) + m.group(3)) if m else str(n or "").strip().lower()


def dup_cancel_apply(db, new):
    """Annule une copie en attente (dup_pending) : elle disparaît, l'original (ou son set) retrouve son exemplaire. Rend True si annulée."""
    dp = (new or {}).get("dup_pending")
    if not dp:
        return False
    db["items"] = [i for i in db["items"] if i is not new]
    if dp.get("host"):
        host = next((i for i in db["items"] if i["id"] == dp["host"]), None)
        if host:
            if dp.get("counts") is None:
                host.pop("fig_counts", None)
            else:
                host["fig_counts"] = dp["counts"]
            host["missing_minifigs"] = dp.get("missing") or []
            orig_figs_sync(db, host, _load(CACHE_FILE, {}))
    elif dp.get("qty"):
        src = next((i for i in db["items"] if i["id"] == dp.get("from")), None)
        if src:
            src["quantity"] = dp["qty"]
    return True


def dup_pending_purge(max_age=3 * 3600):
    """Copies en attente oubliées (plus de max_age secondes) : annulées. Rend leur nombre."""
    with lock:
        db = load_db()
        old = [i for i in db["items"] if i.get("dup_pending") and int(time.time()) - int(i.get("added_at") or 0) > max_age]
        if not old:
            return 0
        backup_db("avant-copies-oubliees")
        for i in old:
            dup_cancel_apply(db, i)
        _save(DB_FILE, db)
        return len(old)


def links_check():
    """Au démarrage : liens parent / enfant remis d'aplomb s'il le faut (sauvegarde « avant-liens » d'abord ; rien n'est supprimé)."""
    with lock:
        db = load_db()
        n = links_fix(db)
        if n:
            backup_db("avant-liens")   # (copie du fichier tel qu'il était : rien n'est encore écrit)
            _save(DB_FILE, db)
        return n


def lego_on_sale(info):
    """Prix public LEGO d'un set ENCORE EN VENTE (ni retiré, ni à venir), sinon None : affiché dans le bouton LEGO.com des pages publiques."""
    av = str((info or {}).get("availability") or "")
    if not av or av.lower() == "retired" or re.search(r"pending|upcoming|coming soon", av, re.I):
        return None
    return (info or {}).get("retail") or None


SHARE_PRICE_KEYS = ("value", "unit_value", "approx", "purchase_price", "retail", "new_value", "used_value", "fig_value", "fig_used", "zones")   # masqués quand le lien est réglé « sans prix »


def share_item(tok):
    sh = _load(SHARES_FILE, {}).get(tok) if re.fullmatch(r"[\w-]{16,64}", tok or "") else None
    if not sh:
        return None, None, None
    db = load_db()
    return next((i for i in db["items"] if i["id"] == sh.get("item")), None), db, sh


def set_fig_entry(it, db, fid):
    """Minifig présente dans ce set (d'après le catalogue et mes quantités), ou None."""
    info = _load(CACHE_FILE, {}).get(cache_key(it)) or {}
    return next((f for f in guest_figs(it, info, list_kinds(db).get(it["list_id"]) == "wishlist") if f["id"] == fid), None), info


def share_head(page, tok):
    """Page d'une fiche partagée : son titre porte le NOM de la fiche (« AT-AT — Briquothèque »). C'est ce titre que montrent les aperçus de lien
    des messageries (WhatsApp, SMS, e-mail…), qui lisent la page sans exécuter son script. Lien inactif ou erreur : page inchangée."""
    try:
        it, db, sh = share_item(tok)
        if not it:
            return page
        memo = _share_memo.get(tok)
        if memo and time.time() - memo[0] < 30 and memo[1].get("_id") == it["id"] and memo[1].get("_u") == it.get("updated_at"):
            name = memo[1].get("name")
        else:
            base = share_fig_payload(it, db, sh.get("fig")) if sh.get("fig") else share_payload(it, db)
            if base is None:
                return page
            _share_memo[tok] = (time.time(), {**base, "_id": it["id"], "_u": it.get("updated_at")})   # (la page demandera ces données juste après)
            name = base.get("name")
        name = re.sub(r"\s+", " ", str(name or "")).strip()[:140]
        if not name:
            return page
        t = (name + " — Briquothèque").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        head = f'<title>{t}</title>\n<meta property="og:title" content="{t}">\n<meta property="og:site_name" content="Briquothèque">\n<meta property="og:type" content="website">'
        return page.replace("<title>Fiche partagée — Briquothèque</title>".encode("utf-8"), head.encode("utf-8"), 1)
    except Exception:
        return page


def merged_hosts(it, db):
    """Figurine seule : les sets où la même figurine est rangée d'origine sans rien à elle (pièces, accessoires, autre nom) — la fiche unique les compte."""
    fk = lambda n: (lambda x: x.group(1) + x.group(2) + x.group(3) if x else str(n or "").lower())(re.fullmatch(r"([a-z]+)0*(\d+)([a-z]?)", str(n or "").lower()))
    by = {i["id"]: i for i in db["items"]}
    out = []
    for x in db["items"]:
        h = by.get(x.get("attached_to"))
        if not h or not x.get("set_orig") or fk(x.get("number")) != fk(it.get("number")):
            continue
        mo = (h.get("fig_mods") or {}).get(x["number"]) or {}
        if mo.get("fig_swaps") or mo.get("accessories") or (mo.get("name") and mo["name"] != (it.get("display_name") or mo["name"])):
            continue
        out.append((h, int(x.get("quantity", 1) or 1)))
    return out


def share_fig_payload(it, db, fid):
    """Minifig d'un set partagée seule : sa photo, ses prix, ses pièces, le set qui la contient."""
    f, info = set_fig_entry(it, db, fid)
    if not f:
        return None
    mod = (it.get("fig_mods") or {}).get(fid) or {}
    fi = _load(CACHE_FILE, {}).get("fig:" + fid) or {}
    used = fig_used(fid)
    new = fi.get("value") if fi.get("value") is not None else next((x.get("value") for x in info.get("minifigs") or [] if x.get("id") == fid), None)
    unit = used if used is not None else new
    return {"kind": "fig", "number": fid, "name": (with_fr_fig({"name": f.get("name")}) or {}).get("name") or fid, "theme": info.get("theme"), "year": fi.get("years") or info.get("year"),
            "quantity": f.get("qty", 1), "condition": it.get("condition"), "image": f.get("image"), "photo_url": mod.get("photo_url") or "", "photo": "",
            "value": round(unit * f.get("qty", 1), 2) if unit is not None else None, "fig_value": new, "fig_used": used,
            "modified": bool(mod.get("fig_swaps")), "swaps": _share_swaps(mod.get("fig_swaps")), "fig_parts": True, "set_parts": False,
            "minifigs": [], "accessories": [], "moc_lots": [], "portion": 100,
            "in_set": {"number": it.get("number"), "name": it.get("display_name") or fr_name(it.get("number")) or info.get("name")}}


def _share_swaps(lst):
    return [{"k": x.get("k"), "orig": x.get("orig"), "new": x.get("new"), "acc": bool(x.get("acc"))} for x in lst or [] if not x.get("free")]


def share_payload(it, db):   # (+ les exemplaires rangés dans mes sets, pour la fiche unique d'une figurine)
    out = _share_payload0(it, db)
    try:
        if out is not None and it.get("kind") == "fig" and not it.get("attached_to") and not bo_behav("noMerge"):
            hs = merged_hosts(it, db)
            if hs:
                out["also_sets"] = [{"number": h.get("number"), "name": h.get("display_name") or fr_name(h.get("number")) or h.get("number"), "qty": q} for h, q in hs]
                out["quantity_total"] = int(it.get("quantity", 1) or 1) + sum(q for _, q in hs)
    except Exception as e:
        print("Partage, exemplaires dans les sets :", e, flush=True)
    return out


def _share_payload0(it, db):
    """Tout ce qu'affiche la fiche, sauf le privé : ni notes, ni tâches, ni listes (le prix d'achat est montré)."""
    cache, kinds = _load(CACHE_FILE, {}), list_kinds(db)
    e = enrich(it, cache, kinds)
    info = e.get("info") or {}
    kind = it.get("kind", "set")
    wish = kinds.get(it["list_id"]) == "wishlist"
    figs = []
    if hostable(it):   # set (ou set partiel) : ses minifigs et celles qui y ont été rattachées
        mods = it.get("fig_mods") or {}
        figs = [{**f, "swaps": _share_swaps((mods.get(f["id"]) or {}).get("fig_swaps"))} for f in guest_figs(it, info, wish)]
        for a in db["items"]:
            if a.get("attached_to") != it["id"] or a.get("set_orig"):   # (figurines d'origine du set : déjà dans guest_figs — jamais deux fois)
                continue
            ac = cache.get(cache_key(a)) or {}
            figs.append({"id": a["number"] if a.get("kind") == "fig" else "moc-" + a["id"], "added": True, "qty": a.get("quantity", 1),
                         "name": (a.get("custom_name") if a.get("kind") == "custom" else ac.get("name")) or a["number"],
                         "image": a.get("photo_url") or (a.get("image") if a.get("kind") == "custom" else ac.get("image")),
                         "swaps": _share_swaps(a.get("fig_swaps")), "parts": a.get("kind") == "fig"})
        for f in figs:
            f.setdefault("parts", True)
    up = lambda u: u if isinstance(u, str) and re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", u) else ""
    return {
        "kind": kind, "custom_type": it.get("custom_type"), "catalog_set": bool(it.get("catalog_set")), "partial_set": bool(it.get("partial_set")),
        "bl_zone": bl_zone_of(kind, it.get("number")),
        "number": it.get("number"), "name": it.get("display_name") or (it.get("custom_name") if kind == "custom" else None) or info.get("name") or it.get("number"),
        "theme": info.get("theme"), "subtheme": info.get("subtheme"), "year": info.get("year") or info.get("years"), "pieces": info.get("pieces"),
        "minifig_count": info.get("minifig_count"), "wish": wish,
        "quantity": it.get("quantity", 1), "condition": it.get("condition"), "with_minifigs": it.get("with_minifigs", True),
        "missing": len(it.get("missing_minifigs") or []), "has_box": it.get("has_box"), "no_plan": it.get("no_plan"), "unbuilt": it.get("unbuilt"),
        "portion": it.get("portion", 100), "portion_note": it.get("portion_note", ""), "modified": is_modified(it),
        "st": {**guest_status(it, info, [a for a in db["items"] if a.get("attached_to") == it["id"]]),   # étiquettes de la fiche, comme la fiche privée (Modifié, Amélioré…)
               "add_parts": kind in ("set", "fig") and has_added_parts(it)},
        "tags": list(it.get("tags") or []), "tags_off": list(it.get("tags_off") or []),   # étiquettes ajoutées à la main / calculées retirées
        "photo": it.get("photo", ""), "photo_url": up(it.get("photo_url")) or (it.get("photo_url") if IMG_OK.match(str(it.get("photo_url") or "")) else ""),
        "image": (it.get("image") if kind == "custom" else info.get("image")),
        "part_image": next((x.get("image") for x in (it.get("parts") or []) if x.get("owned") and x.get("image")), None) if it.get("portion", 100) < 100 else None,
        "value": None if e.get("no_estimate") else e.get("total_value"), "unit_value": None if e.get("no_estimate") else e.get("unit_value"), "approx": bool(e.get("approx")),
        "purchase_price": it.get("purchase_price"),
        "retail": info.get("retail"), "new_value": info.get("new_value"), "used_value": info.get("used_value"),
        "fig_value": info.get("value") if kind == "fig" else None, "fig_used": info.get("used") if kind == "fig" else None,
        "zones": price_zones(kind, it.get("number"), info),   # drapeau de la zone des prix neuf / occasion
        "availability": info.get("availability"), "retirement": info.get("retirement"), "releasing": info.get("releasing"),
        "accessories": [{"name": a.get("name"), "photo": up(a.get("photo"))} for a in it.get("accessories") or []],
        "alts": [{"photo": up(u), "name": ((it.get("alt_names") or [])[k:k + 1] or [""])[0]} for k, u in enumerate(it.get("alt_photos") or []) if up(u)],
        "main_name": it.get("main_name") or "",
        "moc_lots": guest_moc_lots(it) if kind == "custom" and it.get("moc_parts") else [],
        "minifigs": [{k: f.get(k) for k in ("id", "name", "image", "qty", "base", "added", "swaps", "parts")} for f in figs],   # base : nombre fourni par le set (au-delà : « ajoutées »)
        "lego_url": lego_urls().get(it.get("number")) if kind == "set" else None,   # page produit LEGO.com connue (comme les autres fiches)
        "lego_price": lego_on_sale(info) if kind == "set" else None,   # prix public, dans le bouton LEGO.com (set encore en vente)
        "swaps": _share_swaps(it.get("fig_swaps")) if kind == "fig" else [],
        "set_parts": kind == "set" and bool(it.get("number")),
        "fig_parts": kind == "fig",
    }


def share_fig_parts(it, db, fid):
    """Pièces d'une minifig de la fiche partagée (la fiche elle-même si c'est une minifig)."""
    if fid == "self":
        if it.get("kind") != "fig":
            return None
        host = it
    else:
        host = next((a for a in db["items"] if a.get("attached_to") == it["id"] and a.get("kind") == "fig" and a["number"] == fid), None)
        if not host and not any(f["id"] == fid for f in guest_figs(it, (_load(CACHE_FILE, {}).get(cache_key(it)) or {}), list_kinds(db).get(it["list_id"]) == "wishlist")):
            return None
    rb = (host or {}).get("rb_fig") or ((it.get("fig_mods") or {}).get(fid) or {}).get("rb_fig")   # version choisie dans l'application
    if not rb:
        c = rb_fig_candidates(host["number"] if host else fid)
        if not (c and c[0].get("sure")):
            return []
        rb = c[0]["fig_num"]
    return rb_fig_parts(rb) + (cmf_accessories(host) if host else [])


# ---------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    server_version = "Briquotheque/1.0"

    # -- reverse proxy (nginx) : adresse réelle du visiteur et HTTPS
    def _from_proxy(self):
        """La connexion vient-elle d'un proxy de confiance (BQ_PROXIES) ou de la machine elle-même ?
        Sinon, ses en-têtes d'adresse ne sont pas crus (un appareil du réseau ne peut pas se faire passer pour un autre)."""
        try:
            a = ipaddress.ip_address(self.client_address[0])
        except ValueError:
            return False
        return a.is_loopback or str(a) in TRUSTED_PROXIES

    def client_ip(self):
        direct = self.client_address[0]
        if not self._from_proxy():
            return direct
        cand = (self.headers.get("X-Real-IP") or "").strip()
        if not cand:   # dernière adresse = celle ajoutée par nginx (les précédentes viennent du visiteur)
            xff = [x.strip() for x in (self.headers.get("X-Forwarded-For") or "").split(",") if x.strip()]
            cand = xff[-1] if xff else ""
        try:
            return str(ipaddress.ip_address(cand)) if cand else direct
        except ValueError:
            return direct

    def is_https(self):
        return self._from_proxy() and (self.headers.get("X-Forwarded-Proto") or "").lower() == "https"

    def public_origin(self):
        """Adresse de l'application telle que le navigateur la voit (derrière le proxy : https + nom de domaine).
        Sert à l'adresse de retour de la connexion Instagram (à déclarer chez Meta)."""
        host = ((self.headers.get("X-Forwarded-Host") if self._from_proxy() else "") or self.headers.get("Host") or "").split(",")[0].strip()
        if not re.fullmatch(r"[\w.-]+(:\d{1,5})?", host):
            host = "localhost"
        return ("https" if self.is_https() else "http") + "://" + host

    def redirect_to(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass

    def log_request(self, code="-", size="-"):
        """Journal des accès (data/access.log) ; rien de sensible n'est noté."""
        try:
            path = urlparse(self.path).path
            line = (f"{time.strftime('%Y-%m-%d %H:%M:%S')} {self.client_ip()} via {self.client_address[0]} "
                    f"{'https' if self.is_https() else 'http'} {self.command} {path} {code}\n")
            logf = os.path.join(DATA, "access.log")
            if os.path.exists(logf) and os.path.getsize(logf) > 5 * 1024 * 1024:
                os.replace(logf, logf + ".1")
            with open(logf, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass

    # -- utilitaires
    def send_json(self, obj, status=200, prefetch=True):
        if status == 200 and prefetch:
            try:
                urls = image_urls_in(obj)
                if urls:
                    prefetch_images(urls)   # recherche, fiche, inventaire, ajout… : images en local tout de suite
            except Exception:
                pass
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        gz = len(body) > 1400 and "gzip" in (self.headers.get("Accept-Encoding") or "").lower()   # compressé : ~7 fois plus léger
        if gz:
            import gzip
            body = gzip.compress(body, compresslevel=5)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if gz:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def error(self, msg, status=400):
        self.send_json({"erreur": msg}, status)

    def body(self):
        if hasattr(self, "_body"):
            return self._body
        n = min(max(0, int(self.headers.get("Content-Length") or 0)), self.MAX_BODY)
        self._body = self.rfile.read(n) if n else b""
        return self._body

    def json_body(self):
        try:
            return json.loads(self.body() or b"{}")
        except json.JSONDecodeError:
            return {}

    def send_ia(self, f, title, dl, back, back_t, download):
        """Condensé pour IA d'un guide : la page « Tout copier » (ia_page), ou le texte en téléchargement (.txt)."""
        txt = open(f, encoding="utf-8").read()
        data = txt.encode("utf-8") if download else ia_page(txt, title, dl, back, back_t)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8" if download else "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if download:
            self.send_header("Content-Disposition", "attachment; filename=" + os.path.basename(f).replace("-ia.md", "-condense-ia.txt"))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path, ctype=None, cache=False, edit=None):
        with open(path, "rb") as f:
            data = f.read()
        if edit:   # (page complétée avant l'envoi : titre d'une fiche partagée)
            data = edit(data)
        if path.endswith(".html") and b"<html" in data[:400] and b"data-ui=" not in data[:400]:   # thème de l'application (Réglages) : sur chaque page
            data = data.replace(b"<html", f'<html data-ui="{ui_theme()}"'.encode(), 1)
        if DEMO and os.path.basename(path) == "index.html":   # démonstration : bandeau et réglages réduits
            ra = int(os.environ.get("BQ_DEMO_RESET_AT") or 0)   # heure de la prochaine remise à zéro (compte à rebours)
            data = data.replace(b"</head>", f"<script>window.BQ_DEMO = true; window.BQ_DEMO_RESET = {ra};</script></head>".encode(), 1)
        if not DEMO and path.endswith(".html") and os.path.basename(path) not in ("admin.html", "setup.html", "page.html", "backoffice-aide.html", "guide-utilisateur.html", "guide-technique.html", "back-office.html", "aide-memoire.html", "aide-memoire-perso.html"):   # back office : personnalisation
            if COPIE:
                data = data.replace(b"</head>", b"<script>window.BO_COPIE = true;</script></head>", 1)
            data = backoffice.inject(data, public=not auth.valid_session(self.token()), off="bo=off" in (urlparse(self.path).query or ""))
        if perso and os.path.basename(path) in ("index.html", "admin.html"):   # (extensions locales)
            data = perso.inject(data, os.path.basename(path))
        ct = ctype or mimetypes.guess_type(path)[0] or "application/octet-stream"
        texty = ct.startswith("text/") or ct in ("application/javascript", "application/json", "image/svg+xml", "application/manifest+json", "application/xml") \
            or path.endswith((".js", ".css", ".html", ".json", ".svg", ".webmanifest"))
        if texty:   # (texte : ETag + compression — 22/11)
            etag = '"' + hashlib.md5(data).hexdigest()[:20] + '"'
            if etag in (self.headers.get("If-None-Match") or ""):   # le navigateur a déjà cette version : rien à renvoyer
                self.send_response(304)
                self.send_header("ETag", etag)
                self.send_header("Cache-Control", "public, max-age=604800" if cache else "no-cache")
                self.end_headers()
                return
            if len(data) > 1400 and "gzip" in (self.headers.get("Accept-Encoding") or "").lower():
                gz = _gz_cache.get(etag)
                if gz is None:
                    import gzip
                    gz = gzip.compress(data, compresslevel=6)
                    if len(_gz_cache) > 40:
                        _gz_cache.clear()
                    _gz_cache[etag] = gz
                data = gz
                self.send_response(200)
                self.send_header("Content-Encoding", "gzip")
                self.send_header("Vary", "Accept-Encoding")
            else:
                self.send_response(200)
            self.send_header("ETag", etag)
        else:
            self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        if cache:
            self.send_header("Cache-Control", "public, max-age=604800")
        else:   # pages et scripts : toujours la dernière version après une mise à jour (vérifiée par l'ETag)
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    # -- authentification
    def token(self):
        return auth.token_from_cookie(self.headers.get("Cookie"))

    def demo_route(self):
        """Serveur principal : /demo ouvre la démonstration (cookie), /demo/quitter la referme ; avec le cookie, tout est relayé."""
        if DEMO:
            return False
        p = urlparse(self.path).path
        if not DEMO_SITE:   # démonstration publique désactivée (par défaut) : /demo n'existe pas, le cookie est ignoré
            return False
        if p in ("/demo", "/demo/", "/demo/quitter"):
            out = p != "/demo/quitter"
            if out and auth.valid_session(self.token()):   # connecté à sa collection : pas de démo
                self.send_response(302)
                self.send_header("Location", "/?demo=non")
                self.send_header("Set-Cookie", self.demo_cookie(False))
                self.send_header("Content-Length", "0")
                self.end_headers()
                return True
            self.send_response(302)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", self.demo_cookie(out))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return True
        if p.startswith("/s/"):   # fiche partagée : toujours la vraie, même avec le cookie de la démo
            return False
        c = SimpleCookie()
        try:
            c.load(self.headers.get("Cookie") or "")
        except Exception:
            pass
        if not (c.get("bq_demo") and c["bq_demo"].value == DEMO_COOKIE):   # anciens cookies (« 1 », 30 jours) : ignorés
            return False
        if auth.valid_session(self.token()):   # connecté : toujours sa collection, jamais la démo
            return False
        # en démo, TOUT va à la démo, même connecté : rien de ce qui s'y fait ne touche la collection privée
        # (pour revenir à sa collection : « Quitter la démo », /demo/quitter)
        n = int(self.headers.get("Content-Length") or 0)
        if n > self.MAX_BODY:
            self.error("Envoi trop volumineux", 413)
            return True
        body = self.rfile.read(n) if n > 0 else None
        hdrs = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "connection", "cookie", "x-real-ip", "x-forwarded-for", "content-length")}
        hdrs["X-Real-IP"] = self.client_ip()
        if self.is_https():
            hdrs["X-Forwarded-Proto"] = "https"
        try:
            conn = http.client.HTTPConnection("127.0.0.1", DEMO_PORT, timeout=180)
            conn.request(self.command, self.path, body, hdrs)
            r = conn.getresponse()
            data = r.read()
        except Exception:
            msg = "La démonstration redémarre, réessayez dans une minute. <a href='/demo/quitter'>Quitter la démo</a>".encode()
            self.send_response(503)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return True
        self.send_response(r.status)
        for k, v in r.getheaders():
            if k.lower() not in ("transfer-encoding", "connection", "content-length", "server", "date", "set-cookie"):
                self.send_header(k, v)
        if not urlparse(self.path).path.startswith("/api/"):
            self.send_header("Set-Cookie", self.demo_cookie(True))   # démo utilisée : encore une heure
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)
        return True

    MAX_BODY = 16 * 1024 * 1024

    def demo_cookie(self, on):
        """Cookie de la démo : 1 h (prolongée à chaque page de la démo) ; vide = sortie."""
        return (f"bq_demo={DEMO_COOKIE if on else ''}; Path=/; HttpOnly; SameSite=Lax; Max-Age={3600 if on else 0}"
                + ("; Secure" if self.is_https() else ""))

    def end_headers(self):
        for _c in self.__dict__.pop("_bo_cookies", ()):   # (back office : la session de l'application, rouverte par son mot de passe)
            self.send_header("Set-Cookie", _c)
        self.send_header("X-Bq", "1")   # signature : le mode hors ligne (sw.js) distingue une erreur de l'appli d'une erreur du proxy (serveur éteint)
        self.send_header("X-Frame-Options", "SAMEORIGIN")   # pas d'affichage dans le cadre d'un autre site
        # CSP : pas d'objets embarqués, pas de <base> détourné, formulaires envoyés seulement à l'appli
        self.send_header("Content-Security-Policy", "frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Permissions-Policy", "camera=(self), microphone=(), geolocation=(), payment=(), usb=()")   # caméra : photos et codes-barres
        if self.is_https():   # HTTPS : le navigateur n'essaiera plus jamais l'adresse en clair (6 mois)
            self.send_header("Strict-Transport-Security", "max-age=15552000")
        super().end_headers()

    def cross_site(self):
        """Modification demandée par une autre page que l'application (formulaire piégé, autre site ou sous-domaine) ?"""
        if self.command in ("GET", "HEAD"):
            return False
        # navigateurs actuels : en-tête Sec-Fetch-Site (les plus anciens sont protégés par le cookie SameSite=Lax)
        return (self.headers.get("Sec-Fetch-Site") or "").lower() in ("cross-site", "same-site")

    def guard(self):
        """Renvoie True si la requête a été refusée (adresse bannie, autre site, trop gros, ou non connecté)."""
        p = urlparse(self.path).path
        if COPIE:   # copie de travail : jamais publiée — réseau local (ou la machine elle-même) seulement, même derrière un proxy
            _adr = [self.client_address[0]] + [x.strip() for h in ("X-Real-IP", "X-Forwarded-For") for x in (self.headers.get(h) or "").split(",") if x.strip()]
            try:
                _local = all((lambda i: i.is_private or i.is_loopback or i.is_link_local)(ipaddress.ip_address(x)) for x in _adr)
            except ValueError:
                _local = False
            if not _local:
                self.error("Copie de travail : accessible seulement depuis le réseau local", 403)
                return True
        if self.cross_site():
            self.error("Requête refusée : elle ne vient pas de l'application", 403)
            return True
        try:
            if int(self.headers.get("Content-Length") or 0) > self.MAX_BODY:
                self.error("Envoi trop volumineux", 413)
                return True
        except ValueError:
            self.error("Requête invalide", 400)
            return True
        if DEMO:   # démonstration : pas de connexion, mais pas de mot de passe ni de clé à changer, et un débit limité
            if demo_limited(self.client_ip(), p):
                self.error("Démo : trop de requêtes, patientez une minute.", 429)
                return True
            if p in DEMO_BLOCKED or (p.startswith("/api/settings") and self.command == "POST"):   # réglages : pas dans la démo
                self.error("Désactivé dans la démo", 403)
                return True
            if p == "/login":
                self.send_response(302); self.send_header("Location", "/")
                self.send_header("Content-Length", "0"); self.end_headers()
                return True
            return False
        if auth.is_banned(self.client_ip()):
            body = "Accès bloqué : trop de tentatives échouées depuis cette adresse.".encode()
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return True
        if not auth.is_configured():   # installation neuve : rien n'est accessible avant la création du mot de passe
            if p in ("/setup", "/api/setup", "/icon.svg", "/manifest.json"):
                return False
            if p.startswith("/api/"):
                self.error("Installation à terminer : créez d'abord le mot de passe", 401)
            else:
                self.send_response(302); self.send_header("Location", "/setup"); self.send_header("Content-Length", "0"); self.end_headers()
            return True
        if p.startswith(("/backoffice", "/api/bo/", "/admin")):   # back office : sa propre porte (mot de passe à part, voir bo_guard)
            return self.bo_guard(p)
        public = p in ("/login", "/api/login", "/api/ping", "/style.css", "/flags.woff2", "/manifest.json", "/icon.svg", "/bo.js", "/bo-max.js") or (perso is not None and p in perso.PUBLIC) or p in ("/wishlist", "/collection", "/nouveautes", "/a-surveiller", "/calendrier") \
            or p.startswith(("/wishlist/", "/collection/", "/s/", "/nouveautes/", "/a-surveiller/", "/bo-img/", "/p/"))
        if auth.valid_session(self.token()):
            return False
        if public:
            if public_limited(self.client_ip(), p):   # visiteur non connecté : pas plus de N requêtes par minute
                self.error("Trop de requêtes : patientez une minute.", 429)
                return True
            return False
        if p.startswith("/api/"):
            self.error("Connexion requise", 401)
        else:
            self.send_response(302)
            self.send_header("Location", "/login")
            self.send_header("Content-Length", "0")
            self.end_headers()
        return True

    def bo_guard(self, p):
        """Zone du back office (/backoffice…, /api/bo/…, fichiers /admin*). Renvoie True si la requête a été refusée.
        Le back office a son propre mot de passe (backoffice_acces.py) : la session de l'application n'y suffit pas."""
        app_ok, bo_ok = auth.valid_session(self.token()), backoffice_acces.logged(self)
        if p == "/api/bo/values":   # appelée par le site lui-même (champs personnalisés enregistrés depuis une fiche)
            ok = app_ok or bo_ok
        elif p in ("/backoffice", "/backoffice/", "/backoffice/secours", "/api/bo/acces", "/api/bo/login", "/api/bo/setup", "/api/bo/x/rescue", "/admin", "/admin/", "/admin/secours", "/admin.html"):
            ok = True   # pages d'entrée (elles demandent elles-mêmes le mot de passe) et anciennes adresses (redirigées)
        elif p in ("/admin.js", "/admin-plus.js", "/admin-max.js", "/admin.css"):   # fichiers de l'écran du back office
            ok = bo_ok or app_ok
        else:
            ok = bo_ok
        if ok:
            if not (app_ok or bo_ok) and public_limited(self.client_ip(), p):
                self.error("Trop de requêtes : patientez une minute.", 429)
                return True
            return False
        if p.startswith("/api/"):
            self.send_json({"erreur": "Connexion au back office requise", "besoin": "bo"}, 401)
        else:
            self.redirect_to("/backoffice")
        return True

    def auth_routes(self, p):
        if p == "/api/setup" and self.command == "POST":   # première installation : {password, code}
            ip = self.client_ip()
            if auth.is_configured():
                self.error("L'installation est déjà faite", 403)
                return True
            if auth.too_many_attempts(ip):
                self.error("Trop de tentatives. Réessayez dans 15 minutes.", 429)
                return True
            b = self.json_body()
            if auth.is_public(ip) and str(b.get("code") or "").strip().lower() != (_setup["code"] or ""):   # depuis Internet : le code de la console
                auth.record_failure(ip, "code d'installation")
                self.error("Code d'installation incorrect : il est affiché dans la console du serveur (et dans data/setup_code.txt).", 403)
                return True
            pwd = str(b.get("password") or "")
            if len(pwd) < 10:
                self.error("Le mot de passe doit faire au moins 10 caractères")
                return True
            auth.set_password(pwd)
            try:
                os.remove(os.path.join(DATA, "setup_code.txt"))
            except OSError:
                pass
            token = auth.new_session(True)
            body = b'{"ok": true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie", auth.cookie_header(token, remember=True, secure=self.is_https()))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return True
        if p == "/api/setup":   # GET : état de l'installation (pour la page /setup)
            self.send_json({"configured": auth.is_configured(), "code_needed": auth.is_public(self.client_ip())})
            return True
        if p == "/setup":
            if auth.is_configured():
                self.send_response(302); self.send_header("Location", "/"); self.send_header("Content-Length", "0"); self.end_headers()
            else:
                self.send_file(os.path.join(STATIC, "setup.html"))
            return True
        if p == "/api/login":
            ip = self.client_ip()
            if auth.too_many_attempts(ip):
                self.error("Trop de tentatives. Réessayez dans 15 minutes.", 429)
                return True
            self.json_body_cache = self.json_body()
            pwd = self.json_body_cache.get("password") or ""
            if not auth.check_password(pwd):
                auth.record_failure(ip)
                time.sleep(1)
                self.error("Mot de passe incorrect", 401)
                return True
            auth.clear_failures(ip)
            remember = self.json_body_cache.get("remember", True) is not False
            token = auth.new_session(remember)
            body = b'{"ok": true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie", auth.cookie_header(token, remember=remember, secure=self.is_https()))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return True
        if p == "/api/logout":
            auth.end_session(self.token())
            body = b'{"ok": true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie", auth.cookie_header("", clear=True, secure=self.is_https()))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return True
        if p == "/api/password":
            b = self.json_body()
            if not auth.check_password(b.get("current") or ""):
                auth.record_failure(self.client_ip(), "mot de passe actuel")   # compte comme un essai raté
                time.sleep(1)
                self.error("Mot de passe actuel incorrect", 403)
                return True
            new = b.get("new") or ""
            if len(new) < 10:
                self.error("Le nouveau mot de passe doit faire au moins 10 caractères")
                return True
            auth.set_password(new)  # déconnecte toutes les autres sessions
            token = auth.new_session()
            body = b'{"ok": true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie", auth.cookie_header(token, secure=self.is_https()))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return True
        return False

    # -- accès invité (lecture seule, sans prix)
    def send_big(self, path, ctype, name=""):
        """Gros fichier (plan PDF) : envoyé par morceaux, avec reprise (Range) pour les lecteurs PDF."""
        size = os.path.getsize(path)
        start, end, status = 0, size - 1, 200
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", (self.headers.get("Range") or "").strip())
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            status = 206
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Cache-Control", "private, max-age=31536000")
        if name:
            self.send_header("Content-Disposition", "inline; filename*=UTF-8''" + urllib.parse.quote(name))
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_hd(self, u, alt=""):
        """La plus grande version connue d'une image de catalogue (téléchargée une fois, gardée sur le serveur)."""
        if not IMG_OK.match(u or ""):
            return self.error("URL non autorisée", 403)
        alt = [alt] if re.fullmatch(r"https://cdn\.rebrickable\.com/media/sets/fig-\d+\.jpg", alt or "") else []
        hds = alt + hd_candidates(u)
        for c in hds:   # copie locale d'abord (sans internet : aucune attente)
            if os.path.exists(img_path(c)):
                path, ctype = cache_image(c)
                return self.send_file(path, ctype, cache=True)
        for c in hds:
            try:
                path, ctype = cache_image(c)
                return self.send_file(path, ctype, cache=True)
            except Exception:
                continue
        try:   # repli sur l'image d'origine (ou sa source de secours) : pas gardé dans le navigateur (la HD viendra plus tard)
            path, ctype = cache_any(u)
            return self.send_file(path, ctype, cache=False)
        except Exception:
            return self.error("Image indisponible", 404)

    def share(self, tok, sub, q):
        """Fiche partagée : cette fiche seule, en lecture (zoom, minifigs et leurs pièces, pièces du set)."""
        if DEMO:
            return self.error("Page introuvable", 404)
        if sub in ("", "/"):
            return self.send_file(os.path.join(STATIC, "share.html"), edit=lambda page: share_head(page, tok))
        it, db, sh = share_item(tok)
        if not it:
            return self.error("Ce lien de partage n'est plus actif", 404)
        sfig = sh.get("fig")   # minifig d'un set partagée seule
        memo = _share_memo.get(tok)
        if memo and time.time() - memo[0] < 30 and memo[1].get("_id") == it["id"] and memo[1].get("_u") == it.get("updated_at"):
            data = memo[1]
        else:
            base = share_fig_payload(it, db, sfig) if sfig else share_payload(it, db)
            if base is None:
                return self.error("Ce lien de partage n'est plus actif", 404)
            data = {**base, "_id": it["id"], "_u": it.get("updated_at")}
            _share_memo[tok] = (time.time(), data)
        if sub == "/data":
            out = {k: v for k, v in data.items() if not k.startswith("_")}
            show = sh.get("prices") is not False   # prix affichés ou non : réglé par lien dans « 🔗 Partager », lu à chaque visite (le lien ne change pas)
            if not show:
                out.update({k: None for k in SHARE_PRICE_KEYS})
            return self.send_json({**out, "show_prices": show, "ig_user": ig_public_user()})
        if sub == "/img":
            return self.proxy_image((q.get("u") or [""])[0], (q.get("w") or [""])[0])
        if sub == "/hd":
            return self.send_hd((q.get("u") or [""])[0])
        if sub.startswith("/upload/"):   # seulement les photos de cette fiche
            hx = sub.rsplit("/", 1)[1]
            if "/api/upload/" + hx not in json.dumps(data):
                return self.error("Introuvable", 404)
            for ext, ctype in ((".jpg", "image/jpeg"), (".png", "image/png"), (".webp", "image/webp")):
                path = os.path.join(UPLOAD_DIR, hx + ext)
                if os.path.isfile(path):
                    th = upload_thumb(path, hx, (q.get("w") or [""])[0]) if "w" in q else None
                    return self.send_file(th or path, "image/jpeg" if th else ctype, cache=True)
            return self.error("Introuvable", 404)
        try:
            if sub == "/parts":
                if not data.get("set_parts"):
                    return self.error("Introuvable", 404)
                rows = inventory_rows(it["number"])
                prefetch_images([u for r in rows for u in (r.get("image"), r.get("part_image"))])
                return self.send_json([{k: r.get(k) for k in ("part_num", "bricklink", "name", "color_id", "color_name", "color_fr", "rgb", "trans", "quantity", "image", "part_image")} for r in rows])
            m = re.fullmatch(r"/fig/([\w.-]+)/parts", sub)
            if m:
                if sfig and m.group(1) != "self":
                    return self.error("Introuvable", 404)
                rows = share_fig_parts(it, db, sfig) if sfig else share_fig_parts(it, db, m.group(1))
                if rows is None:
                    return self.error("Introuvable", 404)
                return self.send_json(rows)
        except PermissionError:
            return self.error("Liste des pièces indisponible pour le moment", 503)
        except Exception:
            return self.error("Liste des pièces indisponible pour le moment", 502)
        return self.error("Introuvable", 404)

    def guest(self, sub, q, page="wishlist"):
        """Page publique fixe /wishlist : listes de collection et de souhaits en lecture seule."""
        if sub in ("", "/"):
            return self.send_file(os.path.join(STATIC, "guest.html"))
        if sub == "/parts":   # pièces des sets de la collection (ou d'une liste de collection), sans prix
            lid = (q.get("list") or [""])[0][:40]
            if lid and list_kinds().get(lid) != "collection":
                return self.send_json({"parts": [], "pending_sets": 0, "pending_names": 0})
            return self.send_json(collection_parts(lid, with_prices=False))
        if sub == "/figobjs":   # objets (armes, outils…) d'une minifig seule de la collection
            n = (q.get("n") or [""])[0].strip()[:40]
            db = load_db()
            kinds = list_kinds(db)
            it = next((i for i in db["items"] if i.get("kind") == "fig" and i.get("number") == n and kinds.get(i.get("list_id")) == "collection"), None)
            if not it:
                return self.send_json({"objs": []})
            try:
                return self.send_json({"objs": fig_objs_resolve(it)})
            except Exception:
                return self.send_json({"objs": []})
        if sub == "/partcolors":   # photo de la pièce dans chaque couleur
            pn = (q.get("p") or [""])[0].strip()[:40]
            try:
                return self.send_json({str(c["color_id"]): c.get("image") for c in part_colors(pn)["colors"]} if pn else {})
            except Exception:
                return self.send_json({})
        if sub == "/img":
            return self.proxy_image((q.get("u") or [""])[0], (q.get("w") or [""])[0])
        if sub.startswith("/upload/"):
            name = sub.rsplit("/", 1)[1]
            for ext, ctype in ((".jpg", "image/jpeg"), (".png", "image/png"), (".webp", "image/webp")):
                path = os.path.join(UPLOAD_DIR, name + ext)
                if os.path.isfile(path):
                    th = upload_thumb(path, name, (q.get("w") or [""])[0]) if "w" in q and re.fullmatch(r"[0-9a-f]{16,40}", name) else None   # grille
                    return self.send_file(th or path, "image/jpeg" if th else ctype, cache=True)
            return self.error("Introuvable", 404)
        # /data : listes de collection + souhaits, sans aucun prix ni note
        ip = self.client_ip()
        if not auth.valid_session(self.token()) and ip not in SELF_IPS and not ipaddress.ip_address(ip).is_loopback:   # ni mes visites (connecté), ni celles du serveur lui-même (tests)
            try:
                record_visit(page, ip)
            except Exception:
                pass
        db = load_db()
        cache = _load(CACHE_FILE, {})
        kinds = list_kinds(db)
        # « À surveiller » : seulement sur sa page à elle (/a-surveiller) ; jamais avec les autres listes
        watch = {l["id"]: "" for l in db["lists"] if l.get("gift")} if page == "watch" else {}
        pub_prices = _load(sources.SETTINGS_FILE, {}).get("public_prices") is True   # Réglages › Pages publiques : prix de la collection (non par défaut)
        _vlog, _today, _until = (_load(VALUE_LOG_FILE, {}).get("items") or {}) if pub_prices else {}, time.strftime("%Y-%m-%d"), trend_until()
        _chg_map = {}   # (variation de chaque fiche : le même calcul que la page privée — vl_trends, sur mon exemplaire — 22/11)
        if pub_prices:
            try:
                _pre = [enrich(i, cache, kinds) for i in db["items"]]
                vl_trends(_pre, kinds, cache)
                _chg_map = {x["id"]: x["chg"] for x in _pre if x.get("chg") is not None}
            except Exception as _e:
                print("Pages publiques : variations impossibles :", _e, flush=True)
        want = {"collection": ("collection",), "wishlist": ("wishlist",), "watch": ("wishlist",)}.get(page, ("collection",))   # chaque page : ses listes seules
        lists = [{"id": l["id"], "name": l["name"], "kind": l["kind"], "parent_id": "" if page == "watch" else l.get("parent_id", ""), **({"logo": l["logo"]} if l.get("logo") else {}), **({"emoji": l["emoji"]} if l.get("emoji") else {}), **({"hide_name": True} if l.get("hide_name") else {}), **({"show": l["show"]} if isinstance(l.get("show"), dict) else {}), **({"sub_logo": "self"} if l.get("sub_logo") == "self" else {}), **({"color": l["color"]} if l.get("color") else {}), **({"emoji_off": True} if l.get("emoji_off") else {})}
                 for l in db["lists"] if l["kind"] in want and bool(l.get("gift")) == (page == "watch")]
        ok = {l["id"] for l in lists}
        lurls = lego_urls()   # pages produits LEGO.com connues : lien sur la fiche (comme la page privée)
        items = []
        ids = {i["id"]: i for i in db["items"]}
        attached = {}   # set → minifigs qui lui ont été rattachées
        for it in db["items"]:
            host = ids.get(it.get("attached_to") or "")
            if host and hostable(host) and not it.get("set_orig"):   # (figurines d'origine : déjà parmi les figurines du set)
                attached.setdefault(host["id"], []).append(it)
        att_all = {}   # set → toutes ses figurines rangées (d'origine comprises) : leur valeur s'ajoute à celle du set, comme la page privée
        for it in db["items"]:
            host = ids.get(it.get("attached_to") or "")
            if host and hostable(host) and host is not it:
                att_all.setdefault(host["id"], []).append(it)
        guest_fig_like = lambda i: (i.get("kind") == "fig" and not i.get("as_set")) or (i.get("kind") == "custom" and i.get("custom_type") == "fig")
        for it in db["items"]:
            if it["list_id"] not in ok:
                continue
            host = ids.get(it.get("attached_to") or "")
            inset = bool(host and hostable(host) and host is not it)
            if inset and not guest_fig_like(it):
                continue   # montrée avec son set
            mods = (host.get("fig_mods") or {}).get(it["number"]) if inset and it.get("set_orig") else None   # figurine d'origine : ses retouches sont gardées dans le set
            mods = mods if isinstance(mods, dict) else None
            view = {**it, **({"fig_swaps": mods.get("fig_swaps") or []} if mods else {})}
            e = enrich(it, cache, kinds)
            if pub_prices and kinds.get(it["list_id"]) == "collection" and it["id"] in _chg_map:   # flèche de variation : celle de la page privée
                e["chg"] = _chg_map[it["id"]]
            if pub_prices and att_all.get(it["id"]) and e.get("total_value") is not None:   # set : avec ses figurines rangées (celles d'origine valent 0, déjà dans sa cote)
                e = {**e, "total_value": round(e["total_value"] + sum(enrich(a, cache, kinds).get("total_value") or 0 for a in att_all[it["id"]]), 2)}
            info = e.get("info") or {}
            items.append({
                "id": it["id"], **({"in": host["id"]} if inset else {}), **({"orig": True} if it.get("set_orig") else {}),
                **({"msig": fig_msig(it, host if inset else None)} if it.get("kind") == "fig" else {}), **({"hide": True} if view_hidden(it) else {}),   # figurine rangée dans un set : sa carte « Dans un set » (exemplaire à part : aucune carte)
                **({"fig_items": True} if it.get("fig_items") else {}),   # set converti : ses figurines d'origine sont des fiches à part
                **({"listed": True} if info.get("minifigs") else {}),   # liste des figurines du set connue (décompte comme la page privée)
                "list_id": it["list_id"], **({"watch": True} if it["list_id"] in watch else {}), "kind": it.get("kind", "set"), "number": it["number"],
                **({"partial_set": True} if it.get("partial_set") else {}), **({"catalog_set": True} if it.get("catalog_set") else {}),   # (« MOC uniquement » : pas les sets partiels)
                "quantity": it.get("quantity", 1), "condition": it.get("condition"), "bl_zone": bl_zone_of(it.get("kind", "set"), it["number"]),
                "with_minifigs": it.get("with_minifigs", True), "missing": len(it.get("missing_minifigs") or []),
                **({"has_box": bool(it.get("has_box")), "no_plan": bool(it.get("no_plan")), "also_used": bool(it.get("also_used"))} if it["list_id"] in watch else {}),
                **({"note": str(it.get("notes") or "")[:800]} if it["list_id"] in watch and (it.get("notes") or "").strip() else {}),   # (« À surveiller » : la note, seulement là — 22/11)
                "figs": sum(fig_have(it, info.get("minifigs") or []).values()) if it.get("kind", "set") == "set" and it.get("with_minifigs", True) else 0,
                "portion": it.get("portion", 100), "portion_note": it.get("portion_note", ""), "display_name": (mods or {}).get("name") or it.get("display_name", ""),
                "custom_type": it.get("custom_type"), "added_at": it.get("added_at"),
                "updated_at": max((host.get("fig_at") or {}).get(it["number"]) or 0, it.get("added_at") or 0) if inset and it.get("set_orig")
                              else max((it.get("own_at") or 0) if it.get("fig_touch") and it.get("fig_touch") == it.get("updated_at") else (it.get("updated_at") or 0), it.get("added_at") or 0), "photo": it.get("photo", ""),   # figurine d'origine : sa date à elle (comme la page privée)
                "photo_url": it.get("photo_url") or (mods or {}).get("photo_url") or "", "modified": is_modified(view),   # (ma photo d'abord, toujours)   # pièces retirées ou remplacées (pas seulement ajoutées)
                "accessories": it.get("accessories") or [], "catalog_set": bool(it.get("catalog_set")), "tags": list(it.get("tags") or []), "tags_off": list(it.get("tags_off") or []),
                "main_name": it.get("main_name") or "", "as_set": bool(it.get("as_set")), **(lambda lg: {"item_logo": lg} if lg else {})(it.get("item_logo") or ((host.get("item_logo") or "") if inset and not it.get("no_logo") else "")),   # (figurine d'un set : le logo du set, sauf retiré)
                "st": {**guest_status(view, info, attached.get(it["id"], [])),   # étiquettes de la carte (Modifié, Amélioré…), comme la page privée ;
                       "add_parts": it.get("kind", "set") in ("set", "fig") and has_added_parts(it)},   # « pièces ajoutées » : selon sa fiche seule (= hasAddedParts)
                **({"approx": bool(e.get("approx")), **({"chg": e["chg"]} if e.get("chg") is not None else {})} if pub_prices else {}),
                "alts": [{"photo": u, "name": ((it.get("alt_names") or [])[k:k + 1] or [""])[0]} for k, u in enumerate(it.get("alt_photos") or [])
                         if isinstance(u, str) and re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", u) and u not in (it.get("alt_hidden") or [])],   # décochées : pas dans la collection publique
                "partial_set": bool(it.get("partial_set")),   # (corrigé le 17/11 : cette ligne était cachée derrière le commentaire ci-dessus)
                **({"moc_lots": guest_moc_lots(it)} if it.get("kind") == "custom" and it.get("moc_parts") else {}),
                **({"fig_objs": guest_fig_objs(it)} if it.get("kind") == "fig" and kinds.get(it["list_id"]) == "collection" else {}),
                **({"lego_url": lurls[it["number"]]} if it.get("kind", "set") == "set" and it["number"] in lurls else {}),
                **({"lego_price": lego_on_sale(info)} if it.get("kind", "set") == "set" and lego_on_sale(info) else {}),   # prix public dans le bouton LEGO.com (set encore en vente)
                "image": next((x.get("image") for x in (it.get("parts") or []) if x.get("owned") and x.get("image")), None)
                         if it.get("portion", 100) < 100 else None,
                "info": {"name": info.get("name"), "theme": info.get("theme"), "year": info.get("year") or info.get("years"),
                         "pieces": info.get("pieces"), "image": info.get("image"), "availability": info.get("availability"),
                         "retirement": info.get("retirement"), "releasing": info.get("releasing"),
                         "minifig_count": info.get("minifig_count"),
                         **({"retail": info.get("retail"), "new_value": info.get("new_value"), "used_value": info.get("used_value"),
                             "zones": price_zones(it.get("kind", "set"), it.get("number"), info),   # drapeau de la zone des prix
                             "estimate": e["own_total"] if it.get("set_orig") and e.get("own_total") is not None else e.get("total_value"),   # figurine d'origine : son prix à elle (comme la page privée)
                             **({"box_add": e["box_add"]} if e.get("box_add") else {}),   # part de la boîte (ligne « réel » des vignettes)
                             **(lambda sf: {"sf": sf} if sf else {})(sf_prices(it["number"], info) if it.get("kind", "set") == "set" else None),   # prix sans figurines (bulles de la fiche, comme la page privée — 21/11)
                             **({"used": info.get("used") if info.get("used") is not None else info.get("value"), "new": info.get("value")} if it.get("kind") == "fig" else {})}
                            if kinds.get(it["list_id"]) == "wishlist" or pub_prices else {}),   # collection : seulement si l'option est cochée
                         "minifigs": guest_figs(it, info, kinds.get(it["list_id"]) == "wishlist", pub_prices) + [
                             {"id": a["number"] if a.get("kind") == "fig" else "moc-" + a["id"],
                              "name": (a.get("custom_name") if a.get("kind") == "custom" else (a.get("display_name") or (enrich(a, cache, kinds).get("info") or {}).get("name")
                                                                                           or (cache.get(cache_key(a)) or {}).get("name"))) or a["number"],   # nom français, comme la page privée
                              "image": a.get("image") if a.get("kind") == "custom" else hd_img((cache.get(cache_key(a)) or {}).get("image")),
                              "qty": a.get("quantity", 1), "added": True, "mod": is_modified(a),
                              **({"custom": True} if a.get("kind") == "custom" else {}),
                              **({"used": (enrich(a, cache, kinds).get("total_value") or 0) / max(1, a.get("quantity", 1) or 1)} if pub_prices else {})}
                             for a in attached.get(it["id"], [])]},
            })
        warm_fig_objs([i for i in db["items"] if i.get("kind") == "fig" and not i.get("set_orig") and kinds.get(i.get("list_id")) == "collection"])   # objets des figurines seules, en fond
        return self.send_json({"lists": lists, "items": items, "page": page, "owner": owner_name(), "app_color": _load(sources.SETTINGS_FILE, {}).get("app_color") or "", "ig_user": ig_public_user(), "show_prices": pub_prices, "ref_site": ref_site(), "site_logos": site_logos(), **({"trend": trend_cfg(), "trend_ref": vl_ref()} if pub_prices and not bo_behav("noTrend") else {}), **({"no_pub_nav": True} if bo_behav("noPubNav") else {}), **({"no_merge": True} if bo_behav("noMerge") else {})})   # (figurines identiques non regroupées : comme la page privée)

    # -- routes
    def do_GET(self):
        prio_seen(urlparse(self.path).path)   # (priorité à l'écran — 22/11)
        """Mode « fiche ouverte » pour /api/set/<n> et /api/fig/<n> (sauf ?refresh) : réponse tout de suite, relectures en fond."""
        u0 = urlparse(self.path)
        _quick.on = bool(re.fullmatch(r"/api/(?:set|fig)/[\w.-]+", u0.path)) and "refresh" not in parse_qs(u0.query)
        try:
            return self._do_GET()
        finally:
            _quick.on = False

    def _do_GET(self):
        if self.demo_route() or self.guard():
            return
        u = urlparse(self.path)
        p, q = u.path, parse_qs(u.query)
        if p in ("/setup", "/api/setup") and self.auth_routes(p):   # première installation
            return
        if not DEMO and p.startswith(("/backoffice", "/api/bo/", "/bo-img/", "/p/", "/admin")) and p not in ("/admin.js", "/admin-plus.js", "/admin-max.js", "/admin.css"):   # back office
            return self.bo_get(p, q)
        if DEMO and (p.startswith(("/backoffice", "/admin", "/bo-img/", "/p/", "/api/bo/")) or p in ("/bo.js", "/bo-plus.js", "/bo-max.js", "/page.html", "/backoffice-aide.html")):   # démonstration : aucun back office
            return self.error("Page introuvable", 404)
        m = re.fullmatch(r"/s/([\w-]{16,64})(/|/data|/img|/hd|/parts|/fig/[\w.-]+/parts|/upload/[0-9a-f]{16,40})?", p)
        if m:   # fiche partagée (lien secret)
            return self.share(m.group(1), m.group(2) or "", q)
        if p.startswith("/s/"):
            return self.error("Page introuvable", 404)
        m = re.fullmatch(r"/a-surveiller(/|/data|/img|/upload/[0-9a-f]{16,40})?", p)
        if m:   # « 👀 À surveiller » : elle seule, en lecture, sans les notes
            return self.guest(m.group(1) or "", q, "watch")
        if p.startswith("/a-surveiller/"):
            return self.error("Page introuvable", 404)
        if p == "/calendrier":   # page publique : les nouveautés, ouvertes sur le calendrier des sorties
            return self.send_file(os.path.join(STATIC, "nouveautes.html"))
        m = re.fullmatch(r"/nouveautes(/|/data|/img)?", p)
        if m:   # nouveautés lego.com, publiques : lecture seule, tout (rien de ma collection, de mes masqués ni de mes thèmes)
            sub = m.group(1) or ""
            if sub == "/img":
                return self.proxy_image((q.get("u") or [""])[0], (q.get("w") or [""])[0])
            if sub == "/data":
                return self.send_json({**novelties_public(), "owner": owner_name(), "ig_user": ig_public_user()})
            return self.send_file(os.path.join(STATIC, "nouveautes.html"))
        if p.startswith(("/nouveautes/", "/cadeaux")):   # /cadeaux : supprimée (« À surveiller » est sur la page publique)
            return self.error("Page introuvable", 404)
        m = re.fullmatch(r"/(?:wishlist|collection)(/|/data|/img|/parts|/partcolors|/figobjs|/upload/[0-9a-f]{16,40})?", p)
        if m:   # page publique : /wishlist ouvre la liste de souhaits, /collection la collection
            return self.guest(m.group(1) or "", q, "collection" if p.startswith("/collection") else "wishlist")
        if p.startswith(("/wishlist/", "/collection/")):
            return self.error("Page introuvable", 404)
        if p == "/login":
            if auth.valid_session(self.token()) and "bo=apercu" not in (u.query or ""):   # bo=apercu : aperçu dans le back office
                self.send_response(302); self.send_header("Location", "/")
                self.send_header("Content-Length", "0"); self.end_headers()
                return
            return self.send_file(os.path.join(STATIC, "login.html"))
        if p == "/api/ping":   # l'application vérifie qu'elle est en ligne
            return self.send_json({"ok": True})
        if p == "/login.html":
            return self.error("Introuvable", 404)
        try:
            if p == "/api/offline-pack":   # paquet hors ligne (fiches jamais ouvertes) : caches seulement, voir offline_pack()
                return self.send_json(offline_pack(), prefetch=False)   # (sans télécharger les centaines d'images citées : le serveur n'a qu'un processeur)
            if p == "/api/lists":
                return self.send_json(lists_payload())   # (calcul : lists_payload, préchauffé après chaque enregistrement — 22/11)
            if p == "/api/search":
                query = (q.get("q") or [""])[0].strip()
                if len(query) < 2:
                    return self.send_json([])
                paged = "page" in q   # « chercher plus » : {results, more}, page après page
                try:
                    pnum = max(1, min(50, int((q.get("page") or ["1"])[0])))
                except ValueError:
                    pnum = 1
                if paged and pnum > 1:   # pages suivantes : sets seulement, sans enrichissement
                    try:
                        res, more = sources.search_page(query, pnum)
                    except Exception as e:
                        return self.error(f"BrickEconomy ne répond pas : {e}", 502)
                    return self.send_json({"results": res, "more": more})
                more = False
                try:
                    if paged:
                        res, more = sources.search_page(query, 1)
                    else:
                        res = sources.search(query)
                except Exception:   # catalogue des prix injoignable : sets et minifigs par Rebrickable (API officielle), référence BrickLink (22/11)
                    res = fallback_search(query)
                    return self.send_json({"results": res, "more": False, "be_down": True} if paged else res)
                en = sources.translate_fr(query)
                if en and en.lower() != query.lower():   # recherche en français : on cherche aussi la traduction
                    try:
                        seen = {(r["type"], r["number"]) for r in res}
                        res += [r for r in sources.search(en) if (r["type"], r["number"]) not in seen]
                    except Exception:
                        pass
                figs = [r for r in res if r.get("type") == "fig"][:40]   # années de toutes les minifigs (tri du plus récent)
                if figs:   # années et sets d'origine des minifigs
                    import concurrent.futures as cf
                    def det(r):
                        try:
                            f = get_fig(r["number"]); r["years"] = f.get("years"); r["sets"] = (f.get("sets") or [])[:4]
                        except Exception:
                            pass
                    ex = cf.ThreadPoolExecutor(8)
                    cf.wait([ex.submit(det, r) for r in figs], timeout=6)   # au plus 6 s : le reste finit en arrière-plan (en cache pour la suite)
                    ex.shutdown(wait=False)
                if sources.FIG_RE.match(query) and not any(r["number"].lower() == query.lower() for r in res):
                    try:
                        f = get_fig(query.lower())
                        res.insert(0, {"type": "fig", "number": f["number"], "name": f["name"],
                                       "image": f["image"], "value": f.get("value")})
                    except Exception:
                        pass
                # nom français déjà connu (LEGO.com ou traduction) → on ajoute ces sets / minifigs aux résultats
                seen = {(r["type"], r["number"]) for r in res}
                extra = []
                for kind, num, name in fr_matches(query):
                    if (kind, num) in seen:
                        continue
                    try:
                        if kind == "set":
                            info = get_set(num)
                            extra.append({"type": "set", "number": num, "name": info.get("name"), "image": info.get("image"),
                                          "year": info.get("year"), "theme": info.get("theme"), "pieces": info.get("pieces"),
                                          "minifigs": info.get("minifig_count")})
                        else:
                            f = get_fig(num)
                            extra.append({"type": "fig", "number": f["number"], "name": f["name"], "image": f.get("image"),
                                          "value": f.get("value"), "years": f.get("years"), "sets": (f.get("sets") or [])[:4]})
                        seen.add((kind, num))
                    except Exception:
                        pass
                # résultats affichés en anglais (rapide) ; les noms français restent dans les fiches
                with_avail(extra + res)
                return self.send_json({"results": extra + res, "more": more} if paged else extra + res)
            if p == "/api/refresh":
                return self.send_json(refresh_status())
            m = re.fullmatch(r"/api/ean/(\d{8,14})", p)
            if m:   # code-barres d'une boîte de set → son numéro
                return self.send_json(ean_to_set(m.group(1)) or {"number": None, "unavailable": True})
            m = re.fullmatch(r"/api/boxcode/(\d{7})", p)
            if m:   # code scanné sous une boîte de minifig à collectionner
                return self.send_json(box_code_lookup(m.group(1)))
            if perso and p in perso.GET_PATHS:   # (extensions locales)
                return perso.handle_get(self, p, q)
            if p == "/api/variations":   # Statistiques → « Comprendre les variations » (liste affichée, depuis tel jour)
                return self.send_json(variations((q.get("list") or [""])[0][:60], (q.get("since") or [""])[0][:10]))
            m = re.fullmatch(r"/api/state-hist/([\w-]{6,40})", p)
            if m:   # « Le set » dans l'état du mien : le set MOINS ses figurines absentes, date par date, sur les vrais relevés (21/11 soir)
                db, cache = load_db(), _load(CACHE_FILE, {})
                it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                if not it:
                    return self.error("Introuvable", 404)
                info = cache.get(cache_key(it)) or {}
                ih = _load(HISTORY_FILE, {}).get("items") or {}
                col = 1 if it.get("condition") == "neuf" else 2
                q = max(1, int(it.get("quantity", 1) or 1))
                if it.get("with_minifigs") is False:
                    miss = {}
                    for f in info.get("minifigs") or []:
                        if f.get("id"):
                            miss[f["id"]] = miss.get(f["id"], 0) + int(f.get("qty") or 1)
                else:
                    miss = {}
                    for x in it.get("missing_minifigs") or []:
                        fid = x.get("id") if isinstance(x, dict) else x
                        if fid:
                            miss[fid] = miss.get(fid, 0) + 1
                    miss = {k: v / q for k, v in miss.items()}   # (manquantes : comptées sur l'ensemble des exemplaires → par exemplaire)

                def serie(key, c):
                    return [(r[0], r[c]) for r in ih.get(key) or [] if isinstance(r, list) and len(r) > c and isinstance(r[c], (int, float)) and r[c] > 0]
                sp = serie(it["number"], col)
                fp = {fid: (serie("fig:" + fid, 2) or serie("fig:" + fid, 1)) for fid in miss}

                def at(pts, d):
                    v = None
                    for d0, x in pts:
                        if d0 <= d:
                            v = x
                        else:
                            break
                    return v
                rows = []
                for d in sorted({d for d, _ in sp} | {d for pts in fp.values() for d, _ in pts}):
                    sv = at(sp, d)
                    fv = [at(fp[fid], d) for fid in miss]
                    if sv is None or any(v is None for v in fv):
                        continue   # (une donnée manque à cette date : rien n'est inventé)
                    rows.append([d, round(max(0.0, sv - sum(v * miss[fid] for v, fid in zip(fv, miss))), 2)])
                return self.send_json({"rows": rows, "figs": sum(miss.values())})
            m = re.fullmatch(r"/api/vlog/([\w-]{6,40})", p)
            if m:   # relevés de la valeur de MA fiche, à l'unité : [date, valeur] (graphique « Mon exemplaire » — 21/11 soir)
                r = (_load(VALUE_LOG_FILE, {}).get("items") or {}).get(m.group(1)) or {}
                return self.send_json({"rows": [[x[0], round(x[1] / max(1, x[2] or 1), 2)] for x in r.get("rows") or []
                                                if isinstance(x, list) and len(x) > 2 and isinstance(x[1], (int, float)) and x[1] > 0]})
            if p == "/api/history/collection":   # valeur de la collection dans le temps
                return self.send_json(collection_history((q.get("list") or [""])[0][:40]))
            if p in ("/guide-utilisateur/ia", "/guide-utilisateur/ia.txt"):   # « 🤖 Condensé pour IA » du guide utilisateur (même accès que le guide)
                f = os.path.join(ROOT, "docs", "wiki", "guide-utilisateur-ia.md")
                if not os.path.isfile(f):
                    return self.error("Guide pas encore généré (python3 docs/build_docs.py)", 404)
                return self.send_ia(f, "Guide utilisateur", "/guide-utilisateur/ia.txt", "/guide-utilisateur", "Guide utilisateur", p.endswith(".txt"))
            if p in ("/guide-technique/ia", "/guide-technique/ia.md"):   # « 🤖 Condensé pour IA » de la doc technique : connecté seulement, jamais dans la démo (PRIVÉ)
                f = os.path.join(ROOT, "docs", "wiki", "guide-technique-ia.md")
                if DEMO or not os.path.isfile(f):
                    return self.error("Page introuvable", 404)
                txt = open(f, encoding="utf-8").read()
                txt = re.sub(r"^<!--.*?-->\n", "", txt, count=1)   # (repère privé : pas dans le texte copié)
                if p.endswith(".md"):   # téléchargement (.txt)
                    data = txt.encode("utf-8")
                    ctype, disp = "text/plain; charset=utf-8", "attachment; filename=briquotheque-condense-ia.txt"
                else:   # la page : le texte, « Tout copier », « Télécharger »
                    data = ("""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Condensé pour IA — Briquothèque</title><link rel="icon" href="/icon.svg"><style>
body{margin:0;font:15px/1.45 system-ui,sans-serif;background:#111317;color:#e8eaed}header{position:sticky;top:0;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 14px;background:#1b1e24;border-bottom:1px solid #2c313a}
h1{font-size:17px;margin:0 auto 0 0}a,button{font:600 14px system-ui,sans-serif;color:#e8eaed;background:#262a31;border:1px solid #3a404a;border-radius:10px;padding:8px 12px;text-decoration:none;cursor:pointer}
button.main{background:#d01012;border-color:#d01012;color:#fff}p{margin:10px 14px;color:#9aa0a8;font-size:13.5px}textarea{box-sizing:border-box;width:calc(100% - 28px);height:calc(100vh - 140px);margin:0 14px 14px;background:#0b0d10;color:#e8eaed;border:1px solid #2c313a;border-radius:10px;padding:10px;font:12.5px/1.4 ui-monospace,monospace}
</style></head><body><header><h1>🤖 Condensé pour IA</h1><button type="button" class="main" id="cp">📋 Tout copier</button><a href="/guide-technique/ia.md">⬇ Télécharger (.txt)</a><a href="/guide-technique">← Doc technique</a></header>
<p>Copiez tout, puis collez-le au début de la conversation avec l'IA : elle connaîtra l'application et ses règles. Mis à jour à chaque regénération des guides. Privé : ne pas le publier.</p>
<textarea id="t" readonly spellcheck="false">""" + __import__("html").escape(txt) + """</textarea>
<script>document.getElementById("cp").onclick = async () => { const t = document.getElementById("t"), b = document.getElementById("cp");
  try { await navigator.clipboard.writeText(t.value); } catch { t.focus(); t.select(); document.execCommand("copy"); }
  b.textContent = "✔ Copié"; setTimeout(() => b.textContent = "📋 Tout copier", 2000); };</script></body></html>""").encode("utf-8")
                    ctype, disp = "text/html; charset=utf-8", ""
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                if disp:
                    self.send_header("Content-Disposition", disp)
                self.end_headers()
                self.wfile.write(data)
                return
            if p == "/aide-memoire":   # aide-mémoire (21/11) : la version du propriétaire (+ fonctions exclusives) si elle est là, jamais dans la démo
                fs_ = [os.path.join(ROOT, "docs", "wiki", n + ".html") for n in ((() if DEMO else ("aide-memoire-perso",)) + ("aide-memoire",))]
                f = next((x for x in fs_ if os.path.isfile(x)), None)
                return self.send_file(f) if f else self.error("Aide-mémoire pas encore généré (python3 docs/build_docs.py)", 404)
            m = re.fullmatch(r"/(guide-utilisateur|guide-technique)(?:/img/([\w-]{1,80}\.jpg))?", p)
            if m:   # guides en wiki (docs/wiki/*.html, écrits par docs/build_docs.py) : connecté seulement ; le technique : jamais dans la démo
                tech = m.group(1) == "guide-technique"
                if tech and DEMO:
                    return self.error("Page introuvable", 404)
                if m.group(2):   # ses captures (celles de la doc technique, « tech-… », ne sortent que par /guide-technique)
                    f = os.path.join(ROOT, "docs", "captures", m.group(2))
                    if (m.group(2).startswith("tech-") and not tech) or not os.path.isfile(f):
                        return self.error("Image introuvable", 404)
                    return self.send_file(f, cache=True)
                f = os.path.join(ROOT, "docs", "wiki", m.group(1) + ".html")
                if not os.path.isfile(f):
                    return self.error("Guide pas encore généré (python3 docs/build_docs.py)", 404)
                return self.send_file(f)
            if p == "/back-office/guide":   # (autre écriture de l'adresse)
                return self.redirect_to("/backoffice/guide")
            m = re.fullmatch(r"/api/docs/(guide|technique|backoffice)\.pdf", p)
            if m:   # anciens PDF : remplacés par les wikis
                return self.redirect_to({"guide": "/guide-utilisateur", "technique": "/guide-technique", "backoffice": "/backoffice/guide"}[m.group(1)])
            if p == "/api/docs":   # guides installés et leur date (liens des Réglages ; le technique : jamais dans la démo)
                out = {}
                for k, name in (("guide", "guide-utilisateur"), ("technique", "guide-technique"), ("backoffice", "back-office")):
                    path = os.path.join(ROOT, "docs", "wiki", name + ".html")
                    if os.path.isfile(path) and not (k == "technique" and DEMO):
                        out[k] = {"t": int(os.path.getmtime(path)), "size": os.path.getsize(path)}
                return self.send_json(out)
            if p == "/api/orders/extra":   # « Commandes » : les pièces / figurines commandées en plus (non attribuées) — 22/11
                ext_ = [] if DEMO else (_load(ORDERS_EXTRA, {}).get("items") or [])
                pc_, miss_ = _parts_cache(), set()   # (zoom : grande photo Rebrickable de la pièce dans sa couleur — 22/11)
                for e_ in ext_:
                    if e_.get("part_num") and e_.get("color_id") is not None:
                        l_ = pc_.get("pc:" + str(e_["part_num"]))
                        if l_ is None:
                            miss_.add(str(e_["part_num"]))
                        else:
                            e_["hd"] = next((x.get("image") for x in l_ if str(x.get("color_id")) == str(e_["color_id"]) and x.get("image")), "") or ""
                if miss_ and sources.rebrickable_key():
                    threading.Thread(target=lambda m=sorted(miss_): [part_colors(x) for x in m if not time.sleep(0.3)], daemon=True).start()
                return self.send_json({"items": ext_})
            if p == "/api/visits":   # compteur de la page publique (partie privée uniquement)
                return self.send_json(visit_stats())
            if p == "/api/settings":
                key = sources.rebrickable_key()
                st = _load(sources.SETTINGS_FILE, {})
                last = st.get("last_refresh")
                if not last:   # jamais actualisé en entier : date des prix les plus récents de la collection
                    db, cache = load_db(), _load(CACHE_FILE, {})
                    last = max([(cache.get(cache_key(i)) or {}).get("fetched_at") or 0 for i in db["items"]
                                if i.get("kind") not in ("custom", "part")] or [0]) or None
                return self.send_json({"bl_zones": {**sources.bl_zone_cfg(), "order": sources.bl_zone_order()},   # zones BrickLink réglées
                                       "public_prices": _load(sources.SETTINGS_FILE, {}).get("public_prices") is True,
                                       "legal_site": _load(sources.SETTINGS_FILE, {}).get("legal_site") or "",   # (mentions légales : éditeur et hébergement)
                                       "social": _load(sources.SETTINGS_FILE, {}).get("social") or {},   # (réseaux sociaux : pages publiques)
                                       "mod_discount": mod_discount(), "box_bonus": box_bonus(), "plan_cut": plan_cut(), "trend": trend_cfg(),
                                       "parts_pricing": {"running": _pp["busy"], **_ppg,
                                                         "last_done": _load(sources.SETTINGS_FILE, {}).get("parts_priced_at")},
                                       "last_refresh": last, "last_refresh_full": bool(st.get("last_refresh")), "bans": auth.list_bans(), "rebrickable": bool(key),
                                       "rebrickable_hint": ("…" + key[-4:]) if key and not DEMO else None,
                                       "brickowl": bool(sources.brickowl_key()), "brickowl_hint": ("…" + sources.brickowl_key()[-4:]) if sources.brickowl_key() and not DEMO else None,
                                       "brickset": bool(sources.brickset_key()), "brickset_hint": ("…" + sources.brickset_key()[-4:]) if sources.brickset_key() and not DEMO else None,
                                       "bricklink": bl_on(), "bricklink_hint": ("…" + sources.bricklink_keys()["token"][-4:]) if bl_on() else None,
                                       "bricklink_today": bl_today(), "bl_alert": None if DEMO else _bl_state["alert"],
                                       "public_ip": None if DEMO else _load(sources.SETTINGS_FILE, {}).get("public_ip"),   # (réglage : aide BrickLink)
                                       "owner_name": owner_name(),
                                       "bl_night": {**_load(BL_NIGHT_FILE, {}), "budget": price_cfg()["budget"], "hour": BL_BG_HOUR, "max": BL_DAY_MAX}, "prices": price_cfg(),
                                       "demo": None if DEMO or not DEMO_SITE else {"reset_at": int(_demo["reset_at"]) or None}})
            if p == "/api/part-inventories":   # où ranger une pièce reçue
                return self.send_json(inventories_with_part(load_db(), (q.get("p") or [""])[0], (q.get("c") or [""])[0]))
            if p == "/api/inventories":
                db = load_db()
                pc = _parts_cache()
                out = []
                for key, inv in (db.get("inventories") or {}).items():
                    it = next((i for i in db["items"] if i["id"] == key), None)
                    num = it["number"] if it else inv.get("set")
                    if not num or (not it and not key.startswith("set-")):
                        continue
                    rows = pc.get("inv:" + num) or []
                    st = inv.get("rows", {})
                    qty = {}
                    for r in rows:
                        k = f"{r['part_num']}|{r['color_id']}"
                        qty[k] = qty.get(k, 0) + (r.get("quantity") or 0)
                    copies = (it or {}).get("quantity", 1) or 1
                    keep = {k: n * copies for k, n in qty.items() if (st.get(k) or {}).get("s") != "x"}
                    out.append({"key": key, "set": num, "name": inv.get("label") or fr_name(num) or inv.get("name") or ((_load(CACHE_FILE, {}).get(num) or {}).get("name")) or num,
                                "owned": bool(it), "refs": len({f"{r['part_num']}|{r['color_id']}" for r in rows}),
                                "ok": sum(1 for v in st.values() if v.get("s") == "ok"),
                                "order": sum(1 for v in st.values() if v.get("s") == "order"), "updated": inv.get("updated"),
                                "pieces": sum(keep.values()),
                                "pieces_done": sum(n for k, n in keep.items() if (st.get(k) or {}).get("s") == "ok"),
                                "image": inv.get("photo") or ((it or {}).get("photo_url")) or (_load(CACHE_FILE, {}).get(num) or {}).get("image") or ""})   # (photo : celle de l'inventaire, sinon le set — 22/11)
                out.sort(key=lambda x: -(x["updated"] or 0))
                return self.send_json(out)
            m = re.fullmatch(r"/api/inventory/([\w.-]+)", p)
            if m:
                db = load_db()
                key = m.group(1)
                it = next((i for i in db["items"] if i["id"] == key), None)
                if key.startswith("set-"):   # set que l'on ne possède pas
                    num = key[4:]
                    it = {"id": key, "number": num, "quantity": 1, "kind": "set"}
                if not it or it.get("kind", "set") != "set":
                    return self.error("Set introuvable", 404)
                if not sources.rebrickable_key() and _parts_cache().get("inv:" + it["number"]) is None:   # (déjà en cache : pas besoin de clé)
                    return self.error("Il faut une clé API Rebrickable (Réglages) pour l'inventaire")
                try:
                    rows = inventory_rows(it["number"])
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas pour le moment : {e}", 502)
                inv = (db.get("inventories") or {}).get(it["id"], {})
                _keys = {r["key"] for r in rows}
                rows = rows + [{**x, "added": True} for x in inv.get("extra") or [] if x.get("key") not in _keys]   # (lignes ajoutées, hors set — 22/11)
                if it["number"].startswith("xml-"):   # inventaire importé d'un XML : pas un set du catalogue
                    pc, missing = _parts_cache(), []
                    for r in rows:
                        f = pc.get("bl:" + (r.get("bricklink") or r["part_num"]))
                        if f:
                            r["name"] = f.get("name") or r.get("name")
                            r["image"] = r.get("image") or f.get("image")
                            r["part_image"] = r.get("part_image") or f.get("image")
                        else:
                            missing.append(r.get("bricklink") or r["part_num"])
                    if missing:
                        moc_names_fill(list(dict.fromkeys(missing)))
                    return self.send_json({"set": it["number"], "name": inv.get("name") or "Inventaire XML", "name_en": "", "label": inv.get("label") or "",
                                           "photo": inv.get("photo") or "", "image": next((r.get("image") for r in rows if r.get("image")), None), "xml": True,
                                           "owned": False, "copies": 1, "rows": rows, "state": inv.get("rows", {}), "updated": inv.get("updated"),
                                           "swaps": inv.get("swaps", {}), "colors": colors_fr(), "pending_names": len(missing), "sample": bool(inv.get("sample"))})
                info = (_load(CACHE_FILE, {}).get(it["number"]) or {})
                if not info.get("name"):
                    try:
                        info = get_set(it["number"])
                    except Exception:
                        info = {}
                fr_name(it["number"], fetch=True)
                info = with_fr(info, it["number"]) if info.get("name") else info
                return self.send_json({"set": it["number"], "name": info.get("name") or inv.get("name") or it["number"],
                                       "name_en": info.get("name_en") or "",
                                       "label": inv.get("label") or "",
                                       "photo": inv.get("photo") or "",
                                       "image": info.get("image"), "owned": not key.startswith("set-"), "copies": it.get("quantity", 1),
                                       "rows": rows, "state": inv.get("rows", {}), "updated": inv.get("updated"),
                                       "swaps": inv.get("swaps", {}), "colors": colors_fr(), "sample": bool(inv.get("sample"))})
            if p == "/api/part-price":   # prix estimatif d'une pièce (gardé 7 jours)
                el = (q.get("element") or [""])[0].strip()[:20]
                part = (q.get("part") or [""])[0].strip()[:40]
                color = (q.get("color") or [""])[0].strip()[:60]
                blp = (q.get("bl") or [""])[0].strip()[:40] or (part_names().get(part) or {}).get("bl") or part
                cid = (q.get("cid") or [""])[0].strip()
                blc = rbbl_map().get(cid) if cid.lstrip("-").isdigit() else None
                site = ref_site()
                bo_rec = None
                if site != "bricklink":   # (site de référence BrickOwl / les deux : son relevé, gardé 7 jours — 21/11)
                    key = "pp:" + (el or f"{part}|{color}")
                    bo_rec = _parts_cache().get(key)
                    if not bo_rec or time.time() - bo_rec.get("t", 0) >= 7 * 86400 or (bo_rec.get("unit") and "new" not in bo_rec):   # (sans neuf / occasion à part : relu)
                        try:
                            bo_rec = sources.part_price(el, part, color) or {"unit": None}
                            bo_rec["t"] = int(time.time())
                            _parts_cache_put(key, bo_rec)
                        except Exception:
                            bo_rec = bo_rec or None
                bl_rec = None
                if bl_on() and blp and blc is not None:
                    try:
                        bl_rec = bl_part(blp, blc)
                    except Exception as e:
                        print("BrickLink pièce", blp, blc, e, flush=True)
                if site != "bricklink":
                    u, fb = ref_mix(bp_unit(bl_rec) if bl_rec else None, (bo_rec or {}).get("unit"))
                    if u is not None:
                        one = bo_rec if fb == "BrickOwl" or (bo_first() and not fb) else None
                        return self.send_json({"unit": u, "src": "both" if site == "both" and not fb else ("BrickOwl" if one else "BrickLink"),
                                               **({"fb": fb} if fb else {}), "zone": (one or {}).get("zone") or ((bl_rec or {}).get("used") or {}).get("zone"),
                                               "offers": (one or {}).get("offers"), "url": (bo_rec or {}).get("url") if site == "brickowl" else None,
                                               "sites": {"BrickLink": bp_unit(bl_rec) if bl_rec else None, "BrickOwl": (bo_rec or {}).get("unit")},
                                               "cond": part_cond_view(bl_rec, bo_rec), "bl_color": blc, "t": int(time.time())})
                if bl_on() and blp and blc is not None:   # BrickLink, tout de suite : neuf et occasion (médianes)
                    try:
                        r = bl_rec or bl_part(blp, blc)
                        if (q.get("ann") or [""])[0] == "1":   # « À commander » : médiane des annonces en cours, sinon des ventes (21/11)
                            a = bl_part_ann(blp, blc)
                            if a and bp_unit(a):
                                r = {**r, "used": a.get("used"), "new": a.get("new")}
                        u = r.get("used") or {}
                        n = r.get("new") or {}
                        if bp_unit(r):
                            return self.send_json({"unit": bp_unit(r), "zone": u.get("zone") or n.get("zone"), "offers": u.get("offers") or n.get("offers"),
                                                   "used": u or None, "new": n or None, "src": "BrickLink", "t": r.get("t"), "bl_color": blc,
                                                   "url": f"https://www.bricklink.com/v2/catalog/catalogitem.page?P={urllib.parse.quote(blp)}&C={blc}"})
                    except Exception as e:
                        print("BrickLink pièce", blp, blc, e, flush=True)
                key = "pp:" + (el or f"{part}|{color}")
                c = _parts_cache().get(key)
                if c and c.get("unit"):   # (BrickLink seul : plus de relevé BrickOwl ; le dernier prix connu reste, sans mention — 21/11)
                    return self.send_json({"unit": c["unit"], "t": c.get("t")})
                return self.send_json({"unit": None})
            if p == "/api/parts/search":
                query = (q.get("q") or [""])[0].strip()
                if len(query) < 2:
                    return self.send_json([])
                if "page" in q:   # « chercher plus » : {results, more}
                    try:
                        pg = max(1, min(50, int(q["page"][0])))
                    except ValueError:
                        pg = 1
                    try:
                        res, more = sources.parts_search_page(query, pg)
                    except Exception as e:
                        if "404" in str(e):   # page au-delà de la dernière
                            return self.send_json({"results": [], "more": False})
                        return self.error(f"Rebrickable ne répond pas : {e}", 502)
                    return self.send_json({"results": res, "more": more})
                return self.send_json(sources.parts_search(query))
            if p == "/api/part-figs":   # minifigs qui portent cette pièce (dans sa couleur)
                if not sources.rebrickable_key():
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                part = (q.get("part") or [""])[0].strip()[:60]
                pn = (q.get("part_num") or [""])[0].strip()[:60] or ((cached_part_from_bricklink(part) or {}).get("part_num") or part)
                try:
                    col = int((q.get("color") or [""])[0])
                except ValueError:
                    return self.send_json({"figs": [], "partial": False})
                try:
                    res = part_figs(pn, col)
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas pour le moment : {e}", 502)
                return self.send_json({k: v for k, v in res.items() if k != "_t"})
            if p == "/api/part-sets":   # détail d'une pièce + sets où elle apparaît (dans sa couleur)
                if not sources.rebrickable_key():
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                part = (q.get("part") or [""])[0].strip()[:60]
                if not part:
                    return self.error("Pièce manquante")
                try:
                    col = int((q.get("color") or [""])[0])
                except ValueError:
                    col = None
                try:
                    res = part_sets(part, (q.get("part_num") or [""])[0].strip()[:60], col)
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas pour le moment : {e}", 502)
                db = load_db()
                have = {norm_set(i["number"]) or i["number"]: i["list_id"] for i in db["items"] if i.get("kind", "set") == "set"}
                kinds = list_kinds(db)
                sets = [{**x, "owned": kinds.get(have.get(x["set_num"])) if x["set_num"] in have else None} for x in res.get("sets", [])]
                sets.sort(key=lambda x: (x["owned"] != "collection", x["owned"] is None, -(x.get("year") or 0)))
                return self.send_json({**{k: v for k, v in res.items() if k != "_t"}, "sets": sets})
            m = re.fullmatch(r"/api/part/([\w.-]+)/remplacement", p)
            if m:   # pièce de même forme disponible dans la couleur ?color=
                try:
                    return self.send_json({"replacement": replacement_for(m.group(1), int((q.get("color") or ["-1"])[0]))})
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas pour le moment : {e}", 502)
            m = re.fullmatch(r"/api/part/([\w.-]+)/equivalents", p)
            if m:   # pièces proposées pour remplacer celle-ci
                if not sources.rebrickable_key():
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                try:
                    res = part_equivalents(m.group(1))
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas pour le moment : {e}", 502)
                return self.send_json({k: v for k, v in res.items() if k != "_t"})
            m = re.fullmatch(r"/api/part/([\w.-]+)/similaires", p)
            if m:   # même forme : version sans impression, moules et alternatives (Rebrickable)
                try:
                    return self.send_json(similar_parts(m.group(1)))
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas pour le moment : {e}", 502)
            if p == "/api/parts/collection":   # toutes les pièces de la collection, par pièce (couleurs réunies)
                if not sources.rebrickable_key():
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                return self.send_json(collection_parts((q.get("list") or [""])[0][:40]))
            m = re.fullmatch(r"/api/part/([\w.-]+)/owned-sets", p)
            if m:   # mes sets qui contiennent cette pièce
                if not sources.rebrickable_key():
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                return self.send_json(owned_sets_with_part(m.group(1)))
            m = re.fullmatch(r"/api/part/([\w.-]+)/colors", p)
            if m:
                return self.send_json(part_colors(m.group(1), (q.get("set") or [""])[0].strip()))
            m = re.fullmatch(r"/api/set/([\w.-]+)/images", p)
            if m:
                info = get_set(m.group(1))
                if "gallery" not in info:
                    info = get_set(m.group(1), force=True)
                imgs = list(info.get("gallery") or ([info["image"]] if info.get("image") else []))
                # photos de galerie BrickEconomy (« _large-4.jpg ») absentes du cache : le site bloque, l'image de secours serait la photo
                # principale → vignette trompeuse (on croyait choisir le set, on enregistrait une photo de figurine). Retirées.
                imgs = [u for u in imgs if not re.search(r"_large-\d+\.\w+$", u) or os.path.isfile(img_path(u))]
                try:   # photos Rebrickable : voitures / éléments seuls, puis le set
                    imgs = [u for u in get_models(m.group(1)).get("images", []) if u] + imgs
                except Exception:
                    pass
                imgs.append(f"https://cdn.rebrickable.com/media/thumbs/sets/{m.group(1)}.jpg/1000x800p.jpg")
                return self.send_json(list(dict.fromkeys(imgs)))
            m = re.fullmatch(r"/api/upload/([0-9a-f]{16,40})", p)
            if m:
                for ext, ctype in ((".jpg", "image/jpeg"), (".png", "image/png"), (".webp", "image/webp")):
                    path = os.path.join(UPLOAD_DIR, m.group(1) + ext)
                    if os.path.isfile(path):
                        th = upload_thumb(path, m.group(1), (q.get("w") or [""])[0]) if "w" in q else None
                        return self.send_file(th or path, "image/jpeg" if th else ctype, cache=True)
                return self.error("Introuvable", 404)
            m = re.fullmatch(r"/api/fig/([\w.-]+)", p)
            if m:
                try:
                    f = get_fig(m.group(1), force="refresh" in q)
                except Exception:   # catalogue des cotes injoignable (BrickEconomy) : BrickOwl suffit pour le prix
                    fig_used_fetch(m.group(1), max_age=6 * 3600)
                    rec = _fu_cache().get(m.group(1)) or {}
                    if not (rec.get("unit") is not None or rec.get("name") or (q.get("name") or [""])[0]):
                        raise
                    hint_img = (q.get("img") or [""])[0][:400]
                    f = {"type": "fig", "number": m.group(1), "name": (q.get("name") or [""])[0][:150] or rec.get("name") or m.group(1),
                         "image": hint_img if IMG_OK.match(hint_img) else None, "bo_only": True, "pending_prices": True, "fetched_at": 0}
                    return self.send_json({**f, **({"value": rec["new"]["unit"]} if (rec.get("new") or {}).get("unit") else {}), "used": rec.get("unit"),
                                           "used_stats": fig_used_stats(m.group(1)), "market": {"used": fig_used_stats(m.group(1)), "new": rec.get("new"), "src": rec.get("src") or "BrickOwl"}, "own_hist": []})
                fid_ = m.group(1)
                if "history" not in f and not f.get("pending_prices"):   # historique des prix pas encore relu
                    if quick():   # fiche ouverte : en fond (au plus une fois par jour)
                        bg_once("hist:fig:" + fid_, lambda: get_fig(fid_, force=True))
                    else:
                        try:
                            f = get_fig(fid_, force=True)
                        except Exception:
                            pass
                if quick():
                    bg_once("frfig:" + str(f.get("name")), lambda: fr_fig(f.get("name"), fetch=True))
                else:
                    fr_fig(f.get("name"), fetch=True)
                old = _fu_cache().get(fid_)
                if old and "min" not in old and "name" not in old:   # relevé d'avant les statistiques (min / max / moyenne) : relevé à nouveau, une fois
                    bg_once("fuold:" + fid_, lambda: fig_used_fetch(fid_, max_age=0))
                used = fig_used_many([m.group(1)]).get(m.group(1))   # relevé à jour d'abord (BrickLink si branché)
                _fu_mem["t"] = 0
                rec = _fu_cache().get(m.group(1)) or {}
                mk = {"used": fig_used_stats(m.group(1)), "new": rec.get("new"), "src": rec.get("src") or "BrickOwl"}
                return self.send_json({**with_fr_fig(f), **({"value": rec["new"]["unit"]} if (rec.get("new") or {}).get("unit") else {}),
                                       "market": mk, "used": used, "used_stats": fig_used_stats(m.group(1)),
                                       "own_hist": (_load(HISTORY_FILE, {}).get("items") or {}).get("fig:" + m.group(1)) or []})
            m = re.fullmatch(r"/api/set/([\w.-]+)/parts", p)
            if m:   # pièces d'un set (hors figurines), pour les ajouter à une liste à commander
                if not sources.rebrickable_key():
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                try:
                    rows = inventory_rows(m.group(1))
                    prefetch_images([u for r in rows for u in (r.get("image"), r.get("part_image"))])
                    return self.send_json(rows)
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas pour le moment : {e}", 502)
            m = re.fullmatch(r"/api/items/(\w+)/moc-lots", p)
            if m:   # pièces d'un MOC (liste importée), pour les voir et les commander
                it = next((i for i in load_db()["items"] if i["id"] == m.group(1)), None)
                if not it or it.get("kind") != "custom":
                    return self.error("Introuvable", 404)
                return self.send_json(moc_lots_detail(it))   # (ses pièces sont dans la fiche : jamais refusé, même sans clé ni internet — 22/11)
            m = re.fullmatch(r"/api/set/([\w.-]+)/models", p)
            if m:
                return self.send_json(get_models(m.group(1)))
            m = re.fullmatch(r"/api/moc-review/(\w+)", p)
            if m:   # une minifig MOC : propositions du scan
                it = next((i for i in load_db()["items"] if i["id"] == m.group(1)), None)
                if not it:
                    return self.error("Introuvable", 404)
                fig = review_fig(it, _load(REVIEW_FILE, {}))
                review_images_fill([fig])
                return self.send_json({"fig": fig, "colors": colors_fr()})
            if p == "/api/moc-review":   # minifigs MOC sans liste de pièces, avec les pièces proposées
                try:
                    figs = review_pending()
                    review_images_fill(figs)
                    return self.send_json({"figs": figs, "colors": colors_fr()})
                except PermissionError:
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
            m = re.fullmatch(r"/api/fig/([\w.-]+)/sets", p)
            if m:   # sets du catalogue qui contiennent cette figurine (sa fiche, sinon BrickLink)
                return self.send_json({"sets": fig_sets_of(m.group(1))})
            m = re.fullmatch(r"/api/fig/([\w.-]+)/rbmatch", p)
            if m:   # minifigs Rebrickable candidates (gardées : rendues tout de suite)
                try:
                    return self.send_json(rb_fig_match_known(m.group(1)))   # (version déduite de son set ou choisie : en tête, sûre)
                except PermissionError:
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas : {e}", 502)
            if p == "/api/rbsets":   # sets Rebrickable (nom ou numéro) : ceux absents du catalogue des prix peuvent être ajoutés
                query = (q.get("q") or [""])[0].strip()
                if len(query) < 2 or not sources.rebrickable_key():
                    return self.send_json([])
                try:
                    r = sources.rb("lego/sets/?page_size=20&search=" + urllib.parse.quote(query))
                except Exception:
                    return self.send_json([])
                return self.send_json(with_avail([{"number": x["set_num"], "name": x.get("name"), "year": x.get("year"), "pieces": x.get("num_parts"),
                                                   "image": x.get("set_img_url"), "type": "rbset"} for x in r.get("results", [])]))
            if p == "/api/offline-pack":   # 📴 toutes les pièces des figurines de la collection, d'un coup (gardé sur l'appareil par sw.js)
                return self.send_json({} if DEMO else offline_pack())
            m = re.fullmatch(r"/api/rbfig/([\w.-]+)/parts", p)
            if m:
                try:
                    it = next((i for i in load_db()["items"] if i["id"] == (q.get("item") or [""])[0]), None)
                    acc = cmf_accessories(it) if it else []   # minifig à collectionner : ses accessoires en plus
                    return self.send_json(rb_fig_parts(m.group(1)) + acc)
                except PermissionError:
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas : {e}", 502)
            m = re.fullmatch(r"/api/set/([\w.-]+)", p)
            if m:
                try:
                    info = get_set(m.group(1), force="refresh" in q, market_force="refresh" in q)
                    if not info.get("minifigs") and not owns_set(m.group(1)):
                        info = with_bl_figs(info, m.group(1))   # set que je n'ai PAS, sans figurines connues (prix seulement) : celles de BrickLink, pour la fiche (rien d'enregistré)
                except Exception:
                    info = placeholder_set(m.group(1), strict=True)   # connu de Rebrickable : ajout possible, cote plus tard
                    if not info:
                        raise
                    return self.send_json({**info, "own_hist": [], "minifig_used": None, "minifig_used_missing": 0})
                if info.get("pending_prices"):   # (fiche provisoire gardée avant les figurines BrickLink : complétée)
                    return self.send_json({**with_bl_figs(info, m.group(1)), "own_hist": [], "minifig_used": None, "minifig_used_missing": 0})
                num_ = m.group(1)
                if "history" not in info:   # fiche relue avant l'historique des prix : on la relit
                    if quick():   # fiche ouverte : en fond (au plus une fois par jour)
                        bg_once("hist:set:" + num_, lambda: get_set(num_, force=True))
                    else:
                        try:
                            info = get_set(num_, force=True)
                        except Exception:
                            pass
                if quick():
                    bg_once("frset:" + num_, lambda: fr_name(num_, fetch=True))
                else:
                    fr_name(num_, fetch=True)
                info = with_bs(with_lego(with_fr(info, m.group(1)), info.get("number") or m.group(1)), info.get("number") or m.group(1))   # (Brickset : catalogue — 21/11 soir)
                if sources.brickset_key() and not DEMO and not COPIE and bs_rec(info.get("number") or m.group(1)) is None:
                    _bsn = info.get("number") or m.group(1)
                    bg_once("bs:" + _bsn, lambda: brickset_one(_bsn), 86400)   # (prix public et « en vente » d'après lego.com — 21/11)
                fill_fig_names([f.get("name") for f in info.get("minifigs") or []])
                fig_used_many([f["id"] for f in info.get("minifigs") or []])
                info = with_used_figs(info)
                mu = [f.get("used") for f in info.get("minifigs") or []]
                extras_start(info.get("number") or m.group(1))
                return self.send_json({**info, "sf": sf_prices(info.get("number") or m.group(1), info), "bs": bs_dates(info.get("number") or m.group(1)), "extras": set_extras(info.get("number") or m.group(1)),   # (sf : prix sans figurines, 21/11)
                                       "own_hist": (_load(HISTORY_FILE, {}).get("items") or {}).get(m.group(1)) or [], "minifigs": [with_fr_fig(f) for f in info.get("minifigs") or []],
                                       "minifig_used": round(sum((f["used"] if f.get("used") is not None else f.get("value") or 0) * f.get("qty", 1)
                                                                 for f in info.get("minifigs") or []), 2) if mu else None,
                                       "minifig_used_missing": sum(1 for u in mu if u is None)})
            if p == "/api/novelties/blfig":   # ?set=<n° de set>&name=<nom Rebrickable> → {"no", "name", "zone"} (figurine BrickLink) ou {}
                setno, name = (q.get("set") or [""])[0][:20], (q.get("name") or [""])[0][:200]
                if DEMO or not bl_on() or not re.fullmatch(r"[\w.-]+", setno):
                    return self.send_json({})
                pc = _parts_cache()
                done = pc.get(f"nvblr:{setno}|{name}") or {}
                if time.time() - done.get("t", 0) < 86400:   # réponse gardée 24 h (chaque recherche coûte une dizaine d'appels BrickLink)
                    return self.send_json(done.get("r") or {})
                cb = pc.get("nvbl:" + setno) or {}
                figs = cb.get("figs") if time.time() - cb.get("t", 0) < (30 if cb.get("figs") else 1) * 86400 else None   # inventaire pas encore chez BrickLink : réessayé le lendemain
                if figs is None:
                    try:   # figurines du set selon BrickLink (une requête, gardée 30 jours)
                        d = sources.bl_get(f"/items/SET/{urllib.parse.quote(setno)}/subsets") or []
                        import html as _html
                        figs = [{"no": e["item"]["no"], "name": _html.unescape(e["item"].get("name") or "")}
                                for g in d for e in g.get("entries") or [] if (e.get("item") or {}).get("type") == "MINIFIG"]
                    except Exception:
                        figs = []
                    _parts_cache_put("nvbl:" + setno, {"figs": figs, "t": time.time()})
                toks = lambda t: set(re.findall(r"[a-z0-9]+", str(t).lower())) - {"with", "and", "the", "of", "a"}
                want = toks(name)
                best = max(figs, key=lambda f: len(want & toks(f["name"])) / (len(want | toks(f["name"])) or 1), default=None)
                if not best or not want or len(want & toks(best["name"])) / len(want) < 0.5:
                    _parts_cache_put(f"nvblr:{setno}|{name}", {"r": {}, "t": time.time()})
                    return self.send_json({})
                zone = ""
                try:   # ses annonces : la zone où il y en a (France, sinon Europe, sinon monde)
                    m = bl_market("MINIFIG", best["no"])
                    zs = [r.get("zone") for r in (m.get("used"), m.get("new")) if r]
                    zone = next((z for z in sources.bl_zone_order() + ["France", "UE", "monde"] if z in zs), "")
                except Exception:
                    pass
                res = {"no": best["no"], "name": best["name"], "zone": zone}
                _parts_cache_put(f"nvblr:{setno}|{name}", {"r": res, "t": time.time()})
                return self.send_json(res)
            if p == "/api/novelties/count":   # menu : combien (selon mes filtres), dont combien jamais vues
                its = novelties_mine()
                if not os.path.exists(NOV_SEEN):   # premier passage : ce qui existe déjà compte comme vu
                    with lock:
                        _save(NOV_SEEN, sorted(x["number"] for x in its))
                seen = set(_load(NOV_SEEN, []))
                return self.send_json({"count": len(its), "new": sum(1 for x in its if x["number"] not in seen)})
            if p == "/api/novelties":   # nouveautés : sans ce que j'ai (collection, souhaits) ni ce que j'ai masqué
                d = _load(NOV_FILE, {})
                # page ouverte (fresh=1) : sorties relues sur lego.com tout de suite (au plus toutes les 15 min) ; sinon toutes les 12 h
                started = False
                if (not d or time.time() - d.get("t", 0) > (120 if (q.get("fresh") or [""])[0] == "1" else 3600)) and not DEMO and not _nov["busy"]:
                    threading.Thread(target=novelties_build, daemon=True).start()
                    started = True
                db_ = load_db(); wl_ids = {l["id"] for l in db_["lists"] if l.get("kind") == "wishlist"}   # listes de souhaits (et sous-listes)
                sets_ = [i for i in db_["items"] if i.get("kind", "set") == "set"]
                lst_ = {l["id"]: l for l in db_["lists"]}
                watch_ids = {k for k, l in lst_.items() if l.get("gift") or lst_.get(l.get("parent_id") or "", {}).get("gift")}   # « 👀 À surveiller »
                watched = {i.get("number") for i in sets_ if i.get("list_id") in watch_ids}
                wished = {i.get("number") for i in sets_ if i.get("list_id") in wl_ids - watch_ids}   # déjà dans une liste de souhaits
                show_wish = (q.get("wish") or [""])[0] == "1"   # case « Afficher ceux déjà dans la liste de souhaits »
                show_watch = (q.get("watch") or [""])[0] == "1"   # case « Afficher les surveillés »
                mine = ({i.get("number") for i in sets_ if i.get("list_id") not in wl_ids} | (set() if show_wish else wished)
                        | (set() if show_watch else watched - (wished if show_wish else set())))
                hidden, ex_th = set(_load(NOV_HIDDEN, [])), set(_load(NOV_THEMES, []))
                show_hidden = (q.get("hidden") or [""])[0] == "1"
                ex_th = {theme_norm(t) for t in ex_th}
                noimg = lambda u: not u or "/assets/?" in u   # lego.com sans photo pour l'instant : celle de Rebrickable
                def nov_pick(x):   # la première image vraiment disponible (sur le serveur, ou pas encore refusée par sa source) — 20/11
                    cands = [u for u in [x.get("image"), *(x.get("images") or [])] if u and not noimg(u)]
                    for u in cands:
                        if has_local(u):
                            return u
                    for u in cands:
                        if time.time() - _img_miss.get(u, 0) >= 6 * 3600:
                            return u
                    return cands[0] if cands else RB_IMG.format(x["number"])
                src = [{**x, "theme": theme_norm(x.get("theme")), "image": nov_pick(x)}
                       for x in d.get("items") or [] if x.get("pieces")]
                all_themes = sorted({x["theme"] for x in src}, key=str.lower)
                items = [x for x in src if x["number"] not in mine and x["theme"] not in ex_th and (show_hidden or x["number"] not in hidden)]
                seen_nov = set(_load(NOV_SEEN, [])) if os.path.exists(NOV_SEEN) else None
                for x in items:
                    x["hidden"] = x["number"] in hidden
                    x["wished"] = x["number"] in wished
                    x["watched"] = x["number"] in watched
                    x["new"] = (seen_nov is not None and x["number"] not in seen_nov   # apparue depuis ma dernière visite (encadré jaune)
                                and not x["wished"] and not x["watched"])   # déjà souhaitée / surveillée : jamais « nouvelle »
                return self.send_json({"items": items, "t": d.get("t"), "figs_done": d.get("figs_done", False), "building": started or _nov["busy"] or not d,
                                       "themes": all_themes, "excluded_themes": sorted(ex_th, key=str.lower),
                                       "hidden_count": len([n for n in hidden if n not in mine])})
            if p == "/api/img":
                _u = (q.get("u") or [""])[0]
                if _u.startswith("https://cdn.rebrickable.com/media/parts/") and not has_local(_u):   # photo de pièce absente du serveur : sa photo de remplacement cherchée tout de suite
                    _el_img["want"].add(_u); bg_once("elimg-now", el_img_job, every=600)
                if be_fig_no(_u) and not has_local(_u):   # photo de figurine absente du serveur : sa photo Rebrickable cherchée tout de suite (10 min entre deux recherches)
                    bg_once("figimg-now", fig_img_job, every=600)
                return self.proxy_image(_u, (q.get("w") or [""])[0])
            if p == "/api/hd":   # zoom : la plus grande version connue (alt : grande photo Rebrickable d'une minifig dont la version est connue)
                return self.send_hd((q.get("u") or [""])[0], (q.get("alt") or [""])[0])
            if p == "/api/shares":   # fiches partagées (réglages)
                if DEMO:
                    return self.send_json([])
                db, sh = load_db(), _load(SHARES_FILE, {})
                ids = {i["id"]: i for i in db["items"]}
                cache = _load(CACHE_FILE, {})
                figname = lambda it, fid: (with_fr_fig({"name": next((f.get("name") for f in (cache.get(cache_key(it)) or {}).get("minifigs") or [] if f.get("id") == fid), fid)}) or {}).get("name") or fid
                return self.send_json(sorted(({"token": t, "item_id": s["item"], "at": s.get("at"), "fig": s.get("fig") or "", "prices": s.get("prices") is not False,
                                               "set_name": None if not s.get("fig") else ids[s["item"]].get("display_name") or fr_name(ids[s["item"]].get("number")),
                                               "name": figname(ids[s["item"]], s["fig"]) if s.get("fig") else ids[s["item"]].get("display_name") or ids[s["item"]].get("custom_name") or (cache.get(cache_key(ids[s["item"]])) or {}).get("name") or ids[s["item"]].get("number"),
                                               "number": s.get("fig") or ids[s["item"]].get("number"), "kind": "fig" if s.get("fig") else ids[s["item"]].get("kind", "set")}
                                              for t, s in sh.items() if s.get("item") in ids), key=lambda x: -(x["at"] or 0)))
            # fichiers statiques
            rel = "index.html" if p in ("/", "") else p.lstrip("/")
            full = os.path.normpath(os.path.join(STATIC, rel))
            if os.path.commonpath([full, STATIC]) == STATIC and os.path.isfile(full):
                return self.send_file(full)
            return self.error("Introuvable", 404)
        except LookupError as e:
            return self.error(str(e), 404)
        except Exception as e:
            return self.error(f"Erreur de source de données : {e}", 502)

    # ---- back office (personnalisation sans code) : voir backoffice.py ; toujours derrière le mot de passe (guard)
    def bo_get(self, p, q):
        def html(body, status=200):
            self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body))); self.end_headers()
            return self.wfile.write(body)
        if p.startswith("/admin"):   # ancienne adresse du back office
            return self.redirect_to("/backoffice/secours" if p == "/admin/secours" else "/backoffice")
        if p.startswith("/bo-img/"):   # images envoyées depuis le back office (boutons, pages, logo) : publiques
            return backoffice_outils.image_send(self, p[len("/bo-img/"):])
        if p.startswith("/p/"):   # page créée dans le back office et cochée « publique »
            pg = backoffice.public_page(p[3:].strip("/"))
            if not pg:
                return html("<!doctype html><meta charset=utf-8><title>Page introuvable</title><p style='font:16px system-ui;margin:40px'>Page introuvable. <a href='/'>Retour</a></p>".encode("utf-8"), 404)
            with open(os.path.join(STATIC, "page.html"), "rb") as f:
                return html(backoffice.inject(f.read(), public=True, off="bo=off" in (urlparse(self.path).query or ""), page=pg))
        if p == "/backoffice/secours":   # page de secours : remettre une version précédente du code (ne dépend d'aucun autre fichier)
            return html(backoffice_outils.rescue_page())
        if p in ("/backoffice", "/backoffice/"):
            kind, body = backoffice_acces.entry(self)
            if kind == "page":   # première visite, connexion, avertissements : page écrite dans backoffice_acces.py
                return html(body)
            if not auth.valid_session(self.token()):   # la session de l'application a expiré : le mot de passe du back office la rouvre (l'aperçu en a besoin)
                self._bo_cookies = [auth.cookie_header(auth.new_session(False), remember=False, secure=self.is_https())]
            return self.send_file(os.path.join(STATIC, "admin.html"))
        if p in ("/backoffice/guide/ia", "/backoffice/guide/ia.txt"):   # « 🤖 Condensé pour IA » de la notice (même accès que la notice)
            f = os.path.join(ROOT, "docs", "wiki", "back-office-ia.md")
            if not os.path.isfile(f):
                return self.error("Notice pas encore générée (python3 docs/build_docs.py)", 404)
            return self.send_ia(f, "Notice du back office", "/backoffice/guide/ia.txt", "/backoffice/guide", "Notice du back office", p.endswith(".txt"))
        if p in ("/backoffice/guide", "/backoffice/guide/"):   # notice du back office, en wiki (docs/wiki/back-office.html, écrite par docs/build_docs.py)
            f = os.path.join(ROOT, "docs", "wiki", "back-office.html")
            return self.send_file(f) if os.path.isfile(f) else html("<!doctype html><meta charset=utf-8><p style='font:16px system-ui;margin:40px'>La notice n'est pas installée (python3 docs/build_docs.py la fabrique). <a href='/backoffice'>Retour au back office</a></p>".encode(), 404)
        if p == "/backoffice/aide":   # ancienne adresse de la notice
            return self.redirect_to("/backoffice/guide")
        m = re.fullmatch(r"/backoffice/(?:aide|guide/img)/(bo-[\\w-]{1,60}\\.jpg)", p)
        if m:   # captures de la notice
            f = os.path.join(ROOT, "docs", "captures", m.group(1))
            return self.send_file(f, cache=True) if os.path.isfile(f) else self.error("Image introuvable", 404)
        if p == "/api/bo/acces":
            return backoffice_acces.api(self, "GET", "acces", None)
        if p.startswith("/backoffice"):
            return self.error("Page introuvable", 404)
        if p.startswith("/api/bo/x/"):   # outils du serveur : voir backoffice_outils.py
            return backoffice_outils.api(self, "GET", p[len("/api/bo/x/"):], q, None)
        if p == "/api/bo/state":   # réglages publiés, brouillon, historique
            return self.send_json({**backoffice.state(), "copie": COPIE})
        if p == "/api/bo/item":   # une fiche brute, telle qu'elle est enregistrée (panneau « Données »)
            iid = (q.get("id") or [""])[0]
            it = next((i for i in load_db()["items"] if i["id"] == iid), None)
            if not it:
                return self.error("Fiche introuvable", 404)
            body = json.dumps({"item": it}, ensure_ascii=False).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers()
            return self.wfile.write(body)
        if p == "/api/bo/version":   # une publication de l'historique
            v = backoffice.version((q.get("id") or [""])[0])
            return self.send_json({"cfg": v}) if v is not None else self.error("Version introuvable", 404)
        return self.error("Introuvable", 404)

    def bo_post(self, p):
        if p in ("/api/bo/login", "/api/bo/setup", "/api/bo/logout", "/api/bo/compris", "/api/bo/password", "/api/bo/app-password", "/api/bo/options"):   # accès : backoffice_acces.py
            b = self.json_body()
            return backoffice_acces.api(self, "POST", p[len("/api/bo/"):], b if isinstance(b, dict) else {})
        if p.startswith("/api/bo/x/"):   # outils du serveur : voir backoffice_outils.py (import-zip, image : corps binaire)
            b = {} if p.endswith(("/import-zip", "/image")) else self.json_body()
            return backoffice_outils.api(self, "POST", p[len("/api/bo/x/"):], parse_qs(urlparse(self.path).query), b if isinstance(b, dict) else {})
        b = self.json_body()
        if not isinstance(b, dict):
            b = {}
        try:
            if p == "/api/bo/normalize":   # {cfg} : des réglages venus d'un fichier, remis d'aplomb avant d'être repris dans le back office
                return self.send_json({"cfg": backoffice.normalize(b.get("cfg"))}, prefetch=False)
            if p == "/api/bo/draft":   # {cfg} : brouillon enregistré à chaque changement
                backoffice.save_draft(b.get("cfg"))
                return self.send_json({"ok": True})
            if p == "/api/bo/publish":   # {cfg?, note?, count?} : le brouillon devient la version du site
                if isinstance(b.get("cfg"), dict):
                    backoffice.save_draft(b["cfg"])
                vid = backoffice.publish(b.get("note") or "", b.get("count") or 0)
                return self.send_json({"ok": True, "id": vid, **backoffice.state()})
            if p == "/api/bo/discard":   # abandonner le brouillon
                backoffice.discard()
                return self.send_json({"ok": True, **backoffice.state()})
            if p == "/api/bo/values":   # {id, x} : valeurs des champs personnalisés d'une fiche (sans toucher au reste)
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == str(b.get("id") or "")), None)
                    if not it:
                        return self.error("Fiche introuvable", 404)
                    x = backoffice.clean_x(b.get("x"))
                    if x:
                        it["x"] = x
                    else:
                        it.pop("x", None)
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "x": x})
            if p == "/api/bo/item":   # {id, item} : fiche brute réécrite telle quelle (une sauvegarde de la collection est faite avant)
                new = b.get("item")
                if not isinstance(new, dict) or not new.get("id") or new.get("id") != b.get("id"):
                    return self.error("Fiche illisible (l'identifiant « id » ne doit pas changer)")
                with lock:
                    db = load_db()
                    k = next((n for n, i in enumerate(db["items"]) if i["id"] == new["id"]), None)
                    if k is None:
                        return self.error("Fiche introuvable", 404)
                    if new.get("list_id") not in {l["id"] for l in db["lists"]}:
                        return self.error("« list_id » ne correspond à aucune liste")
                    backup_db("backoffice")
                    db["items"][k] = new
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
        except ValueError as e:
            return self.error(str(e))
        return self.error("Introuvable", 404)

    def do_POST(self):
        prio_seen(urlparse(self.path).path)   # (priorité à l'écran — 22/11)
        if self.demo_route() or self.guard():
            return
        p = urlparse(self.path).path
        if self.auth_routes(p):
            return
        if p.startswith("/api/bo/") and not DEMO:
            return self.bo_post(p)
        try:
            if p == "/api/parts/scan-raw":   # une zone de photo → reconnaissance brute (pièces + couleurs BrickLink)
                data = self.body()
                if not data:
                    return self.error("Aucune image reçue")
                try:
                    found, cols = sources.recognize_part_colors(data, self.headers.get("Content-Type", "image/jpeg"), top=5)
                except Exception as e:
                    return self.error(f"Reconnaissance impossible : {e}", 502)
                return self.send_json({"items": [{"id": r["number"], "name": r["name"], "img": r["image"], "score": r["score"]} for r in found],
                                       "colors": [{"bl": c["bl"], "name": c["name"], "score": c["score"]} for c in cols]})
            if p == "/api/parts/scan-objects":   # {"images": [dataURL]} → chaque pièce posée à part, reconnue
                import base64
                imgs = []
                for u in (self.json_body().get("images") or [])[:8]:
                    try:
                        imgs.append(base64.b64decode(str(u).split(",", 1)[-1]))
                    except Exception:
                        pass
                if not imgs:
                    return self.error("Aucune photo reçue")
                try:
                    zones = scan_exploded(imgs)
                    blrb = moc_color_maps()["blrb"]
                except Exception as e:
                    return self.error(f"Scan impossible : {e}", 502)
                cf, pc = colors_fr(), _parts_cache()
                out = []
                for z, zd in sorted(zones.items(), key=lambda kv: int(re.sub(r"\D", "", kv[0]) or 0)):
                    out.append({"thumb": zd.get("thumb", ""),
                                "cands": [{"part": i["id"], "name": i["name"], "score": i["score"],
                                           "image": (pc.get("bl:" + i["id"]) or {}).get("image") or i.get("img") or ""} for i in zd["items"][:3]],
                                "colors": [c for c in (_col_rb(blrb, cf, x) for x in zd.get("colors") or []) if c][:3]})
                return self.send_json(out)
            if p == "/api/novelties/themes":   # {"themes": [...]} : les thèmes exclus des nouveautés (remplace la liste)
                th = [theme_norm(str(t)[:80]) for t in (self.json_body().get("themes") or []) if isinstance(t, str) and t.strip()][:200]
                with lock:
                    _save(NOV_THEMES, sorted(set(th), key=str.lower))
                return self.send_json({"ok": True, "excluded_themes": sorted(set(th), key=str.lower)})
            if p == "/api/novelties/seen":   # page Nouveautés ouverte : tout ce qui y est affiché est « vu »
                with lock:
                    seen = set(_load(NOV_SEEN, []))
                    seen |= {x["number"] for x in novelties_mine()}
                    _save(NOV_SEEN, sorted(seen))
                return self.send_json({"ok": True})
            if p == "/api/novelties/reimg":   # {"number", "fig"?} : chercher tout de suite la photo d'une nouveauté (set ou figurine exclusive)
                b = self.json_body()
                num, fig = str(b.get("number") or ""), str(b.get("fig") or "")
                if not re.fullmatch(r"\d{3,7}-\d+", num) or (fig and not re.fullmatch(r"fig-\d{3,9}", fig)):
                    return self.error("Numéro non valable")
                found, tmp = "", False
                try:
                    if fig:
                        found = sources.rb(f"lego/minifigs/{urllib.parse.quote(fig)}/").get("set_img_url") or ""
                        if not found:   # (pas encore de photo : son torse imprimé, en attendant)
                            ps = sources.rb(f"lego/minifigs/{urllib.parse.quote(fig)}/parts/?page_size=100").get("results", [])
                            tor = next((q["part"] for q in ps if re.search(r"torso", (q.get("part") or {}).get("name") or "", re.I) and (q.get("part") or {}).get("part_img_url")), None)
                            found, tmp = (tor or {}).get("part_img_url") or "", True
                    else:
                        found = sources.rb(f"lego/sets/{urllib.parse.quote(num)}/").get("set_img_url") or ""
                except Exception as e:
                    return self.error("Recherche impossible pour l'instant (Rebrickable indisponible)", 503)
                if found:
                    with lock:
                        d = _load(NOV_FILE, {})
                        for x in d.get("items") or []:
                            if x.get("number") != num:
                                continue
                            if fig:
                                for f in x.get("figs") or []:
                                    if f.get("fig") == fig and (not f.get("image") or f.get("image_tmp")):
                                        f["image"] = found
                                        if tmp: f["image_tmp"] = True
                                        else: f.pop("image_tmp", None)
                            elif not x.get("image") or "/assets/?" in str(x.get("image")):
                                x["image"] = found
                        _save(NOV_FILE, d)
                return self.send_json({"ok": True, "image": found, "tmp": tmp})
            if p == "/api/novelties/hide":   # {"number", "hide": true|false} : ne plus afficher (ou de nouveau) ce set dans les nouveautés
                b = self.json_body()
                num = str(b.get("number") or "")
                if not re.fullmatch(r"\d{3,7}-\d+", num):
                    return self.error("Numéro non valable")
                with lock:
                    h = set(_load(NOV_HIDDEN, []))
                    (h.add if b.get("hide", True) else h.discard)(num)
                    _save(NOV_HIDDEN, sorted(h))
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/to-fig", p)
            if m:   # {"number": "sw0001"} : la fiche devient cette minifig du catalogue
                num = str(self.json_body().get("number") or "").strip()
                if not re.fullmatch(r"[\w.-]{2,30}", num):
                    return self.error("Numéro de figurine non valable (ex : sw0001)")
                try:
                    get_fig(num)
                except Exception:
                    placeholder_fig(num)   # catalogue des prix injoignable : fiche provisoire, cote reprise plus tard
                with lock:
                    db = load_db()
                    idx = next((k for k, i in enumerate(db["items"]) if i["id"] == m.group(1)), None)
                    it = db["items"][idx] if idx is not None else None
                    if not it or it.get("kind", "set") == "part":
                        return self.error("Fiche introuvable", 404)
                    if it.get("set_orig"):   # figurine d'origine d'un set : elle le quitte d'abord (déduite du set)
                        orig_fig_leaves(db, it)
                    photo = it.get("photo_url") or (it.get("image") if _UP_RE.fullmatch(str(it.get("image") or "")) else "")
                    new = {"list_id": it["list_id"], "kind": "fig", "number": num, "quantity": it.get("quantity", 1), "condition": "occasion",
                           "with_minifigs": True, "missing_minifigs": [], "portion": 100, "parts": [], "notes": it.get("notes", ""), "todos": it.get("todos") or [],
                           "accessories": it.get("accessories") or [], "alt_photos": it.get("alt_photos") or [], "alt_names": it.get("alt_names") or [],
                           "alt_hidden": it.get("alt_hidden") or [], "main_name": it.get("main_name") or "", **({"photo_url": photo} if photo else {})}
                    out = self.clean_item(new)
                    out.update(id=it["id"], added_at=it.get("added_at"), updated_at=int(time.time()))
                    db["items"][idx] = out
                    db["items"] = [x for x in db["items"] if not (x.get("attached_to") == it["id"] and x.get("set_orig"))]   # c'était un set : les fiches de ses figurines d'origine n'existaient que par lui (comme à sa suppression)
                    for x in db["items"]:   # une figurine n'accueille pas d'autres figurines : celles qu'on y avait rangées redeviennent seules
                        if x.get("attached_to") == it["id"]:
                            x.pop("attached_to", None)
                    _save(DB_FILE, db)
                try:
                    fig_used_many([num])
                except Exception:
                    pass
                return self.send_json({"ok": True, "id": m.group(1)})
            m = re.fullmatch(r"/api/items/(\w+)/to-set", p)
            if m:   # {"number": "75192"} : la fiche devient ce set du catalogue (erreur de type) ; liste, quantité, notes, tâches et photo gardées
                num = norm_set(str(self.json_body().get("number") or ""))
                if not num:
                    return self.error("Numéro de set non valable (ex : 75192 ou 75192-1)")
                try:
                    get_set(num)
                except Exception:
                    placeholder_set(num)   # catalogue des prix injoignable : fiche provisoire (Rebrickable si possible, sinon son numéro), prix plus tard
                with lock:
                    db = load_db()
                    idx = next((k for k, i in enumerate(db["items"]) if i["id"] == m.group(1)), None)
                    it = db["items"][idx] if idx is not None else None
                    if not it or it.get("kind", "set") == "part" or (it.get("kind", "set") == "set" and it.get("number") == num):
                        return self.error("Fiche introuvable", 404)
                    if it.get("set_orig"):   # figurine d'origine d'un set : elle le quitte d'abord (déduite du set)
                        orig_fig_leaves(db, it)
                    photo = it.get("photo_url") or (it.get("image") if _UP_RE.fullmatch(str(it.get("image") or "")) else "")   # ma photo, si j'en avais une
                    new = {"list_id": it["list_id"], "kind": "set", "number": num, "quantity": it.get("quantity", 1),
                           "condition": it.get("condition") or "occasion", "with_minifigs": True, "missing_minifigs": [], "fig_counts": {}, "portion": 100, "parts": [],
                           "notes": it.get("notes", ""), "todos": it.get("todos") or [], "unbuilt": it.get("unbuilt"),
                           "has_box": it.get("has_box"), "no_plan": it.get("no_plan"), **({"photo_url": photo} if photo else {})}
                    out = self.clean_item(new)
                    out.update(id=it["id"], added_at=it.get("added_at"), updated_at=int(time.time()))
                    db["items"][idx] = out
                    set_figs_sheets(db, out)   # ses figurines d'origine : celles du NOUVEAU set, tout de suite (celles de l'ancien numéro partent avec lui)
                    _save(DB_FILE, db)
                fig_used_fill()
                item_parts_refresh(it["id"])
                return self.send_json({"ok": True, "id": m.group(1)})
            m = re.fullmatch(r"/api/items/(\w+)/to-custom", p)
            if m:   # {"type": "moc" | "partial" | "fig"} : une fiche du catalogue devient un MOC (erreur de type), en gardant l'essentiel
                typ = str(self.json_body().get("type") or "")
                with lock:
                    db = load_db()
                    idx = next((k for k, i in enumerate(db["items"]) if i["id"] == m.group(1)), None)
                    it = db["items"][idx] if idx is not None else None
                    if not it or it.get("kind", "set") not in ("set", "fig"):
                        return self.error("Fiche introuvable", 404)
                    fig = it.get("kind") == "fig"   # fiche d'origine : minifig (sinon set)
                    if typ not in ("moc", "partial", "fig"):
                        return self.error("Type non valable pour cette fiche")
                    if it.get("set_orig"):   # figurine d'origine d'un set : elle le quitte d'abord (déduite du set), puis change de type
                        orig_fig_leaves(db, it)
                    cache = _load(CACHE_FILE, {})
                    info = cache.get(cache_key(it)) or {}
                    img = it.get("photo_url") or it.get("photo") or info.get("image") or ""
                    new = {"list_id": it["list_id"], "kind": "custom", "custom": True, "custom_type": "fig" if typ == "fig" else "set",
                           "custom_name": (it.get("display_name") or fr_name(it["number"]) or info.get("name") or it["number"])[:150],
                           "number": it["number"] if typ == "partial" and not fig else "custom", "partial_set": typ == "partial", "image": img,
                           "quantity": it.get("quantity", 1), "condition": "occasion", "with_minifigs": True, "missing_minifigs": [], "portion": 100, "parts": [],
                           "notes": it.get("notes", ""), "todos": (it.get("todos") or []) + ([] if typ == "fig" else [{"cat": "Pièces", "note": "Ajouter la liste de pièces"}]),
                           "accessories": it.get("accessories") or [], "unbuilt": it.get("unbuilt"),
                           **({"attached_to": it["attached_to"]} if typ == "fig" and it.get("attached_to") else {})}   # seule une figurine (MOC) reste rangée dans son set
                    out = self.clean_item(new)
                    out.update(id=it["id"], added_at=it.get("added_at"), updated_at=int(time.time()))
                    db["items"][idx] = out
                    now = int(time.time())
                    origs = [x for x in db["items"] if x.get("attached_to") == it["id"] and x.get("set_orig")]
                    for o in origs:   # ses figurines d'origine ont déjà leurs fiches : gardées telles quelles (une par figurine, jamais de double), sans la marque « d'origine »
                        orig_fig_free(it, o)
                        if typ != "partial":
                            o.pop("attached_to", None)
                    if not fig and it.get("with_minifigs", True):   # ses figurines : gardées, en figurines seules (rangées dedans si c'est un set partiel)
                        for fid, n in fig_have(it, info.get("minifigs") or []).items():
                            if n > 0 and not any(o.get("number") == fid for o in origs):
                                f = {"id": uuid.uuid4().hex[:12], "list_id": it["list_id"], "kind": "fig", "number": fid, "quantity": n, "condition": "occasion",
                                     "with_minifigs": True, "missing_minifigs": [], "portion": 100, "parts": [], "added_at": now, "updated_at": now}
                                ph = ((it.get("fig_mods") or {}).get(fid) or {}).get("photo_url")
                                if ph:
                                    f["photo_url"] = ph
                                if typ == "partial":
                                    f["attached_to"] = it["id"]
                                db["items"].append(f)
                    if typ == "fig":   # une figurine MOC n'accueille pas de figurines rangées : elles redeviennent seules (un MOC ou un set partiel, si)
                        for x in db["items"]:
                            if x.get("attached_to") == it["id"]:
                                x.pop("attached_to", None)
                    invs = db.get("inventories") or {}
                    if it["id"] in invs and not fig:   # son inventaire reste, comme celui d'un set que je n'ai pas
                        inv = invs.pop(it["id"])
                        inv["set"] = it["number"]
                        invs.setdefault("set-" + it["number"], inv)
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "id": m.group(1)})
            m = re.fullmatch(r"/api/items/(\w+)/dup", p)
            if m:   # {"attach": id du set | ""} : une figurine à part, copie de celle-ci (en attente jusqu'à l'enregistrement)
                import copy as _copy
                bd = self.json_body()
                attach = str(bd.get("attach") or "")
                try:
                    nq = max(1, int(bd.get("qty") or 1))   # combien d'exemplaires sortent (1 par défaut)
                except (TypeError, ValueError):
                    nq = 1
                with lock:
                    db = load_db()
                    cache = _load(CACHE_FILE, {})
                    src = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not src or src.get("kind") != "fig":
                        return self.error("Figurine introuvable", 404)
                    new = _copy.deepcopy(src)
                    for k in ("set_orig", "split_from", "attached_to", "todos", "todo", "todo_note", "dup_pending", "bl_wanted", "bl_qty", "got", "bl_cond"):
                        new.pop(k, None)
                    now = int(time.time())
                    new.update(id=uuid.uuid4().hex[:12], quantity=nq, added_at=now, updated_at=now)
                    if attach:
                        host_t = next((i for i in db["items"] if i["id"] == attach), None)
                        if not host_t or not hostable(host_t):
                            return self.error("Set introuvable", 404)
                        new.update(attached_to=attach, list_id=host_t["list_id"])
                    if attach and bd.get("indiv") in ("orig", "add"):   # 🧩 exemplaire mis à part dans son set : pas de carte dans la vue générale
                        new["indiv"] = bd["indiv"]
                    prev = {}
                    defer = bool(bd.get("defer"))   # ⧉ copie : rien retiré de l'original ici (demandé à l'enregistrement : /dup-deduct)
                    dcopy = bool(bd.get("copy")) and bool(src.get("set_orig")) and bool(attach)   # « Dupliquer puis modifier » d'une ORIGINALE : une en plus, l'originale reste
                    if src.get("set_orig") and (defer or dcopy):   # figurine d'origine d'un set : ses personnalisations sur la copie (le set garde son compte)
                        host = next((i for i in db["items"] if i["id"] == src.get("attached_to")), None)
                        mo = ((host or {}).get("fig_mods") or {}).get(src["number"]) or {}
                        for k in ("display_name", "photo_url", "fig_swaps", "swap_price", "accessories", "rb_fig"):
                            if mo.get(k if k != "display_name" else "name") and not new.get(k):
                                new[k] = mo.get(k if k != "display_name" else "name")
                        new["quantity"] = 1
                        if dcopy:   # repère « copie pas encore modifiée » : ce qu'elle a hérité de l'originale (indiv_rejoin compare)
                            new["indiv_copy"] = {k: new[k] for k in INDIV_KEYS if new.get(k)}
                    elif defer:
                        new["quantity"] = 1
                    elif src.get("set_orig"):   # figurine d'origine d'un set : ses personnalisations sur la copie, le set en compte une de moins
                        host = next((i for i in db["items"] if i["id"] == src.get("attached_to")), None)
                        if host:
                            mo = (host.get("fig_mods") or {}).get(src["number"]) or {}
                            for k in ("display_name", "photo_url", "fig_swaps", "swap_price", "accessories", "rb_fig"):
                                if mo.get(k if k != "display_name" else "name") and not new.get(k):
                                    new[k] = mo.get(k if k != "display_name" else "name")
                            mfs = (cache.get(host["number"]) or {}).get("minifigs") or []
                            prev = {"host": host["id"], "counts": _copy.deepcopy(host.get("fig_counts")), "missing": list(host.get("missing_minifigs") or [])}
                            have = fig_have(host, mfs)
                            tot = have.get(src["number"], 0)
                            nq = min(nq, max(1, tot))
                            new["quantity"] = nq
                            if mo.get("fig_swaps") and tot > nq:   # pièces échangées sur tout le lot : partagées au prorata (pas copiées en entier)
                                t1, t2, p1, p2 = swaps_split(mo["fig_swaps"], mo.get("swap_price"), nq, tot)
                                new.pop("fig_swaps", None); new.pop("swap_price", None)
                                if t1:
                                    new["fig_swaps"] = t1
                                    if p1:
                                        new["swap_price"] = p1
                                if t2:
                                    mo["fig_swaps"] = t2
                                    if p2:
                                        mo["swap_price"] = p2
                                else:
                                    mo.pop("fig_swaps", None); mo.pop("swap_price", None)
                            have[src["number"]] = max(0, have.get(src["number"], 0) - nq)
                            if not have[src["number"]]:   # tous les exemplaires sont partis : leurs pièces échangées avec eux (rien ne reste sur la figurine du set)
                                mo.pop("fig_swaps", None); mo.pop("swap_price", None)
                            host["fig_counts"], host["missing_minifigs"] = have, []
                            orig_figs_sync(db, host, cache)
                    elif int(src.get("quantity", 1) or 1) > 1:   # lot : des exemplaires en moins
                        nq = min(nq, int(src["quantity"]) - 1)
                        new["quantity"] = nq
                        prev = {"qty": int(src["quantity"])}
                        src["quantity"] = int(src["quantity"]) - nq
                    if not bd.get("confirm"):
                        new["dup_pending"] = {"from": src["id"], **prev, **({"defer": True} if defer else {})}   # (effacé par le premier enregistrement de la copie)
                    db["items"].append(new)
                    keep = new
                    if not attach and bd.get("confirm") and not defer and (src.get("set_orig") or not new.get("fig_swaps")):   # sortie d'un set : rejoint la seule identique (pièces sûres seulement)
                        keep = fig_absorb(db, new)
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "id": keep["id"], **({"joined": True} if keep is not new else {})})
            m = re.fullmatch(r"/api/items/(\w+)/dup-deduct", p)
            if m:   # ⧉ copie enregistrée, « retirer un exemplaire de l'original » : l'original (ou son set) en compte un de moins
                with lock:
                    db = load_db()
                    new = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    dp = (new or {}).get("dup_pending") or {}
                    src = next((i for i in db["items"] if i["id"] == dp.get("from")), None)
                    if not src:
                        return self.error("Original introuvable", 404)
                    try:   # autant d'exemplaires que la copie en a (l'original en garde au moins un)
                        n = max(1, int(self.json_body().get("qty") or 1))
                    except (TypeError, ValueError):
                        n = 1
                    if src.get("set_orig"):
                        host = next((i for i in db["items"] if i["id"] == src.get("attached_to")), None)
                        if host:
                            cache = _load(CACHE_FILE, {})
                            have = fig_have(host, (cache.get(host["number"]) or {}).get("minifigs") or [])
                            have[src["number"]] = max(1, have.get(src["number"], 0) - n)
                            host["fig_counts"], host["missing_minifigs"] = have, []
                            orig_figs_sync(db, host, cache)
                    elif int(src.get("quantity", 1) or 1) > 1:
                        src["quantity"] = max(1, int(src["quantity"]) - n)
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/dup-cancel", p)
            if m:   # copie fermée sans être enregistrée : elle disparaît, l'original retrouve son exemplaire
                with lock:
                    db = load_db()
                    new = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not dup_cancel_apply(db, new):   # (la même annulation que celle des copies oubliées : dup_pending_purge)
                        return self.send_json({"ok": True, "kept": True})
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/into-set", p)
            if m:   # {"set": id} : ma figurine seule EST celle de ce set — rangée comme sa figurine d'origine (personnalisations et tâches gardées)
                sid = str(self.json_body().get("set") or "")
                fk = lambda n: (lambda x: x.group(1) + x.group(2) + x.group(3) if x else str(n or "").lower())(re.fullmatch(r"([a-z]+)0*(\d+)([a-z]?)", str(n or "").lower()))
                with lock:
                    db = load_db()
                    cache = _load(CACHE_FILE, {})
                    fig = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    host = next((i for i in db["items"] if i["id"] == sid), None)
                    if not fig or fig.get("kind") != "fig" or fig.get("as_set") or fig.get("attached_to") or not host or host.get("kind", "set") != "set":
                        return self.error("Figurine ou set introuvable", 404)
                    _kd = list_kinds(db)
                    if _kd.get(fig.get("list_id")) != "collection" or _kd.get(host.get("list_id")) != "collection":   # (jamais avec la liste de souhaits)
                        return self.error("La figurine et le set doivent être tous les deux dans la collection")
                    mfs = (cache.get(host["number"]) or {}).get("minifigs") or []
                    f = next((x for x in mfs if fk(x["id"]) == fk(fig["number"])), None)
                    if not f:
                        return self.error("Cette figurine n'est pas dans ce set")
                    backup_db("avant-figurine-rangee-dans-son-set")
                    host["fig_items"] = True
                    have = fig_have(host, mfs)
                    want = int(f.get("qty", 1) or 1) * max(1, int(host.get("quantity", 1) or 1))   # (originales prévues par le set)
                    have0 = have.get(f["id"], 0)
                    if have.get(f["id"], 0) < want:   # le set en comptait moins que prévu (absente, ou sortie avec le −) : elle y revient
                        have[f["id"]] = have.get(f["id"], 0) + 1
                        host["fig_counts"], host["missing_minifigs"] = have, []
                    todos, notes = [], ""
                    if int(fig.get("quantity", 1) or 1) <= 1:   # c'était la seule : elle devient la figurine d'origine du set (tout ce qui est à elle suit)
                        mo = host.setdefault("fig_mods", {}).setdefault(f["id"], {})
                        for a, b2 in (("display_name", "name"), ("photo_url", "photo_url"), ("alt_photos", "alt_photos"), ("alt_names", "alt_names"), ("alt_hidden", "alt_hidden"),
                                      ("main_name", "main_name"), ("fig_swaps", "fig_swaps"), ("swap_price", "swap_price"), ("accessories", "accessories"), ("rb_fig", "rb_fig")):
                            if fig.get(a) and not mo.get(b2):
                                mo[b2] = fig[a]
                        if not mo:
                            host["fig_mods"].pop(f["id"], None)
                        todos, notes = clean_todos(fig), str(fig.get("notes") or "").strip()
                        db["items"] = [i for i in db["items"] if i is not fig]
                    else:   # plusieurs seules : une rejoint le set, les autres restent seules
                        if not have0 and fig.get("fig_swaps") and not ((host.get("fig_mods") or {}).get(f["id"]) or {}).get("fig_swaps"):   # (seule originale du set : ses modifications avec elle)
                            sw1 = fig_swaps_scale(fig["fig_swaps"], int(fig.get("quantity", 1) or 1), 1)
                            if sw1:
                                mo = host.setdefault("fig_mods", {}).setdefault(f["id"], {})
                                mo["fig_swaps"], mo["swap_price"] = sw1, {"delta": 0, "done": False}
                        fig["quantity"] = int(fig["quantity"]) - 1
                    orig_figs_sync(db, host, cache)
                    child = next((i for i in db["items"] if i.get("attached_to") == host["id"] and i.get("set_orig") and i["number"] == f["id"]), None)
                    if child and fig.get("list_id") and fig.get("list_id") != host.get("list_id") and _kd.get(fig.get("list_id")) == "collection":
                        child["list_id"] = fig["list_id"]   # (elle garde SA liste : une figurine peut être dans une autre liste que son set)
                    if child and (todos or notes):
                        ts = clean_todos(child) + todos
                        child["todos"], child["todo"], child["todo_note"] = ts[:12], bool(ts), ts[0]["note"] if ts else ""
                        if notes:
                            child["notes"] = ((child.get("notes") or "") + "\n" + notes).strip()[:2000]
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/attach", p)
            if m:   # {"set": id, "qty": n} : n exemplaires rangés dans un set (lot séparé) ; {"set": ""} : retirés du set
                b = self.json_body()
                set_id = str(b.get("set") or "")
                import copy as _copy
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not it or it.get("kind") not in ("fig", "custom"):
                        return self.error("Figurine introuvable", 404)
                    if set_id:   # règles : seule une figurine (ou une figurine MOC) se range, dans un set / set partiel / set MOC de la même sorte de liste
                        _host = next((i for i in db["items"] if i["id"] == set_id), None)
                        if not childable(it):
                            return self.error("Seule une figurine (ou une figurine MOC) peut être rangée dans un set")
                        if not _host or _host is it or not hostable(_host):
                            return self.error("Set introuvable", 404)
                        _kd = list_kinds(db)
                        if _kd.get(it.get("list_id"), "collection") != _kd.get(_host.get("list_id"), "collection"):
                            return self.error("Ce set n'est pas dans la même sorte de liste que la figurine (collection ou liste de souhaits)")
                    if it.get("set_orig") and set_id != it.get("attached_to"):   # figurine d'origine qui quitte son set : indépendante, déduite du set
                        orig_fig_leaves(db, it)
                    it["updated_at"] = int(time.time())
                    if set_id:
                        host = next((i for i in db["items"] if i["id"] == set_id), None)
                        if host:
                            touch_for_fig(host)   # c'est la figurine qui change (elle a sa propre date)
                        if not host or not hostable(host):
                            return self.error("Set introuvable", 404)
                        have = max(1, int(it.get("quantity", 1) or 1))
                        try:
                            n = max(1, min(have, int(b.get("qty") or have)))
                        except (TypeError, ValueError):
                            n = have
                        if n >= have:
                            it["attached_to"] = set_id
                        else:   # lot séparé : n exemplaires partent dans le set, le reste reste seul
                            it["quantity"] = have - n
                            part = _copy.deepcopy(it)
                            part.update(id=uuid.uuid4().hex[:12], quantity=n, attached_to=set_id, split_from=it["id"], added_at=int(time.time()))
                            db["items"].append(part)
                        moved = it if n >= have else part   # (lot identique déjà dans ce set : il le rejoint, pas de fiche en double)
                        plain = lambda x: not (x.get("notes") or x.get("todos") or x.get("accessories") or x.get("alt_photos") or x.get("indiv") or x.get("set_orig"))
                        same = lambda x: (x.get("kind"), x.get("number"), x.get("display_name") or "", x.get("photo_url") or "", json.dumps(x.get("fig_swaps") or [], sort_keys=True))
                        twin = next((x for x in db["items"] if x is not moved and x.get("attached_to") == set_id and plain(x) and plain(moved) and same(x) == same(moved)), None)
                        if twin:
                            twin["quantity"] = int(twin.get("quantity", 1) or 1) + int(moved.get("quantity", 1) or 1)
                            twin["updated_at"] = int(time.time())
                            db["items"] = [x for x in db["items"] if x is not moved]
                    else:   # retour : les exemplaires rejoignent leur lot d'origine s'il existe encore (ou une minifig identique seule)
                        it.pop("attached_to", None)
                        home = next((i for i in db["items"] if i["id"] == it.get("split_from") and not i.get("attached_to")), None)
                        if not home and it.get("kind") == "fig":
                            home = next((i for i in db["items"] if i is not it and i.get("kind") == "fig" and i["number"] == it["number"]
                                         and i["list_id"] == it["list_id"] and not i.get("attached_to") and not i.get("fig_swaps")), None)
                        if home:
                            home["quantity"] = int(home.get("quantity", 1) or 1) + int(it.get("quantity", 1) or 1)
                            db["items"] = [i for i in db["items"] if i is not it]
                        it.pop("split_from", None)
                        if not home:   # (même modifiée : la seule identique, ses pièces échangées ramenées au total)
                            fig_absorb(db, it)
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/moc-review/(\w+)/cancel", p)
            if m:   # annuler le scan : le MOC sort de « MOC à valider » (ses pièces restent modifiables dans sa fiche)
                with lock:
                    if m.group(1) in _scan_queue:
                        _scan_queue.remove(m.group(1))
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not it or it.get("kind") != "custom":
                        return self.error("MOC introuvable", 404)
                    it["moc_scan"] = "cancelled"
                    if self.json_body().get("remove"):   # et retiré de « MOC à valider »
                        it["moc_reviewed"] = True
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/moc-scan/(\w{16})/slots", p)
            if m:   # pièces repérées d'une photo scannée (jeton) : propositions par emplacement, pour les valider dans la fiche
                tok = _tmp_scans.get(m.group(1))
                if not tok:
                    return self.error("Scan expiré : rescannez la photo", 404)
                slots, others = review_slots({"zones": tok[1]})
                return self.send_json({"slots": slots, "others": others})
            if p == "/api/moc-scan/photo":   # photo d'une figurine MOC pas encore enregistrée : scannée tout de suite → {token, found}
                data = self.body()
                if not data:
                    return self.error("Photo manquante")
                try:
                    zones = scan_fig(data, [])
                except Exception as e:
                    print("Scan immédiat impossible :", e, flush=True)
                    return self.error("Scan indisponible, reprise automatique plus tard", 503)
                now = time.time()
                for k in [k for k, v in _tmp_scans.items() if now - v[0] > 7200]:
                    _tmp_scans.pop(k, None)
                tok = uuid.uuid4().hex[:16]
                _tmp_scans[tok] = (now, zones)
                return self.send_json({"token": tok, "found": sum(1 for z in zones.values() if (z or {}).get("items"))})
            m = re.fullmatch(r"/api/moc-review/(\w+)/scan", p)
            if m:   # scan maintenant : photo de la minifig + photos supplémentaires {"images": ["data:image/jpeg;base64,…"]} (non gardées)
                import base64
                b = self.json_body()
                extras = []
                for u in (b.get("images") or [])[:6]:
                    try:
                        extras.append(base64.b64decode(str(u).split(",", 1)[-1]))
                    except Exception:
                        pass
                if not moc_scan_item(m.group(1), extras, "exploded" if b.get("mode") == "exploded" else "assembled", bool(b.get("append"))):
                    return self.error("Scan impossible (photo de la figurine manquante ?)")
                db = load_db()
                it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                fig = review_fig(it, _load(REVIEW_FILE, {}))
                review_images_fill([fig])
                return self.send_json(fig)
            if p == "/api/parts/photo":
                ctype = self.headers.get("Content-Type", "image/jpeg")
                data = self.body()
                if not data:
                    return self.error("Aucune image reçue")
                found = sources.recognize(data, content_type=ctype, kind="parts")[:5]
                out, t0, later = [], time.time(), []
                for r in found:
                    if "bl:" + r["number"] in _parts_cache() or time.time() - t0 < 4:
                        rbp = cached_part_from_bricklink(r["number"])
                    else:   # temps écoulé : réponse tout de suite, correspondance cherchée en arrière-plan
                        rbp = None
                        later.append(r["number"])
                    out.append({**(rbp or {"part_num": r["number"], "name": r["name"], "image": r["image"],
                                           "bricklink": r["number"]}),
                                "score": r["score"], "photo_image": r["image"], "found_on_rb": bool(rbp) or None if r["number"] in later else bool(rbp)})
                if later:
                    threading.Thread(target=lambda ns: [cached_part_from_bricklink(n) for n in ns], args=(later,), daemon=True).start()
                return self.send_json(out)
            if p == "/api/photo":
                ctype = self.headers.get("Content-Type", "image/jpeg")
                data = self.body()
                if not data:
                    return self.error("Aucune image reçue")
                found = sources.recognize_all(data, content_type=ctype)
                return self.send_json(found)
            if p == "/api/cutout":   # 🪄 détourage ISNet (sur ce serveur, une photo à la fois) → PNG fond blanc ; erreur : l'appli détoure sur l'appareil
                data = self.body()
                if DEMO or not os.path.isfile(CUTOUT_PY) or not os.path.isfile(CUTOUT_MODEL):
                    return self.error("Détourage serveur indisponible", 503)
                if not data or len(data) > 12 * 1024 * 1024 or not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"RIFF"):
                    return self.error("Image absente, trop lourde ou dans un format non accepté")
                if not _cutout_lock.acquire(timeout=90):   # une à la fois (mémoire : ~810 Mo au pic)
                    return self.error("Détourage occupé, réessayez", 503)
                try:
                    with tempfile.TemporaryDirectory() as td:
                        src, dst = os.path.join(td, "in"), os.path.join(td, "out.png")
                        with open(src, "wb") as f:
                            f.write(data)
                        mode = "mask" if (parse_qs(urlparse(self.path).query).get("mask") or [""])[0] == "1" else "photo"   # ?mask=1 : le masque seul (l'appli l'applique en pleine taille)
                        r = subprocess.run([CUTOUT_PY, os.path.join(ROOT, "detourage.py"), CUTOUT_MODEL, src, dst, mode],
                                           capture_output=True, timeout=120)
                        if r.returncode or not os.path.isfile(dst):
                            print("Détourage ISNet :", r.stderr.decode("utf-8", "ignore")[-300:], flush=True)
                            return self.error("Détourage impossible", 500)
                        with open(dst, "rb") as f:
                            out = f.read()
                finally:
                    _cutout_lock.release()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(out)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(out)
                return
            if p == "/api/upload":
                data = self.body()
                if not data or len(data) > 8 * 1024 * 1024:
                    return self.error("Image absente ou trop lourde (8 Mo max)")
                if DEMO and sum(e.stat().st_size for e in os.scandir(UPLOAD_DIR)) > 300 * 1024 * 1024:
                    return self.error("Démo : plus de place pour les photos d'ici la prochaine remise à zéro", 507)
                if data[:3] == b"\xff\xd8\xff":
                    ext = ".jpg"
                elif data[:8] == b"\x89PNG\r\n\x1a\n":
                    ext = ".png"
                elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
                    ext = ".webp"
                else:
                    return self.error("Format d'image non accepté (JPEG, PNG ou WebP)")
                name = uuid.uuid4().hex
                with open(os.path.join(UPLOAD_DIR, name + ext), "wb") as f:
                    f.write(data)
                return self.send_json({"url": f"/api/upload/{name}"}, 201)
            if p == "/api/inventory-xml":   # nouvel inventaire depuis un XML (BrickLink / CSV Rebrickable) : {"name", "text"}
                b = self.json_body()
                text = str(b.get("text") or "")
                name = str(b.get("name") or "").strip()[:150] or "Inventaire XML"
                if not text.strip():
                    return self.error("Collez le contenu du XML")
                if len(text) > 5_000_000:
                    return self.error("Fichier trop gros")
                try:
                    lots, skipped = parse_moc_parts(text)
                    cm = moc_color_maps()
                except PermissionError:
                    return self.error("Il faut une clé API Rebrickable (Réglages) pour lire les couleurs")
                except Exception as e:
                    return self.error(f"Fichier illisible : {e}")
                bo_rb = {}
                for k, v in cm.get("rb", {}).items():
                    bo_rb.setdefault(v, int(k))
                cols, pc, rows = colors_fr(), _parts_cache(), []
                for x in lots:
                    cid = bo_rb.get(x["color"])
                    if cid is None:
                        skipped += 1
                        continue
                    f, col = pc.get("bl:" + x["part"]) or {}, cols.get(str(cid)) or {}
                    rows.append({"part_num": x["part"], "name": f.get("name") or x["part"], "color_id": cid, "color_name": col.get("name") or x["color"],
                                 "rgb": col.get("rgb"), "trans": col.get("trans"), "quantity": x["qty"], "element_id": None,
                                 "image": f.get("image"), "part_image": f.get("image"), "bricklink": x["part"]})
                if not rows:
                    return self.error("Aucune pièce reconnue dans ce XML")
                num = "xml-" + uuid.uuid4().hex[:10]
                _parts_cache_put("inv:" + num, rows)
                with lock:
                    db = load_db()
                    db.setdefault("inventories", {})["set-" + num] = {"rows": {}, "set": num, "name": name, "label": name, "xml": True, "updated": int(time.time()), "created": int(time.time())}
                    _save(DB_FILE, db)
                missing = [x["part"] for x in lots if "bl:" + x["part"] not in pc]
                if missing:
                    moc_names_fill(list(dict.fromkeys(missing)))   # noms et photos des pièces, en arrière-plan
                return self.send_json({"key": "set-" + num, "refs": len(rows), "pieces": sum(r["quantity"] for r in rows), "skipped": skipped})
            m = re.fullmatch(r"/api/inventory/([\w.-]+)/commande", p)
            if m:   # {"parts": [{row, part_num, part_name, bricklink, color_id, color_name, color_rgb, element_id, image, quantity}], "set_number"}
                b, key = self.json_body(), m.group(1)
                with lock:
                    db = load_db()
                    inv = (db.get("inventories") or {}).get(key)
                    if not inv:
                        return self.error("Inventaire introuvable", 404)
                    pls = [l for l in db["lists"] if l.get("kind") == "parts"]
                    lst = next((l for l in pls if l.get("default")), None) or next((l for l in pls if re.search(r"command", l.get("name", ""), re.I)), None) or (pls[0] if pls else None)
                    if not lst:
                        return self.error("Créez d'abord une liste de pièces « À commander »")
                    n = 0
                    for x in (b.get("parts") or [])[:3000]:
                        row = str(x.get("row") or "")[:60]
                        if not row or not x.get("part_num") or x.get("color_id") in (None, "") or (inv.get("rows", {}).get(row) or {}).get("s") != "order":
                            continue
                        try:
                            q = max(1, min(9999, int(x.get("quantity") or 1)))
                        except (TypeError, ValueError):
                            q = 1
                        link = {"inv": key, "row": row, "q": q}
                        same = next((i for i in db["items"] if i["list_id"] == lst["id"] and i.get("kind") == "part" and not i.get("bl_qty")   # exportée : on n'y touche plus
                                     and not i.get("got") and not i.get("ordered") and not i.get("cmd_m")   # (commandée ou reçue : une nouvelle ligne — 22/11)
                                     and i.get("part_num") == x["part_num"] and str(i.get("color_id")) == str(x["color_id"])), None)
                        if same:
                            same["quantity"] = min(9999, same.get("quantity", 1) + q)
                            same["inv_links"] = (same.get("inv_links") or []) + [link]
                            same["updated_at"] = int(time.time())
                        else:
                            it = self.clean_item({**x, **part_img_fix(x), "kind": "part", "number": x["part_num"], "list_id": lst["id"], "quantity": q,
                                                  "set_number": b.get("set_number") or "", "inv_links": [link]})
                            it.update(id=uuid.uuid4().hex[:12], added_at=int(time.time()))
                            db["items"].append(it)
                        inv_row_status(db, key, row, "cmd")
                        n += 1
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "rows": n, "list": lst["name"]})
            m = re.fullmatch(r"/api/inventory/([\w.-]+)/xml", p)
            if m:   # {parts: [{part_num, bricklink, color_id, quantity}]} → XML BrickLink (BrickOwl le lit aussi) — l'inventaire ne bouge pas (21/11 soir)
                from xml.sax.saxutils import escape as _x
                rb, names, out, skipped = rbbl_map(), part_names(), [], []
                for x in (self.json_body().get("parts") or [])[:2000]:
                    pn = str(x.get("part_num") or "")[:40]
                    bl = str(x.get("bricklink") or "") or (names.get(pn) or {}).get("bl") or pn
                    col = rb.get(str(x.get("color_id")))
                    if not bl or col is None:
                        skipped.append(pn)
                        continue
                    try:
                        q = max(1, min(9999, int(x.get("quantity") or 1)))
                    except (TypeError, ValueError):
                        q = 1
                    out.append(f"  <ITEM>\n    <ITEMTYPE>P</ITEMTYPE>\n    <ITEMID>{_x(bl)}</ITEMID>\n    <COLOR>{col}</COLOR>\n    <MINQTY>{q}</MINQTY>\n    <CONDITION>X</CONDITION>\n  </ITEM>\n")
                return self.send_json({"xml": "<INVENTORY>\n" + "".join(out) + "</INVENTORY>\n", "refs": len(out), "skipped": skipped})
            m = re.fullmatch(r"/api/items/(\w+)/recue", p)
            if m:   # {"n"} : pièces reçues — la quantité baisse (ou la pièce sort de la liste) ; les lignes d'inventaire couvertes passent OK
                b = self.json_body()
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1) and i.get("kind") == "part"), None)
                    if not it:
                        return self.error("Pièce introuvable", 404)
                    have = it.get("quantity", 1) or 1
                    try:
                        n = max(1, min(have, int(b.get("n") or have)))
                    except (TypeError, ValueError):
                        n = have
                    left, keep, done = n, [], 0
                    for ln in it.get("inv_links") or []:
                        if left >= ln["q"]:   # quantité suffisante : la ligne de l'inventaire est validée
                            inv_row_status(db, ln["inv"], ln["row"], "ok")
                            left -= ln["q"]
                            done += 1
                        else:
                            if left:
                                ln = {**ln, "q": ln["q"] - left}
                                left = 0
                            keep.append(ln)
                    if n >= have:
                        db["items"].remove(it)
                    else:
                        it["quantity"] = have - n
                        if it.get("bl_qty"):   # reçues : d'abord celles de la wanted list BrickLink
                            it["bl_qty"] = max(0, int(it["bl_qty"]) - n)
                            if not it["bl_qty"]:
                                it.pop("bl_qty"); it.pop("bl_wanted", None)
                        it["updated_at"] = int(time.time())
                        if keep:
                            it["inv_links"] = keep
                        else:
                            it.pop("inv_links", None)
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "left": max(0, have - n), "rows_ok": done})
            m = re.fullmatch(r"/api/inventory/([\w.-]+)/supprimer", p)
            if m:
                b, moved = self.json_body(), 0
                with lock:
                    db = load_db()
                    inv = (db.get("inventories") or {}).get(m.group(1)) or {}
                    mv = [x for x in (b.get("moves") or [])[:3000] if isinstance(x, dict)]   # (pièces COMMANDÉES → « Commandes » — 22/11)
                    if inv and mv:
                        pls = [l for l in db["lists"] if l.get("kind") == "parts"]
                        lst = next((l for l in pls if l.get("default")), None) or next((l for l in pls if re.search(r"command", l.get("name", ""), re.I)), None) or (pls[0] if pls else None)
                        linked = {str(lk.get("row")) for i in db["items"] for lk in i.get("inv_links") or [] if lk.get("inv") == m.group(1)}
                        for x in mv if lst else []:
                            row = str(x.get("row") or "")[:60]
                            rs = (inv.get("rows") or {}).get(row) or {}
                            if rs.get("s") != "cmd" or row in linked or not x.get("part_num") or x.get("color_id") in (None, ""):
                                continue
                            try:
                                q = max(1, min(9999, int(x.get("quantity") or rs.get("q") or 1)))
                            except (TypeError, ValueError):
                                q = 1
                            it = self.clean_item({**x, **part_img_fix(x), "kind": "part", "number": x["part_num"], "list_id": lst["id"], "quantity": q,
                                                  "set_number": b.get("set_number") or inv.get("set") or "",
                                                  "ordered": [{**o, "qty": min(int(o.get("qty") or 0), q) or q} for o in rs.get("o") or [] if isinstance(o, dict)],
                                                  "cmd_m": rs.get("m") or (0 if rs.get("o") else int(time.time())), "o_off": rs.get("o_off") or []})
                            it.update(id=uuid.uuid4().hex[:12], added_at=int(time.time()))
                            db["items"].append(it)
                            moved += 1
                    (db.get("inventories") or {}).pop(m.group(1), None)
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "moved": moved})
            m = re.fullmatch(r"/api/inventory/([\w.-]+)", p)
            if m:   # enregistre l'état d'une ou plusieurs lignes : {"rows": {"3001|5": {"s": "ok"|"order"|"", "q": 2}}}
                b = self.json_body()
                key = m.group(1)
                with lock:
                    db = load_db()
                    if not key.startswith("set-") and not any(i["id"] == key for i in db["items"]):
                        return self.error("Set introuvable", 404)
                    inv = db.setdefault("inventories", {}).setdefault(key, {"rows": {}, "created": int(time.time())})   # (created : une commande d'avant ne le valide jamais)
                    if key.startswith("set-"):
                        inv["set"] = key[4:]
                        if b.get("name"):
                            inv["name"] = str(b["name"])[:150]
                    if "photo" in b:   # photo choisie pour l'inventaire (vide = photo du set)
                        ph = str(b.get("photo") or "")[:400]
                        if re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", ph) or re.match(
                                r"https://(www\.brickeconomy\.com|cdn\.rebrickable\.com|storage\.googleapis\.com/brickognize-static)/", ph):
                            inv["photo"] = ph
                        else:
                            inv.pop("photo", None)
                    if "label" in b:   # nom choisi par l'utilisateur (vide = nom du set)
                        label = str(b.get("label") or "").strip()[:150]
                        if label:
                            inv["label"] = label
                        else:
                            inv.pop("label", None)
                    forced = {}   # lignes dont l'état est corrigé ici (renvoyées à l'appli)
                    for k, v in (b.get("rows") or {}).items():
                        v = v or {}
                        st = v.get("s") if v.get("s") in ("ok", "order", "x", "cmd") else ""
                        prev = (inv["rows"].get(str(k)) or {}).get("s")
                        linked = [i for i in db["items"] if i.get("kind") == "part"
                                  and any(l.get("inv") == key and l.get("row") == str(k) for l in i.get("inv_links") or [])]   # sa pièce dans « À commander »
                        if linked and st == "ok":   # commandée → reçue : ✔ OK dans « À commander » (« Nettoyer » la retire)
                            for i in linked:
                                if all(l.get("row") == str(k) or (inv["rows"].get(l.get("row")) or {}).get("s") == "ok"
                                       for l in i.get("inv_links") or [] if l.get("inv") == key):
                                    i["got"] = True
                        elif linked and prev == "ok" and st in ("", "cmd"):   # OK retiré : de nouveau en commande
                            for i in linked:
                                i.pop("got", None)
                            st = forced[str(k)] = "cmd"
                        elif prev in ("cmd", "ok") and st != "cmd":   # remise à commander, exclue ou vidée : elle quitte « À commander »
                            unlink_order(db, key, str(k))
                        row = {}
                        if st:
                            try:
                                q = max(1, min(9999, int(v.get("q") or 1)))
                            except (TypeError, ValueError):
                                q = 1
                            row.update(s=st, q=q)
                            if st in ("order", "cmd") and prev in ("order", "cmd") and (inv["rows"].get(str(k)) or {}).get("t"):
                                row["t"] = inv["rows"][str(k)]["t"]   # (date du passage « à commander » : gardée)
                            elif st == "order" and prev != "order":
                                row["t"] = int(time.time())   # passée « à commander » maintenant : seules les commandes d'après la servent
                        if str(v.get("c", "")).lstrip("-").isdigit():   # couleur choisie pour cette pièce
                            row["c"] = int(v["c"])
                            ci = str(v.get("ci") or "")
                            if ci.startswith("https://cdn.rebrickable.com/"):
                                row["ci"] = ci[:300]
                            if re.fullmatch(r"[\w.-]{1,40}", str(v.get("p") or "")):   # pièce de même forme choisie
                                row["p"] = str(v["p"])
                                row["pn"] = str(v.get("pn") or "")[:150]
                        prow = inv["rows"].get(str(k)) or {}   # (ce que mes commandes ont posé : gardé — 21/11 soir)
                        if st in ("cmd", "ok") and prow.get("o"):
                            row["o"] = prow["o"]
                            if prow.get("o_lock"):
                                row["o_lock"] = True   # (attribuée à la main depuis « Commandées en plus » — 22/11)
                        if st in ("cmd", "ok") and not row.get("o"):   # « Commandée » à la main : sa date (m) — gardée jusqu'à OK compris
                            try:
                                mm = int(v.get("m") or prow.get("m") or 0)
                            except (TypeError, ValueError):
                                mm = 0
                            if st == "cmd" and prev != "cmd" and not mm:
                                mm = int(time.time())
                            if mm:
                                row["m"] = mm
                        offs = set(prow.get("o_off") or [])
                        if prev == "cmd" and prow.get("o") and st in ("order", ""):   # remise « à commander » à la main : cette commande ne la reprend plus
                            offs |= {o.get("order") for o in prow["o"] if o.get("order")}
                        if offs:
                            row["o_off"] = sorted(offs)
                        if row:
                            inv["rows"][str(k)[:60]] = row
                        else:
                            inv["rows"].pop(str(k), None)
                    if isinstance(b.get("swaps"), dict):   # « remplacer le rose par du rouge »
                        inv["swaps"] = {str(int(a)): int(c) for a, c in b["swaps"].items()
                                        if str(a).lstrip("-").isdigit() and str(c).lstrip("-").isdigit() and int(a) != int(c)}
                    inv["updated"] = int(time.time())
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "updated": inv["updated"], "forced": forced})
            if p == "/api/parts/price":   # Réglages : chiffrer les pièces de la collection
                if not sources.rebrickable_key():
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                return self.send_json(start_parts_pricing())
            if p == "/api/boxcode":   # code inconnu : on retient la minifig choisie pour ce code
                b = self.json_body()
                code, fig = str(b.get("code") or ""), str(b.get("fig") or "")[:30]
                if not re.fullmatch(r"\d{7}", code) or not fig:
                    return self.error("Code ou figurine invalide")
                with lock:
                    t = _load(BOX_CODES_FILE, {})
                    t[code] = {"name": str(b.get("name") or fig)[:120], "series": "Appris", "fig": fig, "learned": int(time.time())}
                    _save(BOX_CODES_FILE, t)
                return self.send_json({"ok": True})
            if p == "/api/demo/reset" and not DEMO:   # Réglages : remettre la démo publique à zéro maintenant
                _demo["now"].set()
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/to-inventory", p)
            if m:   # pièce « à commander » reçue : cochée dans l'inventaire du set, retirée de la liste
                key = str(self.json_body().get("key") or "")
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1) and i.get("kind") == "part"), None)
                    if not it:
                        return self.error("Pièce introuvable", 404)
                    name = inv_mark_ok(db, key, it.get("part_num"), it.get("color_id"), it.get("quantity"))
                    if not name:
                        return self.error("Cette pièce n'est pas dans cet inventaire")
                    db["items"] = [i for i in db["items"] if i["id"] != it["id"]]
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "name": name})
            if p == "/api/part-to-inventory":   # une pièce (d'un set, d'une minifig, d'un MOC…) cochée dans l'inventaire d'un set
                b = self.json_body()
                with lock:
                    db = load_db()
                    name = inv_mark_ok(db, str(b.get("key") or ""), str(b.get("part_num") or ""), b.get("color_id"), b.get("qty"))
                    if not name:
                        return self.error("Cette pièce n'est pas dans cet inventaire")
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "name": name})
            m = re.fullmatch(r"/api/items/(\w+)/moc-lot", p)
            if m:   # une pièce (ou quelques exemplaires) retirée de la liste d'un MOC / set partiel
                b = self.json_body()
                try:
                    col = moc_color_maps()["rb"].get(str(b.get("color_id")))
                except Exception:
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                part = str(b.get("part") or "")
                try:
                    q = max(1, int(b.get("qty") or 1))
                except (TypeError, ValueError):
                    q = 1
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not it or it.get("kind") != "custom":
                        return self.error("MOC introuvable", 404)
                    lots = it.get("moc_parts") or []
                    x = next((x for x in lots if str(x.get("part")) == part and (str(x.get("color")) == str(col) or str(x.get("color_id")) == str(b.get("color_id")))), None)
                    if not x:
                        return self.error("Pièce introuvable dans la liste", 404)
                    x["qty"] = int(x.get("qty") or 1) - q
                    lots = [y for y in lots if int(y.get("qty") or 0) > 0]
                    it.pop("moc_price", None)
                    if lots:
                        it["moc_parts"] = lots
                        it["moc_price"] = {"total": 0, "priced": 0, "missing": 0, "lots": len(lots), "done": False, "t": int(time.time())}
                    else:
                        it.pop("moc_parts", None)
                        it.pop("moc_file", None)
                    it["updated_at"] = int(time.time())
                    _save(DB_FILE, db)
                item_parts_refresh(m.group(1))
                if lots:
                    moc_price_start(m.group(1), front=len(lots) <= 20)
                return self.send_json({"ok": True, "lots": len(lots)})
            if p == "/api/lot-zones":   # {lots} : zone du prix BrickLink de chaque pièce (drapeau des tuiles)
                lots = self.json_body().get("lots")
                return self.send_json(lot_zones([x for x in lots if isinstance(x, dict)] if isinstance(lots, list) else []))
            if p == "/api/lot-chg":   # variation du prix de chaque pièce depuis le relevé d'avant (cache seulement, aucun appel réseau)
                lots, pc, out = self.json_body().get("lots"), _parts_cache(), {}
                for l in (lots if isinstance(lots, list) else [])[:600]:
                    if isinstance(l, dict) and l.get("part"):
                        part, color = str(l.get("part"))[:40], str(l.get("color") or "")[:60]
                        v = part_chg(part, color, pc)
                        if v is not None:
                            out[f"{part}|{color}"] = v
                return self.send_json({"chg": out})
            if p == "/api/lot-prices":   # prix des pièces d'une figurine (connus tout de suite, les autres en fond)
                lots = self.json_body().get("lots")
                return self.send_json(lot_prices_cached([x for x in lots if isinstance(x, dict)] if isinstance(lots, list) else []))
            if p == "/api/manual-price":   # {"part", "part_num", "color", "color_id", "unit"} : mon prix pour une pièce introuvable (null : retiré)
                b = self.json_body()
                try:
                    unit = None if b.get("unit") in (None, "") else round(max(0.0, min(9999.0, float(str(b["unit"]).replace(",", ".")))), 3)
                except (TypeError, ValueError):
                    return self.error("Prix invalide")
                part, color = str(b.get("part") or "")[:40], str(b.get("color") or "")[:60]
                pn, cid = str(b.get("part_num") or "")[:40], b.get("color_id")
                if not color and pn and cid is not None:
                    color = (moc_color_maps().get("rb") or {}).get(str(cid)) or ""
                keys = ([f"rb:{pn}|{cid}"] if pn and cid is not None else []) + ([f"bl:{part}|{color}"] if part and color else [])
                if not keys:
                    return self.error("Pièce non reconnue")
                with lock:
                    mp = _load(MANUAL_FILE, {})
                    for k in keys:
                        if unit is None:
                            mp.pop(k, None)
                        else:
                            mp[k] = {"unit": unit, "t": int(time.time())}
                    _save(MANUAL_FILE, mp)
                    db = load_db()   # fiches qui contiennent la pièce : rechiffrées
                    hit = []
                    names = {part, pn} - {""}
                    for it in db["items"]:
                        touched = False
                        for fid, tgt in _swap_targets(it):
                            sws = tgt.get("fig_swaps") or []
                            if any((x.get(s) or {}).get("part") in names or (x.get(s) or {}).get("part_num") in names for x in sws for s in ("orig", "new")):
                                tgt["swap_price"] = {**(tgt.get("swap_price") or {}), "done": False}
                                touched = True
                        if any(str(x.get("part")) in names for x in it.get("moc_parts") or []):
                            touched = True
                        if touched:
                            hit.append(it["id"])
                    if hit:
                        _save(DB_FILE, db)
                for iid in hit:
                    moc_price_start(iid, front=True)
                return self.send_json({"ok": True, "unit": unit, "items": len(hit)})
            if p in ("/api/shares", "/api/shares/stop", "/api/shares/prices"):   # partage d'une fiche : un lien par fiche, supprimé à l'arrêt
                if DEMO:
                    return self.error("Le partage n'est pas disponible dans la démo", 403)
                b = self.json_body()
                with lock:
                    sh = _load(SHARES_FILE, {})
                    if p == "/api/shares/prices":   # {token, prices} : prix affichés ou non sur ce lien — effet immédiat, le lien reste le même
                        s = sh.get(str(b.get("token") or ""))
                        if not s:
                            return self.error("Lien de partage introuvable", 404)
                        if b.get("prices") is False:
                            s["prices"] = False
                        else:
                            s.pop("prices", None)
                        _save(SHARES_FILE, sh)
                        return self.send_json({"ok": True, "prices": s.get("prices") is not False})
                    if p == "/api/shares/stop":
                        gone = [t for t, s in sh.items() if t == b.get("token") or (b.get("item_id") and s.get("item") == b.get("item_id"))]
                        for t in gone:
                            sh.pop(t, None)
                            _share_memo.pop(t, None)
                        _save(SHARES_FILE, sh)
                        return self.send_json({"ok": True, "stopped": len(gone)})
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == b.get("item_id")), None)
                    if not it:
                        return self.error("Fiche introuvable", 404)
                    fig = str(b.get("fig") or "")[:40]   # minifig d'un set : partagée seule
                    if fig and not set_fig_entry(it, db, fig)[0]:
                        return self.error("Figurine introuvable dans ce set", 404)
                    tok = next((t for t, s in sh.items() if s.get("item") == b.get("item_id") and (s.get("fig") or "") == fig), None)
                    if not tok:
                        tok = secrets.token_urlsafe(18)
                        sh[tok] = {"item": b["item_id"], "at": int(time.time()), **({"fig": fig} if fig else {})}
                        _save(SHARES_FILE, sh)
                return self.send_json({"ok": True, "token": tok, "url": f"/s/{tok}"})
            if p == "/api/rule-todos":   # tâches posées par les règles « si… alors » du back office : l'état voulu COMPLET (les tâches à moi : jamais touchées)
                want = self.json_body().get("items")
                want = want if isinstance(want, dict) else {}
                changed = 0
                with lock:
                    db = load_db()
                    for it in db["items"]:
                        w, seen = [], set()
                        for t in (want.get(it["id"]) if isinstance(want.get(it["id"]), list) else [])[:12]:
                            if not isinstance(t, dict) or not re.fullmatch(r"[\w-]{1,48}", str(t.get("rule") or "")):
                                continue
                            x = {"cat": " ".join(str(t.get("cat") or "").split())[:30] or "Autres", "note": str(t.get("note") or "").strip()[:500], "rule": str(t["rule"])}
                            if (x["rule"], x["note"]) not in seen:
                                seen.add((x["rule"], x["note"])); w.append(x)
                        ts = clean_todos(it)
                        if [t for t in ts if t.get("rule")] == w:
                            continue
                        ts = ([t for t in ts if not t.get("rule")] + w)[:12]
                        it["todos"], it["todo"], it["todo_note"] = ts, bool(ts), ts[0]["note"] if ts else ""
                        changed += 1
                    if changed:
                        _save(DB_FILE, db)
                return self.send_json({"ok": True, "changed": changed})
            if p == "/api/free-todos":   # notes « À faire » libres : la liste entière est renvoyée à chaque changement
                raw = self.json_body().get("todos")
                out = []
                for t in (raw if isinstance(raw, list) else [])[:300]:
                    if not isinstance(t, dict) or not str(t.get("note") or "").strip():
                        continue
                    tid = str(t.get("id") or "")
                    out.append({"id": tid if re.fullmatch(r"[0-9a-f]{8,32}", tid) else uuid.uuid4().hex[:12],
                                "cat": " ".join(str(t.get("cat") or "").split())[:30] or "Autres",
                                "note": str(t.get("note")).strip()[:500], "at": t["at"] if isinstance(t.get("at"), int) else int(time.time())})
                with lock:
                    _save(NOTES_FILE, {"todos": out})
                return self.send_json({"ok": True, "todos": out})
            if p == "/api/settings/todo-cats":   # {cats} : la liste complète des catégories de tâches, dans l'ordre (« Autres » toujours gardée)
                raw = self.json_body().get("cats")
                cats = []
                for c in (raw if isinstance(raw, list) else [])[:40]:
                    c = " ".join(str(c or "").split())[:30]
                    if c and c not in cats:
                        cats.append(c)
                if TODO_OTHER not in cats:
                    cats.append(TODO_OTHER)
                _settings_update(todo_cat_list=cats)
                return self.send_json({"ok": True, "todo_cats": todo_cats(), "todo_icons": todo_icons()})
            if p == "/api/settings/social":   # {instagram} : compte affiché sur les pages publiques (champ libre ; vide : rien)
                u = str(self.json_body().get("instagram") or "").strip().lstrip("@")[:40]
                if u and not re.fullmatch(r"[\w.]{1,30}", u):
                    return self.error("Nom de compte Instagram invalide (lettres, chiffres, points et _)")
                _settings_update(social={"instagram": u})
                return self.send_json({"ok": True, "instagram": u})
            if p == "/api/settings/prices":   # {every_h, budget, consult_h} : actualisation des prix (bornés ; 24 h, 2 000, 24 h par défaut)
                b = self.json_body()
                cur = price_cfg()
                def val(v, d):
                    try:
                        return int(float(v))
                    except (TypeError, ValueError):
                        return d
                new = {k: val(b.get(k), cur[k]) for k in ("every_h", "budget", "consult_h")}
                _settings_update(prices=new)
                return self.send_json({"ok": True, "prices": price_cfg()})
            if p == "/api/settings/legal":   # {site} : mentions légales, paragraphe « Éditeur et hébergement » de ce site (texte libre)
                t = str(self.json_body().get("site") or "").replace("\r", "").strip()[:4000]
                _settings_update(legal_site=t)
                return self.send_json({"ok": True, "site": t})
            if p == "/api/settings/public-prices":   # {on} : prix affichés sur la collection publique (non par défaut)
                _settings_update(public_prices=bool(self.json_body().get("on")))
                return self.send_json({"ok": True})
            if p == "/api/settings/bl-zones":   # {zones: [{c} | {r} | {w}], min} : zones BrickLink dans l'ordre, et le minimum pour en retenir une
                b = self.json_body()
                zs = []
                for z in (b.get("zones") or [])[:8]:
                    if not isinstance(z, dict):
                        continue
                    if isinstance(z.get("c"), str) and re.fullmatch(r"[A-Za-z]{2}", z["c"]):
                        zs.append({"c": z["c"].upper()})
                    elif z.get("r") in sources.BL_REGIONS:
                        zs.append({"r": z["r"]})
                    elif z.get("w"):
                        zs.append({"w": 1})
                zs = [z for k, z in enumerate(zs) if z not in zs[:k]] or sources.BL_ZONES_DEFAULT   # (sans doublon)
                try:
                    mn = max(1, min(50, int(b.get("min") or sources.BL_MIN_SALES)))
                except (TypeError, ValueError):
                    mn = sources.BL_MIN_SALES
                _settings_update(bl_zones=zs, bl_min=mn)
                return self.send_json({"ok": True, **sources.bl_zone_cfg(), "order": sources.bl_zone_order()})
            if p == "/api/settings/sort-def":   # {sort} : tri par défaut de la collection, gardé sur le serveur (22/11)
                srt = str(self.json_body().get("sort") or "")[:30]
                if srt and not re.fullmatch(r"[a-z_]+", srt):
                    return self.error("Tri inconnu")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    st["sort_def"] = srt
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                return self.send_json({"ok": True, "sort_def": srt})
            if p == "/api/settings/side-pub":   # {path, show} : lien d'une page publique affiché ou masqué en bas du menu latéral
                b = self.json_body()
                path = str(b.get("path") or "")
                if path not in ("/collection", "/wishlist", "/nouveautes", "/a-surveiller", "/demo"):
                    return self.error("Page inconnue")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    hide = [x for x in (st.get("side_pub_hide") or []) if x != path] + ([] if b.get("show") else [path])
                    st["side_pub_hide"] = hide
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                return self.send_json({"ok": True, "side_pub_hide": hide})
            if p == "/api/settings/ui":   # {theme} : thème de l'application
                t = str(self.json_body().get("theme") or "")
                if t not in UI_THEMES:
                    return self.error("Thème inconnu")
                _settings_update(ui_theme=t)
                return self.send_json({"ok": True, "theme": t})
            if p == "/api/settings/help":   # {on} : bouton d'aide « ? » affiché (oui par défaut)
                _settings_update(help_on=bool(self.json_body().get("on")))
                return self.send_json({"ok": True})
            if p == "/api/todo-cats/manage":   # {op: "rename" | "delete", cat, to} : renommer / supprimer une catégorie (tâches suivies)
                b = self.json_body()
                clean = lambda v: " ".join(str(v or "").split())[:30]
                if b.get("op") == "icon":   # emoji choisi pour une catégorie ("" : icône d'origine)
                    cat, ic = clean(b.get("cat")), str(b.get("icon") or "").strip()[:16]
                    if ic and not re.fullmatch(r"[^\w<>&\"'\s]{1,16}", ic):
                        return self.error("Choisissez un emoji")
                    if cat not in todo_cats():
                        return self.error("Catégorie introuvable")
                    with lock:
                        st = _load(sources.SETTINGS_FILE, {})
                        icons = todo_icons()
                        icons[cat] = ic   # ("" : aucun emoji pour cette catégorie)
                        st["todo_icons"] = icons
                        _save(sources.SETTINGS_FILE, st)
                        os.chmod(sources.SETTINGS_FILE, 0o600)
                    return self.send_json({"ok": True, "moved": 0, "todo_cats": todo_cats(), "todo_icons": todo_icons()})
                try:
                    moved = todo_cat_change(str(b.get("op") or ""), clean(b.get("cat")), clean(b.get("to")))
                except ValueError as e:
                    return self.error(str(e))
                return self.send_json({"ok": True, "moved": moved, "todo_cats": todo_cats(), "todo_icons": todo_icons()})
            if p == "/api/settings/plan":   # décote d'un set sans ses plans, en %
                try:
                    v = max(0.0, min(90.0, float(self.json_body().get("pct"))))
                except (TypeError, ValueError):
                    return self.error("Pourcentage invalide")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    st["plan_bonus"] = v
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                _pc["t"] = 0
                return self.send_json({"ok": True, "plan_cut": v})
            if p == "/api/settings/box":   # plus-value d'un set avec sa boîte, en %
                try:
                    v = max(0.0, min(100.0, float(self.json_body().get("pct"))))
                except (TypeError, ValueError):
                    return self.error("Pourcentage invalide")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    st["box_bonus"] = v
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                _bb["t"] = 0
                return self.send_json({"ok": True, "box_bonus": v})
            if perso and p in perso.POST_PATHS:   # (extensions locales)
                return perso.handle_post(self, p)
            if p == "/api/settings/theme":   # thème de l'application {color} ; {reset: true} : tous les thèmes effacés (appli et listes)
                b = self.json_body()
                col = str(b.get("color") or "").strip().lower()
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    if not b.get("reset") and re.fullmatch(r"#[0-9a-f]{6}", col):
                        st["app_color"] = col
                    else:
                        st.pop("app_color", None)
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                    if b.get("reset"):
                        db = load_db()
                        for l in db["lists"]:
                            l.pop("color", None)
                        _save(DB_FILE, db)
                return self.send_json({"ok": True, "app_color": _load(sources.SETTINGS_FILE, {}).get("app_color") or ""})
            if p == "/api/settings/trend":   # seuils des flèches de variation, en % (Réglages → Estimations) ; le reste de leur apparence : back office
                b = self.json_body()
                try:
                    up, down = max(0.0, min(100.0, float(b.get("up", 3)))), max(0.0, min(100.0, float(b.get("down", 3))))
                except (TypeError, ValueError):
                    return self.error("Seuil invalide")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    st["trend"] = {**(st.get("trend") or {}), "up": up, "down": down,
                                   **({"period": int(b["period"])} if str(b.get("period") or "").isdigit() and int(b["period"]) in TREND_DAYS else {})}
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                return self.send_json({"ok": True, "trend": trend_cfg()})
            if p in ("/api/orders/extra/done", "/api/orders/extra/to-inventory"):   # « Commandées en plus » : traitée (OK, attribuée) / vers un inventaire (22/11)
                b = self.json_body()
                key = str(b.get("key") or "")[:300]
                with lock:
                    ext = _load(ORDERS_EXTRA, {"items": []})
                    e = next((x for x in ext.get("items") or [] if x.get("key") == key), None)
                    if not e:
                        return self.error("Ligne introuvable (déjà traitée ?)", 404)
                    if p.endswith("/to-inventory"):
                        db = load_db()
                        inv = (db.get("inventories") or {}).get(str(b.get("inv") or ""))
                        rk = str(b.get("row") or "")[:60]
                        if inv and not rk and b.get("add"):   # inventaire qui ne contient pas la pièce : une ligne AJOUTÉE (hors set) — 22/11
                            pn_, cid_ = str(e.get("part_num") or e.get("ref") or ""), e.get("color_id")
                            if not pn_ or cid_ is None:
                                return self.error("Référence ou couleur inconnue : impossible de l'ajouter")
                            rk = f"{pn_}|{cid_}"
                            cc_ = colors_fr().get(str(cid_)) or {}
                            snum_ = inv.get("set") or next((i["number"] for i in db["items"] if i["id"] == str(b.get("inv") or "")), "")
                            base_ = {r["key"] for r in (inventory_rows(snum_) if snum_ else [])}
                            ex_ = inv.setdefault("extra", [])
                            if rk not in base_ and not any(x.get("key") == rk for x in ex_):
                                ex_.append({"key": rk, "part_num": pn_, "name": e.get("name") or pn_, "color_id": cid_, "color_name": cc_.get("name") or "",
                                            "color_fr": cc_.get("fr") or e.get("color_fr") or "", "rgb": cc_.get("rgb") or e.get("rgb") or "", "trans": bool(cc_.get("trans")),
                                            "quantity": int(e.get("qty") or 1), "element_id": "", "image": e.get("image") or "", "part_image": e.get("image") or "",
                                            "bricklink": e.get("bl") or pn_})
                            elif rk not in base_:
                                for x in ex_:
                                    if x.get("key") == rk:
                                        x["quantity"] = int(x.get("quantity") or 0) + int(e.get("qty") or 1)
                        if not inv or not rk:
                            return self.error("Inventaire introuvable", 404)
                        st = inv.setdefault("rows", {}).get(rk) or {}
                        o = {"site": e["site"], "order": e["order"], "date": e["date"], "qty": e["qty"], **({"paid": e["paid"]} if e.get("paid") is not None else {})}
                        st.update(s="cmd", o=(st.get("o") or []) + [o], o_lock=True)
                        st.pop("m", None)
                        inv["rows"][rk] = st
                        inv["updated"] = int(time.time())
                        _save(DB_FILE, db)
                    done = _load(ORDERS_EXTRA_DONE, {})
                    done[key] = {"t": int(time.time()), "how": "inventaire" if p.endswith("/to-inventory") else str(b.get("how") or "ok")[:20]}
                    _save(ORDERS_EXTRA_DONE, done)
                    ext["items"] = [x for x in ext.get("items") or [] if x.get("key") != key]
                    _save(ORDERS_EXTRA, ext)
                return self.send_json({"ok": True})
            if p == "/api/orders/sync":   # « À commander » ouvert : mes commandes relues (au plus une fois par heure ; {force} : tout de suite)
                return self.send_json(orders_sync(bool(self.json_body().get("force"))))
            if p == "/api/settings/brickowl":   # clé de l'API BrickOwl — vérifiée sur la liste de mes commandes (acheteur), puis enregistrée (21/11 soir)
                key = str(self.json_body().get("key") or "").strip()
                if key:
                    try:
                        sources.bo_api("order/list", {"list_type": "customer", "limit": 1}, key=key)
                    except Exception as e:
                        return self.error(f"Clé BrickOwl refusée ou sans accès aux commandes : {e}")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    if key:
                        st["brickowl_key"] = key
                    else:
                        st.pop("brickowl_key", None)
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                return self.send_json({"ok": True, "brickowl": bool(key)})
            if p == "/api/settings/brickset":   # clé de l'API Brickset (dates de mise en vente / de retrait) — vérifiée, puis enregistrée (21/11 soir)
                key = str(self.json_body().get("key") or "").strip()
                if key:
                    try:
                        ok = sources.brickset_check(key)
                    except Exception as e:
                        return self.error(f"Brickset ne répond pas : {e}", 502)
                    if not ok:
                        return self.error("Clé Brickset refusée")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    if key:
                        st["brickset_key"] = key
                    else:
                        st.pop("brickset_key", None)
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                if key:
                    bg_once("brickset-now", lambda: brickset_fill(True), 60)
                return self.send_json({"ok": True, "brickset": bool(key)})
            if p == "/api/settings/ref-site":   # site de référence des prix : bricklink | brickowl | both (21/11)
                v = str(self.json_body().get("site") or "")
                if v not in ("bricklink", "brickowl"):   # (plan de secours : deux choix — 21/11 soir)
                    return self.error("Site inconnu")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    st["ref_site"] = v
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                _ref["t"] = 0
                markets_reapply()   # (cote des sets : tout de suite selon le nouveau réglage)
                if v != "bricklink" and not DEMO and not COPIE:   # (copies d'essai : pas de relevé de fond)
                    bo_fill_start()
                return self.send_json({"ok": True, "ref_site": v})
            if p == "/api/settings/discount":   # décote d'un exemplaire modifié, en %
                try:
                    v = max(0.0, min(90.0, float(self.json_body().get("pct"))))
                except (TypeError, ValueError):
                    return self.error("Pourcentage invalide")
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    st["mod_discount"] = v
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                _md["t"] = 0
                return self.send_json({"ok": True, "mod_discount": v})
            if p == "/api/settings/unban":
                auth.unban(str(self.json_body().get("ip") or ""))
                return self.send_json({"bans": auth.list_bans()})
            if p == "/api/lists/order":   # nouvel ordre des listes (identifiants dans l'ordre voulu)
                ids = [str(x) for x in (self.json_body().get("ids") or [])]
                with lock:
                    db = load_db()
                    rank = {lid: k for k, lid in enumerate(ids)}
                    db["lists"].sort(key=lambda l: rank.get(l["id"], len(ids)))   # tri stable
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            if p == "/api/lists":
                b = self.json_body()
                kind = b.get("kind") if b.get("kind") in ("wishlist", "parts") else "collection"
                name = str(b.get("name") or "").strip()[:80] or {"wishlist": "Liste de souhaits",
                                                         "parts": "À commander"}.get(kind, "Nouvelle liste")
                with lock:
                    db = load_db()
                    lst = {"id": uuid.uuid4().hex[:10], "name": name, "kind": kind, "created_at": int(time.time()),
                           **({"gift": True} if b.get("gift") and kind == "wishlist" else {})}   # « À offrir » : privée, comptée nulle part
                    try:
                        parent = self.check_parent(db, lst, str(b.get("parent_id") or ""))
                    except ValueError as e:
                        return self.error(str(e))
                    if parent:
                        lst["parent_id"] = parent
                    db["lists"].append(lst)
                    _save(DB_FILE, db)
                return self.send_json(lst, 201)
            if p == "/api/items/catalog-set":   # set connu de Rebrickable mais pas du catalogue des prix : ajouté, estimé par ses pièces
                b = self.json_body()
                num = str(b.get("number") or "").strip()[:30]
                if not re.fullmatch(r"[\w.]+-\d+", num):
                    return self.error("Numéro de set invalide")
                try:
                    d = sources.rb(f"lego/sets/{urllib.parse.quote(num)}/")
                    rows, url = [], f"lego/sets/{urllib.parse.quote(num)}/parts/?inc_minifig_parts=1&page_size=1000"
                    while url:
                        r = sources.rb(url)
                        rows += [x for x in r.get("results", []) if not x.get("is_spare")]
                        nxt = r.get("next")
                        url = nxt.split("/api/v3/", 1)[1] if nxt else None
                except PermissionError:
                    return self.error("Il faut une clé API Rebrickable (Réglages)")
                except Exception as e:
                    return self.error(f"Rebrickable ne répond pas : {e}", 502)
                bo = moc_color_maps()["rb"]
                agg = {}
                for x in rows:
                    pt, col = x["part"], x["color"]
                    bl = ((pt.get("external_ids") or {}).get("BrickLink") or [pt["part_num"]])[0]
                    c = bo.get(str(col["id"]))
                    if not c:
                        continue
                    k = (bl, c)
                    if k in agg:
                        agg[k]["qty"] += x["quantity"]
                    else:
                        el = x.get("element_id")
                        agg[k] = {"part": bl, "color": c, "qty": x["quantity"], "color_id": col["id"], "name": pt.get("name") or "",
                                  "color_fr": FR_COLORS.get(col.get("name") or "", col.get("name") or ""),
                                  "image": (f"https://cdn.rebrickable.com/media/parts/elements/{el}.jpg" if el else None) or pt.get("part_img_url") or ""}
                item = self.clean_item({"kind": "custom", "custom_type": "set", "catalog_set": True, "number": num,
                                        "custom_name": d.get("name") or num, "image": d.get("set_img_url") or "",
                                        "list_id": b.get("list_id"), "quantity": b.get("quantity") or 1, "condition": "occasion"})
                lots = list(agg.values())
                item.update(id=uuid.uuid4().hex[:12], added_at=int(time.time()), moc_parts=lots, moc_file=f"Inventaire Rebrickable {num}",
                            moc_price={"total": 0, "priced": 0, "missing": 0, "lots": len(lots), "done": False, "t": int(time.time())},
                            year=d.get("year"), pieces=d.get("num_parts"))
                with lock:
                    db = load_db()
                    if not any(l["id"] == item["list_id"] for l in db["lists"]):
                        return self.error("Liste inconnue")
                    db["items"].append(item)
                    _save(DB_FILE, db)
                moc_price_start(item["id"])
                return self.send_json(enrich(item), 201)
            if p == "/api/items":
                b = self.json_body()
                number = b.get("number") or b.get("part_num") or ("custom" if b.get("kind") == "custom" else None)
                if not number:
                    return self.error("Numéro de set manquant")
                b["number"] = number
                if b.get("kind") == "part":
                    if not b.get("part_num") or b.get("color_id") in (None, ""):
                        return self.error("Choisissez la pièce et sa couleur")
                elif b.get("kind") == "custom":
                    if not (b.get("custom_name") or "").strip():
                        return self.error("Donnez un nom à cet élément")
                elif b.get("kind") == "fig":
                    try:
                        get_fig(number)
                    except Exception:   # catalogue des cotes injoignable (BrickEconomy refuse) : le catalogue officiel de BrickLink, sinon une fiche provisoire
                        bl = bl_fig_info(number) or {}
                        if not bl:   # BrickLink muet aussi : le relevé BrickOwl (celui qui a servi à afficher la fiche) suffit — 20/11
                            try:
                                fig_used_fetch(number, max_age=6 * 3600)
                            except Exception:
                                pass
                            bo_rec = _fu_cache().get(number) or {}
                            if bo_rec.get("name") or bo_rec.get("unit") is not None:
                                bl = {"name": bo_rec.get("name") or ""}
                        # (aucun site ne répond : la figurine est ajoutée quand même, sans prix, sous son nom donné par l'appli ou son numéro)
                        placeholder_fig(number, str(b.get("name_hint") or bl.get("name") or "")[:150], str(b.get("image_hint") or bl.get("image") or ""))
                    try:
                        fig_used_many([number])   # prix d'occasion relevé tout de suite (site muet : relevé plus tard, l'ajout continue)
                    except Exception:
                        pass
                    bg_once("figimg-add", fig_img_job, every=120)   # (sa photo sur le serveur, tout de suite si celle du catalogue ne vient pas)
                    if RB_FIG.fullmatch(str(number)):
                        b["rb_fig"] = number   # ses pièces : celles de cette minifig Rebrickable
                else:
                    number = b["number"] = norm_set(str(number)) or number   # (« 40003 » → « 40003-1 » : même fiche qu'en ligne, pas de doublon)
                    import concurrent.futures as _cf   # (la fiche d'abord : 2,5 s au plus pour les prix, le reste en coulisse — 22/11)
                    _ex = _cf.ThreadPoolExecutor(1)
                    _fu = _ex.submit(get_set, number)   # met en cache les infos et prix
                    _ex.shutdown(wait=False)
                    try:
                        _fu.result(timeout=2.5)
                    except _cf.TimeoutError:   # prix encore en cours : fiche provisoire tout de suite, le relevé continue en coulisse
                        placeholder_set(number, str(b.get("name_hint") or "")[:150], image=str(b.get("image_hint") or ""), soon=str(b.get("release_hint") or "")[:80])
                    except Exception:   # aucun site de prix ne répond : ajouté quand même, sans cote (relue plus tard)
                        placeholder_set(number, str(b.get("name_hint") or "")[:150], image=str(b.get("image_hint") or ""), soon=str(b.get("release_hint") or "")[:80])
                        b["_parts_estimate"] = True
                    try:
                        fig_used_fill()  # prix d'occasion de ses minifigs, en arrière-plan
                    except Exception:
                        pass
                item = self.clean_item(b)
                item["id"] = uuid.uuid4().hex[:12]
                item["added_at"] = int(time.time())
                with lock:
                    db = load_db()
                    if not any(l["id"] == item["list_id"] for l in db["lists"]):
                        return self.error("Liste inconnue")
                    db["items"].append(item)
                    if b.get("_join"):   # figurine sortie d'un set : rejoint la fiche seule identique s'il y en a une (pas de fiche en double)
                        item = fig_absorb(db, item)
                    if b.get("no_scan") and item.get("kind") == "custom" and item.get("custom_type") == "fig":   # pièces données à la création : pas de scan, pas dans « MOC à valider »
                        item["moc_reviewed"] = True
                    if item.get("kind", "set") == "set" and list_kinds(db).get(item["list_id"]) == "collection" \
                            and (_load(CACHE_FILE, {}).get(item["number"]) or {}).get("minifigs"):   # ses figurines : des fiches à part entière
                        item["fig_items"] = True
                        orig_figs_sync(db, item)
                    _save(DB_FILE, db)
                tok = _tmp_scans.pop(str(b.get("scan_token") or ""), None)
                if item.get("moc_reviewed"):
                    pass   # (pièces données à la création : ni scan, ni « MOC à valider »)
                elif tok and item.get("kind") == "custom" and item.get("custom_type") == "fig":   # photo déjà scannée avant l'enregistrement
                    with lock:
                        raw = _load(REVIEW_FILE, {})
                        raw[item["id"]] = {"zones": tok[1], "t": int(time.time()), "extras": 0, "image": item.get("image"), "mode": "assembled"}
                        _save(REVIEW_FILE, raw)
                    _set_scan_status(item["id"], "done")
                elif item.get("kind") == "custom" and item.get("custom_type") == "fig" and item.get("image"):
                    moc_scan_start(item["id"])   # scan des pièces en tâche de fond
                try:
                    item_parts_refresh(item["id"])   # ses pièces : inventaire, noms et prix tout de suite (site muet : plus tard, la fiche est déjà enregistrée)
                except Exception as e:
                    print("Pièces de la nouvelle fiche : plus tard,", e, flush=True)
                if not item.get("no_parts_est") and (b.get("_parts_estimate") or (_load(CACHE_FILE, {}).get(cache_key(item)) or {}).get("pending_prices")):   # sans cote : estimation par ses pièces (case cochée)
                    threading.Thread(target=parts_estimate_start, args=(item["id"],), daemon=True).start()
                return self.send_json(enrich(item), 201)
            m = re.fullmatch(r"/api/items/(\w+)/parts-estimate", p)
            if m:   # set sans cote : « Estimer par les pièces » (aussi lancé d'office, et repris par le gardien horaire)
                if not parts_estimate_start(m.group(1)):
                    return self.error("Inventaire indisponible pour le moment (Rebrickable) : l'estimation se fera automatiquement dès que possible", 502)
                it = next((x for x in load_db()["items"] if x["id"] == m.group(1)), {})
                return self.send_json({"ok": True, "lots": len(it.get("moc_parts") or [])})
            if p == "/api/parts/bl-xml":   # {"list_id", "full"} : « À commander » → XML de wanted list BrickLink (ce qui n'est pas encore exporté)
                b = self.json_body()
                lid, full = str(b.get("list_id") or "")[:40], bool(b.get("full"))
                db = load_db()
                if list_kinds(db).get(lid) != "parts":
                    return self.error("Liste introuvable", 404)
                its = [i for i in db["items"] if i.get("kind") in ("part", "fig") and i.get("list_id") == lid
                       and not i.get("got") and not i.get("ordered") and not i.get("cmd_m")]   # (pièces et figurines À COMMANDER : ni commandées ni reçues — 22/11)
                if not its:
                    return self.error("Aucune pièce dans cette liste")
                try:
                    xml, rows, skipped = bl_wanted_xml(its, full)
                except Exception as e:
                    return self.error(f"Couleurs BrickLink indisponibles pour le moment : {e}", 502)
                sent = [i for i in its if int(i.get("bl_qty") or 0)]
                return self.send_json({"xml": xml if rows else "", "refs": len(rows), "pieces": sum(r["qty"] for r in rows),
                                       "ids": [x for r in rows for x in r["ids"]], "skipped": skipped,
                                       "already": {"refs": len(sent), "pieces": sum(min(int(i["bl_qty"]), int(i.get("quantity") or 1)) for i in sent)}})
            if p == "/api/parts/clean":   # {"list_id"} : pièces ✔ OK (reçues) retirées ; inventaires validés ; note « Commande · Pièces reçues » sur leurs fiches
                lid = str(self.json_body().get("list_id") or "")[:40]
                with lock:
                    db = load_db()
                    kinds = list_kinds(db)
                    if kinds.get(lid) != "parts":
                        return self.error("Liste introuvable", 404)
                    got = [i for i in db["items"] if i.get("kind") in ("part", "fig") and i.get("list_id") == lid and i.get("got")]   # (figurines comprises)
                    ids = {i["id"]: i for i in db["items"]}
                    invs, notes = set(), {}
                    for it in got:
                        for ln in it.get("inv_links") or []:
                            inv_row_status(db, ln["inv"], ln["row"], "ok")
                            invs.add(ln["inv"])
                        col = FR_COLORS.get(it.get("color_name") or "", it.get("color_name") or "")
                        label = f"{it.get('part_name') or it.get('part_num')} ({col}) ×{it.get('quantity', 1)}"
                        hosts = {ln["inv"] for ln in it.get("inv_links") or [] if ln["inv"] in ids and ids[ln["inv"]].get("kind") != "part"}
                        sn = it.get("set_number")
                        if sn:   # set de ma collection pour lequel elle était commandée
                            hosts |= {i["id"] for i in db["items"] if i.get("number") == sn and i.get("kind", "set") != "part" and kinds.get(i.get("list_id")) == "collection"}
                        for h in hosts:
                            notes.setdefault(h, []).append(label)
                    gone = {i["id"] for i in got}
                    db["items"] = [i for i in db["items"] if i["id"] not in gone]
                    for hid, labels in notes.items():
                        h = ids[hid]
                        h["todos"] = (clean_todos(h) + [{"cat": "Commande", "note": ("Pièces reçues : " + ", ".join(labels))[:500]}])[-12:]
                    _save(DB_FILE, db)
                if notes and "Commande" not in todo_cats():   # le libellé « Commande » des tâches (hors du verrou : _settings_update le prend)
                    _settings_update(todo_cat_list=todo_cats() + ["Commande"])
                return self.send_json({"n": len(got), "invs": sorted(invs), "notes": len(notes)})
            if p == "/api/parts/bl-sent":   # {"ids"} : pièces exportées vers la wanted list BrickLink : quantité exportée + date
                ids = {str(x) for x in (self.json_body().get("ids") or [])[:2000]}
                now = int(time.time())
                with lock:
                    db = load_db()
                    n = 0
                    for it in db["items"]:
                        if it["id"] in ids and it.get("kind") in ("part", "fig"):
                            it["bl_qty"] = max(1, int(it.get("quantity") or 1))   # tout ce qu'il faut est maintenant dans la wanted list
                            it["bl_wanted"] = now
                            n += 1
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "n": n})
            m = re.fullmatch(r"/api/items/(\w+)/fig-extra", p)
            if m:   # {"fig", "accessories", "alt_photos", "alt_names", "main_name"} : accessoires et apparences d'une figurine d'un set
                b = self.json_body()
                fid = str(b.get("fig") or "")[:30]
                acc = [acc_clean(a) for a in (b.get("accessories") if isinstance(b.get("accessories"), list) else [])[:40] if isinstance(a, dict)]   # (liste de pièces comprise)
                alts = Handler.clean_alts(b)
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not it or it.get("kind", "set") != "set" or not fid:
                        return self.error("Introuvable", 404)
                    mods = it.setdefault("fig_mods", {})
                    fm = mods.setdefault(fid, {})
                    for k in ("accessories", "alt_photos", "alt_names", "alt_hidden", "main_name"):
                        fm.pop(k, None)
                    if acc:
                        fm["accessories"] = acc
                    fm.update(alts)
                    it["fig_mods"] = {k: v for k, v in mods.items() if v}
                    if not it["fig_mods"]:
                        it.pop("fig_mods")
                    touch_for_fig(it, fid)   # seule la figurine remonte dans « Dernière modification »
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/fig-name", p)
            if m:   # {"fig": id de la figurine (d'un set, sans fiche à elle), "name": nom choisi ("" = nom d'origine)}
                b = self.json_body()
                fid, name = str(b.get("fig") or "")[:30], str(b.get("name") or "").strip()[:150]
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not it or it.get("kind", "set") != "set" or not fid:
                        return self.error("Introuvable", 404)
                    mods = it.setdefault("fig_mods", {})
                    fm = mods.setdefault(fid, {})
                    if name:
                        fm["name"] = name
                    else:
                        fm.pop("name", None)
                    it["fig_mods"] = {k: v for k, v in mods.items() if v}
                    if not it["fig_mods"]:
                        it.pop("fig_mods")
                    touch_for_fig(it, fid)   # seule la figurine remonte dans « Dernière modification »
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/fig-photo", p)
            if m:   # {"fig": id de la figurine (minifig d'un set), "photo_url": photo ("" = celle du catalogue)}
                b = self.json_body()
                u = str(b.get("photo_url") or "")[:400]
                if u and not (re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", u) or re.match(
                        r"https://(www\.brickeconomy\.com|cdn\.rebrickable\.com|storage\.googleapis\.com/brickognize-static)/", u)):
                    return self.error("Photo non acceptée")
                fid = str(b.get("fig") or "")[:30]
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not it:
                        return self.error("Introuvable", 404)
                    if it.get("kind") == "fig" or it.get("kind") == "custom":
                        it["photo_url"] = u
                    else:
                        mods = it.setdefault("fig_mods", {})
                        fm = mods.setdefault(fid, {})
                        if u:
                            fm["photo_url"] = u
                        else:
                            fm.pop("photo_url", None)
                        it["fig_mods"] = {k: v for k, v in mods.items() if v}
                        if not it["fig_mods"]:
                            it.pop("fig_mods")
                    if it.get("kind") == "fig" or it.get("kind") == "custom":
                        it["updated_at"] = int(time.time())
                    else:
                        touch_for_fig(it, fid)   # figurine d'un set : seule elle remonte
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/fig-swaps", p)
            if m:   # {"rb_fig": "fig-000123"} et/ou {"swaps": [{"k", "orig": {part, color_id, qty, name, image}, "new": {...}}]}
                b = self.json_body()
                try:
                    rbc = moc_color_maps()["rb"]
                except Exception:
                    return self.error("Il faut une clé API Rebrickable (Réglages)")

                def lot(x):
                    im = str(x.get("image") or "")
                    try:
                        q = max(1, min(9999, int(x.get("qty") or 1)))   # (nombre pour le lot entier de figurines)
                        per = max(1, min(99, int(x.get("per") or 1)))   # pièces par figurine (pièce d'origine)
                    except (TypeError, ValueError):
                        q, per = 1, 1
                    col = rbc.get(str(x.get("color_id")))
                    if not col or not str(x.get("part") or "").strip():
                        raise ValueError
                    return {"part": str(x["part"]).strip()[:40], "part_num": str(x.get("part_num") or "")[:40], "color": col,
                            "color_id": int(x["color_id"]), "color_fr": str(x.get("color_fr") or "")[:60], "qty": q, **({"per": per} if per > 1 else {}),
                            "name": str(x.get("name") or "")[:150], "image": im if im.startswith("https://cdn.rebrickable.com/") else ""}
                swaps = None
                if isinstance(b.get("swaps"), list):
                    try:
                        swaps = [{"k": int(x["k"]), "orig": lot(x["orig"]) if x.get("orig") else None,   # orig None : pièce ajoutée
                                  "new": lot(x["new"]) if x.get("new") else None,   # new None : pièce retirée
                                  **({"fix": True} if x.get("fix") and x.get("orig") and x.get("new") else {})}   # (pièce d'origine corrigée)
                                 for x in b["swaps"][:300]]
                    except (ValueError, KeyError, TypeError):
                        return self.error("Pièce ou couleur invalide")
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    fid = str(b.get("fig") or "")[:30]
                    if fid:   # figurine d'un set, ou « #set » : pièces du set lui-même
                        if not it or it.get("kind", "set") != "set":
                            return self.error("Set introuvable", 404)
                        it = it.setdefault("set_mod", {}) if fid == "#set" else it.setdefault("fig_mods", {}).setdefault(fid, {})
                    elif not it or it.get("kind") != "fig":
                        return self.error("Figurine introuvable", 404)
                    if b.get("rb_fig") is not None:
                        rbf = str(b["rb_fig"])
                        if rbf != it.get("rb_fig"):   # autre minifig de référence : les remplacements ne valent plus
                            it.pop("fig_swaps", None); it.pop("swap_price", None)
                        if re.fullmatch(r"fig-\d{6}", rbf):
                            it["rb_fig"] = rbf
                        else:
                            it.pop("rb_fig", None)
                    _own = next((i for i in db["items"] if i["id"] == m.group(1)), {})
                    if fid and fid != "#set":
                        touch_for_fig(_own, fid)   # figurine d'un set : seule elle remonte
                    else:
                        _own["updated_at"] = int(time.time())
                    if swaps is not None and not fid and it.get("kind") == "fig":   # accessoire d'une minifig à collectionner
                        accs = {(a["part_num"], a["color_id"]) for a in cmf_accessories(it)}
                        for x in swaps:
                            if x.get("orig") and (x["orig"].get("part_num"), x["orig"].get("color_id")) in accs:
                                x["acc"] = True
                    prev_sw = json.loads(json.dumps(it.get("fig_swaps") or []))   # (avant le changement : seuls les exemplaires identiques suivront)
                    if swaps is not None:
                        if fid == "#set":   # minifig à collectionner : socle retiré sans décote
                            sinfo = _load(CACHE_FILE, {}).get(cache_key(next(i for i in db["items"] if i["id"] == m.group(1)))) or {}
                            for x in swaps:
                                if cmf_stand_removed(sinfo, x):
                                    x["free"] = True
                        if swaps:
                            it["fig_swaps"] = swaps
                            it["swap_price"] = {"delta": 0, "done": False}
                        else:
                            it.pop("fig_swaps", None); it.pop("swap_price", None)
                    shared = []
                    if swaps is not None and fid != "#set" and not b.get("_solo"):   # modifications partagées : tous ses autres exemplaires suivent
                        shared = fig_share_swaps(db, m.group(1), fid, swaps, it.get("rb_fig"), prev_sw)
                    if fid:
                        set_it = next(i for i in db["items"] if i["id"] == m.group(1))
                        set_it["fig_mods"] = {k: v for k, v in (set_it.get("fig_mods") or {}).items() if v}   # figurine sans rien : on l'oublie
                        if not set_it["fig_mods"]:
                            set_it.pop("fig_mods")
                        if not set_it.get("set_mod"):
                            set_it.pop("set_mod", None)
                    _save(DB_FILE, db)
                if swaps:
                    moc_price_start(m.group(1), front=True)
                for tid in shared:   # (exemplaires qui ont suivi : rechiffrés en fond)
                    moc_price_start(tid)
                return self.send_json({"ok": True, "shared": len(shared)})
            m = re.fullmatch(r"/api/items/(\w+)/moc-reviewed", p)
            if m:   # validation d'une minifig MOC sans aucune pièce retenue
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not it or it.get("kind") != "custom":
                        return self.error("MOC introuvable", 404)
                    it["moc_reviewed"] = True
                    it["moc_scan"] = "validated"
                    scan_todo(it, SCAN_TODO_CHECK, False)   # validé : plus de tâche « à valider »
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)/moc-parts", p)
            if m:   # {"text": contenu du fichier, "name": nom} ou {"remove": true} pour retirer la liste
                b = self.json_body()
                text = str(b.get("text") or "")
                if len(text) > 5_000_000:
                    return self.error("Fichier trop gros")
                lots, skipped = [], 0
                merge = bool(b.get("merge"))   # scan d'un set : les pièces validées s'ajoutent à sa liste
                mode = b.get("mode") if b.get("mode") in ("sum", "keep") else ""   # XML ajouté aux pièces : doublons additionnés ou laissés tels quels
                if isinstance(b.get("lots"), list):   # pièces ajoutées une à une (photo) : couleur = n° Rebrickable
                    try:
                        rbc = moc_color_maps()["rb"]
                    except Exception:
                        return self.error("Il faut une clé API Rebrickable (Réglages) pour les couleurs")
                    for x in b["lots"][:3000]:
                        part, col = str(x.get("part") or "").strip()[:40], rbc.get(str(x.get("color_id")))
                        if not part or not col:
                            continue
                        try:
                            qty = max(1, min(999, int(x.get("qty") or 1)))
                        except (TypeError, ValueError):
                            qty = 1
                        im = str(x.get("image") or "")
                        lots.append({"part": part, "color": col, "qty": qty, "color_id": int(x["color_id"]),
                                     "name": str(x.get("name") or "")[:150], "color_fr": str(x.get("color_fr") or "")[:60],
                                     "image": im if im.startswith(("https://cdn.rebrickable.com/", "https://storage.googleapis.com/brickognize-static/")) else ""})
                    b["remove"] = not lots
                    b["name"] = "Pièces ajoutées une à une"
                elif not b.get("remove") and not text.strip():
                    return self.error("Le fichier est vide")
                if not b.get("remove") and not lots:
                    try:
                        lots, skipped = parse_moc_parts(text)
                    except PermissionError:
                        return self.error("Il faut une clé API Rebrickable (Réglages) pour lire les couleurs")
                    except Exception as e:
                        return self.error(f"Fichier illisible : {e}")
                with lock:
                    db = load_db()
                    it = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                    if not it or it.get("kind") != "custom":
                        return self.error("MOC introuvable", 404)
                    if (merge or mode) and lots:
                        old = {(x["part"], x["color"]): x for x in it.get("moc_parts") or []}
                        for x in lots:
                            if (x["part"], x["color"]) in old:
                                if mode != "keep":
                                    old[(x["part"], x["color"])]["qty"] += x["qty"]
                            else:
                                old[(x["part"], x["color"])] = x
                        lots = list(old.values())
                        b["name"] = it.get("moc_file") or ("XML collé" if mode else "Pièces scannées")
                    for k in ("moc_parts", "moc_price", "moc_file"):
                        it.pop(k, None)
                    if b.get("from_scan"):
                        it["moc_scan"] = "validated"
                        scan_todo(it, SCAN_TODO_CHECK, False)
                    if lots:
                        it["moc_parts"] = lots
                        it["moc_file"] = str(b.get("name") or "")[:120]
                        it["moc_price"] = {"total": 0, "priced": 0, "missing": 0, "lots": len(lots), "done": False, "t": int(time.time())}
                    _save(DB_FILE, db)
                item_parts_refresh(m.group(1))
                if merge and b.get("from_scan"):   # scan validé : ses propositions sont oubliées (pas pour une pièce ajoutée depuis la recherche)
                    with lock:
                        raw = _load(REVIEW_FILE, {}); raw.pop(m.group(1), None); _save(REVIEW_FILE, raw)
                if lots:
                    moc_price_start(m.group(1), front=len(lots) <= 20)
                return self.send_json({"ok": True, "lots": len(lots), "pieces": sum(x["qty"] for x in lots), "skipped": skipped})
            if p == "/api/acc-parts":   # {"text", "name"} : liste de pièces d'un accessoire (XML / CSV) → pièces lues + prix déjà connus
                b = self.json_body()
                text = str(b.get("text") or "")
                if not text.strip():
                    return self.error("La liste est vide")
                if len(text) > 2_000_000:
                    return self.error("Fichier trop gros")
                try:
                    lots, skipped = parse_moc_parts(text)
                except PermissionError:
                    return self.error("Il faut une clé API Rebrickable (Réglages) pour lire les couleurs")
                except Exception as e:
                    return self.error(f"Liste illisible : {e}")
                a = acc_clean({"name": "x", "parts": lots, "file": str(b.get("name") or "Liste de pièces")})
                return self.send_json({"parts": a.get("parts") or [], "file": a.get("file") or "", "skipped": skipped, "price": acc_price(a)})
            if p == "/api/items/parts":   # plusieurs pièces d'un coup dans une liste à commander (fusion des doublons)
                b = self.json_body()
                with lock:
                    db = load_db()
                    lst = next((l for l in db["lists"] if l["id"] == b.get("list_id")), None)
                    if not lst or lst.get("kind") != "parts":
                        return self.error("Choisissez une liste de pièces")
                    added = merged = 0
                    for x in (b.get("parts") or [])[:3000]:
                        if not x.get("part_num") or x.get("color_id") in (None, ""):
                            continue
                        if not x.get("color_name") or not x.get("color_rgb"):   # (nom et teinte de la couleur, d'après son n° — 22/11)
                            cc_ = colors_fr().get(str(x.get("color_id"))) or {}
                            x = {**x, "color_name": x.get("color_name") or cc_.get("name") or "", "color_rgb": x.get("color_rgb") or cc_.get("rgb") or ""}
                        try:
                            q = max(1, min(9999, int(x.get("quantity") or 1)))
                        except (TypeError, ValueError):
                            q = 1
                        same = next((i for i in db["items"] if i["list_id"] == lst["id"] and i.get("kind") == "part" and not i.get("bl_qty")   # exportée : on n'y touche plus
                                     and not i.get("got") and not i.get("ordered") and not i.get("cmd_m")   # (commandée ou reçue : une nouvelle ligne — 22/11)
                                     and i.get("part_num") == x["part_num"] and str(i.get("color_id")) == str(x["color_id"])), None)
                        if same:
                            same["quantity"] = min(9999, same.get("quantity", 1) + q)
                            merged += 1
                            continue
                        it = self.clean_item({**x, **part_img_fix(x), "kind": "part", "number": x["part_num"], "list_id": lst["id"], "quantity": q,
                                              "set_number": b.get("set_number") or x.get("set_number") or ""})
                        it["id"] = uuid.uuid4().hex[:12]
                        it["added_at"] = int(time.time())
                        db["items"].append(it)
                        added += 1
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "added": added, "merged": merged})
            if p == "/api/items/move":
                b = self.json_body()
                ids, target, copy = set(b.get("ids") or []), b.get("list_id"), bool(b.get("copy"))
                quiet_fig = str(b.get("fig") or "")[:40] or None   # déplacement demandé depuis une figurine de set : seule elle remonte
                with lock:
                    db = load_db()
                    if not any(l["id"] == target for l in db["lists"]):
                        return self.error("Liste inconnue")
                    if not copy:   # déplacement : les fiches reliées suivent (set ↔ ce qui y est rangé)
                        _lk = list_kinds(db)
                        if _lk.get(target) == "collection":   # (souhait acquis : directement « À construire » — 22/11)
                            for _w in db["items"]:
                                if _w["id"] in ids and _w.get("kind", "set") == "set" and _lk.get(_w.get("list_id")) == "wishlist":
                                    _w["unbuilt"] = True
                        n = move_linked(db, ids, target, quiet_fig)
                        for _h in [i for i in db["items"] if i["id"] in ids and i.get("kind", "set") == "set"]:   # set changé de liste : collection → les fiches de ses figurines ; liste de souhaits → aucune
                            set_figs_sheets(db, _h)
                        _save(DB_FILE, db)
                        return self.send_json({"ok": True, "nb": n, "linked": max(0, n - len(ids))})
                    n = 0
                    for it in list(db["items"]):
                        if it["id"] not in ids:
                            continue
                        n += 1
                        if copy:
                            if it.get("set_orig"):   # (une figurine d'origine se copie seule, sans son set : fiche indépendante)
                                cp = {**it, "id": uuid.uuid4().hex[:12], "list_id": target, "added_at": int(time.time()), "updated_at": int(time.time())}
                                cp.pop("set_orig", None); cp.pop("attached_to", None)
                                db["items"].append(cp)
                                continue
                            cp = {**it, "id": uuid.uuid4().hex[:12],   # copie = un ajout : remonte dans « Dernière modification »
                                  "list_id": target, "added_at": int(time.time()), "updated_at": int(time.time())}
                            db["items"].append(cp)
                            set_figs_sheets(db, cp)   # un set copié : ses propres fiches de figurines (dans la collection seulement)
                        else:
                            it["list_id"] = target
                            it["updated_at"] = int(time.time())
                    _save(DB_FILE, db)
                return self.send_json({"ok": True, "nb": n})
            if p == "/api/items/delete":
                ids = set(self.json_body().get("ids") or [])
                backup_db("avant-suppression")
                with lock:
                    db = load_db()
                    items_removed(db, ids)
                    _save(DB_FILE, db)
                return self.send_json({"ok": True})
            if p == "/api/settings":
                b = self.json_body()
                key = (b.get("rebrickable_key") or "").strip()
                settings = _load(sources.SETTINGS_FILE, {})
                if not key:
                    settings.pop("rebrickable_key", None)
                else:
                    if not re.fullmatch(r"[A-Za-z0-9]{20,64}", key):
                        return self.error("Cette clé n'a pas le format d'une clé API Rebrickable")
                    try:
                        sources.rebrickable("lego/colors/?page_size=1", key=key)
                    except Exception as e:
                        code = getattr(e, "code", None)
                        return self.error("Clé refusée par Rebrickable" if code in (401, 403)
                                          else f"Rebrickable injoignable : {e}")
                    settings["rebrickable_key"] = key
                with lock:
                    _save(sources.SETTINGS_FILE, settings)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                return self.send_json({"ok": True, "rebrickable": bool(key)})
            if p == "/api/settings/owner":   # {name} : nom affiché sur les pages publiques
                if DEMO:
                    return self.error("Désactivé dans la démo", 403)
                name = re.sub(r"\s+", " ", str(self.json_body().get("name") or "")).strip()[:60]
                with lock:
                    st = _load(sources.SETTINGS_FILE, {})
                    st["owner_name"] = name
                    _save(sources.SETTINGS_FILE, st)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                return self.send_json({"ok": True, "owner_name": name})
            if p == "/api/consult":   # {id} | {set} | {fig} : fiche ouverte → ses prix BrickLink relus s'ils ont plus de 24 h
                b = self.json_body()
                it = next((i for i in load_db()["items"] if i["id"] == str(b.get("id") or "")), None) if b.get("id") else None
                sn, fn = str(b.get("set") or "")[:30], str(b.get("fig") or "")[:30]
                changed = consult_prices(it, sn or None, fn or None)
                out = {"changed": changed}
                if changed and not it and sn:   # set du catalogue (pas dans mes listes) : ses nouveaux prix
                    c = _load(CACHE_FILE, {}).get(sn) or {}
                    out["prices"] = {k: c.get(k) for k in ("used_value", "new_value", "market", "used_guess")}
                return self.send_json(out)
            if p == "/api/refresh":   # actualisation des prix en arrière-plan (au chargement de la page ou à la demande)
                b = self.json_body()
                return self.send_json(refresh_start(force=bool(b.get("force"))))
            if p == "/api/settings/bricklink":   # {consumer_key, consumer_secret, token, token_secret} vérifiés auprès de BrickLink ; {} : retirés
                if DEMO:
                    return self.error("Pas de BrickLink dans la démo", 403)
                b = self.json_body()
                keys = {k: re.sub(r"\s", "", str(b.get(k) or "")) for k in sources.BL_KEYS}
                settings = _load(sources.SETTINGS_FILE, {})
                if not any(keys.values()):
                    settings.pop("bricklink", None)
                else:
                    if not all(re.fullmatch(r"[A-Za-z0-9]{16,64}", v) for v in keys.values()):
                        return self.error("Il faut les 4 codes BrickLink (lettres et chiffres)")
                    swapped = {**keys, "consumer_secret": keys["token_secret"], "token_secret": keys["consumer_secret"]}
                    tries = [({**keys, "mode": "header"}, ""), ({**keys, "mode": "query"}, ""),
                             ({**swapped, "mode": "header"}, "ConsumerSecret et TokenSecret étaient inversés : corrigé"), ({**swapped, "mode": "query"}, "ConsumerSecret et TokenSecret étaient inversés : corrigé")]
                    good, note, msgs = None, "", []
                    for cand, why in tries:
                        try:
                            sources.bl_get("/items/SET/10497-1/price", {"guide_type": "stock", "new_or_used": "N", "currency_code": "EUR"}, keys=cand)
                            good, note = cand, why
                            break
                        except Exception as e:
                            msg = str(getattr(e, "reason", "") or e)
                            if hasattr(e, "read"):
                                try:
                                    msg = json.loads(e.read().decode()).get("meta", {}).get("description") or msg
                                except Exception:
                                    pass
                            msgs.append(msg)
                            if "SIGNATURE" not in msg.upper():   # autre refus (code inconnu, adresse IP…) : inutile d'essayer les variantes
                                break
                    if not good:
                        last = msgs[-1] if msgs else ""
                        ip = _load(sources.SETTINGS_FILE, {}).get("public_ip") or "l'adresse IP publique de ce serveur"
                        hint = (f" — vérifiez que l'adresse IP du jeton est bien {ip}" if "IP" in last.upper() else
                                " — recopiez les deux codes secrets (ConsumerSecret, TokenSecret) : l'un d'eux est incomplet ou appartient à un autre jeton" if "SIGNATURE" in last.upper() else "")
                        return self.error("BrickLink refuse ces codes : " + last[:200] + hint)
                    keys = good
                    settings["bricklink"] = keys
                with lock:
                    _save(sources.SETTINGS_FILE, settings)
                    os.chmod(sources.SETTINGS_FILE, 0o600)
                return self.send_json({"ok": True, "bricklink": bl_on(), "note": locals().get("note") or ""})
            return self.error("Introuvable", 404)
        except Exception as e:
            return self.error(f"Erreur : {e}", 502)

    def do_PUT(self):
        prio_seen(urlparse(self.path).path)   # (priorité à l'écran — 22/11)
        if self.demo_route() or self.guard():
            return
        p = urlparse(self.path).path
        b = self.json_body()
        mt = re.fullmatch(r"/api/items/(\w+)", p)
        tok = _tmp_scans.pop(str(b.get("scan_token") or ""), None) if mt else None
        if tok:   # figurine MOC enregistrée : sa nouvelle photo, déjà scannée, remplace le scan précédent (à valider)
            with lock:
                raw = _load(REVIEW_FILE, {})
                raw[mt.group(1)] = {"zones": tok[1], "t": int(time.time()), "extras": 0, "mode": "assembled"}
                _save(REVIEW_FILE, raw)
                db0 = load_db()
                it0 = next((i for i in db0["items"] if i["id"] == mt.group(1)), None)
                if it0:
                    it0.pop("moc_reviewed", None)
                    _save(DB_FILE, db0)
            _set_scan_status(mt.group(1), "done")

        with lock:
            db = load_db()
            m = re.fullmatch(r"/api/lists/(\w+)", p)
            if m:
                for l in db["lists"]:
                    if l["id"] == m.group(1):
                        l["name"] = str(b.get("name") or l["name"]).strip()[:80] or l["name"]
                        if "logo" in b:   # logo de la liste (photo importée, PNG transparent gardé) ; "" : retiré
                            u = str(b.get("logo") or "")
                            if re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", u):
                                l["logo"] = u   # (logo et émoji peuvent coexister : « show » dit lesquels s'affichent)
                            elif not u:
                                l.pop("logo", None)
                        if "emoji" in b:   # emoji choisi à la place d'une image (court, sans lettre ni chiffre) ; "" : retiré
                            e = str(b.get("emoji") or "").strip()[:16]
                            if e == "-":   # aucun émoji, même pas celui « au hasard »
                                l.pop("emoji", None); l["emoji_off"] = True
                            elif e and re.fullmatch(r"[^\w<>&\"'\s]{1,16}", e):
                                l["emoji"] = e; l.pop("emoji_off", None)
                            elif not e:
                                l.pop("emoji", None)
                        if "color" in b:   # couleur du thème de la liste (#rrggbb ; vide : le rouge de l'appli)
                            col = str(b.get("color") or "").strip().lower()
                            if re.fullmatch(r"#[0-9a-f]{6}", col):
                                l["color"] = col
                            else:
                                l.pop("color", None)
                        if "in_menu" in b:   # sous-liste affichée aussi dans le menu latéral (une liste principale y est toujours)
                            if b.get("in_menu") and l.get("parent_id"):
                                l["in_menu"] = True
                            else:
                                l.pop("in_menu", None)
                        l.pop("hide_menu", None)   # (ancienne option, retirée : une liste principale est toujours affichée)
                        if "sub_logo" in b:   # liste principale : sur les vignettes, son logo (« self ») pour toutes ses sous-listes, au lieu du leur
                            if b.get("sub_logo") == "self":   # (toute liste qui a des sous-listes, enfant elle-même ou non)
                                l["sub_logo"] = "self"
                            else:
                                l.pop("sub_logo", None)
                        l.pop("card_logo", None)   # (ancienne option des sous-listes : retirée)
                        if "card_logo" in b:   # (ancien : plus envoyé)
                            if b.get("card_logo") == "parent" and l.get("parent_id"):   # (d'office : son propre logo)
                                l["card_logo"] = "parent"
                            else:
                                l.pop("card_logo", None)
                        if isinstance(b.get("show"), dict):   # affichage à la carte : {"menu"|"view": {"e" émoji, "l" logo, "n" nom}}
                            sh = {}
                            for ctx in ("menu", "bar", "title", "view"):
                                v = b["show"].get(ctx)
                                if isinstance(v, dict):
                                    sh[ctx] = {k: bool(v.get(k)) for k in ("e", "l", "n")}
                            if sh:
                                l["show"] = sh
                            else:
                                l.pop("show", None)
                        if "hide_name" in b:   # nom masqué : seul le logo (ou l'emoji choisi) s'affiche
                            if b.get("hide_name"):
                                l["hide_name"] = True
                            else:
                                l.pop("hide_name", None)
                        if "parent_id" in b:   # ranger dans une autre liste ("" = au premier niveau)
                            try:
                                parent = self.check_parent(db, l, str(b.get("parent_id") or ""))
                            except ValueError as e:
                                return self.error(str(e))
                            if parent:
                                l["parent_id"] = parent
                            else:
                                l.pop("parent_id", None)
                        _save(DB_FILE, db)
                        return self.send_json(l)
            m = re.fullmatch(r"/api/items/(\w+)", p)
            if m:
                for idx, it in enumerate(db["items"]):
                    if it["id"] == m.group(1):
                        base, force = b.pop("_base", None), b.pop("_force", False)
                        fig_of = str(b.pop("_fig", "") or "")[:40]   # enregistrement fait pour une figurine de ce set (sa fiche à elle)
                        if "list_id" in b and not any(l["id"] == b["list_id"] for l in db["lists"]):   # (liste inexistante : jamais de fiche sans liste)
                            return self.error("Liste inconnue")
                        merged = {**it, **b}
                        if "todos" not in b and "todo" in b:   # ancien format envoyé : il remplace les tâches
                            merged.pop("todos", None)
                        new = self.clean_item(merged)
                        new["id"], new["added_at"] = it["id"], it.get("added_at")
                        if new.get("photo_url") and any(t.get("note") == PHOTO_TODO for t in new.get("todos") or []):   # photo ajoutée : « Photo à faire » est faite
                            ts = [t for t in new["todos"] if t.get("note") != PHOTO_TODO]
                            new["todos"], new["todo"], new["todo_note"] = ts, bool(ts), ts[0]["note"] if ts else ""
                        if isinstance(base, (int, float)) and not force and (it.get("updated_at") or 0) > base:   # modifiée ailleurs entre-temps
                            lost = set(_UP_RE.findall(json.dumps(it))) - set(_UP_RE.findall(json.dumps(new)))
                            if lost:
                                return self.error("Cette fiche a été modifiée ailleurs (autre appareil ou autre onglet) depuis que vous l'avez ouverte : "
                                                  f"l'enregistrer maintenant retirerait {len(lost)} photo(s) ajoutée(s) entre-temps.", 409)
                        if new.get("kind") == "custom" and it.get("kind") == "custom" and new.get("custom_type") != it.get("custom_type") \
                                and new.get("moc_scan") in ("done", "running"):
                            new["moc_scan"] = "cancelled"
                        fresh = [u for u in new.get("alt_photos") or [] if u not in set(it.get("alt_photos") or [])]
                        if fresh:   # apparence ajoutée : sa date à elle (seule sa vignette remonte dans la vue générale)
                            new["alt_at"] = {**(new.get("alt_at") or {}), **{u: int(time.time()) for u in fresh}}
                        same = lambda x: {k: v for k, v in x.items() if k not in ("updated_at", "todos")}   # une tâche n'est pas une modification de la fiche
                        no_alt = lambda x: {k: v for k, v in same(x).items() if k not in ("alt_photos", "alt_names", "alt_hidden", "alt_at", "main_name")}
                        before = {**self.clean_item(it), "id": it["id"], "added_at": it.get("added_at")}
                        if same(new) != same(before) and no_alt(new) == no_alt(before):   # seules les apparences ont changé : la fiche garde sa date
                            if it.get("updated_at"):
                                new["updated_at"] = it["updated_at"]
                            else:
                                new.pop("updated_at", None)
                        elif same(new) == same(before):
                            # enregistré sans rien changer : la date de dernière modification ne bouge pas
                            if it.get("updated_at"):
                                new["updated_at"] = it["updated_at"]
                            else:
                                new.pop("updated_at", None)
                        elif fig_of and new.get("kind", "set") == "set":   # changé pour une de ses figurines : seule elle remonte, pas le set
                            prev = {k: it[k] for k in ("updated_at", "added_at", "own_at", "fig_touch", "fig_at") if it.get(k) is not None}
                            touch_for_fig(prev, fig_of)
                            new.update(prev)
                        pending = parts_estimable(new) and (_load(CACHE_FILE, {}).get(cache_key(new)) or {}).get("pending_prices")
                        if pending and new.get("no_parts_est") and str(new.get("moc_file") or "").startswith("Inventaire Rebrickable"):
                            for k in ("moc_parts", "moc_price", "moc_file"):   # « Estimer par les pièces » décoché : estimation retirée
                                new.pop(k, None)
                        if new.get("kind", "set") == "set" and new.get("list_id") != it.get("list_id") and list_kinds(db).get(it.get("list_id")) == "wishlist" \
                                and list_kinds(db).get(new.get("list_id")) == "collection":   # (souhait acquis : directement « À construire » — 22/11)
                            new["unbuilt"] = True
                        if new.get("kind") == "part" and bool(new.get("got")) != bool(it.get("got")):   # ✔ OK ↔ inventaire : la ligne suit
                            for ln in new.get("inv_links") or []:
                                inv_row_status(db, ln["inv"], ln["row"], "ok" if new.get("got") else "cmd")
                        db["items"][idx] = new
                        if new.get("kind") == "fig" and (new.get("display_name") or "") != (it.get("display_name") or ""):   # renommée : ses autres fiches aussi
                            fig_name_spread(db, new.get("number"), it.get("display_name"), new.get("display_name"), skip=new)
                        if new.get("list_id") != it.get("list_id"):   # autre liste : le set qui la contient / ce qui y est rangé suivent
                            move_linked(db, {new["id"]}, new["list_id"], touch_lead=False, prev={new["id"]: it.get("list_id")})   # (sa liste d'avant : ses figurines de cette liste suivent)
                        if new.get("fig_items") or (new.get("kind", "set") == "set" and new.get("list_id") != it.get("list_id")):   # set : ses figurines (fiches) suivent son nombre de figurines, sa liste, son état (set acquis depuis la liste de souhaits : créées tout de suite)
                            set_figs_sheets(db, new)
                        elif new.get("set_orig") and int(new.get("quantity", 1) or 1) != int(it.get("quantity", 1) or 1):   # figurine d'origine : son nombre dans le set
                            host = next((i for i in db["items"] if i["id"] == new.get("attached_to")), None)
                            if host:
                                mfs = (_load(CACHE_FILE, {}).get(host["number"]) or {}).get("minifigs") or []
                                have = fig_have(host, mfs)
                                have[new["number"]] = int(new.get("quantity", 1) or 1)
                                host["fig_counts"], host["missing_minifigs"] = have, []
                        if indiv_rejoin(db, new):   # « Dupliquer puis modifier » enregistrée identique aux autres : elle les rejoint
                            _save(DB_FILE, db)
                            return self.send_json({**enrich(new), "rejoined": True})
                        _save(DB_FILE, db)
                        if pending and not new.get("no_parts_est") and not new.get("moc_parts"):   # recoché (ou jamais faite) : on la lance
                            threading.Thread(target=parts_estimate_start, args=(new["id"],), daemon=True).start()
                        if new.get("updated_at") != it.get("updated_at"):
                            item_parts_refresh(new["id"])
                        if new.get("kind") == "custom" and new.get("custom_type") == "fig" and new.get("image") \
                                and new.get("image") != it.get("image") and not new.get("moc_parts"):
                            threading.Thread(target=moc_scan_start, args=(new["id"],), daemon=True).start()   # nouvelle photo : nouveau scan
                        return self.send_json(enrich(new))
        return self.error("Introuvable", 404)

    def do_DELETE(self):
        prio_seen(urlparse(self.path).path)   # (priorité à l'écran — 22/11)
        if self.demo_route() or self.guard():
            return
        p = urlparse(self.path).path
        with lock:
            db = load_db()
            backup_db("avant-suppression")   # liste ou élément supprimé : copie juste avant
            m = re.fullmatch(r"/api/lists/(\w+)", p)
            if m:
                target = next((l for l in db["lists"] if l["id"] == m.group(1)), None)
                if target and target.get("default"):
                    return self.error("La liste « À commander » par défaut ne peut pas être supprimée")
                if target and target.get("kind") == "wishlist":
                    return self.error("La liste de souhaits ne peut pas être supprimée")
                if any(i.get("list_id") == m.group(1) for i in db["items"]):   # seules les listes vides se suppriment
                    return self.error("Cette liste n'est pas vide : déplacez ou supprimez d'abord ses fiches")
                if target and target.get("kind") != "wishlist" and \
                        sum(1 for l in db["lists"] if l.get("kind") != "wishlist") <= 1:
                    return self.error("Impossible de supprimer la dernière liste de collection")
                for l in db["lists"]:   # ses sous-listes remontent d'un niveau
                    if l.get("parent_id") == m.group(1):
                        if target and target.get("parent_id"):
                            l["parent_id"] = target["parent_id"]
                        else:
                            l.pop("parent_id", None)
                db["lists"] = [l for l in db["lists"] if l["id"] != m.group(1)]
                db["items"] = [i for i in db["items"] if i["list_id"] != m.group(1)]
                _save(DB_FILE, db)
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/items/(\w+)", p)
            if m:
                gone = next((i for i in db["items"] if i["id"] == m.group(1)), None)
                for ln in (gone or {}).get("inv_links") or []:   # pièce plus commandée : la ligne de l'inventaire repasse « à commander »
                    cur = ((db.get("inventories") or {}).get(ln["inv"]) or {}).get("rows", {}).get(ln["row"]) or {}
                    if cur.get("s") == "cmd":
                        inv_row_status(db, ln["inv"], ln["row"], "order")
                items_removed(db, {m.group(1)})
                _save(DB_FILE, db)
                return self.send_json({"ok": True})
        return self.error("Introuvable", 404)

    # -- helpers
    @staticmethod
    def check_parent(db, lst, parent_id):
        """Parent valide pour une liste : existe, même type, et pas elle-même ni une de ses sous-listes."""
        if not parent_id:
            return ""
        par = next((l for l in db["lists"] if l["id"] == parent_id), None)
        if not par or (par.get("kind") or "collection") != (lst.get("kind") or "collection"):
            raise ValueError("Liste parente introuvable")
        seen, cur = set(), par
        while cur and cur["id"] not in seen:
            if cur["id"] == lst.get("id"):
                raise ValueError("Une liste ne peut pas être rangée dans une de ses sous-listes")
            seen.add(cur["id"])
            cur = next((l for l in db["lists"] if l["id"] == cur.get("parent_id")), None)
        return parent_id

    @staticmethod
    def clean_item(b):
        def num(v, default=None):
            try:
                return round(float(v), 2) if v not in (None, "") else default
            except (TypeError, ValueError):
                return default
        return {
            "list_id": b.get("list_id"),
            "number": b.get("number"),
            "kind": b.get("kind") if b.get("kind") in ("fig", "custom", "part") else "set",
            **Handler.clean_part(b),
            **Handler.clean_custom(b),
            "display_name": str(b.get("display_name") or "").strip()[:150],
            **({"also_used": True} if b.get("also_used") and b.get("condition") == "neuf" and b.get("kind", "set") == "set" else {}),   # souhait : neuf ou d'occasion
            **({"gift_note": str(b["gift_note"]).strip()[:300]} if str(b.get("gift_note") or "").strip() else {}),   # « à offrir » : pour qui, quand…
            **({"as_set": True} if b.get("as_set") and b.get("kind") == "fig" else {}),   # minifig du catalogue traitée comme un set (ex. Thwimp)
            **(Handler.clean_alts(b) if b.get("kind", "set") in ("set", "fig") else {}),   # apparences alternatives d'un set du catalogue (ex. la DeLorean)
            "condition": "neuf" if b.get("condition") == "neuf" else "occasion",
            "with_minifigs": bool(b.get("with_minifigs", True)),
            "missing_minifigs": list(b.get("missing_minifigs") or []),
            "fig_counts": {str(k)[:30]: max(0, min(999, int(v))) for k, v in (b.get("fig_counts") or {}).items()
                           if str(v).lstrip("-").isdigit()} if isinstance(b.get("fig_counts"), dict) else {},
            "quantity": max(1, min(9999, int(num(b.get("quantity"), 1)))),
            "purchase_price": num(b.get("purchase_price")),
            "notes": (b.get("notes") or "")[:2000],
            **(lambda ts: {"todos": ts, "todo": bool(ts), "todo_note": ts[0]["note"] if ts else ""})(clean_todos(b)),
            "photo": b.get("photo") if b.get("photo") in ("fig", "set") else "",
            "photo_url": (lambda u: u if re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", u) or re.match(
                r"https://(www\.brickeconomy\.com|cdn\.rebrickable\.com|storage\.googleapis\.com/brickognize-static)/", u) else "")(
                str(b.get("photo_url") or "")[:400]),
            **Handler.clean_parts(b, num),
            **{k: b[k] for k in ("rb_fig", "fig_swaps", "swap_price") if b.get(k) and b.get("kind") == "fig"},
            **({"attached_to": str(b["attached_to"])[:20]} if b.get("attached_to") and childable(b) else {}),   # seule une figurine (ou figurine MOC) a un parent ; le lien lui-même est vérifié à l'enregistrement (links_fix)
            **({"set_orig": True} if b.get("set_orig") and b.get("attached_to") and b.get("kind") == "fig" else {}),   # figurine d'origine de son set
            **({"indiv": b["indiv"]} if b.get("indiv") in ("orig", "add") and b.get("attached_to") and b.get("kind") == "fig" else {}),   # exemplaire mis à part dans son set
            **({"indiv_copy": b["indiv_copy"]} if isinstance(b.get("indiv_copy"), dict) and b.get("indiv") and b.get("attached_to") else {}),   # copie d'une originale pas encore modifiée (indiv_rejoin)
            **({"hide_view": bool(b["hide_view"])} if b.get("hide_view") is not None and (b["hide_view"] or b.get("indiv")) else {}),   # « Afficher dans la vue générale » décochée
            **({"item_logo": str(b["item_logo"])} if re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", str(b.get("item_logo") or "")) else {}),   # logo individuel (vignettes)
            **({"no_logo": True} if b.get("no_logo") and b.get("attached_to") and childable(b) else {}),   # figurine enfant : sans le logo hérité de son set
            **({"fig_items": True} if b.get("fig_items") and b.get("kind", "set") == "set" else {}),   # set dont les figurines sont des fiches
            **({"has_box": True} if b.get("has_box") and (b.get("kind", "set") == "set" or (b.get("kind") == "custom" and b.get("partial_set"))) else {}),
            **({"no_plan": True} if b.get("no_plan") and (b.get("kind", "set") == "set" or (b.get("kind") == "custom" and b.get("partial_set"))) else {}),
            **({"unbuilt": True} if b.get("unbuilt") and (b.get("kind", "set") == "set" or (b.get("kind") == "custom" and b.get("custom_type") != "fig")) else {}),   # « à construire »
            **({"from_inventory": str(b["from_inventory"])[:60]} if b.get("from_inventory") and b.get("kind") == "custom" else {}),   # fiche créée depuis un inventaire
            **({k: b[k] for k in ("moc_parts", "moc_price", "moc_file") if b.get(k) and parts_estimable(b)}),   # estimation par les pièces (posée par le serveur)
            **({"no_parts_est": True} if b.get("no_parts_est") and parts_estimable(b) else {}),   # sans cote : « Estimer par les pièces » décoché
            **({"cmf_set": str(b["cmf_set"])[:20]} if b.get("cmf_set") and b.get("kind") == "fig" and re.fullmatch(r"\w+-\d+", str(b["cmf_set"])) else {}),
            **(Handler.clean_order(b) if b.get("kind") == "fig" else {}),   # figurine à commander : état voulu, export BrickLink, reçue
            "updated_at": int(time.time()),   # dernière modification (tri par défaut)
            **({"x": backoffice.clean_x(b["x"])} if isinstance(b.get("x"), dict) and backoffice.clean_x(b["x"]) else {}),   # champs personnalisés (back office)
            **({"tags": [t for t in dict.fromkeys(b["tags"]) if t in ("complet", "ameliore", "modifie", "partiel", "moc")][:5]}   # étiquettes ajoutées à la main
               if isinstance(b.get("tags"), list) and b["tags"] else {}),
            **({"tags_off": [t for t in dict.fromkeys(b["tags_off"]) if t in ("ameliore", "modifie", "partiel", "moc")][:4]}   # étiquettes calculées retirées de la fiche
               if isinstance(b.get("tags_off"), list) and b["tags_off"] else {}),
            **({"accessories": [acc_clean(a) for a in b["accessories"][:40] if isinstance(a, dict)]}   # nom, photo, liste de pièces facultative
               if isinstance(b.get("accessories"), list) and b["accessories"] and b.get("kind", "set") in ("fig", "custom", "set") else {}),
            **({"split_from": str(b["split_from"])[:20]} if b.get("split_from") and b.get("attached_to") else {}),
            **({"fig_mods": b["fig_mods"]} if isinstance(b.get("fig_mods"), dict) and b["fig_mods"] and b.get("kind", "set") == "set" else {}),
            **({"fig_at": {str(k)[:40]: int(v) for k, v in b["fig_at"].items() if isinstance(v, (int, float))}}   # date de modification de chaque figurine du set
               if isinstance(b.get("fig_at"), dict) and b["fig_at"] and b.get("kind", "set") == "set" else {}),
            **({"set_mod": b["set_mod"]} if isinstance(b.get("set_mod"), dict) and b["set_mod"] and b.get("kind", "set") == "set" else {}),
        }

    @staticmethod
    def clean_order(b):
        """Champs « À commander » d'une pièce ou d'une figurine : état voulu (bl_cond : N neuf, U occasion, X n'importe — absent = neuf),
        dernier export vers la wanted list BrickLink (bl_wanted, date), quantité déjà exportée (bl_qty), reçue (got)."""
        return {**({"bl_cond": b["bl_cond"]} if b.get("bl_cond") in ("N", "U", "X") else {}),
                **({"bl_wanted": int(b["bl_wanted"])} if str(b.get("bl_wanted") or "").isdigit() else {}),   # dernier export vers ma wanted list BrickLink (date)
                **({"bl_qty": int(b["bl_qty"])} if str(b.get("bl_qty") or "").isdigit() and int(b["bl_qty"]) > 0 else {}),   # combien sont déjà dans la wanted list
                **({"got": True} if b.get("got") is True else {}),   # ✔ OK : reçue (sort de la liste au « Nettoyer »)
                **({"ordered": [{"site": str(o.get("site") or "")[:20], "order": str(o.get("order") or "")[:40], "date": int(o.get("date") or 0),
                                 "qty": int(o.get("qty") or 0), **({"paid": float(o["paid"])} if isinstance(o.get("paid"), (int, float)) else {})} for o in b["ordered"][:20] if isinstance(o, dict)]}
                   if isinstance(b.get("ordered"), list) and b["ordered"] else {}),   # commandée d'après mes commandes (lues)
                **({"cmd_m": int(b["cmd_m"])} if str(b.get("cmd_m") or "").isdigit() and int(b["cmd_m"]) > 0 else {}),   # commandée à la main (date)
                **({"o_off": [str(x)[:40] for x in b["o_off"][:50]]} if isinstance(b.get("o_off"), list) and b["o_off"] else {})}   # commandes écartées à la main

    @staticmethod
    def clean_part(b):
        if b.get("kind") != "part":
            return {}
        im = str(b.get("image") or "")
        s_ = lambda k, n=120: str(b.get(k) or "").strip()[:n]
        try:
            color_id = int(b.get("color_id"))
        except (TypeError, ValueError):
            color_id = None
        set_num = s_("set_number", 20)
        return {"part_num": s_("part_num", 40), "part_name": s_("part_name", 200), "bricklink": s_("bricklink", 40),
                "color_id": color_id, "color_name": s_("color_name", 60), "color_rgb": s_("color_rgb", 6),
                "element_id": s_("element_id", 20), "set_number": norm_set(set_num) or set_num or "",
                **Handler.clean_order(b),   # suivi « À commander » : état voulu, export BrickLink, reçue
                "image": im if re.match(r"https://(cdn\.rebrickable\.com|storage\.googleapis\.com/brickognize-static)/", im) else None,
                **({"inv_links": [{"inv": str(x.get("inv") or "")[:60], "row": str(x.get("row") or "")[:60], "q": max(1, min(9999, int(x.get("q") or 1)))}
                                  for x in b["inv_links"][:50] if isinstance(x, dict) and x.get("inv") and x.get("row")]}
                   if isinstance(b.get("inv_links"), list) and b["inv_links"] else {})}

    @staticmethod
    def clean_alts(b):
        """Apparences alternatives (photos importées) d'une fiche : montrées à part, jamais comptées ; avec leur nom."""
        out = {}
        raw_n = b.get("alt_names") if isinstance(b.get("alt_names"), list) else []
        pairs = [(u, " ".join(str(raw_n[k] if k < len(raw_n) else "").split())[:60])
                 for k, u in enumerate(b.get("alt_photos") if isinstance(b.get("alt_photos"), list) else [])
                 if isinstance(u, str) and re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", u)][:6]
        alts = [u for u, _ in pairs]
        if any(n for _, n in pairs):   # nom de chaque apparence (affiché dans la vue générale)
            out["alt_names"] = [n for _, n in pairs]
        mn = " ".join(str(b.get("main_name") or "").split())[:60]
        if mn:   # nom de l'apparence principale
            out["main_name"] = mn
        if alts:
            out["alt_photos"] = alts
            hid = [u for u in (b.get("alt_hidden") if isinstance(b.get("alt_hidden"), list) else []) if u in alts]
            if hid:   # apparences à ne pas montrer dans la vue générale (coche décochée)
                out["alt_hidden"] = hid
            at = b.get("alt_at") if isinstance(b.get("alt_at"), dict) else {}
            at = {u: int(at[u]) for u in alts if isinstance(at.get(u), (int, float))}   # date d'ajout de chaque apparence (sa vignette remonte seule)
            if at:
                out["alt_at"] = at
        return out

    @staticmethod
    def clean_custom(b):
        if b.get("kind") != "custom":
            return {}
        im = str(b.get("image") or "")
        ok = re.fullmatch(r"/api/upload/[0-9a-f]{16,40}", im) or \
            re.match(r"https://(www\.brickeconomy\.com|storage\.googleapis\.com/brickognize-static|cdn\.rebrickable\.com)/", im)
        url = str(b.get("moc_url") or "").strip()[:300]
        out = {"custom_name": (b.get("custom_name") or "").strip()[:150] or "Sans nom",
               "custom_type": "fig" if b.get("custom_type") == "fig" else "set",
               "image": im if ok else None,
               "moc_url": url if re.match(r"https://(www\.)?(rebrickable|bricklink)\.com/", url) else ""}
        out.update(Handler.clean_alts(b))
        if b.get("catalog_set"):   # vrai set LEGO absent du catalogue des prix : estimé par ses pièces, sans être un MOC
            out["catalog_set"] = True
        if b.get("partial_set") and out["custom_type"] == "set":   # partie d'un vrai set (liste de pièces importée) : « Set partiel », pas « MOC »
            out["partial_set"] = True
        for k in ("moc_parts", "moc_price", "moc_file", "moc_reviewed", "moc_scan", "moc_scan_fail", "value_hist", "year"):   # posés par le serveur, conservés tels quels
            if b.get(k):
                out[k] = b[k]
        return out

    @staticmethod
    def clean_parts(b, num):
        """Ancien « set partiel » (pourcentage) supprimé : un set est toujours complet ; les sets partiels sont des fiches à part."""
        return {"portion": 100, "portion_note": "", "parts": []}

    def proxy_image(self, url, w=""):
        if not IMG_OK.match(url):
            return self.error("URL non autorisée", 403)
        try:
            path, ctype = cache_any(url)   # copie locale d'abord (hors ligne), sinon les sources une à une
        except Exception as e:
            return self.error(f"Image indisponible : {e}", 404)
        th = upload_thumb(path, os.path.basename(path), w, IMG_THUMBS) if w else None   # grilles : version réduite
        return self.send_file(th, "image/jpeg", cache=True) if th else self.send_file(path, ctype, cache=True)


# ---------------------------------------------------------------- images : copie locale de toutes les images externes
IMG_OK = re.compile(r"https://(www\.brickeconomy\.com|storage\.googleapis\.com/brickognize-static|cdn\.rebrickable\.com|www\.lego\.com/cdn/product-assets|www\.lego\.com/cdn/cs|img\.bricklink\.com/ItemImage|img\.brickowl\.com/files/image_cache)/")   # (BrickOwl : photos du catalogue, dernier recours des figurines — 20/11)


# 🪄 détourage ISNet : Python à part (onnxruntime) et modèle, hors du dépôt (voir detourage.py) ; absents → détourage sur l'appareil
CUTOUT_DIR = os.environ.get("BQ_CUTOUT_DIR") or os.path.join(os.path.dirname(ROOT), "briquotheque-outils", "detourage")   # à côté du dossier de l'appli
CUTOUT_PY = os.environ.get("BQ_CUTOUT_PY") or os.path.join(CUTOUT_DIR, "venv", "bin", "python")
CUTOUT_MODEL = os.environ.get("BQ_CUTOUT_MODEL") or os.path.join(CUTOUT_DIR, "isnet-general-use.onnx")
_cutout_lock = threading.Lock()


def img_fallbacks(u):
    """Image d'un site qui refuse désormais les robots (BrickEconomy) : la même chose sur un site ouvert —
    Rebrickable ou la banque d'images BrickLink pour un set, BrickLink pour une figurine. Photo « élément » de pièce absente chez
    Rebrickable : l'image de la pièce dans sa couleur (trouvée par el_img_job)."""
    m = re.fullmatch(r"https://cdn\.rebrickable\.com/media/parts/elements/(\d+)\.\w+", u or "")
    if m:
        alt = el_img_map().get(m.group(1)) or ""
        return [alt] if alt else []
    if (u or "").startswith("https://cdn.rebrickable.com/media/parts/"):   # autre photo de pièce absente : l'image de la pièce dans sa couleur
        alt = el_img_map().get("u:" + u) or ""
        return [alt] if alt else []
    m = re.search(r"brickeconomy\.com/resources/images/sets/(?:lego-)?([\w.-]+?)_(?:large|medium|small|thumb)(?:-\d+)?\.\w+", u or "")
    if m:   # (photo principale, ou photo de galerie « <n°>_large-4.jpg » : la photo principale du set ailleurs)
        return [f"https://cdn.rebrickable.com/media/sets/{m.group(1)}.jpg", f"https://img.bricklink.com/ItemImage/SN/0/{m.group(1)}.png"]
    m = re.search(r"brickeconomy\.com/resources/images/minifigs/([\w-]+?)_(?:large|medium|small|thumb)\.\w+", u or "")
    if m:   # BrickEconomy écrit « sh259 », BrickLink « sh0259 » : les deux, l'officielle à 4 chiffres d'abord
        n = m.group(1)
        bl = sources.bl_fig_no(n)
        if bl != n:   # préfixe propre à BrickLink (« adp107 » du catalogue des cotes = « bdp107 ») : son image là-bas
            return [f"https://img.bricklink.com/ItemImage/MN/0/{bl}.png"] + fig_rb_img(n)   # (et sa photo de secours : Rebrickable / BrickOwl)
        p = re.fullmatch(r"([a-z]+)(\d{1,3})([a-z]?)", n)
        pad = f"{p.group(1)}{int(p.group(2)):04d}{p.group(3)}" if p else n
        return [f"https://img.bricklink.com/ItemImage/MN/0/{x}.png" for x in dict.fromkeys((pad, n))] + fig_rb_img(n)
    return []


# ---- pièces : photo « élément » absente chez Rebrickable → l'image de la pièce dans sa couleur (20/11)
EL_IMG_FILE = os.path.join(ROOT, "data", "cache_el_img.json")   # {n° d'élément: image de remplacement, ou "" (rien trouvé)}
_el_img = {"busy": False, "want": set(), "left": False}   # (left : arrêtée par une pause de Rebrickable — reprise dans 15 min)
EL_RE = re.compile(r"https://cdn\.rebrickable\.com/media/parts/elements/(\d+)\.\w+")


def part_shape_img(pn, cid):
    """Image de la forme d'une pièce imprimée (« 92743pr0004 » → « 92743 ») dans sa couleur, sinon dans n'importe quelle couleur ; "" si rien."""
    base = re.sub(r"(?:pr|pat|pb|ps|px|pat)\d+[a-z0-9]*$", "", str(pn or ""))
    if not base or base == pn:
        return ""
    alt = ""
    if cid is not None:
        try:
            alt = (sources.rb(f"lego/parts/{urllib.parse.quote(base)}/colors/{cid}/") or {}).get("part_img_url") or ""
        except sources.RebrickableBusy:
            raise
        except Exception:
            alt = ""
    if not alt:
        try:
            alt = (sources.rb(f"lego/parts/{urllib.parse.quote(base)}/") or {}).get("part_img_url") or ""
        except sources.RebrickableBusy:
            raise
        except Exception:
            alt = ""
    return alt


def el_img_map():
    return _load(EL_IMG_FILE, {})


def el_img_job():
    """Photos « élément » de pièces absentes chez Rebrickable : l'image de la même pièce dans sa couleur, enregistrée sur le serveur."""
    if DEMO or COPIE or _el_img["busy"]:
        return
    _el_img["busy"] = True
    try:
        urls = set(_el_img["want"]); _el_img["want"].clear()
        rows = {}   # photo indiquée → (pièce Rebrickable, couleur) : pour trouver l'image de la pièce dans sa couleur si la photo n'existe pas
        for k, v in list(_parts_cache().items()):   # pièces des figurines (gardées : « mf2:<version> »)
            if k.startswith("mf2:") and isinstance(v, dict):
                for r in v.get("parts") or []:
                    u0 = str((r or {}).get("image") or "") if isinstance(r, dict) else ""
                    if EL_RE.fullmatch(u0):
                        urls.add(u0)
                    if u0.startswith("https://cdn.rebrickable.com/") and r.get("part_num"):
                        rows.setdefault(u0, (r["part_num"], r.get("color_id")))
        mp, got = dict(el_img_map()), 0
        for u, (pn, cid) in sorted(rows.items()):   # (toute photo de pièce, pas seulement « élément » : rendu LDraw, photo…)
            if EL_RE.fullmatch(u) or os.path.exists(img_path(u)):
                continue
            if "u:" + u in mp:   # (remplacement connu : sur le disque, sinon retéléchargé)
                if mp["u:" + u] and not os.path.exists(img_path(mp["u:" + u])):
                    try:
                        cache_image(mp["u:" + u]); got += 1
                    except Exception:
                        pass
                continue
            try:
                cache_image(u)
                continue
            except Exception as e:
                if not (getattr(e, "code", None) in (404, 410, 403) or isinstance(e, LookupError)):
                    continue
            try:
                alt = ""
                if cid is not None:
                    alt = (sources.rb(f"lego/parts/{urllib.parse.quote(str(pn))}/colors/{cid}/") or {}).get("part_img_url") or ""
                alt = alt or (sources.rb(f"lego/parts/{urllib.parse.quote(str(pn))}/") or {}).get("part_img_url") or ""
                alt = alt or part_shape_img(pn, cid)   # (dernier recours : la même forme sans impression)
            except sources.RebrickableBusy:
                _el_img["left"] = True
                break
            except Exception:
                continue
            mp["u:" + u] = alt if alt and IMG_OK.match(alt) and alt != u else ""
            _save(EL_IMG_FILE, mp)
            if mp["u:" + u]:
                try:
                    cache_image(mp["u:" + u]); got += 1
                except Exception:
                    pass
        for u in sorted(urls):
            el = EL_RE.fullmatch(u).group(1)
            if os.path.exists(img_path(u)):
                continue
            if el in mp and not mp[el] and "x:" + el not in mp:   # (rien trouvé : une nouvelle tentative, avec la forme sans impression)
                pass
            elif el in mp:   # déjà cherchée : son remplacement doit être sur le disque (effacé par un ménage : retéléchargé)
                if mp[el] and not os.path.exists(img_path(mp[el])):
                    try:
                        cache_image(mp[el]); got += 1
                    except Exception:
                        pass
                continue
            try:
                cache_image(u)   # (la photo « élément » existe : gardée telle quelle)
                continue
            except Exception as e:
                if not (getattr(e, "code", None) in (404, 410) or isinstance(e, LookupError)):
                    continue   # (erreur passagère : au prochain passage)
            try:
                d = sources.rb(f"lego/elements/{el}/") or {}
                pn, cid = (d.get("part") or {}).get("part_num"), (d.get("color") or {}).get("id")
                alt = ""
                if pn and cid is not None:
                    alt = (sources.rb(f"lego/parts/{urllib.parse.quote(pn)}/colors/{cid}/") or {}).get("part_img_url") or ""
                alt = alt or (d.get("part") or {}).get("part_img_url") or ""
                if not alt and pn:
                    alt = (sources.rb(f"lego/parts/{urllib.parse.quote(pn)}/") or {}).get("part_img_url") or ""
                if not alt and pn:   # dernier recours : la même forme sans impression
                    alt = part_shape_img(pn, cid)
                mp["x:" + el] = 1
            except sources.RebrickableBusy:
                _el_img["left"] = True
                break
            except Exception:
                continue
            mp[el] = alt if alt and IMG_OK.match(alt) else ""
            _save(EL_IMG_FILE, mp)
            if mp[el]:
                try:
                    cache_image(mp[el]); got += 1
                except Exception:
                    pass
        if got:
            print(f"Images de pièces : {got} photo(s) de remplacement enregistrée(s) sur le serveur", flush=True)
    finally:
        _el_img["busy"] = False


def el_img_loop():
    time.sleep(150)   # (après le démarrage)
    while True:
        _el_img["left"] = False
        try:
            el_img_job()
        except Exception as e:
            print("Images de pièces :", e, flush=True)
        time.sleep(900 if _el_img.get("left") else 6 * 3600)   # (interrompue : reprise dans 15 min)


# ---- figurines : la photo Rebrickable de la même figurine, quand BrickEconomy (bloqué) et BrickLink (fermé) ne la donnent pas
FIG_IMG_FILE = os.path.join(ROOT, "data", "cache_fig_img.json")   # {numéro: {"u": photo Rebrickable ou "" (rien de sûr), "t": heure}}
_fig_img = {"busy": False, "mt": None, "d": {}}


def fig_img_map():
    """Correspondances numéro de figurine → photo Rebrickable (relues seulement quand le fichier change)."""
    try:
        mt = os.path.getmtime(FIG_IMG_FILE)
    except OSError:
        return {}
    if mt != _fig_img["mt"]:
        _fig_img["d"], _fig_img["mt"] = _load(FIG_IMG_FILE, {}), mt
    return _fig_img["d"]


def fig_rb_img(n):
    u = (fig_img_map().get(n) or {}).get("u")
    return [u] if u and IMG_OK.match(u) else []


def be_fig_no(u):
    m = re.search(r"brickeconomy\.com/resources/images/minifigs/([\w-]+?)_(?:large|medium|small|thumb)\.\w+", u or "")
    return m.group(1) if m else None


FIG_NAME_STOP = {"with", "and", "the", "minifigure", "minifig", "lego", "of", "in", "a", "an", "figure"}


def fig_pick_by_name(n, cands):
    """Plusieurs versions Rebrickable possibles : celle que le nom BrickOwl désigne sans ambiguïté (tous ses mots distinctifs dans le nom
    de la version), d'abord parmi les versions trouvées dans ses sets ; sinon None."""
    bo = str((_fu_cache().get(n) or {}).get("name") or "").lower()
    words = {w for w in re.findall(r"[a-z]+", bo) if len(w) > 2 and w not in FIG_NAME_STOP}
    if len(words) < 2:   # (un seul mot, ex. « Stormtrooper » : trop vague)
        return None
    for pool in ([c for c in cands if c.get("from") and c.get("from") != "nom"], cands):
        hit = [c for c in pool if words <= set(re.findall(r"[a-z]+", str(c.get("name") or "").lower()))]
        if len(hit) == 1:
            return hit[0]
    return None


def fig_img_job():
    """Pour chaque figurine de la collection dont aucune image n'est sur le serveur : la photo Rebrickable de la même figurine
    (correspondance sûre seulement), enregistrée en local pour toujours. Freinée (Rebrickable : une requête à la fois)."""
    if DEMO or COPIE or _fig_img["busy"]:
        return
    _fig_img["busy"] = True
    try:
        mp, now, got = dict(fig_img_map()), time.time(), 0
        chosen = {}   # n° de figurine → version Rebrickable choisie sur une de ses fiches (correspondance sûre : c'est moi qui l'ai dit)
        for it in load_db().get("items") or []:
            if it.get("kind") == "fig" and RB_FIG.fullmatch(str(it.get("rb_fig") or "")):
                chosen.setdefault(str(it.get("number") or ""), it["rb_fig"])
        todo = []
        for u in sorted(pinned_image_urls()):
            n = be_fig_no(u)
            e = mp.get(n) if n else None
            if n and n not in todo and not has_local(u) and e and e.get("u") and IMG_OK.match(e["u"]):   # secours connu, effacé du disque : retéléchargé
                try:
                    cache_image(e["u"]); got += 1
                except Exception:
                    pass
                continue
            if n and n not in todo and not has_local(u) and (not e or (not e.get("u") and (now - e.get("t", 0) > 30 * 86400 or e.get("v", 0) < 3 or (n in chosen and e.get("rb") != chosen[n])))):
                todo.append(n)
        for n in todo:
            img = None
            try:
                c = _parts_cache().get("fc:" + n) or {}
                rbn = n if RB_FIG.fullmatch(n) else c.get("rb") or chosen.get(n)
                if rbn:   # référence Rebrickable déjà connue : sa photo
                    img = (sources.rb(f"lego/minifigs/{urllib.parse.quote(rbn)}/") or {}).get("set_img_url") or ""
                else:   # sinon : celle de ses sets qui correspond sans ambiguïté
                    try:
                        cands = rb_fig_match(n)
                    except sources.RebrickableBusy:
                        raise
                    except Exception:   # (fiche du catalogue des cotes refusée, etc. : pas de version Rebrickable — BrickOwl ensuite)
                        cands = []
                    sure = [m for m in cands if m.get("sure")]
                    pick = sure[0] if len(sure) == 1 else fig_pick_by_name(n, cands)   # (plusieurs versions : le nom BrickOwl départage, sinon rien)
                    img = (pick.get("image") or "") if pick else ""
                if not img:   # toujours rien de sûr chez Rebrickable : la photo officielle de SA page BrickOwl (son n° BrickLink y figure)
                    pp = re.fullmatch(r"([a-z]+)(\d{1,3})([a-z]?)", n)
                    for bid in dict.fromkeys([sources.bl_fig_no(n), f"{pp.group(1)}{int(pp.group(2)):04d}{pp.group(3)}" if pp else n, n]):
                        try:
                            img = sources.bo_fig_image(bid)
                        except Exception:
                            img = ""
                        time.sleep(1.5)   # (BrickOwl : sans hâte)
                        if img:
                            break
            except sources.RebrickableBusy:
                _fig_img["left"] = True
                break   # (Rebrickable demande une pause : la suite au prochain passage — dans 15 min)
            except Exception:
                continue   # (erreur passagère : réessayé au prochain passage)
            mp[n] = {"u": img if img and IMG_OK.match(img) else "", "t": time.time(), "v": 3, **({"rb": rbn} if rbn else {})}   # (v 3 : essayé avec le nom BrickOwl, puis la page BrickOwl)
            _save(FIG_IMG_FILE, mp)
            if mp[n]["u"]:
                try:
                    cache_image(mp[n]["u"]); got += 1
                except Exception:
                    pass
        if got:
            print(f"Images de figurines : {got} photo(s) Rebrickable enregistrée(s) sur le serveur", flush=True)
    finally:
        _fig_img["busy"] = False


def fig_img_loop():
    time.sleep(90)   # (après le démarrage)
    while True:
        _fig_img["left"] = False
        try:
            fig_img_job()
        except Exception as e:
            print("Images de figurines :", e, flush=True)
        time.sleep(900 if _fig_img.get("left") else 6 * 3600)   # (interrompue : reprise dans 15 min)
IMG_LIMIT = 500 * 1024 * 1024    # au-delà : on fait de la place…
IMG_TARGET = 400 * 1024 * 1024   # … jusqu'à redescendre ici, en supprimant d'abord les images inutilisées les plus anciennes
_img_new, _img_lock = [0], threading.Lock()


def img_path(url):
    return os.path.join(IMG_DIR, hashlib.sha1(url.encode()).hexdigest())


IMG_MAGIC = (b"\xff\xd8\xff", b"\x89PNG", b"GIF8", b"RIFF", b"\x00\x00\x01\x00", b"<svg", b"<?xml")


def is_image(head):
    """Les premiers octets sont-ils ceux d'une image (et pas d'une page web « introuvable ») ? (21/11)"""
    head = head or b""
    return any(head.startswith(m) for m in IMG_MAGIC) or head[4:8] == b"ftyp"   # (ftyp : AVIF / HEIC)


def cache_any(url):
    """Une image et ses sources de secours (BrickEconomy bloqué → Rebrickable, banque BrickLink…) : d'abord une copie locale de
    n'importe laquelle (fonctionne sans internet), sinon chaque source l'une après l'autre ; la première trouvée est gardée.
    Rend (chemin, type) ou lève l'erreur de la dernière source."""
    cands = [url] + img_fallbacks(url)
    for c in cands:
        if os.path.exists(img_path(c)):
            try:
                return cache_image(c)   # (déjà là : aucune requête)
            except Exception:   # (fausse image retirée : la suivante — 21/11)
                pass
    err = LookupError("Image introuvable")
    for c in cands:
        try:
            return cache_image(c)
        except Exception as e:
            err = e
    raise err


def has_local(url):
    """Une copie locale de cette image (ou de l'une de ses sources de secours) existe-t-elle ? (une vraie image — 21/11)"""
    def real(c):
        try:
            with open(img_path(c), "rb") as fh:
                return is_image(fh.read(16))
        except OSError:
            return False
    return any(real(c) for c in [url] + img_fallbacks(url))


_img_miss = {}   # url → heure : image absente chez la source (404), pas redemandée pendant 6 h
def hd_candidates(u):
    """Versions plus grandes d'une image de catalogue (la meilleure d'abord)."""
    m = re.fullmatch(r"https://www\.brickeconomy\.com/resources/images/sets/lego-([\w-]+?)_(?:small|medium|thumb|large)\.(?:jpg|png)", u)
    if m:
        return [f"https://cdn.rebrickable.com/media/sets/{m.group(1)}.jpg", f"https://www.brickeconomy.com/resources/images/sets/lego-{m.group(1)}_large.jpg"]
    m = re.fullmatch(r"https://cdn\.rebrickable\.com/media/thumbs/sets/([\w.-]+?)\.jpg/\d+x\d+p?\.jpg", u)
    if m:
        return [f"https://cdn.rebrickable.com/media/sets/{m.group(1)}.jpg"]
    m = re.fullmatch(r"(https://www\.brickeconomy\.com/resources/images/minifigs/[\w-]+?)_(?:thumb|small|medium)\.\w+", u)
    if m:
        return [m.group(1) + "_large.jpg"]
    m = re.fullmatch(r"https://img\.brickowl\.com/files/image_cache/(?:small|medium|large)/([\w.-]+)", u)   # (BrickOwl : version « larger » — 22/11)
    if m:
        return [f"https://img.brickowl.com/files/image_cache/{z}/{m.group(1)}" for z in ("larger", "large") if z not in u]
    return []


THUMB_DIR = os.path.join(DATA, "thumbs")
IMG_THUMBS = os.path.join(ROOT, "data", "img_thumbs")   # miniatures des images du catalogue (grilles), partagées avec la démo

# ---- images du catalogue en HD : Rebrickable (sets jusqu'à 2400 px, minifigs 800 px) au lieu des petites images BrickEconomy
HD_FILE = os.path.join(ROOT, "data", "cache_hd.json")   # image d'origine → {"u": version HD, "px"} ou {"no": heure} (pas de HD sûre)
HD_MAX = 1400   # la copie locale est réduite à 1400 px (une image Rebrickable de set fait jusqu'à 3 Mo)
RB_IMG = "https://cdn.rebrickable.com/media/sets/{}.jpg"
_hd = {"m": {}, "t": None}


def hd_map():
    try:
        mt = os.path.getmtime(HD_FILE)
    except OSError:
        return {}
    if mt != _hd["t"]:
        _hd["m"], _hd["t"] = _load(HD_FILE, {}), mt
    return _hd["m"]


def hd_img(u):
    """La version HD d'une image du catalogue si elle est prête, sinon l'image elle-même."""
    e = hd_map().get(u) if isinstance(u, str) and u else None
    return (e.get("u") or u) if isinstance(e, dict) else u


def img_px(path):
    from PIL import Image
    with Image.open(path) as im:
        return max(im.size)


def hd_fetch(url):
    """Télécharge une image HD et garde une copie réduite à HD_MAX px ; renvoie sa taille (px)."""
    path, _ = cache_image(url)
    from PIL import Image
    tmp = None
    with Image.open(path) as im:
        px = max(im.size)
        if px > HD_MAX or os.path.getsize(path) > 450_000:
            im.draft("RGB", (HD_MAX, HD_MAX))
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                bg = Image.new("RGB", im.size, "white")
                bg.paste(im, mask=im.split()[-1])
                im = bg
            else:
                im = im.convert("RGB")
            im.thumbnail((HD_MAX, HD_MAX), Image.LANCZOS)
            px = max(im.size)
            tmp = path + f".{threading.get_ident()}.part"
            im.save(tmp, "JPEG", quality=88, optimize=True, progressive=True)
    if tmp:
        os.replace(tmp, path)
        with open(path + ".type", "w") as f:
            f.write("image/jpeg")
    return px


def _on_white(im):
    from PIL import Image
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")
    bg.alpha_composite(im)
    return bg.convert("RGB")


def hd_fig_ok(orig_path, hd_path):
    """Photo de minifig Rebrickable acceptée seulement sur fond blanc net et ressemblante à l'image d'origine
    (beaucoup sont des photos d'utilisateurs : fond coloré, ombres, casque retiré, accessoires absents)."""
    from PIL import Image
    with Image.open(hd_path) as x:
        b = _on_white(x)
    with Image.open(orig_path) as x:
        a = _on_white(x)
    s = b.resize((96, 96))
    edge = [s.getpixel((x, y)) for x in range(96) for y in (0, 1, 2, 93, 94, 95)] + [s.getpixel((x, y)) for y in range(96) for x in (0, 1, 2, 93, 94, 95)]
    if sum(1 for p in edge if min(p) > 242) < .97 * len(edge):
        return False

    def sig(im):
        box = im.convert("L").point(lambda v: 255 if v < 235 else 0).getbbox() or (0, 0) + im.size
        return list(im.crop(box).resize((12, 24)).getdata())
    return sum(abs(x - y) for p, q in zip(sig(a), sig(b)) for x, y in zip(p, q)) / (12 * 24 * 3) < 38


def hd_set_figs(number, mfs):
    """Minifigs BrickEconomy d'un set → minifigs Rebrickable du même set (nom qui correspond nettement, dans les deux sens)."""
    rb = [m for m in sources.rb(f"lego/sets/{urllib.parse.quote(number)}/minifigs/?page_size=100").get("results", []) if m.get("set_num")]
    W = lambda s: {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 2}
    sc = lambda f, m: len(W(f.get("name")) & W(m.get("set_name")))
    mfs = [f for f in mfs if f.get("id")]
    if len(mfs) == 1 and len(rb) == 1:
        return {mfs[0]["id"]: rb[0]}
    out = {}
    for f in mfs:
        s = sorted(rb, key=lambda m: -sc(f, m))
        if not s or sc(f, s[0]) == 0 or (len(s) > 1 and sc(f, s[0]) == sc(f, s[1])):
            continue
        back = sorted(mfs, key=lambda g: -sc(g, s[0]))
        if back[0] is f and (len(back) == 1 or sc(back[0], s[0]) > sc(back[1], s[0])):
            out[f["id"]] = s[0]
    left_f = [f for f in mfs if f["id"] not in out]
    used = {m["set_num"] for m in out.values()}
    left_m = [m for m in rb if m["set_num"] not in used]
    if len(left_f) == 1 and len(left_m) == 1:   # la dernière qui reste de chaque côté (ex. R2-D2 : nom trop court)
        out[left_f[0]["id"]] = left_m[0]
    return out


def hd_scan():
    """Cherche la version HD des images de mes sets et minifigs (toutes listes) ; une image n'est adoptée que si elle est nettement plus grande."""
    db, cache, m = load_db(), _load(CACHE_FILE, {}), dict(hd_map())
    now, n = time.time(), [0]
    fresh = lambda u: u in m and ("u" in m[u] or now - m[u].get("no", 0) < 90 * 86400)
    todo = lambda u: isinstance(u, str) and IMG_OK.match(u) and not fresh(u)

    def base(u, dflt):   # taille de l'image d'origine (au moins celle réellement affichée)
        try:
            return max(img_px(img_path(u)), dflt) if os.path.exists(img_path(u)) else dflt
        except Exception:
            return dflt

    def note(orig, cand, dflt, fig=False):
        px, ok = 0, False
        if cand:
            try:
                px = hd_fetch(cand)
                ok = px >= base(orig, dflt) * 1.2 and (not fig or hd_fig_ok(cache_image(orig)[0], img_path(cand)))
            except Exception:
                ok = False
            time.sleep(1)
        if ok:
            m[orig] = {"u": cand, "px": px}
        else:
            m[orig] = {"no": int(now)}
            if orig.endswith("_thumb.png"):   # minifig : au moins la photo moyenne (300 px) au lieu de la vignette (120 px)
                med = orig[:-len("_thumb.png")] + "_medium.jpg"
                try:
                    cache_image(med)
                    m[orig] = {"u": med, "px": 300}
                except Exception:
                    pass
        n[0] += 1
        if n[0] % 10 == 0:
            _save(HD_FILE, m)

    figs_rb = {it.get("number"): fig_rb_known(it) for it in db["items"] if it.get("kind") == "fig"}
    for it in db["items"]:
        k = it.get("kind", "set")
        if k not in ("set", "fig"):
            continue
        info = cache.get(cache_key(it)) or {}
        u = info.get("image")
        if todo(u):
            if k == "set":
                c = [x for x in hd_candidates(u) if x.startswith("https://cdn.rebrickable.com/media/sets/")]
                note(u, c[0] if c else None, 400)
            else:
                rb = figs_rb.get(it["number"])
                if rb is None:   # comme pour ses pièces : la minifig Rebrickable sûre (gardée en cache)
                    try:
                        c = rb_fig_candidates(it["number"])
                        rb = c[0]["fig_num"] if c and c[0].get("sure") else ""
                        _parts_cache_put("fc:" + it["number"], {"rb": rb, "_t": time.time()})
                    except Exception:
                        rb = None
                if rb is not None:
                    note(u, RB_IMG.format(rb) if rb else None, 300, True)
        mfs = [f for f in info.get("minifigs") or [] if todo(f.get("image"))]
        if k == "set" and mfs:
            known = {f["id"]: figs_rb.get(f.get("id")) or (_parts_cache().get("fc:" + (f.get("id") or "")) or {}).get("rb") for f in mfs}
            try:
                found = hd_set_figs(it["number"], info["minifigs"]) if not all(known.values()) else {}
            except Exception:
                continue
            for f in mfs:
                rb = known.get(f["id"]) or (found.get(f["id"]) or {}).get("set_num")
                if f.get("image") not in m or not fresh(f.get("image")):
                    note(f["image"], RB_IMG.format(rb) if rb else None, 300, True)
    if n[0]:
        _save(HD_FILE, m)
        print(f"Images HD : {sum(1 for e in m.values() if e.get('u'))} adoptées, {n[0]} vérifiées", flush=True)


def hd_keeper():
    """Toutes les heures : les images HD des nouveaux sets et minifigs (une fois trouvées, rien n'est refait)."""
    time.sleep(120)
    while True:
        try:
            hd_scan()
        except Exception as e:
            print("Images HD :", e, flush=True)
        time.sleep(3600)


def upload_thumb(path, hx, w, folder=None):
    """Miniature d'une photo importée (affichage en grille) ; None si la photo est déjà petite ou illisible."""
    try:
        w = 300 if int(w) <= 300 else 600
    except (TypeError, ValueError):
        return None
    out = os.path.join(folder or THUMB_DIR, f"{hx}_{w}.jpg")
    try:
        if os.path.isfile(out) and os.path.getmtime(out) >= os.path.getmtime(path):
            return out
        from PIL import Image
        with Image.open(path) as im:
            if max(im.size) <= w * 1.2:
                return None
            im.draft("RGB", (w, w))
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                bg = Image.new("RGB", im.size, "white")
                bg.paste(im, mask=im.split()[-1])
                im = bg
            else:
                im = im.convert("RGB")
            im.thumbnail((w, w), Image.LANCZOS)
            os.makedirs(folder or THUMB_DIR, exist_ok=True)
            tmp = out + f".{threading.get_ident()}.part"
            im.save(tmp, "JPEG", quality=85, optimize=True)
            os.replace(tmp, out)
        return out
    except Exception:
        return None


def cache_image(url):
    """Télécharge une image externe une fois pour toutes ; renvoie (chemin, type) ou lève une erreur."""
    path = img_path(url)
    meta = path + ".type"
    if os.path.exists(path):
        try:
            with open(path, "rb") as fh:
                ok = is_image(fh.read(16))
        except OSError:
            ok = True
        if not ok:   # gardée par erreur (page « introuvable » déguisée en image) : retirée, la source est dite absente (21/11)
            for f in (path, meta):
                try:
                    os.remove(f)
                except OSError:
                    pass
            _img_miss[url] = time.time()
            raise LookupError("Pas une image")
    if os.path.exists(path):
        try:   # dernière utilisation (au plus une écriture par jour) : sert à choisir quoi supprimer en premier
            if time.time() - os.path.getmtime(path) > 86400:
                os.utime(path)
        except OSError:
            pass
    else:
        if time.time() - _img_miss.get(url, 0) < 6 * 3600:
            raise LookupError("Image absente chez la source")
        try:
            data, ctype = sources.fetch_image(url)
        except Exception as e:
            if getattr(e, "code", None) in (404, 410):
                _img_miss[url] = time.time()
            raise
        if not (ctype or "").startswith("image/") or not data or not is_image(data[:16]):   # (contenu vérifié : pas une page « introuvable » — 21/11)
            _img_miss[url] = time.time()
            raise LookupError("Pas une image")
        tmp = path + f".{threading.get_ident()}.part"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
        with open(meta, "w") as f:
            f.write(ctype)
        _img_new[0] += 1
        if _img_new[0] % 100 == 0:   # beaucoup de nouvelles images : on vérifie la place
            threading.Thread(target=images_cleanup, daemon=True).start()
    return path, (open(meta).read() if os.path.exists(meta) else "image/jpeg")


def pinned_image_urls():
    """Images rattachées à ce que je possède ou ai listé (collection, souhaits, pièces, inventaires) : jamais supprimées."""
    db, cache, urls = load_db(), _load(CACHE_FILE, {}), set()
    add = lambda u: urls.add(u) if isinstance(u, str) and IMG_OK.match(u) else None
    for it in db["items"]:
        info = cache.get(cache_key(it)) or {}
        for u in (info.get("image"), it.get("photo_url"), it.get("image")):
            add(u)
            if isinstance(u, str) and u.endswith("_thumb.png"):
                add(u[:-len("_thumb.png")] + "_medium.jpg")   # photo moyenne d'une minifig (fiche)
        for f in info.get("minifigs") or []:
            add(f.get("image"))
            if (f.get("image") or "").endswith("_thumb.png"):
                add(f["image"][:-len("_thumb.png")] + "_medium.jpg")
        for x in (it.get("parts") or []) + (it.get("moc_parts") or []):
            add(x.get("image"))
        for sw in (it.get("fig_swaps") or []) + [x for m in (it.get("fig_mods") or {}).values() if isinstance(m, dict) for x in m.get("fig_swaps") or []] \
                + ((it.get("set_mod") or {}).get("fig_swaps") or []):
            add((sw.get("orig") or {}).get("image")); add((sw.get("new") or {}).get("image"))
    for inv in (db.get("inventories") or {}).values():
        add(inv.get("photo"))
    for x in (_load(NOV_FILE, {}).get("items") or []):   # nouveautés : photos du set et de ses figurines
        add(x.get("image"))
        for u in x.get("images") or []:
            add(u)
        for f in x.get("figs") or []:
            add(f.get("image"))
    for k, v in list(_parts_cache().items()):   # pièces des figurines (« mf2: ») : leurs photos, et donc leurs remplacements — 20/11
        if k.startswith("mf2:") and isinstance(v, dict):
            for r in v.get("parts") or []:
                if isinstance(r, dict):
                    add(r.get("image"))
    for u in list(urls):   # la source de secours gardée à la place d'une image bloquée
        for c in img_fallbacks(u):
            if os.path.exists(img_path(c)):
                urls.add(c)
    hm = hd_map()
    for u in list(urls):   # leur version HD aussi
        if (hm.get(u) or {}).get("u"):
            urls.add(hm[u]["u"])
    return urls


IMG_DISK_MIN = 1024 * 1048576    # les images téléchargées RESTENT sur le serveur : ménage seulement sous 1 Go libre sur le disque…
IMG_DISK_OK = 1536 * 1048576     # … jusqu'à 1,5 Go libre — et jamais une image de la collection, des listes ou des nouveautés


def images_cleanup():
    """Disque presque plein (moins de 1 Go libre) : supprime les images NON rattachées (ni collection, ni listes, ni nouveautés),
    les moins récemment utilisées d'abord, jusqu'à 1,5 Go libre. Sinon : rien n'est supprimé."""
    try:
        if shutil.disk_usage(IMG_DIR).free >= IMG_DISK_MIN:
            return
    except OSError:
        return
    with _img_lock:   # verrou à part : la collection reste utilisable pendant le ménage
        files = []
        for name in os.listdir(IMG_DIR):
            if name.endswith((".type", ".part")):
                continue
            pth = os.path.join(IMG_DIR, name)
            try:
                st = os.stat(pth)
            except OSError:
                continue
            files.append((st.st_mtime, st.st_size, name))
        total = sum(sz for _, sz, _ in files) + sum(
            os.path.getsize(os.path.join(IMG_DIR, n)) for n in os.listdir(IMG_DIR) if n.endswith(".type"))
        need = IMG_DISK_OK - shutil.disk_usage(IMG_DIR).free   # (ce qu'il faut libérer)
        keep = {hashlib.sha1(u.encode()).hexdigest() for u in pinned_image_urls()}
        freed = 0
        for mt, sz, name in sorted(files):   # les plus anciennes d'abord
            if freed >= need:
                break
            if name in keep:
                continue
            for pth in (os.path.join(IMG_DIR, name), os.path.join(IMG_DIR, name + ".type"),
                        os.path.join(IMG_THUMBS, name + "_300.jpg"), os.path.join(IMG_THUMBS, name + "_600.jpg")):
                try:
                    freed += os.path.getsize(pth); os.remove(pth)
                except OSError:
                    pass
        print(f"Images : {round(freed / 1048576)} Mo libérés ({round((total - freed) / 1048576)} Mo gardés)", flush=True)


IMG_FILE_RE = re.compile(r"\.(jpe?g|png|webp|gif)(/[\w.]+)?$", re.I)   # une adresse d'image (pas une page)
_pf, _pf_lock = {"q": [], "seen": set(), "busy": 0}, threading.Lock()   # verrou propre : jamais bloqué par le ménage


def prefetch_images(urls):
    """Télécharge tout de suite (en arrière-plan, deux à la fois) les images pas encore en local."""
    new = []
    with _pf_lock:
        for u in urls:
            if not isinstance(u, str) or u in _pf["seen"] or not IMG_OK.match(u) or not IMG_FILE_RE.search(u.split("?")[0]):
                continue
            _pf["seen"].add(u)
            if not has_local(u):
                new.append(u)
        if len(_pf["seen"]) > 50000:
            _pf["seen"].clear()
        _pf["q"].extend(new)
        start = max(0, min(2, len(_pf["q"])) - _pf["busy"])
        _pf["busy"] += start

    def run():
        try:
            while True:
                with _pf_lock:
                    if not _pf["q"]:
                        return
                    u = _pf["q"].pop(0)
                try:
                    cache_any(u)   # sources une à une
                except Exception:
                    pass
        finally:
            with _pf_lock:
                _pf["busy"] -= 1
    for _ in range(start):
        threading.Thread(target=run, daemon=True).start()


def image_urls_in(obj, out=None, depth=0):
    """Toutes les adresses d'images d'une réponse (résultats, fiche, inventaire…), avec la photo moyenne des minifigs."""
    out = set() if out is None else out
    if depth > 8:
        return out
    if isinstance(obj, str):
        if obj.startswith("https://") and IMG_OK.match(obj):
            out.add(obj)
            if obj.endswith("_thumb.png"):
                out.add(obj[:-len("_thumb.png")] + "_medium.jpg")
    elif isinstance(obj, dict):
        for v in obj.values():
            image_urls_in(v, out, depth + 1)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            image_urls_in(v, out, depth + 1)
    return out


def images_keeper():
    """Arrière-plan : télécharge les images rattachées pas encore en local, puis vérifie la place (au démarrage, puis toutes les 6 h)."""
    while True:
        try:
            for u in pinned_image_urls():
                if not has_local(u):   # pas encore en local (ni elle, ni une source de secours) : les sources une à une
                    try:
                        cache_any(u)
                    except Exception:
                        pass
                    time.sleep(0.3)
            images_cleanup()
        except Exception as e:
            print("Images locales :", e, flush=True)
        time.sleep(6 * 3600)


# ---------------------------------------------------------------- démonstration publique (/demo)
# Une seconde instance (port local DEMO_PORT, dossier data_demo) avec une copie de 5 sets, 5 minifigs et 5 MOC
# de la collection, sans connexion. Le serveur principal la relaie pour les visiteurs passés par /demo
# (cookie bq_demo) et la remet à zéro toutes les 12 heures.
DEMO_PORT = int(os.environ.get("BQ_DEMO_PORT", "8766"))
DEMO_DIR = os.path.join(ROOT, "data_demo")
DEMO_RESET = 12 * 3600
DEMO_ITEMS = {   # éléments copiés (s'ils existent encore)
    # dont des exemplaires modifiés (pièces échangées) : Supra 77260, 77263, 8088 ; Harleen Quinzel, Jay, Tiefling, Zane
    "sets": ["0870138f5f29", "a00969b7593c", "bf490aaf0d14", "88a63b614c9b", "d9ca0fc4c712", "d0db1c01ab38", "d12c421ece3c"],
    "figs": ["008e206f222c", "dcdc497cb18e", "6c210a1b4821", "eec81078aad8", "acd92feac8eb", "0ab4e316f2c1", "1feda7b950d5"],
    "mocs": ["4658a87e823d", "7c60596d0416", "a1846753f0fa", "f57f0330f34c", "8ad9728324cb"],
}
DEMO_BLOCKED = {"/api/password", "/api/settings/unban", "/api/logout"}   # + clé Rebrickable (POST /api/settings)
DEMO_INVENTORIES = ["set-77241-1"]   # inventaire de la Honda S2000 (rose remplacé par du bleu)
_demo = {"proc": None, "reset_at": 0, "now": threading.Event()}


def _demo_wish_sets(cache):
    """Liste de souhaits de la démo : 4 sets au hasard, un à venir, un en vente, un bientôt retiré, un retiré."""
    import random
    year = time.localtime().tm_year
    sets = [(k, v) for k, v in cache.items() if not k.startswith("fig:") and v.get("name") and v.get("image")
            and v.get("theme") not in CMF_THEMES]
    ry = lambda v: int(m.group(0)) if (m := re.search(r"20\d\d", str(v.get("retirement") or ""))) else None
    groups = [
        [k for k, v in sets if re.search(r"pending|upcoming|coming soon|rumored", str(v.get("availability")), re.I)],
        [k for k, v in sets if v.get("availability") == "Retail" and (ry(v) is None or ry(v) > year + 1)],
        [k for k, v in sets if v.get("availability") == "Retail" and ry(v) is not None and ry(v) <= year + 1],
        [k for k, v in sets if v.get("availability") == "Retired"],
    ]
    return [random.choice(g) for g in groups if g]
_rl = {}


DEMO_PRIVATE_MOCS = {"papa", "maman", "juju", "gogo"}   # minifigs MOC de la famille : jamais dans la démo publique


def demo_pick(db):
    """Éléments de la démo, tirés au hasard à chaque remise à zéro, dans les mêmes proportions :
    5 sets + 2 sets modifiés, 5 minifigs + 2 minifigs modifiées, 5 MOC chiffrés (sets et minifigs)."""
    import random
    kinds = list_kinds(db)
    col = [i for i in db["items"] if kinds.get(i.get("list_id")) == "collection" and not i.get("attached_to")]
    sets = [i for i in col if i.get("kind", "set") == "set"]
    figs = [i for i in col if i.get("kind") == "fig"]
    mocs = [i for i in col if i.get("kind") == "custom" and i.get("moc_parts") and (i.get("custom_name") or "").strip().lower() not in DEMO_PRIVATE_MOCS]
    take = lambda pool, n: [i["id"] for i in random.sample(pool, min(n, len(pool)))]
    msets, mfigs = [i for i in sets if is_modified(i)], [i for i in figs if is_modified(i)]
    ps, pf = take(msets, 2), take(mfigs, 2)
    return {"sets": ps + take([i for i in sets if i["id"] not in ps], 7 - len(ps)),
            "figs": pf + take([i for i in figs if i["id"] not in pf], 7 - len(pf)),
            "mocs": take(mocs, 5)}


def demo_build():
    """Données de la démo, tirées de la collection actuelle (sans notes, prix d'achat ni tâches)."""
    tmp = DEMO_DIR + ".tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.join(tmp, "uploads"))
    os.makedirs(os.path.join(tmp, "images"))
    db, now = load_db(), int(time.time())
    lists = [{"id": "demosets", "name": "Sets", "kind": "collection", "created_at": now},
             {"id": "demofigs", "name": "Figurines", "kind": "collection", "created_at": now},
             {"id": "demomocs", "name": "MOC", "kind": "collection", "created_at": now},
             {"id": "demowish", "name": "Liste de souhaits", "kind": "wishlist", "created_at": now},
             {"id": "demoparts", "name": "À commander", "kind": "parts", "created_at": now}]
    target = {iid: lid for lid, key in (("demosets", "sets"), ("demofigs", "figs"), ("demomocs", "mocs")) for iid in demo_pick(db)[key]}
    items = []
    for it in db["items"]:
        if it["id"] in target or it.get("attached_to") in target:
            x = copy.deepcopy(it)
            x["list_id"] = target.get(x["id"]) or target.get(x.get("attached_to"))
            x.update(notes="", purchase_price=None, todo=False, todo_note="", todos=[])
            items.append(x)
    kinds = list_kinds(db)
    for it in db["items"]:   # pièces à commander : toutes, telles quelles
        if kinds.get(it.get("list_id")) == "parts":
            x = copy.deepcopy(it)
            x.update(list_id="demoparts", notes="", purchase_price=None)
            items.append(x)
    for k, num in enumerate(_demo_wish_sets(_load(CACHE_FILE, {}))):   # liste de souhaits tirée au hasard à chaque remise à zéro
        retired = (_load(CACHE_FILE, {}).get(num) or {}).get("availability") == "Retired"
        items.append({"id": f"demowish{k}", "list_id": "demowish", "number": num, "kind": "set", "display_name": "",
                      "condition": "occasion" if retired else "neuf", "with_minifigs": True, "missing_minifigs": [], "fig_counts": {},
                      "quantity": 1, "purchase_price": None, "notes": "", "todo": False, "todo_note": "", "todos": [], "photo": "", "photo_url": "",
                      "portion": 100, "portion_note": "", "parts": [], "added_at": now - k, "updated_at": now - k})
    keys = {i["number"] for i in items} | {"fig:" + i["number"] for i in items} | {i["id"] for i in items}
    inv = {k: v for k, v in (db.get("inventories") or {}).items() if k in DEMO_INVENTORIES or any(n in k for n in keys)}
    with open(os.path.join(tmp, "collection.json"), "w", encoding="utf-8") as f:
        json.dump({"lists": lists, "items": items, "inventories": inv, "wishlist_init": True, "parts_init": True}, f, ensure_ascii=False)
    for name in os.listdir(DATA):   # caches (prix, noms, inventaires…) : la démo répond tout de suite
        if name.startswith("cache_") and name.endswith(".json") or name == "box_codes.json":
            shutil.copy(os.path.join(DATA, name), os.path.join(tmp, name))
    st = _load(sources.SETTINGS_FILE, {})
    with open(os.path.join(tmp, "settings.json"), "w") as f:
        json.dump({k: st[k] for k in ("rebrickable_key", "mod_discount", "box_bonus", "plan_bonus") if k in st}, f)
    os.chmod(os.path.join(tmp, "settings.json"), 0o600)
    h = _load(HISTORY_FILE, {})
    with open(os.path.join(tmp, "history.json"), "w") as f:
        json.dump({"items": {k: v for k, v in (h.get("items") or {}).items() if k in keys}}, f)
    rv = _load(REVIEW_FILE, {})
    with open(os.path.join(tmp, "moc_review.json"), "w") as f:
        json.dump({k: v for k, v in rv.items() if k in keys}, f)
    for hx in set(re.findall(r"/api/upload/([0-9a-f]{16,40})", json.dumps([items, inv]))):   # photos des éléments et inventaires copiés
        for name in os.listdir(UPLOAD_DIR):
            if name.startswith(hx):
                shutil.copy(os.path.join(UPLOAD_DIR, name), os.path.join(tmp, "uploads", name))
    shutil.rmtree(DEMO_DIR, ignore_errors=True)
    os.rename(tmp, DEMO_DIR)


def demo_manager():
    """Serveur principal : construit la démo, la lance, la relance si elle s'arrête, la remet à zéro toutes les 12 h."""
    while True:
        try:
            if _demo["proc"] and _demo["proc"].poll() is None:
                _demo["proc"].terminate()
                try:
                    _demo["proc"].wait(15)
                except subprocess.TimeoutExpired:
                    _demo["proc"].kill()
            demo_build()
            end = time.time() + DEMO_RESET
            env = {**os.environ, "BQ_DATA": DEMO_DIR, "BQ_DEMO": "1", "PORT": str(DEMO_PORT), "HOST": "127.0.0.1",
                   "BQ_DEMO_RESET_AT": str(int(end))}
            _demo["reset_at"] = end
            _demo["now"].clear()
            while time.time() < end and not _demo["now"].is_set():   # « Remettre la démo à zéro » (Réglages) : tout de suite
                if not _demo["proc"] or _demo["proc"].poll() is not None:
                    log = open(os.path.join(DEMO_DIR, "server.log"), "a")
                    _demo["proc"] = subprocess.Popen([sys.executable, "-u", os.path.join(ROOT, "server.py")], cwd=ROOT, env=env,
                                                     stdout=log, stderr=log)
                    print("Démo lancée (remise à zéro dans 12 h)", flush=True)
                _demo["now"].wait(30)
        except Exception as e:
            print("Démo :", e, flush=True)
            time.sleep(300)


_prl = {}


def public_limited(ip, p):
    """Pages publiques, visiteur non connecté : au plus 900 requêtes par minute et par adresse (images comprises),
    et 60 pour celles qui interrogent des sites extérieurs (pièces, couleurs, objets des figurines)."""
    heavy = any(x in p for x in ("/parts", "/partcolors", "/figobjs"))
    now, key = time.time(), (ip, heavy)
    lst = [t for t in _prl.get(key, []) if now - t < 60] + [now]
    _prl[key] = lst
    if len(_prl) > 5000:
        _prl.clear()
    return len(lst) > (60 if heavy else 900)


def demo_limited(ip, p):
    """Démo publique : limite de requêtes par adresse (les recherches et photos interrogent des sites extérieurs)."""
    heavy = p.startswith(("/api/search", "/api/photo", "/api/parts/scan", "/api/refresh", "/api/part-price", "/api/parts/search",
                          "/api/parts/photo", "/api/ean", "/api/boxcode", "/api/upload", "/api/set/", "/api/fig/"))
    now, key = time.time(), (ip, heavy)
    lst = [t for t in _rl.get(key, []) if now - t < 60] + [now]
    _rl[key] = lst
    if len(_rl) > 5000:
        _rl.clear()
    return len(lst) > (40 if heavy else 900)


def resume_moc_pricing():
    for it in load_db().get("items", []):
        if (it.get("moc_parts") and not (it.get("moc_price") or {}).get("done")) or \
                any(t.get("fig_swaps") and not (t.get("swap_price") or {}).get("done") for _, t in _swap_targets(it)):
            moc_price_start(it["id"])


if __name__ == "__main__":
    if not DEMO:
        backoffice_outils.init(sys.modules[__name__])   # paramètres du serveur réglés dans le back office
        backoffice_acces.init(sys.modules[__name__])    # mot de passe et sessions du back office
    if len(sys.argv) >= 3 and sys.argv[1] == "--mot-de-passe":
        auth.set_password(sys.argv[2])
        print("Mot de passe modifié. Toutes les sessions ont été déconnectées.")
        sys.exit(0)
    install_seed()   # premier lancement : les fiches de démo
    if not auth.is_configured() and not DEMO:   # installation neuve : page /setup (mot de passe, clés API)
        _setup["code"] = secrets.token_hex(3)
        with open(os.path.join(DATA, "setup_code.txt"), "w") as _f:
            _f.write(_setup["code"] + "\n")
        os.chmod(os.path.join(DATA, "setup_code.txt"), 0o600)
        print("Première installation : ouvrez Briquothèque dans un navigateur pour créer votre mot de passe.")
        print(f"Code d'installation (demandé seulement depuis Internet) : {_setup['code']}")
    load_db()
    if not COPIE:
        resume_moc_pricing()   # chiffrages de MOC interrompus par un redémarrage
    with lock:   # MOC déjà chiffrés avant l'historique : leur dernier chiffrage devient le premier point
        _db, _ch = load_db(), False
        for _it in _db["items"]:
            _mp = _it.get("moc_price") or {}
            if _it.get("moc_parts") and _mp.get("done") and _mp.get("priced") and not _it.get("value_hist"):
                moc_hist_add(_it, _mp.get("total") or 0, time.strftime("%Y-%m-%d", time.localtime(_mp.get("t") or time.time())))
                _ch = True
        if _ch:
            _save(DB_FILE, _db)
    if not COPIE:
        threading.Thread(target=convert_cmf_sets, daemon=True).start()   # minifigs à collectionner : minifigs seules
    try:   # pièces échangées des lots de figurines : comptées sur le lot entier (une fois ; sauvegarde avant)
        _n = lot_swaps_migrate()
        if _n:
            print(f"Pièces des lots de figurines comptées sur le lot entier : {_n} fiche(s) converties", flush=True)
    except Exception as e:
        print("Conversion des lots de figurines impossible :", e, flush=True)
    try:   # figurines des sets → fiches à part entière (une fois ; sauvegarde avant)
        _n = orig_figs_convert_all()
        if _n:
            print(f"Figurines des sets converties en fiches : {_n} sets", flush=True)
    except Exception as e:
        print("Conversion des figurines impossible :", e, flush=True)
    if os.path.exists(os.path.join(ROOT, "perso.py")):   # extensions locales (fichiers privés facultatifs ; absents : rien ne change) : branchées une fois tout défini
        try:
            import perso
            if not DEMO and not COPIE:
                perso.start()
        except Exception as e:
            print("Extensions locales indisponibles :", e, flush=True)
            perso = None
    try:   # copies « Dupliquer puis modifier » / « ⧉ » jamais enregistrées (appli fermée pendant la copie) : annulées
        _n = dup_pending_purge()
        if _n:
            print(f"Copies en attente oubliées, annulées : {_n}", flush=True)
    except Exception as e:
        print("Copies en attente : vérification impossible :", e, flush=True)
    try:   # liens parent / enfant : remis d'aplomb s'il le faut (rien n'est supprimé ; sauvegarde avant)
        _n = links_check()
        if _n:
            print(f"Liens entre fiches remis d'aplomb : {_n} correction(s)", flush=True)
    except Exception as e:
        print("Vérification des liens impossible :", e, flush=True)
    if COPIE:   # copie de travail : seulement la sauvegarde quotidienne de SA collection
        threading.Thread(target=backup_keeper, daemon=True).start()
    if not DEMO and not COPIE:   # tâches de fond : seulement pour la vraie collection
        threading.Thread(target=moc_reprice_loop, daemon=True).start()
        threading.Thread(target=images_keeper, daemon=True).start()   # images rattachées en local + limite de place
        threading.Thread(target=extras_keeper, daemon=True).start()   # prix des plans seuls et boîtes vides
        threading.Thread(target=bl_keeper, daemon=True).start()   # prix BrickLink de tout ce qui est enregistré (quota du jour)
        threading.Thread(target=pending_prices_keeper, daemon=True).start()
        threading.Thread(target=uploads_keeper, daemon=True).start()   # photos qui ne servent plus : supprimées chaque jour
        threading.Thread(target=hd_keeper, daemon=True).start()   # images du catalogue en HD (Rebrickable)
        threading.Thread(target=novelties_keeper, daemon=True).start()   # nouveautés lego.com (à venir, récentes) et leurs minifigs
        threading.Thread(target=bo_keeper, daemon=True).start()
        threading.Thread(target=brickset_keeper, daemon=True).start()
        threading.Thread(target=orders_keeper, daemon=True).start()   # mes commandes BrickOwl → « Commandée » (chaque jour — 21/11 soir)   # dates LEGO de mes sets (Brickset), chaque jour pour les nouveaux (21/11 soir)   # site de référence BrickOwl / les deux : prix BrickOwl de la collection (21/11)
        lists_warm(8)   # (au démarrage aussi : la collection prête pour le premier écran — 22/11)
        threading.Thread(target=lego_themes_keeper, daemon=True).start()   # pages des thèmes lego.com : prix public et lien des sets vendus (21/11)
        threading.Thread(target=backup_keeper, daemon=True).start()   # copie quotidienne de la collection   # sets ajoutés sans cote : cote récupérée dès que possible
        threading.Thread(target=parts_pricing_keeper, daemon=True).start()   # prix des pièces : reprise + chaque semaine
        if DEMO_SITE and os.environ.get("BQ_NO_DEMO") != "1":
            threading.Thread(target=demo_manager, daemon=True).start()   # démonstration publique /demo (BQ_DEMO_SITE=1)
    if not COPIE:
        fig_used_fill()        # prix d'occasion relevés des minifigs (BrickOwl)
        threading.Thread(target=moc_scan_retry_keeper, daemon=True).start()
    with lock:   # anciennes tâches automatiques des MOC (scan à valider / à la main) : effacées — « MOC à valider » suffit
        _db = load_db()
        _n = 0
        for _it in _db["items"]:
            _ts = [t for t in _it.get("todos") or [] if not (isinstance(t, dict) and t.get("note") in (SCAN_TODO_CHECK, SCAN_TODO_MANUAL))]
            if len(_ts) != len(_it.get("todos") or []):
                _n += len(_it.get("todos") or []) - len(_ts)
                _it["todos"], _it["todo"], _it["todo_note"] = _ts, bool(_ts), (_ts[0]["note"] if _ts else "")
        if _n:
            _save(DB_FILE, _db)
            print(f"Tâches automatiques des MOC effacées : {_n}", flush=True)
    with lock:   # tâches d'une figurine de set encore rangées sur le set (ancien format, « fig ») → sur la fiche de la figurine
        _db = load_db()
        _moved = 0
        for _h in _db["items"]:
            _keep = []
            for _t in _h.get("todos") or []:
                _c = next((i for i in _db["items"] if isinstance(_t, dict) and _t.get("fig") and i.get("set_orig") and i.get("attached_to") == _h["id"]
                           and i.get("number") == _t["fig"]), None)
                if _c:
                    _c.setdefault("todos", []).append({"cat": _t.get("cat") or "Autres", "note": _t.get("note") or ""})
                    _c["todo"], _c["todo_note"] = True, _c["todos"][0]["note"]
                    _moved += 1
                else:
                    _keep.append(_t)
            if len(_keep) != len(_h.get("todos") or []):
                _h["todos"], _h["todo"] = _keep, bool(_keep)
                _h["todo_note"] = _keep[0]["note"] if _keep else ""
        if _moved:
            _save(DB_FILE, _db)
            print(f"Tâches de figurines rangées sur leur fiche : {_moved}", flush=True)
    if not COPIE:
        threading.Thread(target=nocolor_keeper, daemon=True).start()
        # (« Photo à faire » automatique : retirée le 20/11 — toutes les images sont gardées sur le serveur)   # pièces sans couleur : couleurs revérifiées une fois par jour   # scans de figurines MOC en échec : relancés toutes les 3 h
    _raw = _load(REVIEW_FILE, {})
    for _it in ([] if COPIE else load_db()["items"]):
        if _it.get("kind") == "custom" and _it.get("custom_type") == "fig" and not _it.get("moc_parts") and not _it.get("moc_reviewed") \
                and _it.get("image") and (_it.get("moc_scan") in (None, "running") or "bras_g" not in (_raw.get(_it["id"]) or {}).get("zones", {})):
            moc_scan_start(_it["id"])

    def _releasing():   # sets à venir en cache sans date de sortie : on relit leur fiche
        for k, v in list(_load(CACHE_FILE, {}).items()):
            if not k.startswith("fig:") and "pending" in str(v.get("availability") or "").lower() and not v.get("releasing"):
                try:
                    get_set(k, force=True)
                except Exception:
                    pass
    if not DEMO and not COPIE:
        threading.Thread(target=_releasing, daemon=True).start()
        threading.Thread(target=fig_img_loop, daemon=True).start()
        threading.Thread(target=el_img_loop, daemon=True).start()   # pièces : photo « élément » absente chez Rebrickable → image de la pièce dans sa couleur
        threading.Thread(target=offline_loop, daemon=True).start()   # pièces de toutes les figurines et de tous les sets, prêtes d'avance   # figurines sans image : la photo Rebrickable, gardée en local
    class QuietServer(ThreadingHTTPServer):   # (connexion fermée par le navigateur en cours de réponse : normal, pas une erreur)
        def handle_error(self, request, client_address):
            if isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)):
                return
            super().handle_error(request, client_address)
    srv = QuietServer((HOST, PORT), Handler)
    if not DEMO:
        backoffice_outils.boot_ok()   # démarrage réussi : le code modifié depuis le back office est validé
    print(f"Briquothèque disponible sur http://{'localhost' if HOST in ('127.0.0.1', '0.0.0.0') else HOST}:{PORT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt.")

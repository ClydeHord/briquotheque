# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Briquothèque — BACK OFFICE (personnalisation sans code).

Principe : toute la personnalisation tient dans UN fichier de réglages (data/backoffice.json), écrit par la page /admin.
Rien n'est modifié dans le code de l'application : à chaque page servie, le serveur glisse ces réglages et le script
/bo.js, qui les applique par-dessus (couleurs, textes, blocs des fiches, champs personnalisés, menu…).

Fichiers (tous dans data/) :
  backoffice.json              réglages PUBLIÉS (ceux que le site applique)
  backoffice_brouillon.json    BROUILLON en cours dans /backoffice (visible seulement dans l'aperçu du back office)
  backoffice_historique/       une copie des réglages à chaque publication (pour revenir en arrière)

Les valeurs des champs personnalisés sont rangées dans chaque fiche, sous la clé « x » : {identifiant du champ: valeur}.
"""
import json
import os
import re
import secrets
import threading
import time

_lock = threading.RLock()
_dir = None            # dossier data/ (donné par init)
_cache = {"t": 0, "cfg": None}
KEEP = 80              # publications gardées dans l'historique
PUBLIC_KEYS = ("theme", "texts", "rules", "adds", "moves", "css", "cards", "btn", "sizes")   # ce qu'un visiteur non connecté reçoit (pas les champs, ni le menu)
PUBLIC_BLOCKS = ("titre", "texte", "image", "bouton", "sep", "espace", "note", "html", "cadre")   # blocs d'une page publique (aucune donnée de la collection)
LISTS = ("texts", "rules", "adds", "moves", "vars", "calcs", "auto", "tiles", "sorts", "filters", "views", "fields", "secs", "links", "pages")   # listes de lignes {id, …}
DICTS = ("theme", "sheets", "menu", "cards", "tags", "btn", "sizes", "settings", "behav")   # groupes de réglages
TEXTS = ("css", "secTitle", "js")   # (« js » : script libre de l'appli privée — absent de PUBLIC_KEYS, donc jamais envoyé à un visiteur)
STR_KEYS = frozenset(("text", "label", "title", "sel", "to", "from", "expr", "url", "href", "src", "link", "kind", "pos", "page", "icon", "slug", "html", "color", "bg", "border", "line", "fmt", "help", "type", "k", "v",
                      "key", "list", "view", "sort", "dir", "target", "agg", "scope", "empty", "msg", "block", "note", "align", "attr", "mode", "op", "t", "start", "brand", "font", "logo", "ratio", "css", "secTitle",
                      "primBg", "primInk", "dangBg", "dangInk", "ink", "weight"))   # clés dont la valeur est toujours un TEXTE (un nombre y est converti, le reste écarté)
STR_LISTS = frozenset(("cols", "types", "opts"))   # clés dont la valeur est une liste de textes (« order », « hidden », « hide » : listes OU valeur simple selon l'endroit — voir _strs)
_URL_OK = re.compile(r"(?i)^(https?:|mailto:|tel:|/|#|\?|data:image/(png|jpe?g|gif|webp|svg\+xml|x-icon|avif)[;,])")


def safe_url(u):
    """Adresse utilisable dans un lien ou une image : http(s), mailto, tel, adresse du site (/…, #…), image intégrée.
    Tout autre protocole (javascript:, data:text/html…) donne une adresse vide."""
    if not isinstance(u, str):
        return ""
    u = "".join(c for c in u.strip() if c >= " " and c != "\x7f")
    if not u or _URL_OK.match(u):
        return u
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", u):
        return ""
    if re.match(r"^[\w-]+(\.[\w-]+)+([/:?#]|$)", u):   # « www.exemple.fr/page » : complété
        return "https://" + u
    return u   # adresse relative


def _clean(v, key="", depth=0):
    """Une valeur des réglages, bornée : pas de nombre impossible, pas de texte ni de liste démesurés, pas de clé piégée, adresses vérifiées."""
    if depth > 30:
        return None
    if key in STR_KEYS and not isinstance(v, str) and (key != "css" or depth == 0 or not isinstance(v, dict)):   # (« css » d'une règle : un groupe de propriétés)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return None
        v = str(int(v)) if v == int(v) and abs(v) < 1e15 else str(v)
    if key in STR_LISTS:
        return [x[:1_000_000] for x in v[:100_000] if isinstance(x, str)] if isinstance(v, list) else None
    if v is None or isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v if v == v and v not in (float("inf"), float("-inf")) and abs(v) < 1e15 else None
    if isinstance(v, str):
        if key in ("url", "href", "src", "link"):
            v = safe_url(v)
        cap = 16_000_000 if v.startswith("data:image/") else 8_000_000 if key in ("css", "html", "js") else 1_000_000
        return v[:cap].replace("\x00", "")
    if isinstance(v, list):
        return [x for x in (_clean(i, key, depth + 1) for i in v[:100_000]) if x is not None]
    if isinstance(v, dict):
        out = {}
        for k, x in list(v.items())[:100_000]:
            k = str(k)[:1000]
            if k in ("__proto__", "constructor", "prototype"):
                continue
            c = _clean(x, k, depth + 1)
            if c is not None:
                out[k] = c
        if out.get("k") == "url" and isinstance(out.get("v"), str):   # action « ouvrir une adresse » : sa cible est une adresse comme les autres
            out["v"] = safe_url(out["v"])
        if key == "cond":   # une condition, où qu'elle soit : {mode, rows: [{v, op, val}], expr?}
            out["rows"] = [x for x in out["rows"] if isinstance(x, dict)] if isinstance(out.get("rows"), list) else []
            if not out["rows"]:
                del out["rows"]
        return out
    return None


def _rows(v, cap=100_000):
    """Liste de lignes {id, …} : seulement des groupes, chacun avec un identifiant simple et unique."""
    rows, seen = [], set()
    for r in v[:cap] if isinstance(v, list) else []:
        if not isinstance(r, dict):
            continue
        i = r.get("id")
        if not isinstance(i, str) or not re.fullmatch(r"[\w-]{1,48}", i) or i in seen:
            i = "x" + secrets.token_hex(4)
            r = {**r, "id": i}
        seen.add(i)
        rows.append(r)
    return rows


def _strs(d, *keys):
    for k in keys:
        if k in d:
            if isinstance(d[k], list):
                d[k] = [x for x in d[k] if isinstance(x, str)]
            else:
                del d[k]


def _dict_of(d, k, kind):
    if k in d:
        d[k] = {a: b for a, b in d[k].items() if isinstance(b, kind)} if isinstance(d[k], dict) else {}
        if not d[k]:
            del d[k]


def normalize(cfg):
    """Réglages remis d'aplomb : les mêmes réglages, mais jamais une forme qui casserait le site ou le back office
    (mauvais type, liste à la place d'un groupe, identifiant en double, adresse « javascript: », valeur démesurée…)."""
    if not isinstance(cfg, dict):
        return {}
    out = {}
    for k, v in list(cfg.items())[:5000]:
        k = str(k)[:200]
        if not k or k.startswith("_") or k in ("__proto__", "constructor", "prototype"):   # (_note, _t… : réservés à l'historique)
            continue
        v = _clean(v, k)
        if k in LISTS:
            v = _rows(v)
        elif k in DICTS and not isinstance(v, dict):
            continue
        elif k in TEXTS and not isinstance(v, str):
            continue
        if v is None or v == "" or v == [] or v == {}:
            continue
        out[k] = v
    for k in ("texts", "rules", "adds", "moves"):   # lignes attachées à un élément de la page : il leur faut ce repère
        if k in out:
            need = "from" if k == "texts" else "sel"
            out[k] = [r for r in out[k] if isinstance(r.get(need), str) and r[need].strip() and (k != "moves" or isinstance(r.get("to"), str))]
    for r in out.get("rules", []):
        _dict_of(r, "css", (str, int, float))
        for k in ("ico", "img", "click"):
            if k in r and not isinstance(r[k], dict):
                del r[k]
    for r in out.get("texts", []):
        if not isinstance(r.get("to"), str):
            r["to"] = ""
    for r in out.get("auto", []):
        r["acts"] = [a for a in r.get("acts", []) if isinstance(a, dict)] if isinstance(r.get("acts"), list) else []
    for name in ("auto", "tiles", "filters", "views"):   # conditions : {mode, rows: [{v, op, val}], expr?}
        for r in out.get(name, []):
            c = r.get("cond")
            if c is not None and not isinstance(c, dict):
                del r["cond"]
            elif isinstance(c, dict) and "rows" in c:
                c["rows"] = [x for x in c["rows"] if isinstance(x, dict)] if isinstance(c["rows"], list) else []
    for r in out.get("fields", []):
        _strs(r, "types", "opts")
    for pg in out.get("pages", []):   # pages créées : une adresse simple, des blocs {id, k, …}
        pg["blocks"] = _rows(pg.get("blocks"))
        s = re.sub(r"[^a-z0-9]+", "-", str(pg.get("slug") or pg.get("title") or "").lower()).strip("-")[:120]
        pg["slug"] = s or "page-" + pg["id"].lower()[:12]
    sh = out.get("sheets")
    if sh is not None:
        out["sheets"] = {t: s for t, s in sh.items() if isinstance(s, dict) and re.fullmatch(r"[a-z_]{1,24}", t)}
        for s in out["sheets"].values():
            _strs(s, "order", "hidden")
    th = out.get("theme")
    if th is not None:
        for k in ("both", "light", "dark"):
            _dict_of(th, k, str)
    mn = out.get("menu")
    if mn is not None:
        _strs(mn, "order", "hidden", "off")
        _dict_of(mn, "labels", str)   # (chaque entrée du menu : son texte, et masquée ou non — « off »)
        if "items" in mn:
            mn["items"] = _rows(mn["items"])
    if "cards" in out:
        _strs(out["cards"], "hide")
    st = out.get("settings")
    if st is not None:
        _strs(st, "order", "hidden")
        _dict_of(st, "titles", str)
    tg = out.get("tags")
    if tg is not None:
        _dict_of(tg, "over", dict)
        if "add" in tg:
            tg["add"] = _rows(tg["add"])
    nv = out.get("native")   # éléments d'origine modifiés : {sorts|filters|tiles: {order, hidden, labels}}
    if nv is not None:
        for kk in list(nv):
            if kk not in ("sorts", "filters", "tiles") or not isinstance(nv[kk], dict):
                del nv[kk]
                continue
            _strs(nv[kk], "order", "hidden")
            _dict_of(nv[kk], "labels", str)
    bh = out.get("behav")
    if bh is not None:
        if "keys" in bh:
            bh["keys"] = _rows(bh["keys"], 60)
        _dict_of(bh, "sorts", str)
    return {k: v for k, v in out.items() if v not in (None, "", [], {})}


def public_cfg(cfg, page=None):
    """Ce qu'un visiteur non connecté reçoit : l'apparence seulement ; jamais les champs, le menu, les calculs ni les conditions."""
    out = {k: cfg[k] for k in PUBLIC_KEYS if k in cfg}
    for k in ("texts", "rules", "adds", "moves"):
        if isinstance(out.get(k), list):
            out[k] = [r for r in out[k] if isinstance(r, dict) and r.get("page") != "app"]
    tg = cfg.get("tags")
    if isinstance(tg, dict) and isinstance(tg.get("over"), dict):   # étiquettes d'origine renommées, recolorées ou masquées (sans condition, sans les étiquettes créées)
        ov = {k: {a: b for a, b in v.items() if a in ("text", "color", "bg", "border", "hide", "icon")} for k, v in tg["over"].items() if isinstance(v, dict)}
        ov = {k: v for k, v in ov.items() if v}
        if ov:
            out["tags"] = {"over": ov}
    if isinstance(tg, dict) and tg.get("badges") is True:   # pastilles montrées aussi sur les cartes
        out.setdefault("tags", {})["badges"] = True
    if page is not None:
        out["pages"] = [page]
    return out


def public_page(slug):
    """Une page créée dans le back office et cochée « publique » (adresse /p/<slug>) ; seulement ses blocs sans données."""
    for pg in published().get("pages") or []:
        if isinstance(pg, dict) and slug and pg.get("slug") == slug and pg.get("pub") is True and not pg.get("off"):
            return {**pg, "blocks": [b for b in pg.get("blocks") or [] if isinstance(b, dict) and b.get("k") in PUBLIC_BLOCKS]}
    return None


def init(data_dir):
    global _dir
    _dir = data_dir


def _p(name):
    return os.path.join(_dir, name)


def _read(name, default=None):
    try:
        with open(_p(name), encoding="utf-8") as f:
            v = json.load(f)
        return v if isinstance(v, dict) else default
    except (OSError, ValueError):
        return default


def _write(name, cfg):
    tmp = _p(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _p(name))


def published():
    """Réglages publiés (relus au plus une fois par seconde)."""
    with _lock:
        if _cache["cfg"] is None or time.time() - _cache["t"] > 1:
            _cache["cfg"], _cache["t"] = normalize(_read("backoffice.json", {}) or {}), time.time()   # (fichier retouché à la main : remis d'aplomb à la lecture)
        return _cache["cfg"]


def draft():
    """Brouillon du back office ; à défaut, les réglages publiés."""
    d = _read("backoffice_brouillon.json")
    return normalize(d) if d is not None else published()


def state():
    """Tout ce dont la page /backoffice a besoin à l'ouverture."""
    with _lock:
        pub, dr = published(), _read("backoffice_brouillon.json")
        dr = normalize(dr) if dr is not None else None
        return {"published": pub, "draft": dr if dr is not None else pub,
                "dirty": dr is not None and json.dumps(dr, sort_keys=True) != json.dumps(pub, sort_keys=True),
                "history": history()}


def save_draft(cfg):
    if not isinstance(cfg, dict):
        raise ValueError("Réglages illisibles")
    cfg = normalize(cfg)
    if len(json.dumps(cfg)) > 3_000_000:
        raise ValueError("Réglages trop volumineux : passez les images par la rubrique « Images » au lieu de les intégrer")
    with _lock:
        _write("backoffice_brouillon.json", cfg)
    return True


def discard():
    """Abandonne le brouillon : retour aux réglages publiés."""
    with _lock:
        try:
            os.remove(_p("backoffice_brouillon.json"))
        except OSError:
            pass


def history():
    d = _p("backoffice_historique")
    out = []
    try:
        for n in sorted(os.listdir(d), reverse=True):
            m = re.fullmatch(r"(\d{8}-\d{6})\.json", n)
            if not m:
                continue
            v = _read(os.path.join("backoffice_historique", n), {}) or {}
            out.append({"id": m.group(1), "note": str(v.get("_note") or ""), "t": v.get("_t") or 0, "count": v.get("_count") or 0})
    except OSError:
        pass
    return out


def publish(note="", count=0):
    """Le brouillon devient la version du site ; une copie datée part dans l'historique."""
    with _lock:
        cfg = draft()
        _write("backoffice.json", cfg)
        os.makedirs(_p("backoffice_historique"), exist_ok=True)
        vid = time.strftime("%Y%m%d-%H%M%S")
        _write(os.path.join("backoffice_historique", vid + ".json"), {**cfg, "_note": str(note or "")[:200], "_t": int(time.time()), "_count": count if isinstance(count, int) and not isinstance(count, bool) and 0 <= count < 10**6 else 0})
        for old in sorted(os.listdir(_p("backoffice_historique")), reverse=True)[KEEP:]:
            try:
                os.remove(os.path.join(_p("backoffice_historique"), old))
            except OSError:
                pass
        discard()
        _cache["cfg"] = None
        return vid


def version(vid):
    """Une publication de l'historique (pour la reprendre comme brouillon)."""
    if not re.fullmatch(r"\d{8}-\d{6}", str(vid or "")):
        return None
    v = _read(os.path.join("backoffice_historique", vid + ".json"))
    if v is None:
        return None
    return normalize({k: x for k, x in v.items() if not k.startswith("_")})


def inject(html, public=False, off=False, page=None):
    """Glisse les réglages publiés et les scripts du back office dans une page (avant </head>). off : page servie sans personnalisation.
    page : la page publique à afficher (/p/<adresse>)."""
    if off:
        return html
    cfg = published()
    if public:   # visiteur : seulement l'apparence, et rien de ce qui ne concerne que le site connecté
        cfg = public_cfg(cfg, page)
        if not cfg:   # rien de personnalisé pour les visiteurs : la page part telle quelle (aucun script ajouté)
            return html
    js = json.dumps(cfg, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")   # (« < » jamais écrit tel quel : aucune balise ne peut se former dans le script)
    plus = "" if public else '<script src="/bo-plus.js"></script>'   # fonctions avancées (formules, règles, vues) : site connecté seulement
    tag = (f'<script>window.BO_CFG = {js}; window.BO_PUBLIC = {"true" if public else "false"};</script><script src="/bo.js"></script>{plus}'
           '<script src="/bo-max.js"></script></head>')   # bo-max.js : étiquettes, boutons, pages, réglages de l'appli, comportements
    return html.replace(b"</head>", tag.encode("utf-8"), 1)


def clean_x(x):
    """Valeurs des champs personnalisés d'une fiche : {identifiant: texte | nombre | oui/non | liste de textes}."""
    out = {}
    if not isinstance(x, dict):
        return out
    for k, v in list(x.items())[:10_000]:
        k = str(k)[:40]
        if not re.fullmatch(r"[\w-]{1,40}", k):
            continue
        if isinstance(v, bool) or isinstance(v, (int, float)):
            out[k] = v
        elif isinstance(v, str):
            if v.strip():
                out[k] = v[:1_000_000]
        elif isinstance(v, list):
            vals = [str(i)[:20_000] for i in v[:10_000] if isinstance(i, (str, int, float)) and str(i).strip()]
            if vals:
                out[k] = vals
    return out

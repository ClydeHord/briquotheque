# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Sources de données externes : BrickEconomy (catalogue + prix) et Brickognize (photo)."""
import html
import json
import threading
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
BE = "https://www.brickeconomy.com"


def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,*/*",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def _text(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def _money(s):
    """'€1,234.56' -> 1234.56 ; renvoie None si absent."""
    if not s:
        return None
    m = re.search(r"([\d.,]+)", s)
    if not m:
        return None
    v = m.group(1).replace(",", "")
    try:
        return round(float(v), 2)
    except ValueError:
        return None


def search(query):
    """Première page de résultats, limitée à 30 sets + 30 minifigs."""
    res, _ = search_page(query, 1)
    sets = [r for r in res if r["type"] == "set"][:30]
    return sets + [r for r in res if r["type"] == "fig"][:30]


def search_page(query, page=1):
    """Une page de résultats BrickEconomy → (résultats, il y a une page suivante).
    Page 1 : sets + minifigs ; pages suivantes (formulaire ASP.NET) : sets seulement."""
    import http.cookiejar
    url = f"{BE}/search?query={urllib.parse.quote_plus(query)}"
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    H = {"User-Agent": UA, "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8", "Accept": "text/html,application/xhtml+xml,*/*"}
    page_html = op.open(urllib.request.Request(url, headers=H), timeout=25).read().decode("utf-8", "ignore")
    for n in range(2, page + 1):   # le site n'accepte que la page suivante : on les enchaîne
        if not _has_next(page_html):
            return [], False
        form = {k: html.unescape(v) for k, v in re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', page_html)}
        form.update({"__EVENTTARGET": "ctl00$ContentPlaceHolder1$ctlSets$GridViewSets", "__EVENTARGUMENT": f"Page${n}"})
        act = re.search(r'<form[^>]+action="([^"]+)"', page_html)
        action = urllib.parse.urljoin(url, html.unescape(act.group(1))) if act else url
        page_html = op.open(urllib.request.Request(action, data=urllib.parse.urlencode(form).encode(),
                            headers={**H, "Content-Type": "application/x-www-form-urlencoded"}), timeout=25).read().decode("utf-8", "ignore")
    res = _parse_search(page_html)
    if page > 1:
        res = [r for r in res if r["type"] == "set"]
    return res, _has_next(page_html)


def _has_next(page_html):
    """Pagination de la grille des sets : lien « Next » actif (pas « disabled ») ?"""
    m = re.search(r'<li class="page-item([^"]*)"><a href="javascript:__doPostBack\(\'ctl00\$ContentPlaceHolder1\$ctlSets\$GridViewSets\'[^>]*>Next</a>', page_html)
    return bool(m) and "disabled" not in m.group(1)


def _parse_search(page):
    results, seen = [], set()
    for block in page.split('class="hidden-xs ctlsets-image"')[1:]:
        block = block[:6000]
        m = re.search(r'href="/set/([^/"]+)/[^"]*"', block)
        if not m or m.group(1) in seen:
            continue
        num = m.group(1)
        seen.add(num)
        title = re.search(r"<h4><a[^>]*>(.*?)</a></h4>", block, re.S)
        name = _text(title.group(1)) if title else num
        name = re.sub(r"^\d+(-\d+)?\s+", "", name)
        img = re.search(r'<img src="([^"]+)"', block)
        year = re.search(r"Year</small>\s*<a[^>]*>(\d{4})", block)
        theme = re.search(r"Theme / Subtheme</small>\s*<a[^>]*>(.*?)</a>", block, re.S)
        pm = re.search(r"Pieces / Minifigs</small>\s*([\d,]+)\s*/\s*(\d+)", block)
        pieces = re.search(r"Pieces</small>\s*([\d,]+)", block)
        avail = re.search(r"Availability</small>\s*(?:<[^>]+>\s*)*([^<]+)", block)
        results.append({
            "availability": _text(avail.group(1)).strip() if avail else None,
            "number": num,
            "name": name,
            "image": BE + img.group(1) if img else None,
            "year": int(year.group(1)) if year else None,
            "theme": _text(theme.group(1)) if theme else None,
            "pieces": int((pm or pieces).group(1).replace(",", "")) if (pm or pieces) else None,
            "minifigs": int(pm.group(2)) if pm else 0,
        })
    # minifigs trouvées par la même recherche
    figs, seen_f = [], set()
    for fm in re.finditer(
            r'<a href="/minifig/([^/"]+)/[^"]*"[^>]*>\s*<div[^>]*>\s*<div class="setminifigpanel">(.*?)</a>', page, re.S):
        fid, block = fm.group(1), fm.group(2)
        if fid in seen_f:
            continue
        seen_f.add(fid)
        name = re.search(r'setminifigpanel-name">(.*?)</div>', block, re.S)
        img = re.search(r'<img src="([^"]+)"', block)
        val = re.search(r'setminifigpanel-value">(.*?)</div>', block, re.S)
        figs.append({"type": "fig", "number": fid, "name": _text(name.group(1)) if name else fid,
                     "image": BE + img.group(1) if img else None,
                     "value": _money(_text(val.group(1))) if val else None})
    for r in results:
        r["type"] = "set"
    return results + figs


FIG_RE = re.compile(r"^[a-z]{2,8}\d{2,5}[a-z]?$", re.I)


def fig_id_variants(fid):
    """Variantes d'écriture d'une référence de minifig : njo0523 → njo523, sh0086 → sh086 / sh86."""
    m = re.match(r"^([a-z]+)(\d+)([a-z]?)$", fid, re.I)
    out = [fid]
    if m:
        pre, num, suf = m.groups()
        for n in (str(int(num)), str(int(num)).zfill(3), str(int(num)).zfill(4)):
            v = pre + n + suf
            if v not in out:
                out.append(v)
    return out


def fig_details(fid):
    """Fiche d'une minifig ; essaie aussi les autres écritures de la référence."""
    last = None
    for v in fig_id_variants(fid):
        try:
            d = _fig_details(v)
            d["requested"] = fid
            return d
        except LookupError as e:
            last = e
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            last = LookupError("Minifig introuvable")
    raise last or LookupError("Minifig introuvable")


def _fig_details(fid):
    raw, _ = _get(f"{BE}/minifig/{urllib.parse.quote(fid)}/")
    page = raw.decode("utf-8", "ignore")
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    flat = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", body)))
    flat = re.sub(r"(\|\s?)+", "|", flat)
    start = flat.find("Minifig Details")
    if start < 0:
        raise LookupError("Minifig introuvable")
    sect = flat[start:start + 3000]

    def field(label):
        m = re.search(r"\|" + re.escape(label) + r"\|([^|]+)", sect)
        return m.group(1).strip() if m else None

    m = re.search(r"New/Loose\|Value\|([^|]+)", sect) or re.search(r"\|Value\|([^|]+)", sect)
    img = re.search(r'src="(/resources/images/minifigs/[^"]+_medium\.jpg)"', page) or \
        re.search(r'src="(/resources/images/minifigs/[^"]+)"', page)
    sets = []
    for n in re.findall(r'href="/set/([^/"]+)/', page):
        if n not in sets:
            sets.append(n)
    return {
        "type": "fig",
        "number": fid,
        "name": field("Name") or fid,
        "theme": field("Theme"),
        "subtheme": field("Subtheme"),
        "years": field("Years") or field("Year"),
        "availability": (field("Availability") or "").strip() or None,
        "value": _money(m.group(1)) if m else None,
        "image": BE + img.group(1) if img else None,
        "sets": sets[:20],
        "source": f"{BE}/minifig/{fid}/",
        "fetched_at": int(time.time()),
        **price_history(page),
    }


# ---------------------------------------------------------------- historique des prix (graphiques des pages BrickEconomy)
_CHART_RE = re.compile(r"var data = new google\.visualization\.DataTable\(\);.*?data\.addRows\(\[(.*?)\]\);.*?getElementById\('([^']+)'\)", re.S)
_ROW_RE = re.compile(r"\[new Date\((\d+), (\d+), (\d+)\), ([\d.]+)")


def price_history(page):
    """Valeur (neuf/scellé pour un set, neuve/détachée pour une minifig) : historique mensuel + prévision,
    et prix moyen des ventes par mois. Dates « AAAA-MM-JJ »."""
    today = time.strftime("%Y-%m-%d")
    out = {}
    for m in _CHART_RE.finditer(page):
        rows = sorted({(f"{int(y):04d}-{int(mo) + 1:02d}-{int(d):02d}", round(float(v), 2)) for y, mo, d, v in _ROW_RE.findall(m.group(1))})
        if not rows:
            continue
        if m.group(2) == "pricechart":
            past = [r for r in rows if r[0] <= today]
            monthly = {}
            for d, v in past:   # un point par mois (le dernier du mois) : léger, suffisant pour une courbe
                monthly[d[:7]] = (d, v)
            out["history"] = [list(x) for x in sorted(monthly.values())]
            out["forecast"] = [list(r) for r in rows if r[0] > today][:40]
        elif m.group(2) == "saleschartmonth":
            out["sales"] = [list(r) for r in rows if r[0] <= today]
    return out


# ---------------------------------------------------------------- Fiche set
def set_details(number):
    raw, _ = _get(f"{BE}/set/{urllib.parse.quote(number)}/")
    page = raw.decode("utf-8", "ignore")
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    flat = re.sub(r"<[^>]+>", "|", body)
    flat = html.unescape(re.sub(r"\s+", " ", flat))
    flat = re.sub(r"(\|\s?)+", "|", flat)

    start = flat.find("Set Details")
    if start < 0:
        raise LookupError("Set introuvable")
    sect = flat[start:start + 4000]

    def field(label, src=sect):
        m = re.search(r"\|" + re.escape(label) + r"\|([^|]+)", src)
        return m.group(1).strip() if m else None

    pricing = sect[sect.find("Set Pricing"):] if "Set Pricing" in sect else sect
    new_value = used_value = None
    m = re.search(r"New/Sealed\|Value\|([^|]+)", pricing)
    if m:
        new_value = _money(m.group(1))
    m = re.search(r"Used\|Value\|([^|]+)", pricing)
    if m:
        used_value = _money(m.group(1))
    market = _money(field("Market price", pricing))
    retail = _money(field("Retail price", pricing))
    if new_value is None:
        new_value = market or retail

    used_range = None
    m = re.search(r"Used\|Value\|[^|]+\|Range\|([^|]+)", pricing)
    if m:
        nums = [_money(x) for x in m.group(1).split("-")]
        if len(nums) == 2 and all(nums):
            used_range = nums

    pieces = field("Pieces")
    year = field("Year")

    # Figurines
    minifigs = []
    for panel in page.split('<div class="setminifigpanel">')[1:]:
        panel = panel[:2500]
        num = re.search(r'setminifigpanel-number"><span>([^<]+)</span>', panel)
        if not num:
            continue
        name = re.search(r'setminifigpanel-name">(.*?)</div>', panel, re.S)
        im = re.search(r'setminifigpanel-img"><img src="([^"]+)"', panel)
        val = re.search(r'setminifigpanel-value">(.*?)</div>', panel, re.S)
        qty = re.search(r'setminifigpanel-qty">\s*x?\s*(\d+)', panel)   # ex. « x2 » : même figurine en 2 exemplaires
        minifigs.append({
            "id": num.group(1).strip(),
            "name": _text(name.group(1)) if name else num.group(1).strip(),
            "image": BE + im.group(1) if im else None,
            "value": (_money(_text(val.group(1))) or 0.0) if val else 0.0,
            "qty": int(qty.group(1)) if qty else 1,
        })
    # Quantités (un même personnage peut apparaître plusieurs fois)
    mf_total = None
    m = re.search(r"\|Minifigs\|(\d+)\|\(Value ([^)]+)\)", sect)
    mf_count = int(m.group(1)) if m else len(minifigs)
    if m:
        mf_total = _money(m.group(2))
    if mf_total is None:
        mf_total = round(sum(f["value"] * f.get("qty", 1) for f in minifigs), 2)
    if minifigs:   # nombre réel d'exemplaires (BrickEconomy compte les modèles différents)
        mf_count = max(mf_count, sum(f.get("qty", 1) for f in minifigs))

    img = re.search(r'id="setimagesimage" src="([^"]+)"', page)
    gallery = []
    for g in ([img.group(1)] if img else []) + re.findall(r"attr\('src', '(/resources/images/sets/[^']+)'\)", page):
        if BE + g not in gallery:
            gallery.append(BE + g)
    name = field("Name") or number
    if used_value is None and new_value:
        used_value = round(new_value * 0.6, 2)  # repli : décote typique occasion

    m = re.search(r"\|Retirement\|([^|]+)", flat[start:start + 9000])
    retirement = m.group(1).strip() if m and re.search(r"20\d\d", m.group(1)) else None
    return {
        "retirement": retirement,
        "number": number,
        "name": name,
        "theme": field("Theme"),
        "subtheme": field("Subtheme"),
        "year": int(year) if year and year.isdigit() else None,
        "pieces": int(pieces.replace(",", "")) if pieces and pieces.replace(",", "").isdigit() else None,
        "availability": field("Availability"),
        "releasing": field("Releasing"),   # set à venir : date de sortie (ex. « January 2027 »)
        "retail": retail,
        "new_value": new_value,
        "used_value": used_value,
        "used_range": used_range,
        "minifig_count": mf_count,
        "minifig_value": mf_total,
        "minifigs": minifigs,
        "image": BE + img.group(1) if img else None,
        "gallery": gallery[:12],
        "source": f"{BE}/set/{number}/",
        "fetched_at": int(time.time()),
        **price_history(page),
    }


# ---------------------------------------------------------------- Photo
def recognize(image_bytes, filename="photo.jpg", content_type="image/jpeg", kind="sets"):
    boundary = "----briq" + uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="query_image"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + image_bytes + f"\r\n--{boundary}--\r\n".encode()
    url = f"https://api.brickognize.com/predict/{kind}/?top_k_items=8&min_similarity_items=0.3"
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "Briquotheque/1.0",
        "Accept": "application/json",
    })
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt:
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt:
                raise
        time.sleep(1)
    out = []
    for it in data.get("items", []):
        out.append({
            "number": it.get("id"),
            "name": it.get("name"),
            "image": it.get("img_url"),
            "score": round(float(it.get("score", 0)) * 100),
            "type": it.get("type"),
        })
    return out


def recognize_box(image_bytes, kind="figs", top=8):
    """Reconnaissance d'UN objet (le plus visible) : (propositions [{number, name, score, type}], cadre de l'objet ou None).
    Le cadre : {left, upper, right, lower, image_width, image_height} (sert à le masquer pour trouver l'objet suivant)."""
    boundary = "----briq" + uuid.uuid4().hex
    body = (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="query_image"; filename="photo.jpg"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n").encode() + image_bytes + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"https://api.brickognize.com/predict/{kind}/?top_k_items={top}&min_similarity_items=0.3", data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "Briquotheque/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = json.loads(r.read())
    items = [{"number": it.get("id"), "name": it.get("name"), "score": round(float(it.get("score", 0)) * 100), "type": it.get("type")}
             for it in data.get("items") or []]
    return items, data.get("bounding_box") or None




def recognize_part_colors(image_bytes, content_type="image/jpeg", top=3):
    """Pièce sur une zone de photo : meilleures pièces + couleurs prédites (n° BrickLink)."""
    boundary = "----briq" + uuid.uuid4().hex
    body = (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="query_image"; filename="zone.jpg"\r\n'
            f"Content-Type: {content_type}\r\n\r\n").encode() + image_bytes + f"\r\n--{boundary}--\r\n".encode()
    url = f"https://api.brickognize.com/predict/parts/?top_k_items={top}&predict_color=true&min_similarity_items=0.1"
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "Briquotheque/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return ([{"number": it.get("id"), "name": it.get("name"), "image": it.get("img_url"), "score": round(float(it.get("score", 0)) * 100)}
             for it in data.get("items", [])],
            [{"bl": str(c.get("id")), "name": c.get("name"), "score": round(float(c.get("score", 0)) * 100)} for c in data.get("colors") or []])


def recognize_all(image_bytes, content_type="image/jpeg"):
    """Interroge la reconnaissance des sets ET des minifigs, résultats fusionnés par score."""
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(2) as ex:
        futs = {k: ex.submit(recognize, image_bytes, content_type=content_type, kind=k) for k in ("sets", "figs")}
        out, errs = [], []
        for k, f in futs.items():
            try:
                for r in f.result():
                    r["type"] = "set" if k == "sets" else "fig"
                    out.append(r)
            except Exception as e:
                errs.append(e)
    if not out and errs:
        raise errs[0]
    return sorted(out, key=lambda r: -r["score"])[:12]


LEGO_FR = "https://www.lego.com/fr-fr/service/building-instructions/"
_FR_RE = re.compile(r'"CS_BuildingInstructionData","name":"((?:[^"\\]|\\.)*)","setNumber":"([\w-]+)"')


def lego_fr_name(number):
    """Nom officiel français d'un set (LEGO.com, pages des notices). None si LEGO ne le connaît pas.
    Lève une exception en cas de problème réseau (pour réessayer plus tard)."""
    base = re.sub(r"-1$", "", (number or "").strip())
    if not re.fullmatch(r"\d{3,7}", base):   # variantes (-2…) et références non numériques : pas de page LEGO
        return None
    try:
        page = _get(LEGO_FR + base, timeout=25)[0].decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    for m in _FR_RE.finditer(page):
        if m.group(2) == base:
            name = json.loads('"' + m.group(1) + '"').replace("\u2019", "'").replace("™", "").replace("®", "").strip()
            return name or None
    return None


# ---------------------------------------------------------------- noms français des minifigs (traduction automatique)
# Lexique LEGO appliqué avant la traduction (termes officiels ou que le traducteur rate)
FIG_LEXIQUE = [
    (r"^(.+?) Driver$", r"Pilote \1"),
    (r"^(.+?) Clone Trooper$", r"Soldat clone \1"),
    (r"\bDarth Vader\b", "Dark Vador"), (r"\bDarth\b", "Dark"),
    (r"\bClone Troopers?\b", "Soldat clone"), (r"\bClone Pilot\b", "Pilote clone"),
    (r"\bClone Commander\b", "Commandant clone"), (r"\bClone Captain\b", "Capitaine clone"),
    (r"\bSuper Battle Droid\b", "Super droïde de combat"), (r"\bBattle Droid\b", "Droïde de combat"),
    (r"\bAstromech Droid\b", "Droïde astromécano"), (r"\bProtocol Droid\b", "Droïde de protocole"),
    (r"\bDroid\b", "Droïde"), (r"\bDroideka\b", "Droïdeka"),
    (r"\bGrand Admiral\b", "Grand amiral"), (r"\bTusken Raider\b", "Pillard Tusken"),
    (r"\bEmperor Palpatine\b", "Empereur Palpatine"), (r"\bThe Child\b", "L'Enfant"),
    (r"\bThe Mandalorian\b", "Le Mandalorien"), (r"\bMandalorian\b", "Mandalorien"),
    (r"^The Riddler$", "L'Homme-Mystère"), (r"^Scarecrow$", "L'Épouvantail"), (r"^Two-Face$", "Double-Face"),
    (r"^The Penguin$", "Le Pingouin"), (r"^Child$", "Enfant"),
    (r"\bJedi Knight\b", "Chevalier Jedi"), (r"\bJedi Master\b", "Maître Jedi"),
    (r"\bPilot\b", "pilote"), (r"\bFirefighter\b", "Pompier"), (r"\bPolice Officer\b", "Policier"),
]


def fig_lexique(name):
    """Applique le lexique ; renvoie le texte et les mots français ajoutés (à retrouver après traduction)."""
    t, added = name or "", []
    for a, b in FIG_LEXIQUE:
        if re.search(a, t):
            t = re.sub(a, b, t)
            ph = re.sub(r"\\\d", "", b).strip(" ,")
            if len(ph) > 2:
                added.append(ph)
    return t, added


class QuotaError(Exception):
    pass


def mt_fr(text):
    """Traduction anglais → français (MyMemory, gratuit, quota journalier)."""
    url = "https://api.mymemory.translated.net/get?langpair=en|fr&q=" + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={"User-Agent": "Briquotheque/1.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        d = json.loads(r.read().decode("utf-8", "ignore"))
    if d.get("quotaFinished") or d.get("responseStatus") == 429:
        raise QuotaError("quota de traduction atteint")
    if d.get("responseStatus") not in (200, "200"):
        raise RuntimeError(str(d.get("responseDetails") or "traduction indisponible"))
    # seulement la traduction machine : la mémoire collaborative donne parfois n'importe quoi pour les noms propres
    mt = next((m.get("translation") for m in d.get("matches") or [] if m.get("created-by") == "MT!"), "")
    return html.unescape(str(mt or "")).strip()


def fig_fr_name(name):
    """Nom français d'une minifig : lexique LEGO puis traduction automatique, avec garde-fous."""
    pre, added = fig_lexique(name)
    out = pre
    if re.fullmatch(r"Pilote .+", pre) and name.endswith(" Driver"):   # « Pilote <voiture> » : rien d'autre à traduire
        return pre
    if not re.search(r"\s", name.strip()):   # un seul mot : presque toujours un nom propre (Emmet, Cotton, Bane…)
        return pre
    try:
        tr = mt_fr(pre)
    except QuotaError:
        raise
    except Exception:
        tr = ""
    if tr:   # nettoyage : numéros, ponctuation ajoutés par la mémoire de traduction
        if not re.match(r"\d", pre):
            tr = re.sub(r"^\d+[.)]\s*", "", tr)
        if not re.match(r"the\b", pre, re.I):   # « Captain X » → « Capitaine X », pas « Le capitaine X »
            tr = re.sub(r"^(le|la|les)\s+|^l['’]", "", tr, flags=re.I)
        if "Mr. " in pre:
            tr = re.sub(r"\bM\. ", "Mr. ", tr)
        tail = re.search(r"[\s!?.…]*$", pre).group(0).strip()
        tr = re.sub(r"[\s!?.…]+$", "", tr) + tail
        # références et noms à tiret (C-3PO, D-O, R4-P17, AT-AT, U-wing) : à conserver tels quels
        codes = re.findall(r"\b\w*(?:\d\w*-|-\w*\d|[A-Z]-[A-Z0-9]|-wing)\w*(?:-\w+)*", pre) + re.findall(r"\b[A-Z]-[A-Z]\b", pre)
        if any(c not in tr for c in codes):
            tr = ""
    words = lambda x: len(re.findall(r"[\w'-]+", x))
    if tr and "MYMEMORY" not in tr.upper() and words(tr) >= 0.75 * words(pre) and len(tr) <= 2.5 * len(pre) + 10 \
            and all(w.lower() in tr.lower() for w in added):   # expressions du lexique retrouvées telles quelles
        out = tr
    out = re.sub(r"\s+", " ", out).strip()
    return (out[:1].upper() + out[1:]) if out else None


def fetch_image(url):
    return _get(url, timeout=20)


# ---------------------------------------------------------------- Notices de montage officielles (lego.com)
def lego_instructions(num):
    """Livrets PDF d'un set sur lego.com : [{"url", "kind": core|extra|info, "el", "total", "cover"}].
    Les doublons « accessibles / traduits » (additional.main) sont ignorés."""
    raw, _ = _get(f"https://www.lego.com/fr-fr/service/building-instructions/{urllib.parse.quote(num)}", timeout=30)
    page = raw.decode("utf-8", "ignore")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', page, re.S)
    found = []

    def walk(o):
        if isinstance(o, dict):
            if o.get("__typename") == "BuildingInstruction" and (o.get("pdf") or {}).get("pdfUrl"):
                found.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    if m:
        walk(json.loads(m.group(1)))
    out, seen = [], set()
    for b in found:
        u = b["pdf"]["pdfUrl"]
        if u in seen or not u.startswith("https://www.lego.com/cdn/product-assets/"):
            continue
        seen.add(u)
        kind = "core" if ".bi.core." in u else "info" if ".additional.info." in u else "extra" if ".additional.extra." in u else "main"
        if kind == "main":
            continue
        seq = b.get("sequence") or {}
        out.append({"url": u, "kind": kind, "el": str(seq.get("element") or ""), "total": str(seq.get("total") or ""),
                    "cover": (b["pdf"].get("coverImage") or {}).get("src") or ""})
    return out


# ---------------------------------------------------------------- Modèles d'un set
def lego_category(slug, max_pages=8):
    """Produits d'une catégorie lego.com (fr-fr), toutes pages : [{code, name, theme, image, price, status, when, pieces, new}]."""
    out, seen = [], set()
    for page in range(1, max_pages + 1):
        raw, _ = _get(f"https://www.lego.com/fr-fr/categories/{slug}" + (f"?page={page}" if page > 1 else ""), timeout=30)
        html = raw.decode("utf-8", "ignore")
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
        if not m:
            break
        data = json.loads(m.group(1))
        variants, prods, assets = {}, [], {}

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(k, str) and k.startswith("ProductVariant:") and isinstance(v, dict):
                        variants[k] = v
                    if isinstance(k, str) and k.startswith("ListingProductAsset:") and isinstance(v, dict) and v.get("url"):
                        assets[k] = v["url"]   # photos officielles du produit (le set, sa boîte…)
                if o.get("productCode") and o.get("name") and o.get("__typename", "").endswith("Product"):
                    prods.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(data)
        new = 0
        for p in prods:
            code = str(p.get("productCode"))
            if code in seen or not re.fullmatch(r"\d{4,7}", code):
                continue
            seen.add(code)
            new += 1
            var = p.get("variant") or {}
            v = variants.get(var.get("__ref", ""), var) if isinstance(var, dict) else {}
            at = v.get("attributes") or {}
            imgs = [assets.get(r.get("__ref"), r.get("url")) for k, l in p.items() if isinstance(k, str) and k.startswith("listingAssets") and isinstance(l, list)
                    for r in l if isinstance(r, dict)]
            imgs = list(dict.fromkeys(u for u in imgs if isinstance(u, str) and u.startswith("https://www.lego.com/cdn/")))
            pdp = p.get("pdpPath") or ""   # page du produit sur lego.com
            out.append({"url": "https://www.lego.com" + pdp if pdp.startswith("/") else "", "images": imgs, "code": code, "name": p.get("name") or code, "theme": (p.get("brandCategory") or {}).get("name") or "",
                        "image": p.get('primaryImage({"size":"THUMBNAIL"})') or p.get("primaryImage") or "",
                        "price": (v.get("price") or {}).get("formattedValue"), "status": at.get("availabilityStatus") or "",
                        "when": at.get("availabilityText") or "", "pieces": at.get("pieceCount"), "new": bool(at.get("isNew"))})
        if not new:
            break
    return out


def full_name(number):
    """Nom complet du set d'après Brickset (souvent plus détaillé)."""
    raw, _ = _get(f"https://brickset.com/sets/{urllib.parse.quote(number)}")
    page = raw.decode("utf-8", "ignore")
    m = re.search(r"<dt>Name</dt>\s*<dd>(.*?)</dd>", page, re.S)
    if m:
        return _text(m.group(1))
    m = re.search(r"<title>\s*LEGO\s+[\d-]+\s+(.*?)\s*\|", page, re.S)
    return _text(m.group(1)) if m else None


def split_models(name):
    """« A & B » / « A and B » → ['A', 'B']."""
    if not name:
        return []
    parts = re.split(r"\s+(?:&|and|et)\s+", name)
    parts = [p.strip(" ,") for p in parts if p.strip(" ,")]
    return parts if len(parts) >= 2 else []


# ---------------------------------------------------------------- Rebrickable (clé API)
SETTINGS_FILE = __import__("os").path.join(__import__("os").environ.get("BQ_DATA") or __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "data"), "settings.json")


def rebrickable_key():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f).get("rebrickable_key") or None
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def rebrickable(path, key=None, timeout=20):
    key = key or rebrickable_key()
    if not key:
        raise PermissionError("Aucune clé API Rebrickable")
    url = "https://rebrickable.com/api/v3/" + path.lstrip("/")
    req = urllib.request.Request(url, headers={
        "Authorization": "key " + key, "Accept": "application/json", "User-Agent": "Briquotheque/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


# ---------------------------------------------------------------- Pièces (Rebrickable + Brickognize)
_rb_last = [0.0]
_rb_lock = threading.Lock()   # une requête Rebrickable à la fois (toutes les tâches de fond confondues)
_rb_pause = [0.0]             # refus « trop de requêtes » (429) : plus aucune requête jusqu'à cette heure
RB_GAP = 1.2                  # secondes au moins entre deux requêtes (limite de l'API : 1 par seconde)


class RebrickableBusy(RuntimeError):
    """Rebrickable a demandé de ralentir : requête non envoyée (pause en cours)."""


def rb(path):
    """Appel Rebrickable FREINÉ : une requête à la fois, RB_GAP secondes au moins entre deux, et pause complète (10 min au moins,
    ou la durée demandée par Rebrickable) dès un refus « trop de requêtes » — pour ne jamais être bloqué."""
    with _rb_lock:
        if time.time() < _rb_pause[0]:
            raise RebrickableBusy(f"Rebrickable : pause jusqu'à {time.strftime('%H:%M', time.localtime(_rb_pause[0]))} (trop de requêtes)")
        wait = RB_GAP - (time.time() - _rb_last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            return rebrickable(path)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):   # trop de requêtes (429), ou adresse bloquée (403) : tout s'arrête un moment
                try:
                    ra = int(e.headers.get("Retry-After") or 0)
                except (TypeError, ValueError):
                    ra = 0
                pause = max(600 if e.code == 429 else 1800, ra)
                _rb_pause[0] = time.time() + pause
                print(f"Rebrickable : refus {e.code}, pause de {pause // 60} min", flush=True)
            raise
        finally:
            _rb_last[0] = time.time()


def _part(p):
    ext = p.get("external_ids") or {}
    return {"part_num": p["part_num"], "name": p.get("name"), "image": p.get("part_img_url"),
            "bricklink": (ext.get("BrickLink") or [p["part_num"]])[0], "url": p.get("part_url")}


def parts_search(q):
    return parts_search_page(q, 1)[0]


FR_PARTS = {"jambes": "legs", "jambe": "leg", "tete": "minifig head", "tête": "minifig head", "visage": "minifig head", "figurine": "minifig",
            "corps": "torso", "taille": "hips", "hanches": "hips", "chevelure": "hair", "coiffure": "hair", "moustache": "moustache", "lunette": "goggles",
            "fusil": "blaster", "lance": "spear", "hache": "axe", "arc": "bow", "baguette": "wand", "couronne": "crown", "ailes": "wings", "aile": "wing",
            "queue": "tail", "socle": "stand", "support": "stand", "porte": "door", "fenetre": "window", "fenêtre": "window", "toit": "roof", "pente": "slope",
            "fleur": "flower", "feuille": "leaf", "plante": "plant", "arbre": "tree", "rocher": "rock", "poisson": "fish", "cheval": "horse", "chien": "dog",
            "chat": "cat", "oiseau": "bird", "gant": "glove", "bottes": "boots", "écharpe": "scarf", "echarpe": "scarf", "veste": "jacket", "armure": "armor",
            "cagoule": "balaclava", "foulard": "bandana", "ceinture": "belt", "collier": "neck", "lampe": "lamp", "torche": "torch", "bouteille": "bottle",
            "tasse": "cup", "assiette": "plate", "long": "long", "longs": "long", "longue": "long", "longues": "long", "court": "short", "courts": "short",
            "petit": "small", "petite": "small", "petits": "small", "grand": "large", "grande": "large", "rond": "round", "ronde": "round", "carré": "square",
            "carre": "square", "plat": "flat", "plate": "flat", "bouclés": "curly", "boucles": "curly", "frisés": "curly", "queue-de-cheval": "ponytail",
            "chignon": "bun", "mèche": "fringe", "raie": "parted", "ébouriffés": "tousled", "décoiffés": "tousled", "pierre": "stone", "cristal": "crystal", "lumineux": "light", "transparent": "trans", "transparente": "trans", "torse": "torso", "buste": "torso", "casque": "helmet", "cheveux": "hair",
            "chapeau": "hat", "casquette": "cap", "bras": "arm", "main": "hand", "mains": "hands", "cape": "cape", "visiere": "visor", "visière": "visor",
            "barbe": "beard", "arme": "weapon", "epee": "sword", "épée": "sword", "bouclier": "shield", "sabre": "lightsaber", "pistolet": "blaster",
            "masque": "mask", "lunettes": "goggles", "jupe": "skirt", "sac": "backpack", "capuche": "hood", "brique": "brick", "plaque": "plate",
            "tuile": "tile", "roue": "wheel", "pneu": "tire", "imprimé": "print", "imprimée": "print", "imprime": "print", "courtes": "short", "courte": "short"}
FR_COLORS = {"blanc": "White", "blanche": "White", "blancs": "White", "blanches": "White", "noir": "Black", "noire": "Black", "noirs": "Black", "noires": "Black",
             "rouge": "Red", "rouges": "Red", "bleu": "Blue", "bleue": "Blue", "bleus": "Blue", "bleues": "Blue", "jaune": "Yellow", "jaunes": "Yellow",
             "vert": "Green", "verte": "Green", "verts": "Green", "vertes": "Green", "gris": "Gray", "grise": "Gray", "grises": "Gray", "marron": "Brown",
             "brun": "Brown", "brune": "Brown", "beige": "Tan", "orange": "Orange", "oranges": "Orange", "rose": "Pink", "roses": "Pink", "violet": "Purple",
             "violette": "Purple", "doré": "Gold", "dorée": "Gold", "dorées": "Gold", "argent": "Silver", "argentées": "Silver", "olive": "Olive"}


def plain_legs(colors_wanted):
    """Jambes unies de figurine : chez Rebrickable une pièce par couleur de jambes (BrickLink 970c00). colors_wanted : mots anglais à retrouver dans le nom."""
    d = rb("lego/parts/?page_size=100&bricklink_id=970c00")
    res = [p for p in d.get("results", []) if "Legs" in p.get("name", "")]
    if colors_wanted:
        res = [p for p in res if all(c.lower() in p["name"].lower() for c in colors_wanted)] or res
    return [_part(p) for p in res]


_TR = {"m": None}


def translate_fr_auto(text):
    """Français → anglais (MyMemory, gratuit, sans compte), gardé dans data/cache_traductions.json. Rend "" si impossible."""
    import os, json, re, html
    path = os.path.join(os.path.dirname(SETTINGS_FILE), "cache_traductions.json")
    if _TR["m"] is None:
        try:
            _TR["m"] = json.load(open(path, encoding="utf-8"))
        except Exception:
            _TR["m"] = {}
    key = text.strip().lower()
    if key in _TR["m"]:
        return _TR["m"][key]
    try:
        req = urllib.request.Request("https://api.mymemory.translated.net/get?" + urllib.parse.urlencode({"q": key, "langpair": "fr|en"}),
                                     headers={"User-Agent": "Briquotheque/1.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            d = json.load(r)
        t = html.unescape(str((d.get("responseData") or {}).get("translatedText") or ""))
    except Exception:
        return ""
    t = re.sub(r"'s\b", "", t)
    t = re.sub(r"[^\w\s-]", " ", t).strip().lower()
    t = " ".join(w for w in t.split() if w not in ("the", "a", "an", "of", "with", "and"))
    if not t or t == key:
        return ""
    _TR["m"][key] = t
    try:
        tmp = path + ".tmp"
        json.dump(_TR["m"], open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        pass
    return t


def parts_search_page(q, page=1):
    """Recherche de pièces ; rien trouvé : traduite (français → anglais) et relancée (traducteur intégré)."""
    out, more = parts_search_page0(q, page)
    words = [w[:4] for w in re.findall(r"[^\W\d_]{4,}", q.lower())]
    relevant = any(any(w in (p.get("name") or "").lower() for w in words) for p in out[:30]) if words else bool(out)   # (Rebrickable rend parfois n'importe quoi pour un mot inconnu)
    if page == 1 and not relevant and re.search(r"[^\W\d_]{3}", q) and not re.search(r"\d", q):
        t = translate_fr_auto(q)
        if t:
            o2, m2 = parts_search_page0(t, page)
            if o2:
                out, more = o2, m2
    elif page > 1:
        t = _TR["m"].get(q.strip().lower()) if _TR["m"] else None
        if t:
            out, more = parts_search_page0(t, page)
    return out, more


def parts_search_page0(q, page=1):
    """Pièces Rebrickable par référence ou nom → (résultats, il y a une page suivante). Mots français courants traduits ; « jambes (unies) [couleur] » :
    les jambes unies d'abord (une pièce par couleur de jambes chez Rebrickable)."""
    q = q.strip()
    out, seen = [], set()
    words = q.lower().split()
    if any(w in FR_PARTS or w in FR_COLORS or w in ("uni", "unie", "unis", "unies", "legs") for w in words):
        cols = [FR_COLORS[w] for w in words if w in FR_COLORS]
        legs = any(w in ("jambes", "jambe", "legs") for w in words) and not any(w in ("courtes", "courte", "short", "imprimé", "imprimée", "imprime", "print") for w in words)
        if legs and page == 1:
            try:
                for p in plain_legs(cols):
                    out.append(p); seen.add(p["part_num"])
            except Exception:
                pass
        q = " ".join(FR_PARTS.get(w, w) for w in words if w not in ("uni", "unie", "unis", "unies") and w not in FR_COLORS)   # (la couleur se choisit ensuite : pas dans le nom)
        if legs and "short" not in q:
            q = "hips and " + " ".join(c.lower() for c in cols) + " legs" if cols else "hips and legs"
        if any(w in ("jambes", "jambe", "legs") for w in words) and "short" in q.split():   # jambes courtes : Legs Short d'abord
            q = "legs short"
            if page == 1:
                try:
                    p0 = _part(rb("lego/parts/41879a/")); out.insert(0, p0); seen.add(p0["part_num"])
                except Exception:
                    pass
    if page == 1:
        try:  # référence exacte d'abord
            p = rb(f"lego/parts/{urllib.parse.quote(q)}/")
            out.append(_part(p)); seen.add(p["part_num"])
        except Exception:
            pass
    d = rb(f"lego/parts/?page_size=30&page={page}&search={urllib.parse.quote(q)}")
    for p in d.get("results", []):
        if p["part_num"] not in seen:
            out.append(_part(p)); seen.add(p["part_num"])
    return out, bool(d.get("next"))


def part_from_bricklink(bl_id):
    d = rb(f"lego/parts/?bricklink_id={urllib.parse.quote(bl_id)}")
    if d.get("results"):
        return _part(d["results"][0])
    try:
        return _part(rb(f"lego/parts/{urllib.parse.quote(bl_id)}/"))
    except Exception:
        return None


def part_colors(part_num):
    d = rb(f"lego/parts/{urllib.parse.quote(part_num)}/colors/?page_size=500")
    return [{"color_id": c["color_id"], "color_name": c["color_name"], "num_sets": c.get("num_sets"),
             "image": c.get("part_img_url"), "elements": c.get("elements") or []} for c in d.get("results", [])]


def all_colors():
    d = rb("lego/colors/?page_size=500")
    return {str(c["id"]): {"name": c["name"], "rgb": c["rgb"], "trans": c["is_trans"]} for c in d.get("results", [])}


def set_parts(set_num):
    out, url = [], f"lego/sets/{urllib.parse.quote(set_num)}/parts/?page_size=1000&inc_minifig_parts=1"
    while url:
        d = rb(url)
        for r in d.get("results", []):
            out.append({"part_num": r["part"]["part_num"], "color_id": r["color"]["id"],
                        "quantity": r["quantity"], "element_id": r.get("element_id"), "spare": r.get("is_spare")})
        nxt = d.get("next")
        url = nxt.split("/api/v3/", 1)[1] if nxt else None
    return out


def submodel_image(set_num, k):
    """Photo Rebrickable du k-ième sous-modèle d'un set (CDN public), ou None si elle n'existe pas."""
    url = f"https://cdn.rebrickable.com/media/thumbs/sets/{set_num}-s{k}.jpg/1000x800p.jpg"
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Briquotheque/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return url if r.status == 200 and "image" in (r.headers.get("Content-Type") or "") else None
    except Exception:
        return None


def set_inventory(set_num):
    """Pièces d'un set (hors figurines et pièces de rechange) avec nom, couleur, n° d'élément et photo."""
    out, url = [], f"lego/sets/{urllib.parse.quote(set_num)}/parts/?page_size=1000&inc_minifig_parts=0"
    while url:
        d = rb(url)
        for r in d.get("results", []):
            if r.get("is_spare"):
                continue
            p, c = r["part"], r["color"]
            el = r.get("element_id")
            out.append({
                "part_num": p["part_num"], "name": p.get("name"), "color_id": c["id"], "color_name": c.get("name"),
                "rgb": c.get("rgb"), "trans": c.get("is_trans"), "quantity": r["quantity"], "element_id": el,
                "image": (f"https://cdn.rebrickable.com/media/parts/elements/{el}.jpg" if el else None) or p.get("part_img_url"),
                "part_image": p.get("part_img_url"),
                "bricklink": ((p.get("external_ids") or {}).get("BrickLink") or [p["part_num"]])[0],
            })
        nxt = d.get("next")
        url = nxt.split("/api/v3/", 1)[1] if nxt else None
    return out


# ---------------------------------------------------------------- recherche en français
FR_EN = {
    "faucon": "falcon", "millenium": "millennium", "château": "castle", "chateau": "castle", "vaisseau": "ship",
    "navette": "shuttle", "chasseur": "fighter", "croiseur": "cruiser", "destroyer": "destroyer", "étoile": "star",
    "etoile": "star", "noire": "death", "mort": "death", "bateau": "ship", "pirate": "pirate", "pirates": "pirates",
    "voiture": "car", "camion": "truck", "train": "train", "gare": "station", "maison": "house", "ville": "city",
    "rue": "street", "magasin": "shop", "boutique": "shop", "café": "cafe", "cafe": "cafe", "musée": "museum",
    "musee": "museum", "jardin": "garden", "fleurs": "flowers", "fleur": "flower", "bouquet": "bouquet",
    "arbre": "tree", "bonsaï": "bonsai", "bonsai": "bonsai", "orchidée": "orchid", "orchidee": "orchid",
    "dragon": "dragon", "chevalier": "knight", "chevaliers": "knights", "sorcier": "wizard", "école": "school",
    "ecole": "school", "poudlard": "hogwarts", "pompiers": "fire", "pompier": "fire", "caserne": "station",
    "police": "police", "commissariat": "police station", "hôpital": "hospital", "hopital": "hospital",
    "avion": "plane", "hélicoptère": "helicopter", "helicoptere": "helicopter", "fusée": "rocket", "fusee": "rocket",
    "espace": "space", "station": "station", "base": "base", "robot": "robot", "moto": "motorcycle", "tour": "tower",
    "pont": "bridge", "phare": "lighthouse", "temple": "temple", "forêt": "forest", "foret": "forest",
    "montagne": "mountain", "île": "island", "ile": "island", "plage": "beach", "parc": "park", "manège": "carousel",
    "grande roue": "ferris wheel", "attraction": "ride", "batmobile": "batmobile", "chauve-souris": "bat",
    "araignée": "spider", "araignee": "spider", "homme": "man", "dark vador": "darth vader", "vador": "vader",
    "étoile de la mort": "death star", "etoile de la mort": "death star", "faucon millenium": "millennium falcon",
    "x-wing": "x-wing", "chasseur tie": "tie fighter", "clone": "clone", "soldat": "trooper", "soldats": "troopers",
    "char": "tank", "tank": "tank", "canon": "cannon", "marcheur": "walker", "quadripode": "at-at", "casque": "helmet",
    "figurine": "minifigure", "figurines": "minifigures", "personnage": "minifigure", "ninja": "ninja",
    "tortue": "turtle", "chat": "cat", "chien": "dog", "cheval": "horse", "dinosaure": "dinosaur", "requin": "shark",
    "sous-marin": "submarine", "nature morte": "still life", "tableau": "art", "mosaïque": "mosaic", "mosaique": "mosaic",
    "rouge": "red", "bleu": "blue", "vert": "green", "jaune": "yellow", "noir": "black", "blanc": "white",
    "doré": "gold", "dore": "gold", "géant": "giant", "geant": "giant", "petit": "small", "grand": "large",
}


def translate_fr(q):
    """Traduction mot à mot des termes LEGO courants (les catalogues sont en anglais)."""
    t = " " + q.lower().strip() + " "
    for fr in sorted(FR_EN, key=len, reverse=True):
        t = re.sub(r"(?<![\w-])" + re.escape(fr) + r"(?![\w-])", FR_EN[fr], t)
    t = re.sub(r"\b(le|la|les|de|du|des|d|l|un|une|et|à|a|en|au|aux)\b'?", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------- prix estimatif d'une pièce (BrickOwl)
EU = {"France", "Germany", "Belgium", "Netherlands", "Italy", "Spain", "Portugal", "Austria", "Czech Republic",
      "Poland", "Slovakia", "Slovenia", "Hungary", "Denmark", "Sweden", "Finland", "Ireland", "Luxembourg", "Greece",
      "Croatia", "Romania", "Bulgaria", "Estonia", "Latvia", "Lithuania", "Malta", "Cyprus"}


def _get_en(url, timeout=30):
    """Page BrickOwl en anglais (prix « €0.01 », pays en anglais)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def _cell_price(cell):
    t = html.unescape(re.sub(r"<[^>]+>", "", cell)).replace("\xa0", "").replace("€", "").replace(" ", "").strip()
    if t.count(",") == 1 and "." not in t:
        t = t.replace(",", ".")
    t = t.replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None


def part_price(element_id="", part_num="", color_name=""):
    """Prix unitaire estimé pour un acheteur en France : médiane des offres BrickOwl de vendeurs français
    (au moins 3), sinon de l'Union européenne. Hors frais de port."""
    q = element_id or f"{part_num} {color_name}".strip()
    page = _get_en("https://www.brickowl.com/search/catalog?query=" + urllib.parse.quote(q))
    links = re.findall(r'href="(/catalog/lego-[^"]+)"', page)
    if not element_id:   # sans n° d'élément : la page dont l'adresse contient la référence de la pièce
        links = [l for l in links if l.endswith("-" + part_num.lower()) or ("-" + part_num.lower() + "-") in l]
    if not links:
        return None
    return _brickowl_offers("https://www.brickowl.com" + links[0])


def zone_pick(offers):
    """[(prix, pays)] → (prix triés de la zone retenue, zone) : la France s'il y a une annonce en France, sinon l'UE, sinon le monde."""
    fr = sorted(p for p, c in offers if c == "France")
    eu = sorted(p for p, c in offers if c in EU)
    return (fr, "France") if fr else (eu, "UE") if eu else (sorted(p for p, _ in offers), "monde")


def price_stats(offers):
    """Statistiques d'annonces [(prix, pays)] : {unit (médiane), min, max, avg, offers, zone} ; prix aberrants (> 3 × la médiane) écartés."""
    pool, zone = zone_pick(offers)
    if not pool:
        return None
    mid = pool[len(pool) // 2]
    pool = [p for p in pool if p <= mid * 3] or pool
    med = pool[len(pool) // 2] if len(pool) % 2 else (pool[len(pool) // 2 - 1] + pool[len(pool) // 2]) / 2
    return {"unit": round(med, 2), "min": round(pool[0], 2), "max": round(pool[-1], 2), "avg": round(sum(pool) / len(pool), 2),
            "offers": len(pool), "zone": zone}


def _bo_rows(p):
    """Annonces d'une page BrickOwl : [(état, prix, pays)]."""
    body = p.split("buy-table", 1)[-1]
    out = []
    for row in re.findall(r'<tr class="(?:odd|even)">(.*?)</tr>', body, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        country = re.search(r'class="flag[^"]*"[^>]*alt="([^"]+)"', row)
        if len(cells) >= 5:
            cond = html.unescape(re.sub(r"<[^>]+>", " ", cells[1])).strip().lower()
            price = _cell_price(cells[4])
            if price:
                out.append((cond, price, country.group(1) if country else ""))
    return out


def set_market(number):
    """Annonces BrickOwl d'un set (n° LEGO, ex. 77256-1) : {"new": stats, "used": stats, "url"} ou None (introuvable)."""
    base = re.sub(r"-\d+$", "", number)
    page = _get_en("https://www.brickowl.com/search/catalog?query=" + urllib.parse.quote(base))
    links = [l for l in dict.fromkeys(re.findall(r'href="(/catalog/lego-[^"]+)"', page)) if re.search(r"-set-" + re.escape(base) + r"(?:-\d+)?$", l)]
    for l in links[:2]:
        url = "https://www.brickowl.com" + l
        rows = _bo_rows(_get_en(url))
        return {"new": price_stats([(p, c) for cond, p, c in rows if cond.startswith("new")]),
                "used": price_stats([(p, c) for cond, p, c in rows if cond.startswith("used")]), "url": url, "t": int(time.time())}
    return None


def fig_used_price(fid):
    """Prix d'occasion relevé d'une minifig (réf. BrickLink, ex. sw0002) : médiane des offres « Used » BrickOwl,
    vendeurs français (au moins 3), sinon UE, sinon monde. None si aucune offre d'occasion."""
    page = _get_en("https://www.brickowl.com/search/catalog?query=" + urllib.parse.quote(fid))
    links = [l for l in dict.fromkeys(re.findall(r'href="(/catalog/lego-[^"]+)"', page))
             if "-set-" not in l and not l.endswith("-instructions")]
    for l in links[:3]:
        url = "https://www.brickowl.com" + l
        p = _get_en(url)
        if not re.search(r"(?<![\w-])" + re.escape(fid) + r"(?![\w-])", p, re.I):   # bonne minifig ?
            continue
        body = p.split("buy-table", 1)[-1]
        offers = []
        for row in re.findall(r'<tr class="(?:odd|even)">(.*?)</tr>', body, re.S):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
            country = re.search(r'class="flag[^"]*"[^>]*alt="([^"]+)"', row)
            cond = html.unescape(re.sub(r"<[^>]+>", " ", cells[1])).strip() if len(cells) > 1 else ""
            if len(cells) >= 5 and cond.lower().startswith("used"):
                price = _cell_price(cells[4])
                if price:
                    offers.append((price, country.group(1) if country else ""))
        fr = sorted(x for x, c in offers if c == "France")
        pool, zone = zone_pick(offers)   # France s'il y a une annonce, sinon UE, sinon monde
        new = price_stats([(pr, c) for cond, pr, c in _bo_rows(p) if cond.startswith("new")])
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", p, re.S)
        name = re.sub(r"^LEGO\s+|\s+Minifigure$", "", html.unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip()) if h1 else ""
        if not pool:
            return {"unit": None, "offers": 0, "url": url, "name": name, **({"new": new} if new else {})}
        med = pool[len(pool) // 2] if len(pool) % 2 else (pool[len(pool) // 2 - 1] + pool[len(pool) // 2]) / 2
        return {"unit": round(med, 2), "offers": len(pool), "zone": zone, "url": url, "name": name,
                "min": round(pool[0], 2), "max": round(pool[-1], 2), "avg": round(sum(pool) / len(pool), 2), "fr": len(fr), **({"new": new} if new else {})}
    return None


def moc_part_price(part_num, color_name):
    """Prix d'une pièce dans une couleur précise (nom BrickOwl) : la page « lego-<couleur>-…-<réf> ».
    Pièces de minifig : BrickOwl range « 3626c » sous « 3626 », « 970c00 » sous les jambes génériques…"""
    slug = re.sub(r"[^a-z0-9]+", "-", color_name.lower()).strip("-")
    pn = part_num.lower()
    base = re.match(r"\d+", pn).group(0) if re.match(r"\d+", pn) else pn
    printed = bool(re.search(r"(pb|pr|pat)\d", pn))
    for q in dict.fromkeys([pn, base]):
        page = _get_en("https://www.brickowl.com/search/catalog?query=" + urllib.parse.quote(f"{color_name} {q}"))
        links = [l for l in dict.fromkeys(re.findall(r'href="(/catalog/lego-[^"]+)"', page))
                 if l.startswith(f"/catalog/lego-{slug}-") and "-set-" not in l and not l.endswith("-instructions")]
        if not printed:   # pièce unie : pas les versions décorées
            links = [l for l in links if "decoration" not in l and "-with-" not in l] or links
        tok = lambda l: l.rsplit("/", 1)[-1].split("-")
        if printed and q == pn:   # pièce tampographiée : sa page BrickOwl n'a pas de couleur dans l'adresse
            deco = [l for l in dict.fromkeys(re.findall(r'href="(/catalog/lego-[^"]+)"', page))
                    if "-set-" not in l and not l.endswith("-instructions") and base in tok(l)]   # recherche par référence exacte : 1er résultat de cette pièce
            if deco:
                return _brickowl_offers("https://www.brickowl.com" + deco[0])
            return None   # introuvable : jamais le prix de la pièce unie pour une pièce imprimée
        hit = next((l for l in links if pn in tok(l)), None) or next((l for l in links if base in tok(l)), None) \
            or (links[0] if links else None)
        if hit:
            return _brickowl_offers("https://www.brickowl.com" + hit)
    return None


def set_extra_price(number, what):
    """Prix BrickOwl des plans seuls (what="instructions") ou de la boîte vide (what="packaging") d'un set.
    {"unit": None} si BrickOwl ne la référence pas."""
    m = re.fullmatch(r"(\w+?)-(\d+)", number or "")
    if not m:
        return {"unit": None}
    base, v = m.group(1).lower(), m.group(2)
    ends = [f"-set-{base}-{v}-{what}"] + ([f"-set-{base}-{what}"] if v == "1" else [])
    page = _get_en("https://www.brickowl.com/search/catalog?query=" + urllib.parse.quote(f"{base} {what}"))
    links = [l for l in dict.fromkeys(re.findall(r'href="(/catalog/lego-[^"]+)"', page)) if any(l.endswith(e) for e in ends)]
    if not links:
        return {"unit": None}
    return _brickowl_offers("https://www.brickowl.com" + links[0])


def _brickowl_offers(url):
    page = _get_en(url)
    body = page.split('buy-table', 1)[-1]
    offers = []
    for row in re.findall(r'<tr class="(?:odd|even)">(.*?)</tr>', body, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        country = re.search(r'class="flag[^"]*"[^>]*alt="([^"]+)"', row)
        if len(cells) >= 5 and country:
            price = _cell_price(cells[4])   # colonne « Price » (hors port)
            if price:
                offers.append((price, country.group(1)))
    pool, zone = zone_pick(offers)   # la France s'il y a une annonce, sinon l'UE, sinon le monde
    if not pool:
        return {"unit": None, "url": url, "offers": 0, "zone": None}
    mid = pool[len(pool) // 2]
    pool = [p for p in pool if p <= mid * 3] or pool   # prix aberrants (plus du triple de l'offre médiane) écartés
    med = pool[len(pool) // 2] if len(pool) % 2 else (pool[len(pool) // 2 - 1] + pool[len(pool) // 2]) / 2
    return {"unit": round(med, 3), "url": url, "offers": len(pool), "zone": zone}


# ---------------------------------------------------------------- BrickLink (API officielle, OAuth 1.0a) : guide des prix
BL_API = "https://api.bricklink.com/api/store/v1"
BL_KEYS = ("consumer_key", "consumer_secret", "token", "token_secret")
bl_hooks = {"before": None, "ok": None, "error": None}


def bricklink_keys():
    """Les 4 codes de l'API BrickLink (Réglages), ou None."""
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            k = json.load(f).get("bricklink") or {}
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return k if all(k.get(x) for x in BL_KEYS) else None


BL_FIG_PREFIX = {"adp": "bdp"}   # préfixe du catalogue des cotes → préfixe BrickLink (figurines du BrickLink Designer Program : adp107 = bdp107)


def bl_fig_no(no):
    """Référence d'une figurine chez BrickLink quand son préfixe n'est pas celui du catalogue des cotes (« adp107 » → « bdp107 ») ; sinon la même."""
    m = re.fullmatch(r"([a-z]+)(\d+[a-z]?)", str(no or ""), re.I)
    return BL_FIG_PREFIX[m.group(1).lower()] + m.group(2) if m and m.group(1).lower() in BL_FIG_PREFIX else no


def _bl_q(s):
    return urllib.parse.quote(str(s), safe="~-._")


def bl_get(path, params=None, keys=None, timeout=20):
    """GET signé sur l'API BrickLink ; rend « data » (ou lève une erreur avec le message de BrickLink)."""
    import base64, hashlib, hmac, secrets as _s
    keys = keys or bricklink_keys()
    if not keys:
        raise PermissionError("Codes BrickLink absents")
    if bl_hooks.get("before"):
        bl_hooks["before"]()   # quota du jour (le serveur lève une erreur au-delà)
    path = re.sub(r"^/items/MINIFIG/([^/?]+)", lambda m: "/items/MINIFIG/" + urllib.parse.quote(str(bl_fig_no(urllib.parse.unquote(m.group(1))))), path)   # (figurine : sa référence BrickLink)
    url = BL_API + path
    params = {k: str(v) for k, v in (params or {}).items() if v not in (None, "")}
    oauth = {"oauth_consumer_key": keys["consumer_key"], "oauth_token": keys["token"], "oauth_signature_method": "HMAC-SHA1",
             "oauth_timestamp": str(int(time.time())), "oauth_nonce": _s.token_hex(12), "oauth_version": "1.0"}
    allp = sorted({**params, **oauth}.items())
    base = "&".join(["GET", _bl_q(url), _bl_q("&".join(f"{_bl_q(k)}={_bl_q(v)}" for k, v in allp))])
    key = f"{_bl_q(keys['consumer_secret'])}&{_bl_q(keys['token_secret'])}"
    oauth["oauth_signature"] = base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    mode = keys.get("mode") or "header"
    if mode == "query":   # paramètres OAuth dans l'adresse (« Authorization » = JSON)
        full = url + "?" + urllib.parse.urlencode({**params, "Authorization": json.dumps(oauth, separators=(",", ":"))})
        req = urllib.request.Request(full, headers={"User-Agent": UA, "Accept": "application/json"})
    else:
        head = 'OAuth realm="", ' + ", ".join(f'{k}="{_bl_q(v)}"' for k, v in sorted(oauth.items()))
        full = url + ("?" + urllib.parse.urlencode(params) if params else "")
        req = urllib.request.Request(full, headers={"Authorization": head, "User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:   # refus avec un message de BrickLink
        try:
            d = json.loads(e.read().decode("utf-8"))
        except Exception:
            raise e
    meta = d.get("meta") or {}
    if meta.get("code") not in (200, None):
        msg = f"BrickLink : {meta.get('message') or ''} {meta.get('description') or ''}".strip()
        if bl_hooks.get("error"):
            bl_hooks["error"](msg)
        raise RuntimeError(msg)
    if bl_hooks.get("ok"):
        bl_hooks["ok"]()
    return d.get("data")


BL_MIN_SALES = 3   # ventes (ou annonces) qu'il faut dans une zone pour s'y fier (sinon : zone plus large) — par défaut (réglable)
BL_REGIONS = ("europe", "eu", "north_america", "south_america", "asia", "middle_east", "africa", "oceania")   # régions de l'API BrickLink
BL_ZONES_DEFAULT = [{"c": "FR"}, {"r": "europe"}, {"w": 1}]


def bl_zone_label(z):
    """Libellé d'une zone dans les relevés : « France », « UE », « monde » (compatibles avec l'existant), sinon le code du pays
    (« BE ») ou le nom de la région BrickLink (« north_america »)."""
    if z.get("c"):
        return "France" if z["c"] == "FR" else z["c"]
    if z.get("r"):
        return "UE" if z["r"] == "europe" else z["r"]
    return "monde"


def bl_zone_cfg():
    """Réglages › Prix : {"zones": [{"c": "FR"} | {"r": "europe"} | {"w": 1}, …] dans l'ordre, "min": ventes/annonces minimum}."""
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            st = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        st = {}
    zones = [z for z in (st.get("bl_zones") or []) if isinstance(z, dict) and (
        (isinstance(z.get("c"), str) and len(z["c"]) == 2 and z["c"].isalpha()) or z.get("r") in BL_REGIONS or z.get("w"))] or BL_ZONES_DEFAULT
    try:
        mn = max(1, min(50, int(st.get("bl_min") or BL_MIN_SALES)))
    except (TypeError, ValueError):
        mn = BL_MIN_SALES
    return {"zones": zones, "min": mn}


def bl_zone_order():
    """Libellés des zones, dans l'ordre réglé (la première d'abord)."""
    return [bl_zone_label(z) for z in bl_zone_cfg()["zones"]]


def _bl_zone_price(itype, no, cond, guide, color_id=None, keys=None):
    """Guide des prix BrickLink pour un état (N / U) : les zones réglées l'une après l'autre (par défaut France, Europe, monde) — la
    première qui a au moins « min » ventes (guide « sold ») ou annonces (« stock ») ; aucune n'en a assez : la plus fournie. None : rien nulle part."""
    best, cfg = None, bl_zone_cfg()
    for z in cfg["zones"]:
        zone, extra = bl_zone_label(z), ({"country_code": z["c"].upper()} if z.get("c") else {"region": z["r"]} if z.get("r") else {})
        d = bl_get(f"/items/{itype}/{urllib.parse.quote(no)}/price",
                   {"guide_type": guide, "new_or_used": cond, "currency_code": "EUR", "vat": "Y", "color_id": color_id, **extra}, keys=keys) or {}
        n = int(d.get("unit_quantity") or 0)   # ventes : nombre de ventes (lots) ; annonces : nombre d'annonces
        if not n:
            continue
        unit = float(d.get("qty_avg_price") or 0) or float(d.get("avg_price") or 0)   # « Qty Avg Price » de BrickLink : prix moyen payé par exemplaire
        rec = {"unit": round(unit, 2), "min": round(float(d.get("min_price") or 0), 2), "max": round(float(d.get("max_price") or 0), 2),
               "avg": round(float(d.get("avg_price") or 0), 2), "offers": n, "qty": int(d.get("total_quantity") or 0), "zone": zone,
               "src": "BrickLink", "kind": "ventes" if guide == "sold" else "annonces", **({"sold": True} if guide == "sold" else {})}
        if n >= cfg["min"]:
            return rec
        if not best or n > best["offers"]:
            best = {**rec, "few": True}   # pas assez ici : zone plus large (on garde la plus fournie, marquée « few » : trop mince pour s'y fier)
    return best


def bl_guide(itype, no, cond, color_id=None, keys=None):
    """Prix de référence d'un état (N / U) : la moyenne des VENTES RÉELLES des 6 derniers mois sur BrickLink (« Qty Avg Price »),
    France puis Europe puis monde s'il manque de ventes ; aucune vente nulle part : les annonces en cours (kind « annonces »).
    Rend {unit, min, max, avg, offers, qty, zone, src, kind, sold} ou None."""
    return _bl_zone_price(itype, no, cond, "sold", color_id, keys) or _bl_zone_price(itype, no, cond, "stock", color_id, keys)


# ---------------------------------------------------------------- Instagram (API officielle « Instagram API with Instagram Login »)
# Aucune page Instagram n'est aspirée : seulement l'API officielle, avec le jeton d'accès fourni par le propriétaire du compte.
FB_API = "https://graph.facebook.com/v21.0"   # jetons « EAA… » : API Instagram avec connexion Facebook (compte relié à une Page)




















def fetch_bytes(url, timeout=30):
    """Télécharge une image (photos d'Instagram : adresses signées, temporaires)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

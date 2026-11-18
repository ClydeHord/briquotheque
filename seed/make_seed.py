#!/usr/bin/env python3
"""Fabrique les données d'exemple livrées avec Briquothèque (dossier seed/), à partir de la collection du propriétaire.

Usage (sur l'installation du propriétaire) : python3 seed/make_seed.py
Une nouvelle installation copie seed/ dans data/ au premier lancement (server.py : install_seed) : chaque type de fiche
y a un exemple, marqué « Fiche de démo » (champ "sample"), ainsi qu'un inventaire.

Ce qui est copié : les fiches choisies (sans notes, prix d'achat, tâches), l'inventaire choisi, et SEULEMENT les entrées
des caches qui les concernent (noms, images, prix, pièces) — pour que les exemples s'affichent même sans clé API.
Les photos du propriétaire reçoivent un filigrane « Clýde Hørd » bien visible et des métadonnées (auteur, droits, source).
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "seed")
AUTHOR = "Clýde Hørd"
SOURCE = "Briquothèque — https://github.com/ClydeHord/briquotheque"

# un exemple de chaque type de fiche (identifiants dans la collection du propriétaire)
SAMPLES = {
    "16bc4e6d323d": "set complet",
    "d7b94c892d05": "set complet avec des pièces ajoutées",
    "a00969b7593c": "set avec une figurine modifiée (et des pièces remplacées)",
    "ab35f18bb281": "set avec des figurines ajoutées",
    "0e6f79de0f55": "set partiel",
    "a1846753f0fa": "MOC",
    "8ad9728324cb": "figurine MOC",   # le Slayer (choix du propriétaire)
    "b644c230ac81": "figurine non modifiée",
    "dcdc497cb18e": "figurine modifiée",
}
TODO_SAMPLE = "16bc4e6d323d"   # le set d'exemple qui porte une tâche « À faire »
INVENTORIES = ["set-77241-1"]   # Honda S2000, tel quel
LIST_ID = "exemples"


def load(name, default):
    try:
        return json.load(open(os.path.join(DATA, name), encoding="utf-8"))
    except (OSError, ValueError):
        return default


def sign(path, watermark):
    """Métadonnées (auteur, droits, source) et, pour une photo du propriétaire, filigrane « Clýde Hørd » bien visible, en travers au centre."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(path)
    fmt = im.format
    if watermark:
        import math
        im = im.convert("RGBA")
        w, h = im.size
        angle = math.degrees(math.atan2(h, w))   # en travers : le long de la diagonale (bas gauche → haut droit)
        diag = math.hypot(w, h)
        size = max(16, int(diag / 7))   # grand : en travers de toute la photo
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except OSError:
            font = ImageFont.load_default()
        probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        box = probe.textbbox((0, 0), AUTHOR, font=font, stroke_width=max(2, size // 10))
        tw, th = box[2] - box[0], box[3] - box[1]
        text = Image.new("RGBA", (tw + 8, th + 8), (0, 0, 0, 0))   # le texte seul, puis tourné et posé au centre
        ImageDraw.Draw(text).text((4 - box[0], 4 - box[1]), AUTHOR, font=font, fill=(255, 255, 255, 175),
                                  stroke_width=max(2, size // 10), stroke_fill=(0, 0, 0, 160))   # très visible (demande du propriétaire)
        text = text.rotate(angle, expand=True, resample=Image.BICUBIC)
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        layer.paste(text, ((w - text.width) // 2, (h - text.height) // 2), text)
        im = Image.alpha_composite(im, layer)
        im = im.convert("RGB") if fmt == "JPEG" else im
    if fmt == "PNG":
        from PIL.PngImagePlugin import PngInfo
        meta = PngInfo()
        for k, v in (("Author", AUTHOR), ("Copyright", f"© 2026 {AUTHOR} — tous droits réservés"), ("Source", SOURCE)):
            meta.add_text(k, v)
        im.save(path, "PNG", pnginfo=meta)
    else:
        exif = im.getexif()
        ascii_ = lambda t: t.replace("ý", "y").replace("ø", "o").replace("è", "e").replace("é", "e").replace("—", "-").replace("©", "(c)")
        exif[0x013B] = ascii_(AUTHOR)                                        # Artist (EXIF : ASCII seulement)
        exif[0x8298] = ascii_(f"© 2026 {AUTHOR} - tous droits réservés")    # Copyright
        exif[0x010E] = ascii_(SOURCE)                                        # ImageDescription
        exif[0x9C9D] = (AUTHOR + "\0").encode("utf-16-le")                   # XPAuthor (Windows, avec les accents)
        exif[0x9C9C] = (f"© 2026 {AUTHOR} — tous droits réservés — {SOURCE}\0").encode("utf-16-le")   # XPComment
        im.convert("RGB").save(path, "JPEG", quality=88, exif=exif)


def main():
    db = load("collection.json", {})
    ids = {i["id"]: i for i in db.get("items", [])}
    missing = [k for k in SAMPLES if k not in ids]
    if missing:
        sys.exit(f"Fiches introuvables : {missing}")
    chosen = list(SAMPLES) + [i["id"] for i in db["items"] if i.get("attached_to") in SAMPLES]   # + figurines rattachées
    items = []
    for iid in chosen:
        x = json.loads(json.dumps(ids[iid]))
        x.update(list_id=LIST_ID, notes="", purchase_price=None, todo=False, todo_note="", todos=[], gift_note="", sample=True)
        if iid == TODO_SAMPLE:   # un exemple de tâche « À faire »
            x.update(todos=[{"cat": "Photo", "note": "Refaire la photo du set monté"}], todo=True, todo_note="Refaire la photo du set monté")
        items.append(x)
    invs = {k: {**db["inventories"][k], "sample": True} for k in INVENTORIES if k in (db.get("inventories") or {})}
    lists = [{"id": LIST_ID, "name": "Exemples", "kind": "collection", "created_at": 0}]
    shutil.rmtree(OUT + "/data", ignore_errors=True)
    os.makedirs(os.path.join(OUT, "data", "uploads"))
    json.dump({"lists": lists, "items": items, "inventories": invs}, open(os.path.join(OUT, "data", "collection.json"), "w", encoding="utf-8"), ensure_ascii=False)

    # --- jetons : numéros des sets et figurines, pièces concernées
    sets = {i["number"] for i in items if i.get("kind", "set") in ("set", "custom") and i["number"] not in ("custom", "")}
    sets |= {re.sub(r"^set-", "", k) for k in invs}
    cache = load("cache_sets.json", {})
    figs = {i["number"] for i in items if i.get("kind") == "fig"}
    for n in list(sets):
        figs |= {f.get("id") for f in (cache.get(n) or {}).get("minifigs") or [] if f.get("id")}
    for i in items:
        figs |= set((i.get("fig_mods") or {}).keys()) | {m.get("rb_fig") for m in (i.get("fig_mods") or {}).values() if isinstance(m, dict) and m.get("rb_fig")}
        if i.get("rb_fig"):
            figs.add(i["rb_fig"])
    pc = load("cache_parts.json", {})
    parts = set()
    for n in sets:
        for r in pc.get("inv:" + n) or []:
            parts |= {r.get("part_num"), r.get("bricklink")}
    for i in items:
        for l in i.get("moc_parts") or []:
            parts |= {l.get("part"), l.get("part_num")}
        blob = json.dumps([i.get("set_mod"), i.get("fig_mods"), i.get("fig_swaps"), i.get("accessories")])
        parts |= set(re.findall(r'"part(?:_num)?": "([^"]+)"', blob))
    for f in figs:
        for r in pc.get("fp:" + str(f)) or []:
            if isinstance(r, dict):
                parts |= {r.get("part_num"), r.get("part")}
    tokens = {t for t in sets | {s.replace("-1", "") for s in sets} | figs | parts if t}
    fig_names = {(cache.get("fig:" + f) or {}).get("name") for f in figs} | {f.get("name") for n in sets for f in (cache.get(n) or {}).get("minifigs") or []}

    def keep(key):
        comps = re.split(r"[:|]", key)
        return any(c in tokens for c in comps) or (key.startswith("fig:") and key[4:] in fig_names)

    stats = {}
    for name in sorted(os.listdir(DATA)):
        if not (name.startswith("cache_") and name.endswith(".json")) or name in ("cache_novelties.json", "cache_upload_orphans.json", "cache_ean.json"):
            continue
        d = load(name, None)
        if not isinstance(d, dict):
            continue
        if name == "cache_hd.json":
            sub = {k: v for k, v in d.items() if any(t in k for t in sets | figs)}
        else:
            sub = {k: v for k, v in d.items() if keep(k)}
        json.dump(sub, open(os.path.join(OUT, "data", name), "w", encoding="utf-8"), ensure_ascii=False)
        stats[name] = len(sub)
    shutil.copy(os.path.join(DATA, "box_codes.json"), os.path.join(OUT, "data", "box_codes.json"))
    keys = sets | {"fig:" + f for f in figs} | {i["id"] for i in items}
    h = load("history.json", {})
    json.dump({"items": {k: v for k, v in (h.get("items") or {}).items() if k in keys}}, open(os.path.join(OUT, "data", "history.json"), "w"))
    rv = load("moc_review.json", {})
    json.dump({k: v for k, v in rv.items() if k in keys}, open(os.path.join(OUT, "data", "moc_review.json"), "w"))

    # --- photos du propriétaire : copiées, signées, filigranées
    n = 0
    for hx in set(re.findall(r"/api/upload/([0-9a-f]{16,40})", json.dumps([items, invs]))):
        for name in os.listdir(os.path.join(DATA, "uploads")):
            if name.startswith(hx):
                dst = os.path.join(OUT, "data", "uploads", name)
                shutil.copy(os.path.join(DATA, "uploads", name), dst)
                sign(dst, watermark=False)   # métadonnées (auteur, droits) seulement : plus de filigrane (demande du 15/11)
                n += 1
    # --- images du catalogue des exemples (copiées du cache) : visibles même sans clé API ni accès aux sites d'images
    import hashlib
    blob = json.dumps([items, {k: cache.get(k) for k in list(sets) + ["fig:" + f for f in figs]}, {k: pc.get(k) for k in ["inv:" + n for n in sets]}])
    urls = set(re.findall(r'"(https://[^"]+\.(?:jpg|jpeg|png|webp)(?:/\d+x\d+p?\.jpg)?)"', blob))
    hd = load("cache_hd.json", {})
    urls |= {v for u in list(urls) for v in ([hd.get(u)] if isinstance(hd.get(u), str) else []) if v}
    os.makedirs(os.path.join(OUT, "data", "images"), exist_ok=True)
    ni = 0
    for u in urls:
        h = hashlib.sha1(u.encode()).hexdigest()
        src = os.path.join(DATA, "images", h)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, "data", "images", h))
            if os.path.exists(src + ".type"):
                shutil.copy(src + ".type", os.path.join(OUT, "data", "images", h + ".type"))
            ni += 1
    print(f"Images du catalogue : {ni} / {len(urls)} copiées")
    print(f"Exemples : {len(items)} fiches ({len(SAMPLES)} types + figurines rattachées), {len(invs)} inventaire(s), {n} photos signées")
    print("Caches filtrés :", ", ".join(f"{k} {v}" for k, v in stats.items()))


if __name__ == "__main__":
    main()

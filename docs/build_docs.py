#!/usr/bin/env python3
# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Écrit les guides de Briquothèque sous forme de wikis (une page par chapitre, sommaire, recherche) : docs/wiki/*.html.

Usage :
    python3 docs/build_docs.py                 # refait les wikis
    python3 docs/build_docs.py --captures      # reprend d'abord les captures d'écran dans la DÉMO (node docs/captures.js)
    python3 docs/build_docs.py --captures-bo   # reprend d'abord les captures de la notice du back office (node docs/captures_bo.js : instance temporaire)

Servis par l'application : /guide-utilisateur (contenu : guide_content.py), /backoffice/guide (backoffice_content.py) et, s'il est
installé, /guide-technique (privé). Le moteur du wiki est dans wiki.py. Plus aucun PDF : imprimer une page de wiki imprime le guide entier.
Besoins : Python 3 (standard) ; Node 20 et Chromium seulement pour reprendre les captures.
"""
import html
import json
import os
import re
import subprocess
import sys
import time

DOCS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DOCS)
BUILD = os.path.join(DOCS, "build")
CAPS = os.path.join(DOCS, "captures")
e = html.escape


# ============================================================ page HTML commune (feuille de style d'impression)
def page(title, body, guide=False):
    css = """
@page { size: A4; margin: 14mm 13mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "DejaVu Sans", Arial, sans-serif; color: #1d2230; font-size: 10.5pt; line-height: 1.45; margin: 0; }
h1 { font-size: 30pt; margin: 8px 0 0; } h2 { font-size: 15pt; color: #b3191f; border-bottom: 2px solid #e8c9ca; padding-bottom: 3px; margin: 22px 0 8px; break-after: avoid; }
h3 { font-size: 12pt; margin: 14px 0 4px; break-after: avoid; } h4 { font-size: 10.5pt; margin: 12px 0 4px; color: #4a6fa5; break-after: avoid; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.6pt; background: #f2f3f6; padding: 0 3px; border-radius: 3px; }
table { width: 100%; border-collapse: collapse; margin: 6px 0 10px; font-size: 9pt; }
th, td { border-bottom: 1px solid #e3e5ea; padding: 3px 5px; text-align: left; vertical-align: top; }
th { background: #f6f7f9; } tr { break-inside: avoid; }
table.ref td:first-child { width: 36%; word-break: break-all; } table.ref td:nth-child(2) { width: 6%; color: #888; }
.muted { color: #999; } figure { margin: 10px 0; break-inside: avoid; } figcaption { font-size: 8.5pt; color: #666; text-align: center; }
.cover { text-align: center; padding: 90px 0 50px; break-after: page; }
.cover .brick { width: 90px; height: 54px; background: #d6181f; border-radius: 8px; margin: 0 auto 10px; position: relative; }
.cover .brick::before, .cover .brick::after { content: ""; position: absolute; top: -16px; width: 26px; height: 18px; background: #d6181f; border-radius: 5px 5px 0 0; }
.cover .brick::before { left: 12px; } .cover .brick::after { right: 12px; }
figure.annot { margin: 6px 0 4px; break-inside: avoid; } figure.annot svg { max-height: 235mm; }
table.annot-t td:first-child { width: 5%; } table.annot-t td:nth-child(2) { width: 30%; } table.annot-t code { font-size: 8.2pt; }
a { color: #1f5fbf; text-decoration: none; } a code { color: #1f5fbf; }
.toc-box { break-after: page; } .toc { list-style: none; padding: 0; columns: 2; column-gap: 18px; font-size: 9.5pt; }
.toc li.t2 { font-weight: 700; margin-top: 4px; } .toc li.t3 { padding-left: 12px; font-size: 8.8pt; } .toc li { break-inside: avoid; }
.fn { border-left: 3px solid #e3e5ea; padding: 3px 0 3px 8px; margin: 5px 0 8px; break-inside: avoid; font-size: 9pt; }
.fn-h { display: flex; justify-content: space-between; gap: 8px; align-items: baseline; }
.fn-n { font-weight: 700; background: none; padding: 0; font-size: 9pt; word-break: break-all; } .fn-l { color: #888; font-size: 8pt; white-space: nowrap; }
.fn-d { margin: 2px 0; } .fn-x { color: #444; font-size: 8.4pt; line-height: 1.5; }
table.routes td:nth-child(3), table.routes td:nth-child(4) { font-size: 8pt; width: 30%; } table.consts td:nth-child(2) code { word-break: break-all; }
p.idx { font-size: 8.4pt; line-height: 1.6; }
.cover .author { font-size: 11pt; color: #444; margin: -18px 0 22px; }
.legal h3 { font-size: 11.5pt; margin: 12px 0 3px; } .legal p { margin: 0 0 6px; }
.cover .sub { font-size: 18pt; color: #555; margin: 4px 0 30px; } .cover .meta { color: #777; font-size: 9.5pt; }
.tip { background: #fff7dc; border-left: 4px solid #e2b33c; padding: 6px 9px; border-radius: 4px; }
ol.toc { columns: 2; }
section.g { display: flex; gap: 14px; align-items: flex-start; break-inside: avoid; }
section.g { display: grid; grid-template-columns: 1fr 64mm; column-gap: 14px; }
section.g { margin: 6px 0 14px; } section.g.noimg { grid-template-columns: 1fr; }
h2.chap { break-before: page; } .gtext h3:first-child { margin-top: 0; } .gtext ol, .gtext ul { padding-left: 18px; margin: 4px 0 8px; }
figure.shot { margin: 0; } figure.shot img { width: 100%; border-radius: 10px; border: 1px solid #ccc; }
section.w { margin: 6px 0 14px; } figure.wshot { margin: 8px 0 4px; } figure.wshot img { width: 100%; border-radius: 6px; border: 1px solid #ccc; }
.go { font-size: 9pt; color: #1f5fbf; font-weight: 700; } ol.bo-toc { columns: 2; padding-left: 18px; } ol.bo-toc li { margin: 3px 0; font-weight: 700; } ol.rec li { margin: 6px 0; }
"""
    return f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{e(title)}</title><style>{css}</style></head><body>{body}</body></html>'


# ============================================================ mentions légales et anonymisation
AUTHOR = "Clýde Hørd"


def legal_html():
    """Les mentions légales de l'application (LEGAL_HTML dans static/app.js) : un seul texte pour l'appli et la doc."""
    src = open(os.path.join(ROOT, "static", "app.js"), encoding="utf-8").read()
    m = re.search(r"/\* LEGAL-DEBUT \*/`(.*?)`/\* LEGAL-FIN \*/", src, re.S)
    return m.group(1) if m else f"<p>© {time.strftime('%Y')} {AUTHOR} — tous droits réservés.</p>"


def anonymize(text):
    """Rien de personnel dans la documentation : domaine remplacé par un domaine factice, adresses IP et e-mails masqués."""
    try:   # domaines personnels à masquer : data/doc_private.json {"mask": ["mon-domaine.fr", …]} (jamais dans le dépôt)
        mask = json.load(open(os.path.join(ROOT, "data", "doc_private.json"), encoding="utf-8")).get("mask") or []
    except (OSError, ValueError):
        mask = []
    for dom in mask:
        text = re.sub(r"\b(?:[\w-]+\.)*" + re.escape(dom), "briquotheque.example.org", text, flags=re.I)
    text = re.sub(r"\b(?!127\.0\.0\.1\b)(?:\d{1,3}\.){3}\d{1,3}\b", "203.0.113.10", text)   # (adresse de documentation, RFC 5737)
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "contact@example.org", text)
    return text


# ============================================================ liens cliquables
def with_toc(body, levels=(2, 3)):
    """Ajoute une ancre à chaque titre (h2, h3) et un sommaire cliquable juste après la couverture."""
    toc, n = [], [0]
    def anchor(m):
        lvl, attrs, txt = int(m.group(1)), m.group(2) or "", m.group(3)
        if lvl not in levels or "id=" in attrs:
            return m.group(0)
        n[0] += 1
        toc.append((lvl, f"s{n[0]}", re.sub(r"<[^>]+>", "", txt)))
        return f'<h{lvl}{attrs} id="s{n[0]}">{txt}</h{lvl}>'
    body = re.sub(r"<h([23])((?: class=\"[^\"]*\")?)>(.*?)</h\1>", anchor, body, flags=re.S)
    items = "".join(f'<li class="t{l}"><a href="#{a}">{t}</a></li>' for l, a, t in toc)
    nav = f'<nav class="toc-box"><h2 class="toc-h">Sommaire</h2><ul class="toc">{items}</ul></nav>'
    i = body.find("</header>")
    return body[:i + 9] + nav + body[i + 9:] if i >= 0 else nav + body


# ============================================================ wikis (une page par chapitre : docs/wiki.py)
WIKI = os.path.join(DOCS, "wiki")


def _fig(name, cap, cls="shot"):
    if not name or not os.path.exists(os.path.join(CAPS, name + ".jpg")):
        return ""
    return f'<figure class="{cls}"><img src="../captures/{name}.jpg" alt="" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>'


def wiki_guide():
    """Guide utilisateur → /guide-utilisateur (contenu : guide_content.py)."""
    import importlib
    import guide_content
    import wiki
    importlib.reload(guide_content)
    pages, seen = [], set()
    for ch in guide_content.GUIDE:
        pid = wiki.slug(ch["title"])
        while pid in seen:
            pid += "-2"
        seen.add(pid)
        body = ch.get("intro", "") + "".join(f'<section class="w"><div class="gtext">{text}</div>{_fig(img, cap)}</section>' for img, cap, text in ch["blocks"])
        pages.append((pid, ch["title"], body))
    pages.append(("mentions-legales", "Mentions légales", f'<div class="legal">{legal_html()}</div>'))
    write_ia_pub("guide-utilisateur", "Guide utilisateur", pages, IA_HOW)
    return wiki.build("guide-utilisateur", "Guide utilisateur", pages, others=[("🤖 Condensé pour IA", "/guide-utilisateur/ia"), ("🛠 Notice du back office", "/backoffice/guide")],
                      img_to="/guide-utilisateur/img/", note="Captures prises dans la démo.")


def wiki_backoffice():
    """Notice du back office → /backoffice/guide (contenu : backoffice_content.py)."""
    import importlib
    import backoffice_content as bc
    import wiki
    importlib.reload(bc)

    def go(m):
        pid = m.group(1)
        return f'<a class="go" href="/backoffice#{pid}" target="_blank" rel="noopener">Ouvrir : {e(bc.PANELS.get(pid, pid))} ↗</a>'
    pages = []
    for ch in bc.NOTICE:
        body = ch.get("intro", "") + "".join(f'<section class="w"><div class="gtext">{text}</div>{_fig(img, cap, "wshot")}</section>' for img, cap, text in ch["blocks"])
        pages.append((ch["id"], ch["title"], re.sub(r"\[\[go:([a-z_]+)\]\]", go, body)))
    pages.append(("mentions-legales", "Mentions légales", f'<div class="legal">{legal_html()}</div>'))
    write_ia_pub("back-office", "Notice du back office", pages, IA_HOW.replace("le guide complet de Briquothèque", "la notice complète du back office de Briquothèque (les coulisses : apparence, textes, fiches, étiquettes, pages, sauvegardes… sans code)").replace("ce guide", "cette notice").replace("le guide", "la notice"))
    return wiki.build("back-office", "Notice du back office", pages, home=("← Back office", "/backoffice"),
                      others=[("🤖 Condensé pour IA", "/backoffice/guide/ia"), ("📘 Guide utilisateur", "/guide-utilisateur")], img_to="/backoffice/guide/img/", note="Captures prises sur des données d'exemple.")


def wiki_technique():
    """Documentation technique → /guide-technique (PRIVÉE : docs/technique.py n'est pas publié ; None s'il est absent)."""
    try:
        import technique
        import wiki
    except ImportError:
        return None
    full = technique.build_technique()
    body = full[full.index("<body>") + 6:full.rindex("</body>")]
    body = re.sub(r'<header class="cover">.*?</header>', "", body, count=1, flags=re.S)
    body = re.sub(r'<nav class="toc-box">.*?</nav>', "", body, count=1, flags=re.S)
    parts = re.split(r"<h2([^>]*)>(.*?)</h2>", body, flags=re.S)   # [avant, attrs, titre, contenu, attrs, titre, contenu, …]
    pages, seen = [], set()
    for k in range(1, len(parts) - 2, 3):
        attrs, title, content = parts[k], re.sub(r"<[^>]+>", "", parts[k + 1]).strip(), parts[k + 2]
        pid = wiki.slug(title)
        while pid in seen:
            pid += "-2"
        seen.add(pid)
        m = re.search(r'id="([^"]+)"', attrs)
        pages.append((pid, html.unescape(title), (f'<a id="{m.group(1)}"></a>' if m else "") + content))
    write_ia(full)   # (le condensé pour IA, à partir de la même doc)
    return wiki.build("guide-technique", "Documentation technique", pages,
                      others=[("🤖 Condensé pour IA", "/guide-technique/ia"), ("📘 Guide utilisateur", "/guide-utilisateur"), ("🛠 Notice du back office", "/backoffice/guide")],
                      img_to="/guide-technique/img/", private=True, note="Privée : réservée au propriétaire, jamais publiée.")


def html_to_md(h):
    """HTML de la doc → texte Markdown compact (titres, listes, code, tableaux) : lisible par une IA, sans mise en page."""
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S | re.I)
    h = re.sub(r"<img[^>]*>", "", h, flags=re.I)   # (captures : sans objet pour une IA)
    for n in range(1, 5):
        h = re.sub(rf"<h{n}[^>]*>(.*?)</h{n}>", lambda m, n=n: "\n\n" + "#" * (n + 1) + " " + re.sub(r"<[^>]+>", "", m.group(1)).strip() + "\n", h, flags=re.S | re.I)
    h = re.sub(r"<pre[^>]*>(.*?)</pre>", lambda m: "\n```\n" + re.sub(r"<[^>]+>", "", m.group(1)).strip() + "\n```\n", h, flags=re.S | re.I)
    h = re.sub(r"<code[^>]*>(.*?)</code>", lambda m: "`" + re.sub(r"<[^>]+>", "", m.group(1)) + "`", h, flags=re.S | re.I)
    h = re.sub(r"<(b|strong)>(.*?)</\1>", r"**\2**", h, flags=re.S | re.I)
    h = re.sub(r"<li[^>]*>", "\n- ", h, flags=re.I)
    h = re.sub(r"</t[dh]>\s*<t[dh][^>]*>", " | ", h, flags=re.I)
    h = re.sub(r"<tr[^>]*>", "\n| ", h, flags=re.I)
    h = re.sub(r"<(br|/p|/div|/ul|/ol|/table|p|div)[^>]*>", "\n", h, flags=re.I)
    h = html.unescape(re.sub(r"<[^>]+>", "", h))
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r"\n[ \t]+", "\n", h)
    return re.sub(r"\n{3,}", "\n\n", h).strip()


def write_ia_pub(name, title, pages, intro):
    """« Condensé pour IA » d'un guide public (guide utilisateur, notice du back office) : tout le guide en texte, précédé de la consigne pour l'IA."""
    out = [f"# Briquothèque — {title} (condensé pour IA)", "", f"Généré le {time.strftime('%d/%m/%Y %H:%M')}.", "", intro, ""]
    for pid, ptitle, body in pages:
        if pid == "mentions-legales":
            continue
        out += [f"## {ptitle}", "", html_to_md(body), ""]
    text = anonymize("\n".join(out))
    os.makedirs(WIKI, exist_ok=True)
    dst = os.path.join(WIKI, name + "-ia.md")
    with open(dst + ".tmp", "w", encoding="utf-8") as f:
        f.write(text + "\n")
    os.replace(dst + ".tmp", dst)
    print("condensé IA :", dst, os.path.getsize(dst) // 1024, "Ko")


IA_HOW = ("Consigne pour l'IA : ce texte est le guide complet de Briquothèque, une application web (sur téléphone et ordinateur) pour gérer "
          "une collection LEGO : sets, figurines, MOC, pièces, liste de souhaits, estimations de valeur. Quand l'utilisateur te demande comment "
          "faire quelque chose, réponds en français, simplement, en t'appuyant UNIQUEMENT sur ce guide : les étapes dans l'ordre, avec les noms "
          "exacts des boutons et des menus (et leur emoji). Si le guide ne couvre pas la demande, dis-le plutôt que d'inventer. "
          "Vocabulaire : « figurine » (jamais « minifig »).")


def write_ia(full):
    """« Condensé pour IA » (bouton de la doc technique) : les règles du projet (CLAUDE.md), la carte des fichiers et toute la doc technique,
    en un seul fichier Markdown. PRIVÉ (docs/wiki/guide-technique-ia.md, comme le wiki technique) ; rien de personnel (anonymize), clés masquées."""
    out = ["# Briquothèque — condensé pour IA", "",
           f"Généré le {time.strftime('%d/%m/%Y %H:%M')} à partir de la documentation technique. À donner en entier à une IA avant de lui demander un travail.",
           "Réponses en français, courtes ; le propriétaire valide point par point. Les règles ci-dessous priment sur tout le reste.", ""]
    try:
        out += ["## Règles du projet (CLAUDE.md)", "", open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read().split("\n", 1)[1].strip(), ""]
    except (OSError, IndexError):
        pass
    files = []
    for d in ("", "static", "docs"):
        for f in sorted(os.listdir(os.path.join(ROOT, d))):
            p = os.path.join(ROOT, d, f)
            if os.path.isfile(p) and re.search(r"\.(py|js|html|css)$", f) and not f.endswith(".tmp"):
                try:
                    n = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
                except OSError:
                    continue
                files.append(f"- `{(d + '/' if d else '') + f}` — {n} lignes")
    md = html_to_md(full[full.index("<body>") + 6:full.rindex("</body>")] if "<body>" in full else full)
    parts = re.split(r"(?m)^(?=### )", md)   # chapitres de la doc ; sans les références fonction par fonction (l'IA lit le code), ni le sommaire
    skip = re.compile(r"^### (?:\d+\. )?(Référence|Apparence|Index des fonctions|Où modifier quoi|Mentions légales|Sommaire)")
    md = "".join(x for x in parts[1:] if not skip.match(x))
    out += ["## Carte des fichiers", "", *files, "", "## Documentation technique (l'essentiel)", "",
            "(Les références détaillées — fonctions de server.py, app.js, sources.py, auth.py, repères de style.css — sont dans le wiki /guide-technique ; le code fait foi.)", "", md]
    text = anonymize("\n".join(out))
    text = re.sub(r"\b(ghp_|github_pat_|gho_)[A-Za-z0-9_]{10,}", "[jeton masqué]", text)   # (filet : aucun jeton, même cité par erreur)
    text = re.sub(r"\b[A-Fa-f0-9]{32,}\b", "[clé masquée]", text)
    os.makedirs(WIKI, exist_ok=True)
    dst = os.path.join(WIKI, "guide-technique-ia.md")
    with open(dst + ".tmp", "w", encoding="utf-8") as f:
        f.write("<!-- PRIVE-NE-JAMAIS-" + "PUBLIER : condensé de la documentation technique -->\n" + text + "\n")
    os.replace(dst + ".tmp", dst)
    print("condensé IA :", dst, os.path.getsize(dst) // 1024, "Ko")


def write_wiki(name, text):
    if not text:
        return None
    os.makedirs(WIKI, exist_ok=True)
    dst = os.path.join(WIKI, name + ".html")
    tmp = dst + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(anonymize(text))   # (filet de sécurité : rien de personnel ne sort dans la doc)
    os.replace(tmp, dst)   # remplacée d'un coup : jamais de page à moitié écrite
    print("wiki :", dst, os.path.getsize(dst) // 1024, "Ko")
    return dst


def wiki_memo(perso=False):
    """Aide-mémoire → /aide-memoire (contenu : memo_content.py) : la suite des évènements de chaque fonction (21/11).
    perso : + les fiches des fonctions exclusives (memo_perso.py, privé) → aide-memoire-perso.html, servie au propriétaire seulement."""
    import importlib
    import memo_content
    import wiki
    importlib.reload(memo_content)
    cards = list(memo_content.MEMO)
    if perso:
        try:
            import memo_perso
            importlib.reload(memo_perso)
        except ImportError:
            return None
        cards += memo_perso.MEMO
    css = ("<style>.memo-steps{counter-reset:m;list-style:none;padding:0;margin:14px 0}.memo-steps li{position:relative;padding:10px 12px 10px 46px;"
           "margin:0 0 8px;border:1px solid rgba(127,127,127,.3);border-radius:12px}.memo-steps li::before{counter-increment:m;content:counter(m);position:absolute;"
           "left:12px;top:9px;width:24px;height:24px;border-radius:50%;background:#d01012;color:#fff;font-weight:700;display:grid;place-items:center;font-size:13px}"
           ".memo-steps li:not(:last-child)::after{content:'↓';position:absolute;left:19px;bottom:-14px;opacity:.5}.memo-know{opacity:.9}"
           ".memo-steps li.done{opacity:.5}.memo-steps li.done::before{content:'✓';background:#1f8a4c}"
           ".memo-steps li.here{border:2px solid #d01012;box-shadow:0 0 0 4px rgba(208,16,18,.15)}"
           ".memo-here-tag{display:inline-block;margin-left:6px;padding:1px 8px;border-radius:999px;background:#d01012;color:#fff;font-size:12px;font-weight:700}"
           ".memo-where{padding:10px 12px;border-radius:12px;background:rgba(208,16,18,.1);font-weight:600;margin:10px 0}</style>"
           # « 📍 Vous en êtes là » : ?ici=2 (ou 4,5) &nom=… — l'étape en cours de l'élément d'où l'on vient (21/11 nuit)
           "<script>addEventListener('DOMContentLoaded',()=>{const q=new URLSearchParams(location.search),ici=(q.get('ici')||'').split(',').map(Number).filter(n=>n>0);"
           "if(!ici.length)return;const id=(location.hash.match(/^#\\/([\\w-]+)/)||[])[1],a=id&&document.getElementById('p-'+id);if(!a)return;const lis=[...a.querySelectorAll('.memo-steps li')],m=Math.min(...ici);"
           "lis.forEach((li,k)=>{if(ici.includes(k+1)){li.classList.add('here');li.insertAdjacentHTML('beforeend','<span class=\"memo-here-tag\">📍 Vous en êtes là</span>');}else if(k+1<m)li.classList.add('done');});"
           "const w=document.createElement('p');w.className='memo-where';w.textContent='📍 '+(q.get('nom')?q.get('nom')+' : ':'')+'vous en êtes à l\\'étape '+ici.join(' et ')+' sur '+lis.length+'.';"
           "a.querySelector('.memo-steps')?.before(w);});</script>")
    pages = []
    for k, c in enumerate(cards):
        steps = "".join(f"<li><b>{e(w)}</b> — {t}</li>" for w, t in c["steps"])
        know = "".join(f"<li>{t}</li>" for t in c.get("know") or [])
        body = (css if not k else "") + f"<p>{c.get('intro', '')}</p><ol class=\"memo-steps\">{steps}</ol>" \
            + (f"<h3>Bon à savoir</h3><ul class=\"memo-know\">{know}</ul>" if know else "")   # (sans renvoi au guide : retiré le 22/11)
        pages.append((c["id"], c["title"], body))
    return wiki.build("aide-memoire-perso" if perso else "aide-memoire", "Aide-mémoire", pages,
                      others=[("📘 Guide utilisateur", "/guide-utilisateur")], private=perso)


def main():
    if "--captures" in sys.argv:
        subprocess.run(["node", os.path.join(DOCS, "captures.js")], check=True)
    if "--captures-bo" in sys.argv:
        subprocess.run(["node", os.path.join(DOCS, "captures_bo.js")], check=True)
    sys.path.insert(0, DOCS)
    write_wiki("guide-utilisateur", wiki_guide())
    if os.path.exists(os.path.join(DOCS, "backoffice_content.py")):
        write_wiki("back-office", wiki_backoffice())
    write_wiki("aide-memoire", wiki_memo())   # aide-mémoire : la suite des évènements de chaque fonction (21/11)
    write_wiki("aide-memoire-perso", wiki_memo(perso=True))   # (+ fonctions exclusives : privé, seulement si memo_perso.py est là)
    write_wiki("guide-technique", wiki_technique())   # (privée : seulement si docs/technique.py est là)


if __name__ == "__main__":
    main()

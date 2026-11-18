# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Les guides de Briquothèque en « wiki » : une page par chapitre, sommaire à gauche, recherche, liens entre pages, impression.

Un guide = un seul fichier HTML autonome (docs/wiki/<nom>.html), écrit par docs/build_docs.py et servi par l'application :
    /guide-utilisateur    le guide utilisateur            (contenu : docs/guide_content.py)
    /backoffice/guide     la notice du back office        (contenu : docs/backoffice_content.py)
    /guide-technique      la documentation technique      (privée : jamais publiée, voir CLAUDE.md)

Chaque chapitre est un <article> ; un petit script n'en montre qu'un à la fois (adresse « #/chapitre »), fabrique le sommaire de la page,
cherche dans tout le guide et agrandit les captures. Imprimer la page imprime le guide entier (c'est ce qui remplace les anciens PDF).
"""
import html
import re
import time

e = html.escape


def slug(text):
    """« Modifier une fiche » → « modifier-une-fiche » (adresse de la page)."""
    t = text.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c"), ("œ", "oe")):
        for ch in a:
            t = t.replace(ch, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-") or "page"


CSS = """
:root{--bg:#f4f5f7;--panel:#fff;--ink:#1b1d22;--muted:#6b7280;--line:#e4e6eb;--red:#d01012;--tip:#fff7dc;--tipb:#e2b33c;--code:#f2f3f6;--mark:#ffe58a;--link:#2563eb}
@media (prefers-color-scheme:dark){:root{--bg:#14161b;--panel:#1c1f26;--ink:#f1f2f4;--muted:#9aa1ad;--line:#2c313b;--tip:#3a3118;--tipb:#8a6d1a;--code:#262a33;--mark:#7a6412;--link:#7fb0ff}}
*{box-sizing:border-box}html{scroll-padding-top:70px}
body{margin:0;background:var(--bg);color:var(--ink);font:15.5px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--link)}
.wk-top{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:10px;padding:9px 16px;background:var(--panel);border-bottom:1px solid var(--line)}
.wk-menu{display:none;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:8px;font-size:18px;line-height:1;padding:6px 10px;cursor:pointer}
.wk-home{color:var(--red);font-weight:700;text-decoration:none;white-space:nowrap}
.wk-title{font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.wk-search{flex:1 1 180px;min-width:0;max-width:420px;margin-left:auto;padding:7px 12px;border:1px solid var(--line);border-radius:99px;background:var(--bg);color:var(--ink);font:inherit}
.wk-others{display:flex;gap:6px;flex-wrap:wrap}.wk-others a{font-size:13px;font-weight:600;text-decoration:none;border:1px solid var(--line);border-radius:99px;padding:4px 10px;color:var(--ink);background:var(--panel);white-space:nowrap}
.wk-others a:hover,.wk-toc a:hover{border-color:var(--red)}
.wk-wrap{display:grid;grid-template-columns:280px minmax(0,1fr);align-items:start}
.wk-side{position:sticky;top:52px;max-height:calc(100vh - 52px);overflow:auto;padding:16px 12px 30px;border-right:1px solid var(--line);font-size:14px}
.wk-toc{list-style:none;margin:0;padding:0}.wk-toc>li{margin:1px 0}
.wk-toc a{display:block;padding:5px 9px;border-radius:8px;border:1px solid transparent;color:var(--ink);text-decoration:none}
.wk-toc a.on{background:var(--panel);border-color:var(--line);font-weight:700;color:var(--red)}
.wk-sub{list-style:none;margin:2px 0 6px;padding:0 0 0 14px;border-left:2px solid var(--line)}.wk-sub a{padding:3px 8px;font-size:13px;color:var(--muted)}
.wk-meta{color:var(--muted);font-size:12.5px;margin:18px 8px 0}
.wk-links{display:none;gap:6px;flex-wrap:wrap;margin:16px 6px 0}.wk-links a{font-size:13px;font-weight:600;text-decoration:none;border:1px solid var(--line);border-radius:99px;padding:5px 11px;color:var(--ink);background:var(--panel)}
.wk-main{max-width:980px;padding:22px 34px 90px;min-width:0}
.wk-page{display:none}.wk-page.on{display:block}
.wk-crumb{color:var(--muted);font-size:13px;margin-bottom:2px}
h1{font-size:28px;margin:0 0 12px;line-height:1.25}h2{font-size:22px;margin:30px 0 8px;color:var(--red)}h3{font-size:17.5px;margin:22px 0 6px}h4{font-size:15.5px;margin:16px 0 4px;color:var(--muted)}
section.w{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 20px;margin:14px 0;overflow-wrap:anywhere}
section.w>.gtext>h3:first-child,section.w>h3:first-child{margin-top:0}
figure{margin:14px 0 2px}figure img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:10px;display:block;margin:0 auto;cursor:zoom-in}
figure.shot img{max-height:560px}figcaption{font-size:13px;color:var(--muted);text-align:center;margin-top:6px}
figure svg{max-width:100%;height:auto}
.tip{background:var(--tip);border-left:4px solid var(--tipb);padding:9px 12px;border-radius:6px}
code{font-family:ui-monospace,Consolas,monospace;font-size:13.5px;background:var(--code);padding:1px 5px;border-radius:5px;overflow-wrap:anywhere}
table{width:100%;border-collapse:collapse;margin:8px 0 12px;font-size:14.5px;display:block;overflow-x:auto}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.03em}
a.go{display:inline-block;margin:2px 0;padding:4px 11px;border:1px solid var(--line);border-radius:99px;background:var(--panel);font-size:13.5px;font-weight:700;text-decoration:none}
ol,ul{padding-left:22px}li{margin:3px 0}ol.rec li{margin:9px 0}
.fn{border-left:3px solid var(--line);padding:3px 0 3px 10px;margin:6px 0 10px;font-size:14px}.fn-h{display:flex;justify-content:space-between;gap:8px;align-items:baseline;flex-wrap:wrap}
.fn-n{font-weight:700;background:none;padding:0}.fn-l{color:var(--muted);font-size:12.5px}.fn-x{color:var(--muted);font-size:13px}.muted{color:var(--muted)}p.idx{font-size:13px;line-height:1.7}
.wk-nav{display:flex;justify-content:space-between;gap:10px;margin-top:40px;padding-top:14px;border-top:1px solid var(--line);flex-wrap:wrap}
.wk-nav a{text-decoration:none;font-weight:700;border:1px solid var(--line);border-radius:10px;padding:8px 12px;background:var(--panel);color:var(--ink);max-width:48%}.wk-nav a:hover{border-color:var(--red)}
.wk-nav small{display:block;color:var(--muted);font-weight:400}
.wk-results{margin-bottom:20px}.wk-results h2{margin-top:0}.wk-hit{display:block;width:100%;text-align:left;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:10px;padding:9px 12px;margin:6px 0;cursor:pointer;font:inherit}
.wk-hit:hover{border-color:var(--red)}.wk-hit b{display:block}.wk-hit span{color:var(--muted);font-size:13.5px}
mark{background:var(--mark);color:inherit;border-radius:3px;padding:0 1px}
.wk-zoom{position:fixed;inset:0;z-index:50;background:rgba(0,0,0,.82);display:flex;align-items:center;justify-content:center;padding:16px;cursor:zoom-out}.wk-zoom img{max-width:100%;max-height:100%;border-radius:8px}
.legal h3{font-size:15.5px}
@media (max-width:900px){.wk-menu{display:block}.wk-wrap{display:block}.wk-title{display:none}
 .wk-side{display:none;position:fixed;top:52px;left:0;right:0;bottom:0;max-height:none;z-index:15;background:var(--bg);border-right:0}
 body.wk-open .wk-side{display:block}.wk-main{padding:16px 14px 70px}.wk-others{display:none}.wk-links{display:flex}h1{font-size:23px}section.w{padding:13px 14px}.wk-nav a{max-width:100%;flex:1 1 100%}}
@media print{.wk-top,.wk-side,.wk-nav,.wk-results{display:none!important}.wk-wrap{display:block}.wk-page{display:block!important;break-before:page}.wk-main{max-width:none;padding:0}body{background:#fff;color:#000}section.w{border:0;padding:0}}
"""

JS = r"""
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const pages = $$(".wk-page"), toc = $(".wk-toc"), res = $(".wk-results"), search = $(".wk-search");
  const norm = s => s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const E = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");   // texte → HTML sûr
  pages.forEach(p => $$("h2, h3", p).forEach((h, k) => { if (!h.id) h.id = p.id.slice(2) + "--" + (k + 1); }));   // une ancre par titre
  const unmark = () => $$("mark.wk-m").forEach(m => m.replaceWith(document.createTextNode(m.textContent)));
  const mark = (root, q) => {   // surligne le mot cherché dans la page ouverte
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), nodes = []; let n;
    while ((n = w.nextNode())) if (n.nodeValue.trim() && !n.parentElement.closest("script, style, mark, svg")) nodes.push(n);
    let first = null;
    for (const t of nodes) {
      const i = norm(t.nodeValue).indexOf(q); if (i < 0 || norm(t.nodeValue).length !== t.nodeValue.length) continue;
      const r = document.createRange(); r.setStart(t, i); r.setEnd(t, i + q.length);
      const m = document.createElement("mark"); m.className = "wk-m"; try { r.surroundContents(m); } catch { continue; } first = first || m;
    }
    return first;
  };
  function show(id, anchor, q) {
    const p = pages.find(x => x.id === "p-" + id) || pages[0];
    unmark(); res.hidden = true;
    pages.forEach(x => x.classList.toggle("on", x === p));
    $$("a", toc).forEach(a => a.classList.toggle("on", a.dataset.page === p.id.slice(2)));
    $$(".wk-sub", toc).forEach(u => u.remove());
    const heads = $$("h2, h3", p);
    if (heads.length > 1) {   // « sur cette page »
      const u = document.createElement("ul"); u.className = "wk-sub";
      u.innerHTML = heads.map(h => `<li><a href="#/${E(p.id.slice(2))}/${E(h.id)}">${E(h.textContent)}</a></li>`).join("");
      $("a.on", toc)?.after(u);
    }
    document.title = p.dataset.title + " — " + document.body.dataset.wiki;
    document.body.classList.remove("wk-open");
    const hit = q ? mark(p, q) : null, t = hit || (anchor && document.getElementById(anchor));
    if (t) t.scrollIntoView({ block: hit ? "center" : "start" }); else scrollTo(0, 0);
  }
  function route() {
    const h = decodeURIComponent(location.hash || "");
    if (h.startsWith("#/")) { const [id, anchor] = h.slice(2).split("/"); return show(id, anchor); }
    const t = h.length > 1 && (document.getElementById(h.slice(1)) || document.getElementById("p-" + h.slice(1)));   // ancienne ancre (ex. #souris, #fn-…) : la page qui la contient
    const p = t && t.closest(".wk-page");
    if (p) return show(p.id.slice(2), t === p ? "" : t.id);
    show(pages[0].id.slice(2));
  }
  addEventListener("hashchange", route);
  document.addEventListener("click", e => {
    const a = e.target.closest('a[href^="#"]');
    if (a && !a.getAttribute("href").startsWith("#/")) {   // lien interne vers une ancre : sa page, puis l'ancre
      const t = document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1))), p = t && t.closest(".wk-page");
      if (p) { e.preventDefault(); location.hash = "#/" + p.id.slice(2) + (t === p ? "" : "/" + t.id); }
      return;
    }
    const img = e.target.closest("figure img");
    if (img) { const z = document.createElement("div"); z.className = "wk-zoom"; z.innerHTML = `<img src="${E(img.src)}" alt="">`; z.onclick = () => z.remove(); document.body.append(z); }
  });
  $(".wk-menu").onclick = () => document.body.classList.toggle("wk-open");
  let timer = 0;
  search.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(() => {
    const q = norm(search.value.trim());
    if (q.length < 2) { res.hidden = true; if (!$(".wk-page.on")) route(); return; }
    const hits = [];
    for (const p of pages) for (const b of $$("section, .wk-block", p).concat($$(":scope > p, :scope > ul, :scope > table, :scope > div.fn", p))) {
      const txt = b.textContent.replace(/\s+/g, " "), i = norm(txt).indexOf(q); if (i < 0) continue;
      const h = b.querySelector("h2, h3") || [...$$("h2, h3", p)].filter(x => x.compareDocumentPosition(b) & 4).pop();
      hits.push({ p, h, snip: (i > 60 ? "… " : "") + txt.slice(Math.max(0, i - 60), i + 110) + " …" });
      if (hits.length >= 60) break;
    }
    unmark(); pages.forEach(x => x.classList.remove("on")); res.hidden = false;
    res.innerHTML = `<h2>${hits.length ? hits.length + (hits.length >= 60 ? "+" : "") + " résultat" + (hits.length > 1 ? "s" : "") : "Aucun résultat"} pour « ${E(search.value)} »</h2>`
      + hits.map((x, k) => `<button type="button" class="wk-hit" data-k="${k}"><b>${E(x.p.dataset.title)}${x.h ? " › " + E(x.h.textContent) : ""}</b><span>${E(x.snip)}</span></button>`).join("");
    $$(".wk-hit", res).forEach(b => b.onclick = () => { const x = hits[+b.dataset.k]; history.replaceState(null, "", "#/" + x.p.id.slice(2)); show(x.p.id.slice(2), x.h?.id, q); });
    scrollTo(0, 0);
  }, 180); });
  search.addEventListener("keydown", e => { if (e.key === "Escape") { search.value = ""; res.hidden = true; route(); } });
  route();
})();
"""


def build(name, title, pages, home=("← Briquothèque", "/"), others=(), img_from="../captures/", img_to="", private=False, note=""):
    """Écrit un guide : pages = [(identifiant, titre, html)] → le HTML complet (une page par chapitre).
    img_from → img_to : les captures (« ../captures/x.jpg » du contenu) deviennent l'adresse servie par l'application.
    private : la page porte le repère des fichiers à ne jamais publier (documentation technique)."""
    toc, arts = "", ""
    for k, (pid, ptitle, body) in enumerate(pages):
        prev_, next_ = pages[k - 1] if k else None, pages[k + 1] if k + 1 < len(pages) else None
        nav = (f'<a href="#/{prev_[0]}"><small>← Précédent</small>{e(prev_[1])}</a>' if prev_ else "<span></span>") \
            + (f'<a href="#/{next_[0]}" style="text-align:right"><small>Suivant →</small>{e(next_[1])}</a>' if next_ else "")
        toc += f'<li><a href="#/{pid}" data-page="{pid}">{e(ptitle)}</a></li>'
        arts += f'<article class="wk-page" id="p-{pid}" data-title="{e(ptitle)}"><div class="wk-crumb">{e(title)} › {e(ptitle)}</div><h1>{e(ptitle)}</h1>{body}<footer class="wk-nav">{nav}</footer></article>\n'
    if img_to:
        arts = arts.replace(img_from, img_to)
    links = "".join(f'<a href="{h}">{e(t)}</a>' for t, h in others)
    # (repère des fichiers privés, écrit en deux morceaux : ce moteur, lui, est publié et ne doit pas le porter)
    mark_ = "<!-- " + "PRIVE-NE-JAMAIS-" + "PUBLIER" + " : documentation technique, réservée au propriétaire -->\n" if private else ""
    return f"""<!doctype html>
{mark_}<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>{e(title)} — Briquothèque</title><link rel="icon" href="/icon.svg"><style>{CSS}</style></head><body data-wiki="{e(title)}">
<header class="wk-top"><button type="button" class="wk-menu" aria-label="Sommaire">☰</button><a class="wk-home" href="{home[1]}">{e(home[0])}</a><b class="wk-title">{e(title)}</b>
<input type="search" class="wk-search" placeholder="Chercher dans ce guide…" aria-label="Chercher dans ce guide"><span class="wk-others">{links}</span></header>
<div class="wk-wrap"><nav class="wk-side"><ol class="wk-toc">{toc}</ol><p class="wk-links">{links}</p><p class="wk-meta">Version du {time.strftime("%d/%m/%Y")}{("<br>" + note) if note else ""}<br>Imprimer cette page imprime tout le guide.</p></nav>
<main class="wk-main"><div class="wk-results" hidden></div>
{arts}</main></div>
<script>{JS}</script></body></html>"""

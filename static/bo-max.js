/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
/* Briquothèque — BACK OFFICE : moteur, 3e partie (chargé sur toutes les pages, après bo.js et bo-plus.js).
   Applique les réglages faits dans les rubriques « Étiquettes », « Boutons et tailles », « Pages », « Page Réglages », « Comportements »
   et les compléments de « Modifier à la souris » (icône ou image d'un bouton, lien, comportement au clic, décalage) :
     1. feuille de style : icône / image / décalage par élément (cfg.rules[].ico | img | tx), boutons (cfg.btn), tailles (cfg.sizes),
        étiquettes d'origine recolorées ou masquées (cfg.tags.over) ;
     2. étiquettes : celles de l'application sont repérées ([data-bo-tag]), renommées, montrées sous condition ; les vôtres (cfg.tags.add)
        sont ajoutées aux cartes et à la fiche quand leur condition est remplie ;
     3. liens et clics : adresse d'un lien changée (rules[].href), comportement au clic (rules[].click) ;
     4. page « Réglages » de l'application : ordre, sections masquées, titres (cfg.settings) ;
     5. pages créées (cfg.pages) : lien dans le menu, affichage dans le site ; version publique sur /p/<adresse> ;
     6. comportements (cfg.behav) : page de départ, vue et tri par défaut, raccourcis clavier, titre de l'onglet.
   Rien ici n'utilise eval ni innerHTML sur un texte non vérifié : tout texte est échappé, toute adresse passe par safeUrl,
   le HTML libre d'une page passe par sanitize (liste blanche de balises et d'attributs). Une valeur absurde est ignorée. */
(() => {
"use strict";
const W = window, D = document, B = W.BO;
if (!B || !B._ || B.max) return;
const { HOOKS, esc, all, app, PAGE, PUBLIC, schedule } = B._;
const cfg = () => B._.cfg() || {};
const P = () => B.plus || null;   // formules et conditions (site connecté seulement)
const ADMIN = () => { try { return B._.admin(); } catch { return null; } };
const arr = v => Array.isArray(v) ? v : [];
const obj = v => v && typeof v === "object" && !Array.isArray(v) ? v : {};
const str = v => typeof v === "string" ? v : v == null || typeof v === "object" ? "" : String(v);
const num = (v, lo, hi, d) => { const n = typeof v === "number" ? v : parseFloat(v); return isFinite(n) ? Math.max(lo, Math.min(hi, n)) : d; };
const color = c => /^#[0-9a-f]{3,8}$/i.test(str(c)) ? str(c) : "";
const safeSel = s => { try { D.createDocumentFragment().querySelector(s); return typeof s === "string" && !!s.trim(); } catch { return false; } };
const keyOf = s => str(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 40);
const URL_OK = /^(https?:|mailto:|tel:|\/|#|\?|data:image\/(png|jpe?g|gif|webp|svg\+xml|x-icon|avif)[;,])/i;
function safeUrl(u) {   // même règle que le serveur (backoffice.safe_url) : http(s), mailto, tel, adresse du site, image intégrée — rien d'autre
  u = str(u).trim().replace(/[\u0000-\u001f\u007f]/g, "");
  if (!u || URL_OK.test(u)) return u;
  if (/^[a-z][a-z0-9+.-]*:/i.test(u)) return "";
  if (/^[\w-]+(\.[\w-]+)+([/:?#]|$)/.test(u)) return "https://" + u;
  return u;
}
const cssUrl = u => 'url("' + safeUrl(u).replace(/["\\\n\r\f]/g, c => "\\" + c.charCodeAt(0).toString(16) + " ") + '")';
const wideList = sel => { const out = [sel];   // un élément déplacé à la souris garde ses réglages (comme wide() de bo.js)
  for (const m of arr(cfg().moves)) if (m && m.id && typeof m.sel === "string" && (sel === m.sel || sel.startsWith(m.sel + " "))) out.push(`bo-mv[data-bo-mv="${m.id}"] > *${sel.slice(m.sel.length)}`);
  return out; };
const liveRules = need => arr(cfg().rules).filter(r => r && typeof r.sel === "string" && !r.off && (!r.page || r.page === PAGE) && need(r) && safeSel(r.sel));
let stamp = 0;   // change à chaque relecture des réglages

/* ------------------------------------------------------------------ étiquettes de l'application (catalogue)
   [clé, nom affiché dans le back office, genre, classe qui la reconnaît, texte qui la reconnaît (s'il n'y a pas de classe à elle)] */
const TAGS = [
  ["t-moc", "MOC", "tg", "tg-moc"], ["t-mod", "Modifié / Modifiée", "tg", "tg-mod"], ["t-imp", "Amélioré / Améliorée", "tg", "tg-imp"], ["t-part", "Set partiel", "tg", "tg-part"],
  ["t-add", "+ N figurines ajoutées", "tg", "tg-add"], ["t-rep", "N figurines remplacées", "tg", "tg-rep"],
  ["t-complet", "Complet (étiquette posée à la main)", "tg", "", /^Complet$/], ["t-pieces", "Pièces ajoutées", "tg", "", /^Pièces ajoutées$/], ["t-nofig", "Sans figurines", "tg", "", /^Sans figurines$/], ["t-prix", "Prix par les pièces", "tg", "", /^Prix par les pièces$/],
  ["b-moc", "MOC", "badge", "moc"], ["b-partial", "🧩 Set partiel", "badge", "partial-set"], ["b-scan", "Scan en cours / à valider", "badge", "scan"],
  ["b-upcoming", "Bientôt disponible", "badge", "upcoming"], ["b-soon", "Bientôt retiré", "badge", "soon"], ["b-onsale", "En vente", "badge", "onsale"], ["b-retired", "Retiré", "badge", "retired"],
  ["b-inset", "Dans un set / Dans N sets", "badge", "in-set"], ["b-neuf", "Neuf", "badge", "neuf"], ["b-nofig", "Sans figurines", "badge", "nofig"], ["b-qty", "×N (plusieurs exemplaires)", "badge", "qty"],
  ["b-plans", "Sans plans", "badge", "plain", /^Sans plans$/], ["b-partiel", "Partiel", "badge", "plain", /^Partiel$/], ["b-attente", "En Attente 🚧", "badge", "plain", /^En Attente/], ["b-boite", "📦 Avec boîte", "badge", "plain", /Avec boîte/],
];
function tagKey(el) {
  const kind = el.classList.contains("tg") ? "tg" : "badge", t = el.textContent.trim();
  for (const [k, , g, cl, re] of TAGS) if (g === kind && (cl ? el.classList.contains(cl) : true) && (!re || re.test(t)) && (cl || re)) return k;
  return "";
}

/* ------------------------------------------------------------------ 1. feuille de style */
const BASE = `
.bo-tag-off,.tg-w:has(> .bo-tag-off){display:none!important}
.card .bo-ctags{display:flex;flex-wrap:wrap;gap:4px;margin:2px 0}
.card .pic{position:relative}
.card .pic .bo-cbadges{position:absolute;left:8px;bottom:8px;z-index:1;display:flex;gap:4px;flex-wrap:wrap;max-width:calc(100% - 16px);pointer-events:none}
.bo-ctag.tg{display:inline-block;padding:0 6px;border-radius:99px;font-size:10.5px;font-weight:700;line-height:1.6;border:1px solid var(--line);color:var(--muted)}
.bo-sheet-tags{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px}.bo-sheet-tags .bo-ctag{font-size:12px;padding:1px 9px;border-radius:99px;border:1px solid var(--line);font-weight:700}
.sidebar .bo-plink.on{background:var(--accent-bg);color:var(--red);font-weight:700}
body.bo-page-on .main > :not(#boPage){display:none!important}
#boPage{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:16px 18px;align-items:start;margin:0 auto;width:100%}
#boPage > *{grid-column:span 6;min-width:0;margin:0}
#boPage .bo-pb-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}#boPage .bo-pb-head h1{margin:0;font-size:26px}
#boPage h2.bo-pb{font-size:21px}#boPage h3.bo-pb{font-size:17px}#boPage h4.bo-pb{font-size:15px;color:var(--muted)}
#boPage .bo-pb-texte{line-height:1.6}#boPage .bo-pb-texte p{margin:0 0 .7em}#boPage .bo-pb-texte ul{margin:0 0 .7em;padding-left:22px}#boPage a{color:var(--red)}
#boPage .bo-pb-note{padding:12px 14px;border-radius:12px;border:1px solid var(--c,var(--line));background:color-mix(in srgb,var(--c,var(--yellow)) 14%,transparent);line-height:1.5}
#boPage .bo-pb-note p{margin:0 0 .5em}#boPage .bo-pb-note p:last-child{margin:0}
#boPage figure.bo-pb{text-align:center}#boPage figure.bo-pb img{max-width:100%;height:auto;border-radius:12px}#boPage figcaption{font-size:13px;color:var(--muted);margin-top:4px}
#boPage hr.bo-pb{border:0;border-top:1px solid var(--line);width:100%}
#boPage .bo-pb-cadre{width:100%;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
#boPage .bo-pb-fiches .grid{margin:0}#boPage .bo-pcard{cursor:pointer}#boPage .bo-pcard .pic img{width:100%;height:100%;object-fit:contain}
#boPage .bo-pb-empty{color:var(--muted);font-style:italic;padding:10px 0}
#boPage .bo-ptile{margin:0}
#boPage .bo-pb-tableau{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
#boPage .bo-pb-tableau table{border-collapse:collapse;width:100%;font-size:13.5px}#boPage .bo-pb-tableau th,#boPage .bo-pb-tableau td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}
#boPage .bo-pb-tableau th{font-size:12px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted);position:sticky;top:0;background:var(--panel)}
#boPage .bo-pb-tableau tr[data-bo-open]{cursor:pointer}#boPage .bo-pb-tableau tr[data-bo-open]:hover td{background:var(--accent-bg)}
#boPage .bo-pb-html{line-height:1.55;overflow-wrap:anywhere}#boPage .bo-pb-html img{max-width:100%;height:auto}
@media (max-width:620px){#boPage > *{grid-column:span 6!important}}
body.bo-public-page{margin:0;background:var(--bg);color:var(--ink)}body.bo-public-page .bo-pp-main{max-width:1100px;margin:0 auto;padding:22px 16px 60px}`;
const style = D.createElement("style");
style.id = "bo-max-style";
function buildCss() {
  const c = cfg(), out = [BASE], imp = d => d.map(v => v + "!important").join(";");
  for (const r of liveRules(r => r.ico || r.img || r.tx)) {   // par élément : décalage / échelle / rotation, image de fond, icône ou image à côté du texte
    const S = wideList(r.sel), sel = suf => S.map(s => s + suf).join(","), d = [];
    const ic = obj(r.ico), im = obj(r.img), tx = obj(r.tx), url = safeUrl(im.url), mode = str(im.mode) || "before";
    const x = num(tx.x, -3000, 3000, 0), y = num(tx.y, -3000, 3000, 0), s = num(tx.s, 10, 500, 100), ro = num(tx.r, -360, 360, 0);
    if (x || y) d.push(`translate:${x}px ${y}px`);
    if (s !== 100) d.push(`scale:${s / 100}`);
    if (ro) d.push(`rotate:${ro}deg`);
    if (d.length) out.push(`${sel(":where(span,a,b,i,em,strong,small,label,code):not([hidden])")}{display:inline-block}`);   // (un texte « en ligne » ne se décale pas sinon)
    if (url && (mode === "bg" || mode === "bgc")) d.push(`background-image:${cssUrl(url)}`, `background-size:${mode === "bg" ? "cover" : "contain"}`, "background-position:center", "background-repeat:no-repeat");
    if (d.length) out.push(`${sel("")}{${imp(d)}}`);
    const icon = str(ic.t).slice(0, 12), side = url && ["before", "after", "only"].includes(mode) ? mode : !url && icon ? (["after", "only"].includes(ic.pos) ? ic.pos : "before") : "";
    if (!side) continue;
    const pe = side === "after" ? "::after" : "::before", only = side === "only", w = num(im.w, 4, 2000, 20), h = num(im.h, 4, 2000, w);
    out.push(`${sel(pe)}{${url ? `content:"";display:inline-block;width:${w}px;height:${h}px;background:${cssUrl(url)} center/contain no-repeat;vertical-align:middle;flex:none`
      : `content:${JSON.stringify(icon)};font-size:${only ? num(ic.size, 8, 200, 18) + "px" : "inherit"}`};margin-${side === "after" ? "left" : "right"}:${only ? 0 : ".4em"}}`);
    if (only) out.push(`${sel("")}{font-size:0!important;gap:0!important}`);
  }
  const b = obj(c.btn), bd = [];   // tous les boutons
  if (str(b.radius) !== "") bd.push(`border-radius:${num(b.radius, 0, 60, 10)}px`);
  if (str(b.padY) !== "" || str(b.padX) !== "") bd.push(`padding:${num(b.padY, 0, 40, 9)}px ${num(b.padX, 0, 80, 14)}px`);
  if (str(b.size) !== "") bd.push(`font-size:${num(b.size, 9, 32, 14)}px`);
  if (["400", "600", "800"].includes(str(b.weight))) bd.push(`font-weight:${b.weight}`);
  if (b.upper === true) bd.push("text-transform:uppercase", "letter-spacing:.03em");
  if (str(b.border) !== "") bd.push(`border-width:${num(b.border, 0, 8, 1)}px`, "border-style:solid");
  if (b.shadow === true) bd.push("box-shadow:0 2px 7px rgba(0,0,0,.2)");
  if (bd.length) out.push(`.btn{${imp(bd)}}`);
  const pair = (S, bg, ink, line) => { const d = []; if (color(bg)) d.push(`background:${bg}`, `border-color:${color(line) || bg}`); else if (color(line)) d.push(`border-color:${line}`); if (color(ink)) d.push(`color:${ink}`); if (d.length) out.push(`${S}{${imp(d)}}`); };
  pair(".btn:not(.primary):not(.danger):not(.ghost)", b.bg, b.ink, b.line);
  pair(".btn.primary", b.primBg, b.primInk);
  pair(".btn.danger", b.dangBg, b.dangInk);
  const z = obj(c.sizes);   // tailles générales
  if (str(z.menu) !== "") out.push(`@media (min-width:821px){.layout{grid-template-columns:${num(z.menu, 160, 600, 320)}px 1fr!important}}`);
  if (str(z.sheet) !== "") out.push(`@media (min-width:821px){#modal > .modal-box{width:min(${num(z.sheet, 420, 1800, 680)}px,100%)!important}}`);
  if (str(z.content) !== "") out.push(`@media (min-width:821px){.main{max-width:${num(z.content, 600, 4000, 1600)}px;margin-inline:auto}}`);
  if (str(z.gap) !== "") out.push(`.grid{gap:${num(z.gap, 0, 60, 16)}px!important}`);
  if (str(z.title) !== "") out.push(`#listTitle,.g-main > h1{font-size:${num(z.title, 12, 80, 26)}px!important}`);
  for (const [k, o] of Object.entries(obj(obj(c.tags).over))) {   // étiquettes d'origine : masquées ou recolorées
    if (!/^[a-z0-9-]{1,30}$/.test(k) || !o || typeof o !== "object") continue;
    const S = `[data-bo-tag="${k}"]`, d = [];
    if (o.hide === true) { out.push(`${S},.tg-w:has(> ${S}){display:none!important}`); continue; }   // (fiche : son ✕ part avec elle)
    if (color(o.color)) d.push(`color:${o.color}`);
    if (color(o.bg)) d.push(`background:${o.bg}`);
    if (color(o.border)) d.push(`border:1px solid ${o.border}`);
    if (d.length) out.push(`${S}{${imp(d)}}`);
  }
  if (obj(c.tags).badges === true) out.push(`.card .pic .badges{display:flex!important}`);   // pastilles de l'application : montrées aussi sur les cartes de la collection
  for (const k of arr(obj(c.settings).hidden)) if (/^[a-z0-9_]{1,40}$/.test(str(k))) out.push(`.settings-page [data-bo-set="${k}"]{display:none!important}`);
  if (obj(c.behav).noAnim === true) out.push(`*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}`);
  const css = out.join("\n");
  if (!style.isConnected) (D.head || D.documentElement).append(style);
  if (style.textContent !== css) style.textContent = css;
}

/* ------------------------------------------------------------------ 2. étiquettes */
const memo = new WeakMap();   // fiche → { stamp, ids } : étiquettes créées qu'elle porte
const myTags = () => arr(obj(cfg().tags).add).filter(t => t && typeof t.id === "string" && str(t.label).trim() && !t.off);
function tagsOf(it) {
  let m = memo.get(it);
  if (!m || m.stamp !== stamp) {
    const p = P(), type = B._.itemType(it);
    m = { stamp, tags: p ? myTags().filter(t => (!arr(t.types).length || t.types.includes(type)) && (() => { try { return p.test(t.cond, it); } catch { return false; } })()) : [] };
    memo.set(it, m);
  }
  return m.tags;
}
const tagStyle = t => [color(t.color) && `color:${t.color}`, color(t.bg) && `background:${t.bg}`, color(t.border) && `border-color:${t.border}`].filter(Boolean).join(";");
function tagHtml(t, it, sheet) {
  let label = str(t.label).slice(0, 80);
  try { if (P() && P().fill && /\{/.test(label)) label = P().fill(label, it); } catch {}
  return `<span class="${(t.kind === "badge" && !sheet ? "badge " : "tg ")}bo-ctag bo-x" data-bo-ctag="${esc(t.id)}" style="${tagStyle(t)}">${esc((t.icon ? str(t.icon).slice(0, 8) + " " : "") + label)}</span>`;
}
function put(host, sel, html, make) {   // garde un petit conteneur à jour (créé au besoin, retiré s'il est vide)
  let box = host.querySelector(sel);
  if (!html) { box?.remove(); return; }
  if (!box) box = make();
  if (box && box._sig !== html) { box._sig = html; box.innerHTML = html; }
}
function tagsPass() {
  const c = obj(cfg().tags), over = obj(c.over), mine = myTags(), hasOver = Object.keys(over).length > 0;
  if (hasOver || D.querySelector("[data-bo-tag]") || ADMIN()) {
    for (const el of all(".tg:not(.bo-ctag):not([data-bo-tag]), .badge:not(.bo-badge):not(.bo-ctag):not([data-bo-tag])")) el.dataset.boTag = tagKey(el) || "autre";
    const p = !PUBLIC && app() ? P() : null;
    for (const el of all("[data-bo-tag]")) {
      const o = obj(over[el.dataset.boTag]), t0 = el.dataset.boT0;
      if (str(o.text).trim() || str(o.icon).trim()) {   // renommée (« {n} » reprend le nombre du texte d'origine) et / ou précédée d'une icône
        const src = t0 !== undefined ? t0 : el.textContent;
        if (t0 === undefined) el.dataset.boT0 = src;
        const t = (str(o.icon).trim() ? str(o.icon).trim().slice(0, 8) + " " : "") + (str(o.text).trim() ? str(o.text).slice(0, 80).replace(/\{n\}/g, (src.match(/\d+/) || [""])[0]) : src.trim());
        if (el.textContent !== t) el.textContent = t;
      } else if (t0 !== undefined) { if (el.textContent !== t0) el.textContent = t0; delete el.dataset.boT0; }
      let off = false;   // « afficher seulement si… » (site connecté : la condition se lit sur la fiche de la carte, ou sur la fiche ouverte)
      if (p && o.cond && typeof o.cond === "object") {
        const card = el.closest(".card[data-id], .card[data-altof]"), it = card ? p.itemOf?.(card.dataset.id || card.dataset.altof) : el.closest("#modal") ? B._.ownItem() : null;   // (carte d'une apparence alternative : la fiche dont elle dépend)
        if (it) try { off = !p.test(o.cond, it); } catch {}
      }
      if (el.classList.contains("bo-tag-off") !== off) el.classList.toggle("bo-tag-off", off);
    }
  }
  if (PUBLIC || !app() || !P() || !P().itemOf) return;
  const box = D.getElementById("items");
  if (box && (mine.length || box.querySelector(".bo-ctag"))) {   // vos étiquettes, sur les cartes
    for (const card of all(".card[data-id], .card[data-altof]", box)) {
      const it = P().itemOf(card.dataset.id || card.dataset.altof), ts = it && mine.length ? tagsOf(it) : [], body = card.querySelector(":scope > .body"), pic = card.querySelector(":scope > .pic");
      if (body) put(body, ":scope > .bo-ctags", ts.filter(t => t.kind !== "badge" && t.card !== false).map(t => tagHtml(t, it)).join(""),
        () => { const d = D.createElement("div"); d.className = "bo-ctags bo-x"; (body.querySelector(":scope > .tagline") || body.querySelector(":scope > .name") || body.firstElementChild)?.after(d); return d.isConnected ? d : null; });
      if (pic) put(pic, ":scope > .bo-cbadges", ts.filter(t => t.kind === "badge" && t.card !== false).map(t => tagHtml(t, it)).join(""),   // vos pastilles : dans leur propre coin de l'image (l'application masque les siennes sur les cartes de la collection)
        () => { const d = D.createElement("div"); d.className = "bo-cbadges bo-x"; pic.append(d); return d; });
    }
  }
  const form = D.getElementById("stepConfig");   // …et en haut de la fiche ouverte
  if (form && !form.hidden && typeof modal !== "undefined" && !modal.hidden && state.draft) {
    const it = B._.ownItem(), ts = it && mine.length ? tagsOf(it).filter(t => t.sheet !== false) : [];
    put(form, ":scope > .bo-sheet-tags", ts.map(t => tagHtml(t, it, true)).join(""), () => { const d = D.createElement("div"); d.className = "bo-sheet-tags bo-x"; d.dataset.boKey = "bo-etiquettes"; form.prepend(d); return d; });
  } else form?.querySelector(":scope > .bo-sheet-tags")?.remove();   // (fiche refermée : rien ne reste)
}

/* ------------------------------------------------------------------ 3. liens et clics */
function hrefPass() {
  const rs = liveRules(r => typeof r.href === "string" || r.blank === true);
  for (const a of all("a[data-bo-href0]")) {   // règle disparue : le lien d'origine revient
    if (rs.some(r => wideList(r.sel).some(s => { try { return a.matches(s); } catch { return false; } }))) continue;
    if (a.dataset.boHref0) a.setAttribute("href", a.dataset.boHref0); else a.removeAttribute("href");
    if (a.dataset.boTarget0 !== undefined) { if (a.dataset.boTarget0) a.target = a.dataset.boTarget0; else a.removeAttribute("target"); }
    delete a.dataset.boHref0; delete a.dataset.boTarget0;
  }
  for (const r of rs) for (const a of all(wideList(r.sel).join(",")).slice(0, 200)) {
    if (a.tagName !== "A" || a.closest(".bo-ui")) continue;
    if (a.dataset.boHref0 === undefined) { a.dataset.boHref0 = a.getAttribute("href") || ""; a.dataset.boTarget0 = a.getAttribute("target") || ""; }
    const u = typeof r.href === "string" && r.href.trim() ? safeUrl(r.href) : a.dataset.boHref0;
    if (u && a.getAttribute("href") !== u) a.setAttribute("href", u);
    if (r.blank === true && a.target !== "_blank") { a.target = "_blank"; a.rel = "noopener"; }
  }
}
function act(a) {   // une action : ouvrir une adresse, une liste, une vue, une page, une fiche…
  a = obj(a);
  const k = str(a.k), v = str(a.v);
  try {
    if (k === "url") { const u = safeUrl(v); if (u) { if (a.same === true) location.href = u; else W.open(u, "_blank", "noopener"); } }
    else if (k === "top") W.scrollTo({ top: 0, behavior: "smooth" });
    else if (k === "back") history.back();
    else if (!app()) return;
    else if (k === "list") { closePage(); B._.openList(v); }
    else if (k === "all") { closePage(); B._.openList(ALL); }
    else if (k === "view") { closePage(); P()?.openView(v); }
    else if (k === "page") openPage(v);
    else if (k === "item") B._.goItem(v);
    else if (k === "new") openAdd();
    else if (k === "settings") D.getElementById("btnSettings")?.click();
    else if (k === "search") { closePage(); const f = D.getElementById("filter"); if (f) { f.scrollIntoView({ block: "center" }); f.focus(); } }
  } catch (e) { console.warn("BO action", e); }
}
function actOk(a) {   // l'action peut-elle aboutir ? (une liste, une vue, une page ou une fiche supprimée depuis : le clic n'est alors PAS détourné, l'élément refait son travail d'origine)
  a = obj(a);
  const k = str(a.k), v = str(a.v);
  if (k === "none" || k === "confirm" || k === "top" || k === "back") return true;
  if (k === "url") return !!safeUrl(v);
  if (!app()) return false;
  try {
    if (k === "list") return state.lists.some(l => l.id === v);
    if (k === "view") return arr(cfg().views).some(x => x && x.id === v) && !!P();
    if (k === "page") return pagesOn().some(p => p.id === v || p.slug === v);
    if (k === "item") return state.items.some(i => i.id === v);
  } catch { return false; }
  return ["all", "new", "settings", "search"].includes(k);
}
D.addEventListener("click", e => {
  if (D.documentElement.matches(".bo-picking, .bo-moving")) return;   // aperçu du back office en mode « cliquer pour modifier » / « déplacer »
  const t = e.target.nodeType === 1 ? e.target : e.target.parentElement;
  if (!t || t.closest(".bo-ui")) return;
  const pb = t.closest("#boPage [data-bo-b], #boPage [data-bo-open]");   // bouton ou fiche d'une page créée
  if (pb) {
    if (pb.dataset.boOpen) { if (app()) B._.goItem(pb.dataset.boOpen); return; }
    const pg = arr(cfg().pages).find(p => p && p.id === pageId()), b = pg && arr(pg.blocks).find(b => b && b.id === pb.dataset.boB);
    if (b) { e.preventDefault(); act(b.act); }
    return;
  }
  for (const r of liveRules(r => str(obj(r.click).k) && actOk(r.click))) {
    let el = null;
    try { el = t.closest(wideList(r.sel).join(",")); } catch {}
    if (!el) continue;
    const k = r.click.k;
    if (k === "confirm") { if (!W.confirm(str(r.click.msg).trim() || "Continuer ?")) { e.preventDefault(); e.stopImmediatePropagation(); } return; }
    e.preventDefault(); e.stopImmediatePropagation();
    if (k !== "none") act(r.click);
    return;
  }
}, true);

/* ------------------------------------------------------------------ 4. page « Réglages » de l'application : ordre, sections masquées, titres */
function settingsPass() {
  const grid = D.querySelector(".settings-page .set-grid"); if (!grid) return;
  const s = obj(cfg().settings), nav = D.querySelector(".settings-page [data-setnav]");
  for (const f of grid.children) {   // clé stable de chaque section : son nom dans le sommaire (sinon son titre)
    if (f.dataset.boSet) continue;
    const b = nav && f.dataset.secid ? nav.querySelector(`[data-goto="${f.dataset.secid}"]`) : null, lg = f.querySelector(":scope > legend");
    const lab = ((b ? b.textContent : lg?.textContent) || "").trim();
    f.dataset.boSet = keyOf(lab) || "section"; f.dataset.boLab = lab;
    if (b) { b.dataset.boSet = f.dataset.boSet; b.dataset.boLab = lab; }
    if (lg) lg.dataset.boLab = lg.textContent.trim();
  }
  const order = arr(s.order).filter(k => typeof k === "string"), rank = el => { const i = order.indexOf(el.dataset.boSet); return i < 0 ? 999 : i; };
  if (order.length) for (const box of [grid, nav]) {
    if (!box) continue;
    const cur = [...box.children], keep = cur.filter(x => !x.dataset.boSet), want = cur.filter(x => x.dataset.boSet).map((x, i) => [x, i]).sort((a, b) => rank(a[0]) - rank(b[0]) || a[1] - b[1]).map(x => x[0]);
    const next = box === nav ? [...want, ...keep] : [...want, ...keep];
    if (next.some((x, i) => x !== cur[i])) next.forEach(x => box.append(x));
  }
  const titles = obj(s.titles);
  for (const el of all(".settings-page [data-bo-set]")) {
    const lg = el.tagName === "FIELDSET" ? el.querySelector(":scope > legend") : el, t = str(titles[el.dataset.boSet]).trim().slice(0, 80), src = lg && lg.dataset.boLab;
    if (!lg || src === undefined) continue;
    const want = t || src;
    if (lg.textContent.trim() !== want) lg.textContent = want;
  }
}

/* ------------------------------------------------------------------ 5. pages créées dans le back office */
let openId = null, pageFor = null, pageSig = "";
const pageId = () => PAGE === "page" ? str(obj(arr(cfg().pages)[0]).id) : openId;
const pagesOn = () => arr(cfg().pages).filter(p => p && typeof p.id === "string" && !p.off);
const OKTAGS = new Set("a,abbr,b,blockquote,br,caption,center,code,col,colgroup,dd,details,div,dl,dt,em,figcaption,figure,h1,h2,h3,h4,h5,h6,hr,i,img,li,mark,ol,p,pre,s,section,small,span,strong,sub,summary,sup,table,tbody,td,tfoot,th,thead,tr,u,ul,video,audio,source".split(","));
const OKATTR = new Set("href,src,alt,title,width,height,colspan,rowspan,style,class,controls,loop,muted,poster,align,open,loading".split(","));
const DROP = /^(script|style|iframe|object|embed|link|meta|base|form|input|button|textarea|select|option|svg|math|template|noscript|frame|frameset|applet|title|head)$/;
function sanitize(html) {   // HTML libre d'une page : seulement des balises et des attributs sans danger, des adresses vérifiées, aucun script
  let doc;
  try { doc = new DOMParser().parseFromString("<body>" + str(html).slice(0, 300000), "text/html"); } catch { return ""; }
  const walk = n => {
    for (const c of [...n.children]) {
      const t = c.tagName.toLowerCase();
      if (!OKTAGS.has(t)) { if (DROP.test(t)) c.remove(); else { walk(c); c.replaceWith(...c.childNodes); } continue; }
      for (const a of [...c.attributes]) {
        const an = a.name.toLowerCase();
        if (!OKATTR.has(an)) { c.removeAttribute(a.name); continue; }
        if (an === "href" || an === "src" || an === "poster") { const u = safeUrl(a.value); if (!u) c.removeAttribute(a.name); else if (u !== a.value) c.setAttribute(a.name, u); }
        else if (an === "style" && /url\s*\(|expression|@import|behavior|binding|position\s*:\s*(fixed|sticky|absolute)|[<>{}\\]/i.test(a.value)) c.removeAttribute(a.name);
        else if (an === "class" && /(^|\s)(bo-|modal|sidebar|topbar)/.test(a.value)) c.removeAttribute(a.name);
      }
      if (t === "a") { c.setAttribute("rel", "noopener noreferrer"); if (/^https?:/i.test(c.getAttribute("href") || "")) c.setAttribute("target", "_blank"); }
      walk(c);
    }
  };
  walk(doc.body);
  return doc.body.innerHTML;
}
function rich(text) {   // texte simple : **gras**, *italique*, [texte](adresse), lignes « - » en liste, ligne vide = nouveau paragraphe
  const inl = s => esc(s).replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<i>$2</i>")
    .replace(/\[([^\]]{1,200})\]\(([^)\s]{1,2000})\)/g, (m, t, u) => { const x = safeUrl(u.replace(/&amp;/g, "&")); return x ? `<a href="${esc(x)}"${/^https?:/i.test(x) ? ' target="_blank" rel="noopener noreferrer"' : ""}>${t}</a>` : t; });
  return str(text).slice(0, 20000).split(/\n\s*\n/).map(par => {
    const lines = par.split("\n").filter(l => l.trim());
    if (!lines.length) return "";
    return lines.every(l => /^\s*[-•]\s+/.test(l)) ? `<ul>${lines.map(l => `<li>${inl(l.replace(/^\s*[-•]\s+/, ""))}</li>`).join("")}</ul>` : `<p>${lines.map(inl).join("<br>")}</p>`;
  }).join("");
}
function pick(b) {   // les fiches d'un bloc : périmètre, condition, tri, nombre
  const p = P(); if (!p || !app()) return [];
  const sc = str(b.scope) || "collection";
  let its = state.items.filter(i => i.kind !== "part" && (sc === "all" ? true : sc === "wish" ? isWish(i.list_id) : sc.startsWith("list:") ? i.list_id === sc.slice(5) : !isWish(i.list_id)));
  if (b.cond && typeof b.cond === "object") its = its.filter(i => { try { return p.test(b.cond, i); } catch { return false; } });
  const sx = str(b.sort).trim();
  if (sx) {
    const ex = /[{(]/.test(sx) ? sx : "{" + sx + "}", dir = b.dir === "asc" ? 1 : -1, val = new Map(its.map(i => { const r = p.calc(ex, i); return [i, r.ok ? r.value : null]; }));
    const cmp = (a, c) => typeof a === "number" && typeof c === "number" ? a - c : String(a).localeCompare(String(c), "fr", { numeric: true });
    its = [...its].sort((a, c) => { const x = val.get(a), y = val.get(c), ex = x == null || x === "", ey = y == null || y === ""; return ex || ey ? ex - ey : cmp(x, y) * dir; });
  }
  return its.slice(0, num(b.limit, 1, 1000, 60));
}
const spanOf = b => `grid-column:span ${({ 2: 3, 3: 2 })[b.w] || 6}`;
function blockHtml(b) {
  const k = str(b.k), st = spanOf(b), p = P(), priv = !PUBLIC && app() && !!p;
  if (k === "titre") { const l = [2, 3, 4].includes(+b.level) ? +b.level : 2; return `<h${l} class="bo-pb" style="${st}">${esc(str(b.text))}</h${l}>`; }
  if (k === "texte") return `<div class="bo-pb bo-pb-texte" style="${st}">${rich(b.text)}</div>`;
  if (k === "note") return `<div class="bo-pb bo-pb-note" style="${st};${color(b.color) ? "--c:" + b.color : ""}">${rich(b.text)}</div>`;
  if (k === "image") { const u = safeUrl(b.url), l = safeUrl(b.link); if (!u) return "";
    const img = `<img src="${esc(u)}" alt="${esc(str(b.text))}" loading="lazy" style="${str(b.width) !== "" ? "width:" + num(b.width, 10, 3000, 400) + "px" : ""}">`;
    return `<figure class="bo-pb" style="${st}">${l ? `<a href="${esc(l)}"${/^https?:/i.test(l) ? ' target="_blank" rel="noopener noreferrer"' : ""}>${img}</a>` : img}${str(b.text).trim() ? `<figcaption>${esc(b.text)}</figcaption>` : ""}</figure>`; }
  if (k === "bouton") return `<div class="bo-pb" style="${st};text-align:${["left", "center", "right"].includes(b.align) ? b.align : "left"}"><button type="button" class="btn${b.primary === true ? " primary" : ""}" data-bo-b="${esc(str(b.id))}">${esc(str(b.text) || "Bouton")}</button></div>`;
  if (k === "sep") return `<hr class="bo-pb" style="${st}">`;
  if (k === "espace") return `<div class="bo-pb" style="${st};height:${num(b.h, 2, 600, 24)}px"></div>`;
  if (k === "html") return `<div class="bo-pb bo-pb-html" style="${st}">${sanitize(b.html)}</div>`;
  if (k === "cadre") { const u = safeUrl(b.url); return /^(https?:|\/)/i.test(u) ? `<iframe class="bo-pb bo-pb-cadre" style="${st};height:${num(b.h, 80, 3000, 480)}px" src="${esc(u)}" loading="lazy" referrerpolicy="no-referrer" sandbox="allow-scripts allow-same-origin allow-popups allow-forms" title="${esc(str(b.text))}"></iframe>` : ""; }
  if (!priv) return "";   // blocs de données : seulement sur le site connecté
  if (k === "fiches") { const its = pick(b);
    return `<div class="bo-pb bo-pb-fiches" style="${st}">${its.length ? `<div class="grid">${its.map(i => `<article class="card bo-pcard" data-bo-open="${esc(i.id)}"><div class="pic"><img src="${esc(thumb(itemImage(i)) || "")}" alt="" loading="lazy"></div>
      <div class="body"><div class="num">${esc(i.number && i.number !== "custom" ? i.number : "")}${i.quantity > 1 ? " · ×" + i.quantity : ""}</div><div class="name">${esc(itemName(i))}</div>
      <div class="foot"><span class="value">${i.total_value != null ? esc(money(i.total_value)) : ""}</span></div></div></article>`).join("")}</div>` : `<div class="bo-pb-empty">${esc(str(b.empty) || "Aucune fiche ne correspond.")}</div>`}</div>`; }
  if (k === "total") { const its = pick({ ...b, sort: "", limit: 100000 }), ag = str(b.agg) || "count"; let v = its.length, fmt = str(b.fmt) || (ag === "count" ? "entier" : "");
    if (ag !== "count") { const vs = its.map(i => { const r = p.calc(str(b.expr), i); return r.ok && typeof r.value === "number" && isFinite(r.value) ? r.value : null; }).filter(x => x != null);
      v = !vs.length ? null : ag === "sum" ? vs.reduce((a, c) => a + c, 0) : ag === "avg" ? vs.reduce((a, c) => a + c, 0) / vs.length : ag === "min" ? Math.min(...vs) : ag === "max" ? Math.max(...vs) : vs.length; }
    return `<div class="bo-pb stat bo-ptile" style="${st}"><div class="lbl">${esc(str(b.text) || "Total")}</div><div class="val">${esc(v == null ? "—" : p.show(v, fmt) || "—")}</div></div>`; }
  if (k === "tableau") { const its = pick(b), vars = p.vars(), cols = arr(b.cols).map(str).filter(Boolean).slice(0, 12);
    const use = cols.length ? cols : ["numero", "nom", "valeur"];
    const head = use.map(c => `<th>${esc(vars.find(v => v.id === c)?.label || c)}</th>`).join("");
    const rows = its.map(i => `<tr data-bo-open="${esc(i.id)}">${use.map(c => { const r = p.calc(/[{(]/.test(c) ? c : "{" + c + "}", i); return `<td>${esc(r.ok ? p.show(r.value, vars.find(v => v.id === c)?.fmt || "") : "")}</td>`; }).join("")}</tr>`).join("");
    return `<div class="bo-pb bo-pb-tableau" style="${st}">${its.length ? `<table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table>` : `<div class="bo-pb-empty" style="padding:10px 12px">${esc(str(b.empty) || "Aucune fiche ne correspond.")}</div>`}</div>`; }
  return "";
}
function pageHtml(pg) {
  const head = pg.head === false ? "" : `<div class="bo-pb-head"><h1>${esc((str(pg.icon).trim() ? str(pg.icon).trim().slice(0, 8) + " " : "") + (str(pg.title) || "Page"))}</h1></div>`;
  return head + arr(pg.blocks).filter(b => b && typeof b === "object" && !b.off).slice(0, 400).map(b => { try { return blockHtml(b); } catch (e) { console.warn("BO bloc", e); return ""; } }).join("");
}
function drawPage(pg) {
  const host = D.getElementById("boPage"); if (!host || !pg) return;
  const data = app() ? state.items.length + "|" + (state.items[0]?.updated_at || "") : "";
  const sig = stamp + "|" + JSON.stringify(pg) + "|" + data;
  if (pageSig === sig) return;
  pageSig = sig;
  host.style.maxWidth = str(pg.width) !== "" ? num(pg.width, 320, 4000, 1100) + "px" : "";
  host.innerHTML = pageHtml(pg);
}
function openPage(id) {
  const pg = pagesOn().find(p => p.id === id || p.slug === id);
  if (!pg || !app()) { try { toast("Cette page n'existe plus"); } catch {} return false; }
  const main = D.querySelector(".main"); if (!main) return false;
  let host = D.getElementById("boPage");
  if (!host) { host = D.createElement("section"); host.id = "boPage"; host.className = "bo-x"; main.prepend(host); }
  openId = pg.id; pageFor = state.current; pageSig = "";
  D.body.classList.add("bo-page-on");
  try { setMenu(false); } catch {}
  drawPage(pg); W.scrollTo(0, 0); schedule();
  return true;
}
function closePage() {
  if (!openId) return;
  openId = null; pageSig = "";
  D.body.classList.remove("bo-page-on");
  D.getElementById("boPage")?.remove();
  schedule();
}
D.addEventListener("click", e => {   // on va ailleurs dans le site (menu, boutons du haut, logo) : la page créée se referme
  if (!openId) return;
  const t = e.target.nodeType === 1 ? e.target : e.target.parentElement;
  if (t && t.closest(".sidebar .nav-item:not(.bo-plink), .sidebar .bo-vlink, .topbar .top-views button, .topbar .brand, #btnAdd")) closePage();
}, true);
function pagesPass() {
  if (PAGE === "page") { const pg = pagesOn()[0], host = D.getElementById("boPage"); if (pg && host) { drawPage(pg); const t = str(pg.title).trim(); if (t && D.title !== t) D.title = t; } return; }
  if (PUBLIC || !app()) return;
  const sb = D.getElementById("sidebar"), want = pagesOn().filter(p => p.menu !== false);
  if (sb) {
    all(":scope > .bo-plink", sb).forEach(a => { if (!want.some(p => p.id === a.dataset.boPage)) a.remove(); });
    for (const pg of want) {
      let a = all(":scope > .bo-plink", sb).find(x => x.dataset.boPage === pg.id);
      if (!a) { a = D.createElement("button"); a.type = "button"; a.className = "nav-item bo-plink bo-x"; a.dataset.boPage = pg.id; a.dataset.boKey = "bo-page-" + pg.id; a.innerHTML = `<span class="nm"></span>`;
        a.onclick = () => openPage(a.dataset.boPage); (D.getElementById("shareNav") || D.getElementById("wishNav") || sb.lastElementChild)?.after(a); }
      const t = (str(pg.icon).trim() ? str(pg.icon).trim().slice(0, 8) : "📄") + " " + (str(pg.title) || "Page");
      if (a.firstChild.textContent !== t) a.firstChild.textContent = t;
      if (a.classList.contains("on") !== (openId === pg.id)) a.classList.toggle("on", openId === pg.id);
    }
  }
  if (!openId) return;
  const pg = pagesOn().find(p => p.id === openId);
  if (!pg || state.current !== pageFor) return closePage();
  if (!D.getElementById("boPage")) { const main = D.querySelector(".main"); if (!main) return; const host = D.createElement("section"); host.id = "boPage"; host.className = "bo-x"; main.prepend(host); pageSig = ""; }
  drawPage(pg);
}

/* ------------------------------------------------------------------ 6. comportements */
let started = false, sortFor = null, mergeOff = null;
let trendSig = null;   // (dernier réglage des flèches vu par l'aperçu)
function behavPass() {
  const b = obj(cfg().behav);
  const t = str(b.title).trim().slice(0, 120);
  if (t && PAGE === "app" && D.title !== t) D.title = t;
  if (PUBLIC || !app() || !arr(state.lists).length) return;
  if (!started) {   // une seule fois, quand les données sont là (jamais dans l'aperçu du back office, ni si l'adresse demande déjà quelque chose)
    started = true;
    if (!ADMIN() && !location.hash && !/[?&](item|fig|list|s)=/.test(location.search)) {
      try { if (["sets", "figs", "all"].includes(b.view)) toggleView(b.view); } catch {}
      const s = str(b.start), i = s.indexOf(":"), k = s.slice(0, i), v = s.slice(i + 1);
      if (i > 0 && v) setTimeout(() => act({ k, v }), 0);
    }
  }
  {   // apparence des flèches de variation (Comportements → Prix et variations) : l'aperçu suit le brouillon tout de suite
    const sig = JSON.stringify([b.trend || null, b.noTrend === true]);
    if (trendSig !== sig) { const first = trendSig === null; trendSig = sig; if (!first) try { trendSync(); render(); } catch {} }
  }
  if (mergeOff !== (b.noMerge === true)) {   // « ne pas regrouper les figurines identiques » coché ou décoché : les cartes suivent tout de suite
    const first = mergeOff === null; mergeOff = b.noMerge === true;
    if (!first || mergeOff) try { mergeFigs(); render(); } catch {}
  }
  const so = obj(b.sorts), sel = D.getElementById("sort");   // tri par défaut selon le genre de liste (tant que vous n'en avez pas choisi un pour cette liste)
  if (sel && sortFor !== state.current) {
    sortFor = state.current;
    try {
      const kind = state.current === ALL ? "all" : isWish(state.current) ? "wishlist" : isPartsList(state.current) ? "" : "collection", want = str(so[kind]);
      if (want && !state.sortBy?.[state.current] && sel.value !== want && [...sel.options].some(o => o.value === want && !o.disabled)) { sel.value = want; render(); }
    } catch {}
  }
}
D.addEventListener("keydown", e => {   // raccourcis clavier (jamais pendant une saisie)
  const ks = arr(obj(cfg().behav).keys).filter(k => k && str(k.key).trim() && obj(k.act).k);
  if (!ks.length || e.repeat || D.documentElement.matches(".bo-picking, .bo-moving")) return;
  const t = e.target;
  if (t && t.nodeType === 1 && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
  const key = str(e.key).toLowerCase();
  const k = ks.find(k => str(k.key).trim().toLowerCase() === key && !!k.ctrl === (e.ctrlKey || e.metaKey) && !!k.alt === e.altKey);
  if (k) { e.preventDefault(); act(k.act); }
});

/* ------------------------------------------------------------------ branchement sur bo.js */
const step = (name, f) => { try { f(); } catch (e) { console.warn("BO max " + name, e); } };
/* éléments d'origine modifiés (back office → 🧩 Éléments d'origine, cfg.native) : tris, filtres, tuiles — renommés, masqués, réordonnés */
let natSortSig = "";
function nativePass() {
  const N = obj(cfg().native);
  const conf = k => { const c = obj(N[k]); return { hid: arr(c.hidden), lab: obj(c.labels), ord: arr(c.order) }; };
  const reorder = (els, keyOf, ord) => { if (!els.length) return; const par = els[0].parentNode, idx = e => { const p = ord.indexOf(keyOf(e)); return p < 0 ? 1000 + +e.dataset.natI : p; };
    const sorted = [...els].sort((a, b) => idx(a) - idx(b)); if (sorted.every((e, i) => e === els[i])) return;
    const anchor = els[els.length - 1].nextSibling; for (const e of sorted) par.insertBefore(e, anchor); };
  {   /* tris : les options de #sort (gardent leur valeur ; « Trier par » les relit) */
    const sel = D.getElementById("sort");
    if (sel) { const c = conf("sorts"), opts = [...sel.options];
      opts.forEach((o, i) => { if (o.dataset.natI == null) { o.dataset.natI = i; o.dataset.natOrig = o.textContent; }
        if (!o.value.startsWith("bo:")) { o.textContent = str(c.lab[o.value]).trim() || o.dataset.natOrig; if (c.hid.includes(o.value)) o.dataset.natHide = "1"; else delete o.dataset.natHide; } });
      reorder(opts, o => o.value, c.ord);
      const sig = JSON.stringify(N.sorts || null); if (sig !== natSortSig) { natSortSig = sig; try { syncSortMenu(); } catch {} } } }
  {   /* filtres : les cases de « ⚙️ Filtres » (étiquettes, options des cartes) */
    const pop = D.getElementById("filtPop");
    if (pop) { const c = conf("filters"), labs = [...pop.querySelectorAll("label")].filter(l => l.querySelector("[data-ftag], [data-cardopt]"));
      const keyOf = l => { const i = l.querySelector("[data-ftag], [data-cardopt]"); return i.dataset.ftag || i.dataset.cardopt; };
      labs.forEach((l, i) => { l.dataset.natI = i; const k = keyOf(l), tn = [...l.childNodes].find(n => n.nodeType === 3 && n.textContent.trim());
        if (tn) { if (l.dataset.natOrig == null) l.dataset.natOrig = tn.textContent.trim(); tn.textContent = " " + (str(c.lab[k]).trim() || l.dataset.natOrig) + " "; }
        l.hidden = c.hid.includes(k); l.style.display = c.hid.includes(k) ? "none" : ""; });
      const tags = labs.filter(l => l.querySelector("[data-ftag]")), opts = labs.filter(l => l.querySelector("[data-cardopt]"));
      reorder(tags, keyOf, c.ord); reorder(opts, keyOf, c.ord); } }
  {   /* tuiles du haut : repérées par leur titre d'origine */
    const st = D.getElementById("stats");
    if (st) { const c = conf("tiles"), tiles = [...st.querySelectorAll(".stat")];
      const keyOf = t => t.dataset.natOrig;
      tiles.forEach((t, i) => { const l = t.querySelector(".lbl"); if (!l) return; if (t.dataset.natOrig == null || (t.dataset.natLbl !== l.textContent)) { t.dataset.natOrig = l.textContent.trim(); }
        const k = t.dataset.natOrig; t.dataset.natI = i; const nm = str(c.lab[k]).trim(); if (nm) { l.textContent = nm; } t.dataset.natLbl = l.textContent;
        t.style.display = c.hid.includes(k) ? "none" : ""; });
      const byPar = new Map(); for (const t of tiles) { if (!byPar.has(t.parentNode)) byPar.set(t.parentNode, []); byPar.get(t.parentNode).push(t); }
      for (const g of byPar.values()) reorder(g, keyOf, c.ord); } }
}
const pass = () => { step("étiquettes", tagsPass); step("liens", hrefPass); step("réglages", settingsPass); step("pages", pagesPass); step("comportements", behavPass); step("éléments d'origine", nativePass); };
HOOKS.apply.push(() => { stamp++; pageSig = ""; step("style", buildCss); });
HOOKS.refresh.push(pass);
step("style", buildCss);
if (PAGE === "page") D.addEventListener("DOMContentLoaded", () => { D.body.classList.add("bo-public-page"); pass(); });

/* ------------------------------------------------------------------ pour le back office (aperçu) */
B.max = {
  TAGS: TAGS.map(([key, label, kind]) => ({ key, label, kind })), safeUrl, sanitize, keyOf, act, actOk, openPage, closePage,
  page: () => openId,
  tagsSeen() { tagsPass(); const n = {}; for (const el of all("[data-bo-tag]")) n[el.dataset.boTag] = (n[el.dataset.boTag] || 0) + 1; return n; },
  settings() {   // sections de la page « Réglages » de l'application (elle doit être ouverte dans l'aperçu)
    settingsPass();
    const grid = D.querySelector(".settings-page .set-grid");
    return grid ? [...grid.children].filter(f => f.dataset.boSet).map(f => ({ key: f.dataset.boSet, label: f.dataset.boLab || f.dataset.boSet })) : null;
  },
  openSettings() { if (!app()) return false; if (!D.querySelector(".settings-page")) D.getElementById("btnSettings")?.click(); return true; },
  closeSettings() { D.querySelector(".settings-page [data-x]")?.click(); },
  count(b) { try { return pick({ ...obj(b), sort: "", limit: 100000 }).length; } catch { return 0; } },
};
schedule();
/* script libre (Comportements → Avancé) : exécuté UNE fois, au chargement de l'appli privée — jamais sur une page publique ; « ?bo=off » le coupe */
try {
  const _ = W.BO._, js = _.cfg().js;
  if (js && !_.PUBLIC && _.PAGE === "app") {
    const run = () => { try { new Function("BO", String(js))(W.BO); } catch (e) { console.warn("Back office — script libre :", e); } };
    if (D.readyState === "complete") setTimeout(run, 0); else W.addEventListener("load", () => setTimeout(run, 0));
  }
} catch (e) { console.warn(e); }
})();

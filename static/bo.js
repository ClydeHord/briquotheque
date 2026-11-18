/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
/* Briquothèque — BACK OFFICE : moteur de personnalisation.
   Chargé sur chaque page (avant l'application). Il lit les réglages faits dans /backoffice (window.BO_CFG, glissés par le serveur)
   et les applique PAR-DESSUS l'application, sans modifier son code :
     1. apparence (couleurs, arrondis, police, logo)                 → une feuille de style générée
     2. textes (remplacements)                                       → les textes de la page sont réécrits à l'affichage
     3. règles sur un élément (masquer, style, position)             → feuille de style
     4. éléments ajoutés (texte, bouton, image, séparateur)          → insérés à côté de l'élément choisi
     5. fiches : ordre et visibilité des blocs, blocs et champs personnalisés, liens automatiques
     6. menu : ordre, visibilité, raccourcis ; cartes des listes : taille, parties affichées, champs personnalisés
   Dans l'aperçu du back office (page affichée dans /backoffice), il applique le BROUILLON en direct et offre le mode
   « cliquer pour modifier ». Une page ouverte avec ?bo=off est servie sans personnalisation (secours). */
(() => {
"use strict";
if (window.BO) return;
const W = window, D = document;
let ADMIN = null;   // la page /backoffice, quand cette page est son aperçu (sinon null)
try { if (W.parent !== W && W.parent.BO_ADMIN) ADMIN = W.parent.BO_ADMIN; } catch {}
let cfg = (ADMIN && ADMIN.cfg()) || W.BO_CFG || {};
const PUBLIC = !!W.BO_PUBLIC, path = location.pathname;
const PAGE = path.startsWith("/s/") ? "partage" : /^\/(wishlist|collection|a-surveiller)/.test(path) ? "public"
  : path.startsWith("/nouveautes") ? "nouveautes" : path.startsWith("/login") ? "connexion" : path.startsWith("/p/") ? "page" : "app";
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const safeSel = s => { try { D.createDocumentFragment().querySelector(s); return true; } catch { return false; } };
const matches = (el, s) => { try { return el.matches(s); } catch { return false; } };
const all = (s, r = D) => { try { return [...r.querySelectorAll(s)]; } catch { return []; } };
const cssVal = v => String(v).replace(/[{}<>;]/g, "");
const safeUrl = u => { u = String(u ?? "").trim().replace(/[\u0000-\u001f\u007f]/g, "");   // adresse d'un lien ou d'une image : http(s), mailto, tel, adresse du site, image intégrée — rien d'autre
  return !u || /^(https?:|mailto:|tel:|\/|#|\?|data:image\/(png|jpe?g|gif|webp|svg\+xml|x-icon|avif)[;,])/i.test(u) ? u : /^[a-z][a-z0-9+.-]*:/i.test(u) ? "" : /^[\w-]+(\.[\w-]+)+([/:?#]|$)/.test(u) ? "https://" + u : u; };
const app = () => typeof state !== "undefined" && PAGE === "app";   // l'application (pas une page publique), une fois chargée
let ghost = false;   // aperçu : éléments masqués montrés en transparence (pour pouvoir les recliquer)
/* crochets : bo-plus.js (formules, règles « si… alors », tuiles, vues) s'y inscrit — refresh : la page a changé ; sheet : une fiche est affichée ; apply : réglages relus */
const HOOKS = { refresh: [], sheet: [], apply: [] };
const run = (k, ...a) => { for (const f of HOOKS[k]) try { f(...a); } catch (e) { console.warn("BO+ " + k, e); } };
/* un élément déplacé à la souris garde ses réglages : son sélecteur d'origine vaut aussi pour sa nouvelle place (dans son enveloppe <bo-mv>) */
function wide(sel) {
  let out = sel;
  for (const m of cfg.moves || []) if (m.id && m.sel && (sel === m.sel || sel.startsWith(m.sel + " "))) out += `, bo-mv[data-bo-mv="${m.id}"] > *${sel.slice(m.sel.length)}`;
  return out;
}

/* ------------------------------------------------------------------ 1. feuille de style générée */
const FONTS = {
  arrondie: 'ui-rounded, "Nunito", "Varela Round", "Segoe UI", system-ui, sans-serif', serif: 'Georgia, "Times New Roman", serif',
  mono: 'ui-monospace, "Cascadia Mono", Consolas, "Courier New", monospace', humaniste: 'Verdana, "Trebuchet MS", "DejaVu Sans", sans-serif',
  etroite: '"Arial Narrow", "Roboto Condensed", "Liberation Sans Narrow", Arial, sans-serif',
};
const CARD_PARTS = {   // parties d'une carte de liste (panneau « Cartes »)
  num: ".card .body > .num", meta: '.card .body > .meta[class="meta"]', tags: ".card .tagline", badges: ".card .badges", value: ".card .foot",
  listtag: ".card .list-tag", todo: ".card .todo-tag", qty: ".card .qty-tag", sel: ".card .sel", prices3: ".card .prices3",
  insets: ".card .in-sets-line", pcsunit: ".card .pcs-unit", img: ".card .pic",
};
const BASE_CSS = `
.bo-sec .bo-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px 14px}
.bo-f{display:flex;flex-direction:column;gap:4px;min-width:0}
.bo-f.bo-wide{grid-column:1/-1}
.bo-l{font-size:13px;font-weight:600;color:var(--muted)}
.bo-h{font-size:12px;color:var(--muted)}
.bo-f input[type=text],.bo-f input[type=number],.bo-f input[type=date],.bo-f input[type=url],.bo-f select,.bo-f textarea{width:100%}
.bo-inl{display:flex;gap:6px;align-items:center}.bo-inl>input{flex:1;min-width:0}
.bo-chk{display:flex;gap:8px;align-items:center;font-weight:600;cursor:pointer}
.bo-multi{display:flex;flex-wrap:wrap;gap:6px}
.bo-multi label{display:inline-flex;gap:6px;align-items:center;padding:4px 10px;border:1px solid var(--line);border-radius:999px;cursor:pointer;font-size:13px}
.bo-multi label:has(input:checked){border-color:var(--red);background:var(--accent-bg)}
.bo-stars{display:flex;gap:2px}.bo-stars button{background:none;border:0;padding:0 2px;font-size:24px;line-height:1;cursor:pointer;color:var(--line)}
.bo-stars button.on{color:var(--yellow)}
.bo-chips{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.bo-chip{display:inline-flex;gap:6px;align-items:center;padding:4px 6px 4px 10px;border:1px solid var(--line);border-radius:999px;background:var(--bg);font-size:13px;cursor:pointer;max-width:100%}
.bo-chip>span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bo-chip>button{border:0;background:none;cursor:pointer;color:var(--muted);font-size:14px;padding:0 4px}
.bo-mini{border:1px dashed var(--line);background:none;border-radius:999px;padding:4px 10px;font-size:13px;cursor:pointer;color:var(--muted)}
.bo-pop{position:fixed;inset:0;z-index:9000;background:rgba(10,12,16,.55);display:grid;place-items:center;padding:16px}
.bo-pop>div{background:var(--panel);color:var(--ink);border-radius:14px;padding:16px;width:min(520px,100%);max-height:80vh;display:flex;flex-direction:column;gap:10px;box-shadow:0 10px 40px rgba(0,0,0,.3)}
.bo-pop .bo-res{overflow:auto;display:flex;flex-direction:column;gap:2px}
.bo-pop .bo-res button{text-align:left;border:0;background:none;padding:8px 10px;border-radius:8px;cursor:pointer;color:inherit}
.bo-pop .bo-res button:hover{background:var(--bg)}
.card .bo-meta{display:flex;flex-direction:column;gap:1px}
.bo-add{display:block}.bo-add.bo-add-sep{height:1px;background:var(--line);margin:10px 0}
.bo-add.bo-add-titre{font-weight:800;font-size:17px;margin:10px 0 4px}
.bo-add.bo-add-texte{margin:6px 0;white-space:pre-wrap}
.bo-add.bo-add-bouton{display:inline-flex;margin:4px 4px 4px 0;text-decoration:none}
.bo-add.bo-add-image{max-width:100%;margin:6px 0}
.bo-ribbon{position:fixed;left:10px;bottom:10px;z-index:8000;display:flex;gap:8px;align-items:center;background:#1d4ed8;color:#fff;font:600 12px system-ui,sans-serif;padding:6px 10px;border-radius:999px;box-shadow:0 2px 10px rgba(0,0,0,.25);opacity:.92}
.bo-ribbon a{color:#fff;text-decoration:underline}.bo-ribbon button{border:0;background:none;color:#fff;cursor:pointer;font-size:14px;padding:0 2px}
.bo-hl,.bo-hl-sel{position:fixed;z-index:99990;pointer-events:none;border-radius:4px;display:none}
.bo-hl{border:2px solid #2563eb;background:rgba(37,99,235,.10)}
.bo-hl-sel{border:2px solid #f59e0b;background:rgba(245,158,11,.10)}
.bo-tip{position:fixed;z-index:99991;pointer-events:none;background:#111827;color:#fff;font:600 12px system-ui,sans-serif;padding:3px 8px;border-radius:6px;white-space:nowrap;display:none;max-width:70vw;overflow:hidden;text-overflow:ellipsis}
.bo-flash{outline:3px solid #f59e0b!important;outline-offset:2px}
html.bo-picking, html.bo-picking *{cursor:crosshair!important}
bo-mv{display:contents}[data-bo-ph]{display:none!important}
.bo-mvbar{position:fixed;z-index:99992;pointer-events:none;background:#16a34a;border-radius:3px;display:none;box-shadow:0 0 0 2px rgba(255,255,255,.75)}
.bo-ctx{position:fixed;z-index:99995;min-width:236px;max-width:330px;background:#111827;color:#f9fafb;border-radius:10px;padding:5px;box-shadow:0 10px 30px rgba(0,0,0,.4);font:500 13px system-ui,sans-serif;cursor:default!important}
.bo-ctx *{cursor:default!important}.bo-ctx-h{padding:5px 9px 6px;font-weight:700;font-size:12px;color:#fbbf24;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bo-ctx button{display:flex;gap:8px;align-items:center;width:100%;text-align:left;border:0;background:none;color:inherit;font:inherit;padding:6px 9px;border-radius:6px;cursor:pointer!important}
.bo-ctx button:hover:not(:disabled){background:#374151}.bo-ctx button:disabled{opacity:.38}
.bo-ctx hr{border:0;border-top:1px solid #374151;margin:4px 2px}.bo-ctx button span{width:18px;text-align:center;flex:none}
html.bo-moving, html.bo-moving *{cursor:grab!important;user-select:none!important;-webkit-user-select:none!important}
.bo-calc output{display:block;font-weight:700;font-variant-numeric:tabular-nums;padding:7px 0}
`;
let styleEl = null;
function buildCss() {
  const out = [BASE_CSS], th = cfg.theme || {};
  const vars = o => Object.entries(o || {}).filter(([k, v]) => v && /^[a-z0-9-]+$/.test(k)).map(([k, v]) => `--${k}:${cssVal(v)}`).join(";");
  if (vars(th.both)) out.push(`html:root{${vars(th.both)}}`);
  if (vars(th.light)) out.push(`@media (prefers-color-scheme: light){html:root{${vars(th.light)}}}`);
  if (vars(th.dark)) out.push(`@media (prefers-color-scheme: dark){html:root{${vars(th.dark)}}}`);
  if (th.radius != null && th.radius !== "") out.push(`html:root{--radius:${+th.radius || 0}px}.btn,input,select,textarea{border-radius:${Math.min(+th.radius || 0, 14)}px}fieldset,.card,.modal-box{border-radius:${+th.radius || 0}px}`);
  if (th.font && FONTS[th.font]) out.push(`body,button,input,select,textarea{font-family:"Drapeaux",${FONTS[th.font]}!important}`);
  if (th.zoom && +th.zoom !== 100) out.push(`body{zoom:${Math.max(70, Math.min(160, +th.zoom)) / 100}}`);
  if (th.logo) {
    const im = /^data:image\//.test(th.logo);
    out.push(`.brand .brick{display:none!important}.brand::before{content:${im ? '""' : JSON.stringify(String(th.logo).slice(0, 8))};${im ? `width:30px;height:30px;background:url("${cssVal(th.logo)}") center/contain no-repeat;flex:none` : "font-size:24px;line-height:1"}}`);
  }
  for (const r of cfg.rules || []) {   // règles posées « à la souris » sur un élément
    if (!r.sel || r.off || (r.page && r.page !== PAGE) || !safeSel(r.sel)) continue;
    const d = [];
    if (r.hide) d.push(...(ghost ? ["opacity:.3", "outline:2px dashed #f59e0b"] : ["display:none"]));
    for (const [k, v] of Object.entries(r.css || {})) if (v !== "" && v != null && /^[a-z-]+$/.test(k)) d.push(`${k}:${cssVal(v)}`);
    if (r.order != null && r.order !== "") d.push(`order:${+r.order || 0}`);
    if (d.length) out.push(`${wide(r.sel)}{${d.map(x => x + "!important").join(";")}}`);
  }
  for (const [t, sc] of Object.entries(cfg.sheets || {})) {   // squelette de fiche, par type
    if (!/^[a-z_]+$/.test(t) || !sc) continue;
    const P = `#stepConfig[data-bo-type="${t}"]`, ord = sc.order || [];
    if (ord.length) {
      out.push(`${P}{display:flex;flex-direction:column}${P}>*{flex:none;order:500}${P}>fieldset{margin-block:6px}`);
      ord.forEach((k, i) => out.push(`${P}>[data-bo-key="${CSS.escape(k)}"]{order:${k === "estimate" && i === ord.length - 1 ? 900 : i + 1}}`));
    }
    for (const k of sc.hidden || []) out.push(`${P}>[data-bo-key="${CSS.escape(k)}"]{${ghost ? "opacity:.3;outline:2px dashed #f59e0b" : "display:none!important"}}`);
  }
  const mn = cfg.menu || {};
  if ((mn.order || []).length) {
    out.push(`.sidebar>*{order:500}`);
    mn.order.forEach((k, i) => out.push(`.sidebar>[data-bo-key="${CSS.escape(k)}"]{order:${i + 1}}`));
  }
  for (const k of mn.hidden || []) out.push(`.sidebar>[data-bo-key="${CSS.escape(k)}"]{${ghost ? "opacity:.3;outline:2px dashed #f59e0b" : "display:none!important"}}`);
  const cd = cfg.cards || {};
  if (cd.min) out.push(`.grid{grid-template-columns:repeat(auto-fill,minmax(${Math.max(110, Math.min(520, +cd.min))}px,1fr))!important}`);
  if (cd.ratio && /^\d+\/\d+$/.test(cd.ratio)) out.push(`.card .pic{aspect-ratio:${cd.ratio}!important}`);
  if (cd.lines) out.push(`.card .body > .name{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:${+cd.lines};overflow:hidden}`);
  for (const k of cd.hide || []) if (CARD_PARTS[k]) out.push(`${CARD_PARTS[k]}{display:none!important}`);
  if (cfg.css) out.push(String(cfg.css));
  if (!styleEl) { styleEl = D.createElement("style"); styleEl.id = "bo-style"; }
  if (!styleEl.isConnected) (D.head || D.documentElement).append(styleEl);
  if (styleEl.textContent !== out.join("\n")) styleEl.textContent = out.join("\n");
}

/* ------------------------------------------------------------------ 2. textes : remplacements à l'affichage
   Chaque texte garde son original en mémoire (seenText) : si la règle change ou disparaît, l'original revient. */
const T = { any: false, scoped: [], exact: new Map(), reCS: null, mapCS: new Map(), reCI: null, mapCI: new Map() };
const seenText = new WeakMap(), seenAttr = new WeakMap();
const ATTRS = ["placeholder", "title", "aria-label"], SKIP = "script,style,textarea,.bo-ui,[contenteditable]";
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
function buildTexts() {
  T.scoped = []; T.exact = new Map(); T.mapCS = new Map(); T.mapCI = new Map();
  const list = [...(cfg.texts || [])];
  const brand = (cfg.theme?.brand || "").trim();
  if (brand && brand !== "Briquothèque") list.push({ from: "Briquothèque", to: brand, mode: "mot" });
  for (const [t, sc] of Object.entries(cfg.sheets || {}))   // blocs de fiche renommés : le titre du bloc, pour ce type de fiche
    for (const [k, v] of Object.entries(sc?.labels || {})) if (v) list.push({ any: true, to: v, sel: `#stepConfig[data-bo-type="${t}"] > [data-bo-key="${CSS.escape(k)}"] > legend` });
  for (const r of list) {
    const from = String(r.from ?? "").trim();
    if ((!from && !r.any) || r.to == null || r.off || (r.page && r.page !== PAGE)) continue;
    if (r.sel) { if (safeSel(r.sel)) T.scoped.push({ from, to: String(r.to), sel: r.sel, attr: r.attr || "", any: !!r.any }); }
    else if (r.mode === "mot") (r.ci ? T.mapCI : T.mapCS).set(r.ci ? from.toLowerCase() : from, String(r.to));
    else T.exact.set(from, String(r.to));
  }
  const mk = (m, fl) => m.size ? new RegExp("(?<![\\p{L}\\p{N}])(" + [...m.keys()].sort((a, b) => b.length - a.length).map(reEsc).join("|") + ")(?![\\p{L}\\p{N}])", fl) : null;
  try { T.reCS = mk(T.mapCS, "gu"); T.reCI = mk(T.mapCI, "giu"); } catch { T.reCS = T.reCI = null; }
  T.any = !!(T.scoped.length || T.exact.size || T.reCS || T.reCI);
}
const caseLike = (m, to) => !to ? to : m.length > 1 && m === m.toUpperCase() && m !== m.toLowerCase() ? to.toUpperCase()
  : m[0] !== m[0].toLowerCase() ? to[0].toUpperCase() + to.slice(1) : m[0] !== m[0].toUpperCase() ? to[0].toLowerCase() + to.slice(1) : to;
function tr(s, el, attr) {
  if (!T.any || !s) return s;
  const t = s.trim();
  if (!t) return s;
  if (el) for (const r of T.scoped) if ((r.any ? !attr : r.from === t) && r.attr === (attr || "") && matches(el, r.sel)) return s.replace(t, () => r.to);
  const ex = T.exact.get(t);
  if (ex != null) return s.replace(t, () => ex);
  let o = s;
  if (T.reCS) o = o.replace(T.reCS, m => T.mapCS.get(m) ?? m);
  if (T.reCI) o = o.replace(T.reCI, m => { const to = T.mapCI.get(m.toLowerCase()); return to == null ? m : caseLike(m, to); });
  return o;
}
function trText(n) {
  const p = n.parentElement;
  if (!p || p.closest(SKIP)) return;
  const cur = n.nodeValue, m = seenText.get(n), src = m && m.out === cur ? m.src : cur, out = tr(src, p);
  if (out !== src || m) seenText.set(n, { src, out });
  if (out !== cur) n.nodeValue = out;
}
function trAttrs(el) {
  if (el.closest(SKIP)) return;
  for (const a of ATTRS) {
    const cur = el.getAttribute(a);
    if (cur == null) continue;
    let m = seenAttr.get(el);
    const e = m?.[a], src = e && e.out === cur ? e.src : cur, out = tr(src, el, a);
    if (out !== src || e) { if (!m) seenAttr.set(el, m = {}); m[a] = { src, out }; }
    if (out !== cur) el.setAttribute(a, out);
  }
}
function trTree(root) {
  if (root.nodeType === 3) return trText(root);
  if (root.nodeType !== 1) return;
  const w = D.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) trText(n);
  if (root.matches("[placeholder],[title],[aria-label]")) trAttrs(root);
  root.querySelectorAll("[placeholder],[title],[aria-label]").forEach(trAttrs);
}
const srcText = n => { const m = seenText.get(n); return m && m.out === n.nodeValue ? m.src : n.nodeValue; };   // texte d'origine d'un nœud
for (const k of ["alert", "confirm", "prompt"]) {   // fenêtres du navigateur : mêmes remplacements
  const o = W[k];
  W[k] = function (m, ...r) { return o.call(W, typeof m === "string" ? tr(m) : m, ...r); };
}

/* ------------------------------------------------------------------ 3. éléments ajoutés à côté d'un élément choisi */
function applyAdds() {
  const want = new Map((cfg.adds || []).filter(a => a.sel && !a.off && (!a.page || a.page === PAGE) && safeSel(a.sel)).map(a => [a.id, a]));
  all(".bo-add").forEach(n => { const a = want.get(n.dataset.boAdd); if (!a || n.dataset.boSig !== JSON.stringify(a)) n.remove(); });
  for (const a of want.values()) {
    const sig = JSON.stringify(a);
    for (const t of all(wide(a.sel)).slice(0, 40)) {
      if (t.closest(".bo-add,.bo-ui")) continue;
      const pos = a.pos || "after";
      const have = pos === "before" ? t.previousElementSibling : pos === "after" ? t.nextElementSibling : pos === "start" ? t.firstElementChild : t.lastElementChild;
      const near = (pos === "before" || pos === "after" ? [...(t.parentElement?.children || [])] : [...t.children]).find(n => n.dataset?.boAdd === a.id && n.dataset.boFor === (t.dataset.boUid || ""));
      if (near || (have && have.dataset?.boAdd === a.id)) continue;
      if (!t.dataset.boUid) t.dataset.boUid = Math.random().toString(36).slice(2, 9);
      const k = a.kind || "texte";
      const n = D.createElement(k === "bouton" ? "a" : k === "image" ? "img" : "div");
      n.className = `bo-add bo-x bo-add-${k}` + (k === "bouton" ? " btn" : "");
      n.dataset.boAdd = a.id; n.dataset.boSig = sig; n.dataset.boFor = t.dataset.boUid;
      if (k === "image") { n.src = safeUrl(a.url); n.alt = a.text || ""; if (a.w) n.style.width = (+a.w || 100) + "px"; }
      else if (k === "bouton") { n.textContent = a.text || "Lien"; n.href = safeUrl(a.url) || "#"; if (!a.same) { n.target = "_blank"; n.rel = "noopener"; } }
      else if (k !== "sep") n.textContent = a.text || "";
      pos === "before" ? t.before(n) : pos === "after" ? t.after(n) : pos === "start" ? t.prepend(n) : t.append(n);
    }
  }
}

/* ------------------------------------------------------------------ 3 bis. éléments déplacés à la souris (cfg.moves)
   Chaque déplacement : { id, sel (l'élément), to (l'élément repère), pos: "before" | "after", page }.
   L'élément est glissé dans une enveloppe <bo-mv> (transparente pour la mise en page : display:contents) posée à côté du repère ;
   un jeton caché [data-bo-ph], de même balise, garde sa place d'origine (les autres réglages qui comptent les éléments restent justes).
   Les sélecteurs se lisent toujours sur la page D'ORIGINE : avant de les relire, tout est remis en place, puis redéplacé. */
const mvSig = m => m.sel + "|" + m.to + "|" + (m.pos || "after");
const mvW = id => all("bo-mv").find(w => w.dataset.boMv === id), mvPh = id => all("[data-bo-ph]").find(x => x.dataset.boPh === id);
function undoMove(id) {   // l'élément retourne à sa place d'origine (si elle existe encore)
  const w = mvW(id), ph = mvPh(id), el = w && w.firstElementChild;
  if (w && el && ph) ph.replaceWith(el);
  if (w) w.remove();
  if (ph && ph.isConnected) ph.remove();
}
let mvPass = 0, mvPassT = 0;
function applyMoves() {
  const want = (cfg.moves || []).filter(m => m.id && m.sel && m.to && !m.off && (!m.page || m.page === PAGE) && safeSel(m.sel) && safeSel(m.to));
  const have = all("bo-mv");
  if (!want.length && !have.length) return;
  const by = new Map(want.map(m => [m.id, m]));
  for (const w of have) { const m = by.get(w.dataset.boMv); if (!m || w.dataset.boSig !== mvSig(m)) undoMove(w.dataset.boMv); }
  all("[data-bo-ph]").forEach(x => { if (!mvW(x.dataset.boPh)) x.remove(); });
  const ok = m => { const w = mvW(m.id); if (!w || !w.firstElementChild || !mvPh(m.id)) return false;
    const t = w._boT; return !!t && t.isConnected && ((m.pos || "after") === "before" ? w.nextElementSibling === t : w.previousElementSibling === t); };
  const todo = want.filter(m => !ok(m));
  if (!todo.length) return;
  if (!todo.some(m => mvW(m.id) || (all(m.sel)[0] && all(m.to)[0]))) return;   // rien de ce qui manque n'est à l'écran (ex. : élément d'une fiche fermée)
  const now = Date.now();
  if (now - mvPassT > 2000) { mvPassT = now; mvPass = 0; }
  if (++mvPass > 6) return;   // garde-fou : jamais de boucle
  for (const m of want) undoMove(m.id);
  let left = want.map(m => ({ m, el: all(m.sel)[0], t: all(m.to)[0] })).filter(x => x.el && x.t && x.el !== x.t && !x.el.contains(x.t) && !x.el.closest(".bo-ui"));
  for (let guard = 0; left.length && guard < 60; guard++) {   // un repère lui-même déplacé : il part d'abord, on se pose ensuite à côté de lui
    const srcs = new Set(left.map(x => x.el)), ready = left.filter(x => !srcs.has(x.t)), batch = ready.length ? ready : [left[0]];
    for (const { m, el, t } of batch) {
      const ph = D.createElement(el.tagName); ph.hidden = true; ph.setAttribute("aria-hidden", "true"); ph.dataset.boPh = m.id;
      el.before(ph);
      const w = D.createElement("bo-mv"); w.dataset.boMv = m.id; w.dataset.boSig = mvSig(m); w._boT = t; w.append(el);
      (m.pos || "after") === "before" ? t.before(w) : t.after(w);
    }
    left = left.filter(x => !batch.includes(x));
  }
}

/* ------------------------------------------------------------------ 4. menu : repères d'ordre + raccourcis personnalisés */
function openList(id) {
  const b = all(".sidebar .nav-item[data-id]").find(x => x.dataset.id === id);
  if (b) return b.click();
  if (!state.lists.some(l => l.id === id)) return toast("Cette liste n'existe plus");
  state.current = id; render(); renderNav();
  if (typeof setMenu === "function") setMenu(false);
}
function goItem(id) {
  if (!state.items.some(i => i.id === id)) return toast("Cette fiche n'existe plus");
  const d = state.draft;
  try { if (d && !modal.hidden && d._sig !== undefined && draftSig() !== d._sig && !confirm("Des modifications ne sont pas enregistrées. Ouvrir quand même l'autre fiche ?")) return; } catch {}
  if (typeof setMenu === "function") setMenu(false);
  openEdit(id);
}
function menu() {
  const sb = D.getElementById("sidebar");
  if (!sb) return;
  let n = 0;
  for (const c of sb.children) {
    if (c.classList.contains("bo-link")) continue;
    const k = c.id || (c.classList.contains("side-sep") ? "sep" + (++n) : c.classList[0]) || c.tagName.toLowerCase();
    if (c.dataset.boKey !== k) c.dataset.boKey = k;
  }
  const want = new Map((cfg.menu?.items || []).map(i => [i.id, i]));
  all(":scope > .bo-link", sb).forEach(a => { if (!want.has(a.dataset.boId)) a.remove(); });
  for (const it of want.values()) {
    let a = all(":scope > .bo-link", sb).find(x => x.dataset.boId === it.id);
    if (!a) {
      a = D.createElement("button"); a.type = "button"; a.className = "nav-item bo-link bo-x"; a.dataset.boId = it.id; a.dataset.boKey = "bo-" + it.id;
      a.innerHTML = `<span class="nm"></span>`;
      a.onclick = () => { const i = (cfg.menu?.items || []).find(x => x.id === a.dataset.boId); if (!i) return;
        if (i.kind === "liste") openList(i.target); else if (i.kind === "fiche") goItem(i.target);
        else if (i.kind === "vue") W.BO.plus?.openView(i.target);
        else if (safeUrl(i.url)) W.open(safeUrl(i.url), i.same ? "_self" : "_blank", "noopener"); };
      sb.append(a);
    }
    if (a.firstChild.textContent !== (it.label || "Raccourci")) a.firstChild.textContent = it.label || "Raccourci";
  }
  /* (le lien vers le back office est dans la page « Réglages » de l'application, section « 🛠 Back office ») */
}

/* ------------------------------------------------------------------ 5. fiches : type, blocs, champs personnalisés, liens */
const SHEET_TYPES = ["set", "fig", "moc", "partial", "mocfig"];
const itemType = i => i.kind === "part" ? "part" : i.kind === "custom" ? (i.custom_type === "fig" ? "mocfig" : i.partial_set ? "partial" : "moc")
  : i.kind === "fig" && !i.as_set ? "fig" : "set";
function sheetType() {   // type de la fiche ouverte
  const d = state.draft;
  if (!d) return "";
  if (d.kind === "custom") {
    const ct = D.querySelector("input[name=cutype]:checked")?.value || d.custom?.type || "set";
    return ct === "fig" ? "mocfig" : D.querySelector("input[name=cukind]:checked")?.value === "partial" ? "partial" : "moc";
  }
  return d.kind === "fig" && !d.item?.as_set ? "fig" : "set";
}
const ownItem = () => { const d = state.draft; if (!d) return null;   // la fiche enregistrée derrière la fenêtre ouverte (figurine d'un set : sa propre fiche)
  return d.item || (d.adjust?.fid && d.adjust.it && state.items.find(i => i.set_orig && i.attached_to === d.adjust.it.id && i.number === d.adjust.fid)) || null; };
const blockKey = c => c.dataset.boKey || c.id || c.classList[0] || c.tagName.toLowerCase();
let xvals = {}, xFor = null;   // valeurs des champs personnalisés de la fiche ouverte
const allFields = () => [...(cfg.fields || []), ...(cfg.calcs || []).map(c => ({ ...c, type: "calc" }))];   // champs saisis, puis champs calculés (formules)
const fieldsFor = t => allFields().filter(f => f.id && !f.off && (!(f.types || []).length || f.types.includes(t)));
const fmtDate = v => /^\d{4}-\d{2}-\d{2}$/.test(v || "") ? v.split("-").reverse().join("/") : v || "";
const nameOf = id => { const i = state.items.find(x => x.id === id); return i ? [i.number && i.number !== "custom" ? i.number : "", i.custom_name || (typeof itemName === "function" ? itemName(i) : i.number)].filter(Boolean).join(" · ") : "(fiche supprimée)"; };

function pickItem(done) {   // petite fenêtre : choisir une fiche à relier
  const p = D.createElement("div"); p.className = "bo-pop bo-ui";
  p.innerHTML = `<div><strong>Relier une fiche</strong><input type="text" placeholder="Nom ou numéro…"><div class="bo-res"></div><button type="button" class="btn">Fermer</button></div>`;
  const inp = p.querySelector("input"), res = p.querySelector(".bo-res");
  const me = ownItem()?.id;
  const draw = () => { const q = inp.value.trim().toLowerCase();
    const list = state.items.filter(i => i.kind !== "part" && i.id !== me && (!q || nameOf(i.id).toLowerCase().includes(q))).slice(0, 40);
    res.innerHTML = list.map(i => `<button type="button" data-id="${esc(i.id)}">${esc(nameOf(i.id))}</button>`).join("") || `<span class="bo-h">Aucune fiche trouvée.</span>`; };
  inp.oninput = draw; draw();
  p.onclick = e => { const b = e.target.closest("[data-id]"); if (b) { p.remove(); done(b.dataset.id); } else if (e.target === p || e.target.closest(".btn")) p.remove(); };
  D.body.append(p); inp.focus();
}
function fieldHtml(f) {
  const v = xvals[f.id], id = "bo-f-" + f.id, opts = (f.opts || []).filter(Boolean);
  const lab = `<span class="bo-l">${esc(f.label || "Champ")}</span>`, help = f.help ? `<span class="bo-h">${esc(f.help)}</span>` : "";
  let h = "", wide = false;
  switch (f.type) {
    case "calc": return `<div class="bo-f bo-calc" data-field="${esc(f.id)}">${lab}<output data-calc="${esc(f.id)}">…</output>${help}</div>`;   // valeur calculée : remplie par bo-plus.js
    case "long": wide = true; h = `<textarea rows="3" data-x="${esc(f.id)}">${esc(v ?? "")}</textarea>`; break;
    case "number": h = `<input type="number" step="any" data-x="${esc(f.id)}" value="${esc(v ?? "")}">`; break;
    case "money": h = `<span class="bo-inl"><input type="number" step="0.01" data-x="${esc(f.id)}" value="${esc(v ?? "")}"><span>€</span></span>`; break;
    case "date": h = `<input type="date" data-x="${esc(f.id)}" value="${esc(v ?? "")}">`; break;
    case "check": return `<div class="bo-f" data-field="${esc(f.id)}"><label class="bo-chk"><input type="checkbox" data-x="${esc(f.id)}" ${v ? "checked" : ""}> ${esc(f.label || "Champ")}</label>${help}</div>`;
    case "choice": h = `<select data-x="${esc(f.id)}"><option value="">—</option>${opts.concat(v && !opts.includes(v) ? [v] : []).map(o => `<option ${o === v ? "selected" : ""}>${esc(o)}</option>`).join("")}</select>`; break;
    case "multi": wide = true; h = `<div class="bo-multi" data-xm="${esc(f.id)}">${opts.map(o => `<label><input type="checkbox" value="${esc(o)}" ${(v || []).includes(o) ? "checked" : ""}> ${esc(o)}</label>`).join("")}</div>`; break;
    case "stars": h = `<div class="bo-stars" data-xs="${esc(f.id)}">${[1, 2, 3, 4, 5].map(k => `<button type="button" data-k="${k}" class="${k <= (+v || 0) ? "on" : ""}" aria-label="${k} sur 5">★</button>`).join("")}</div>`; break;
    case "url": h = `<span class="bo-inl"><input type="url" placeholder="https://…" data-x="${esc(f.id)}" value="${esc(v ?? "")}"><a class="btn small-btn" style="margin:0" target="_blank" rel="noopener" data-xopen="${esc(f.id)}" ${v ? `href="${esc(v)}"` : "hidden"}>Ouvrir ↗</a></span>`; break;
    case "item": wide = true; h = `<div class="bo-chips" data-xi="${esc(f.id)}">${(Array.isArray(v) ? v : []).map(i => `<span class="bo-chip" data-go="${esc(i)}" title="Ouvrir cette fiche"><span>🔗 ${esc(nameOf(i))}</span><button type="button" data-rm="${esc(i)}" aria-label="Retirer">✕</button></span>`).join("")}<button type="button" class="bo-mini" data-link>+ Relier une fiche</button></div>`; break;
    case "list": h = `<span class="bo-inl"><select data-x="${esc(f.id)}"><option value="">—</option>${state.lists.map(l => `<option value="${esc(l.id)}" ${l.id === v ? "selected" : ""}>${esc(l.name)}</option>`).join("")}</select><button type="button" class="btn small-btn" style="margin:0" data-golist="${esc(f.id)}" ${v ? "" : "hidden"}>Ouvrir</button></span>`; break;
    default: h = `<input type="text" data-x="${esc(f.id)}" value="${esc(v ?? "")}">`;
  }
  return `<label class="bo-f ${wide ? "bo-wide" : ""}" data-field="${esc(f.id)}" ${["multi", "stars", "item"].includes(f.type) ? 'onclick="event.target.tagName===\'LABEL\'&&event.preventDefault()"' : ""}>${lab}${h}${help}</label>`;
}
function readInputs(form) {   // les champs affichés → xvals
  for (const f of cfg.fields || []) {
    const box = all("[data-field]", form).find(b => b.dataset.field === f.id);
    if (!box) continue;
    const inp = box.querySelector("[data-x]");
    let v;
    if (f.type === "check") v = inp.checked || undefined;
    else if (f.type === "number" || f.type === "money") v = inp.value === "" || isNaN(+inp.value) ? undefined : +inp.value;
    else if (f.type === "multi") { v = all("input:checked", box).map(c => c.value); if (!v.length) v = undefined; }
    else if (f.type === "stars" || f.type === "item") v = xvals[f.id];
    else v = inp.value.trim() || undefined;
    if (v === undefined || (Array.isArray(v) && !v.length)) delete xvals[f.id]; else xvals[f.id] = v;
  }
  return { ...xvals };
}
const directSave = () => { const d = state.draft; return !!(d && !d.item && d.adjust?.fid); };   // figurine d'un set : champs enregistrés tout de suite
function xChanged(form) {
  readInputs(form);
  if (!directSave()) return;
  const it = ownItem();
  if (it) api("/api/bo/values", { method: "POST", body: { id: it.id, x: xvals } }).then(() => { it.x = { ...xvals }; toast("Enregistré"); }).catch(e => toast(e.message));
}
function customBlocks(form, t) {
  const d = state.draft, own = ownItem();
  const usable = !!d && !d.view && !(d.adjust && !d.adjust.fid && !d.item) && !(d.adjust?.fid && !own);   // pas sur une fiche seulement consultée
  const fs = usable ? fieldsFor(t) : [], secs = cfg.secs || [];
  const groups = new Map();
  for (const f of fs) { const s = secs.some(x => x.id === f.sec) ? f.sec : "_"; groups.set(s, [...(groups.get(s) || []), f]); }
  all(":scope > .bo-sec", form).forEach(b => { if (!groups.has(b.dataset.boSec)) b.remove(); });
  const order = [...secs.map(s => s.id), "_"].filter(s => groups.has(s));
  for (const sid of order) {
    let b = all(":scope > .bo-sec", form).find(x => x.dataset.boSec === sid);
    if (!b) {
      b = D.createElement("fieldset"); b.className = "bo-sec bo-x"; b.dataset.boSec = sid; b.dataset.boKey = "x-" + sid;
      (form.querySelector(":scope > .links-row") || form.querySelector(":scope > .estimate") || {}).before?.(b) ?? form.append(b);
      if (!b.isConnected) form.append(b);
    }
    const title = sid === "_" ? (cfg.secTitle || "Informations personnelles") : secs.find(s => s.id === sid)?.label || "Bloc";
    b.innerHTML = `<legend>${esc(title)}</legend><div class="bo-grid">${groups.get(sid).map(fieldHtml).join("")}</div>`;
  }
}
function wireFields() {   // (une seule fois) : écoute des champs personnalisés, par délégation sur le formulaire
  const form = D.getElementById("stepConfig");
  if (!form || form._boWired) return;
  form._boWired = true;
  form.addEventListener("change", e => {
    if (e.target.closest(".bo-sec")) {
      const o = e.target.closest("[data-field]")?.querySelector("[data-xopen]"); if (o) { o.hidden = !e.target.value; o.href = e.target.value || "#"; }
      const g = e.target.closest("[data-field]")?.querySelector("[data-golist]"); if (g) g.hidden = !e.target.value;
      xChanged(form);
    } else if (e.target.matches("input[name=cutype], input[name=cukind], #cfgList, #cuKindSel")) setTimeout(() => sheet(false), 0);   // le type de fiche a pu changer
  });
  form.addEventListener("click", e => {
    const sec = e.target.closest(".bo-sec");
    if (!sec) return;
    const star = e.target.closest(".bo-stars button"), rm = e.target.closest("[data-rm]"), go = e.target.closest("[data-go]"), link = e.target.closest("[data-link]"), gl = e.target.closest("[data-golist]");
    const fid = e.target.closest("[data-field]")?.dataset.field;
    const redraw = () => { const f = (cfg.fields || []).find(x => x.id === fid), box = e.target.closest("[data-field]"); if (f && box) box.outerHTML = fieldHtml(f); xChanged(form); };
    if (star) { e.preventDefault(); const k = +star.dataset.k; if (xvals[fid] === k) delete xvals[fid]; else xvals[fid] = k; redraw(); }
    else if (rm) { e.preventDefault(); e.stopPropagation(); xvals[fid] = (xvals[fid] || []).filter(i => i !== rm.dataset.rm); redraw(); }
    else if (go) { e.preventDefault(); goItem(go.dataset.go); }
    else if (link) { e.preventDefault(); pickItem(id => { xvals[fid] = [...new Set([...(Array.isArray(xvals[fid]) ? xvals[fid] : []), id])]; redraw(); }); }
    else if (gl) { e.preventDefault(); const v = xvals[gl.dataset.golist]; if (v) { modal.hidden = true; openList(v); } }
  });
}
function autoLinks(t) {   // liens automatiques : boutons ajoutés aux liens du bas de la fiche (adresse avec {numero}, {nom}…)
  const box = D.getElementById("cfgLinks");
  if (!box) return;
  const d = state.draft, info = d?.info || {}, own = ownItem();
  const vals = { numero: info.number && info.number !== "custom" ? info.number : "", nom: own?.custom_name || own?.display_name || info.name || "", theme: info.theme || "", annee: info.year || "" };
  const want = (cfg.links || []).filter(l => l.url && !l.off && (!(l.types || []).length || l.types.includes(t)))
    .map(l => { let ok = true; const url = l.url.replace(/\{(\w+)\}/g, (_, k) => { const v = vals[k] ?? (own?.x?.[k]); if (v == null || v === "") ok = false; return encodeURIComponent(v ?? ""); }); return ok ? { id: l.id, label: l.label || "Lien", url } : null; }).filter(Boolean);
  const sig = JSON.stringify(want), cur = all(":scope > .bo-autolink", box);
  if (box.dataset.boLinks === sig && cur.length === want.length) return;
  cur.forEach(a => a.remove());
  box.dataset.boLinks = sig;
  for (const l of want) { const a = D.createElement("a"); a.className = "btn small-btn bo-autolink bo-x"; a.target = "_blank"; a.rel = "noopener"; a.href = l.url; a.textContent = l.label; box.append(a); }
}
function sheet(fresh) {   // appelée quand une fiche vient d'être remplie (fresh) ou quand son type a pu changer
  if (!app()) return;
  const form = D.getElementById("stepConfig");
  if (!form || !state.draft) return;
  wireFields();
  for (const c of form.children) { const k = blockKey(c); if (c.dataset.boKey !== k) c.dataset.boKey = k; }
  const t = sheetType();
  let wish = false;
  try { wish = isWish(D.getElementById("cfgList").value || state.draft.item?.list_id); } catch {}
  const real = wish && ["set", "fig"].includes(t) ? t + "_wish" : t, eff = cfg.sheets?.[real] ? real : t;
  const changed = form.dataset.boType !== eff;
  form.dataset.boType = eff; form.dataset.boReal = real;
  const own = ownItem(), key = (own?.id || "nouvelle") + "|" + (state.draft.info?.number || "");
  if (fresh || xFor !== key) { xFor = key; xvals = { ...(own?.x || {}) }; } else readInputs(form);
  customBlocks(form, t);
  autoLinks(t);
  if (changed || fresh) trTree(form);
  run("sheet", form, t, own);
  if (ADMIN) try { ADMIN.onSheet?.(sheetInfo()); } catch {}
}
function sheetInfo() {   // pour le panneau « Fiches » du back office : les blocs de la fiche ouverte
  const form = D.getElementById("stepConfig");
  if (!form || form.hidden || !app() || modal.hidden || !state.draft) return null;
  return { type: form.dataset.boType || "", real: form.dataset.boReal || "", base: sheetType(),
    blocks: [...form.children].map(c => { const lg = c.querySelector(":scope > legend"), tn = lg && [...lg.childNodes].find(n => n.nodeType === 3 && n.nodeValue.trim());
      return { key: blockKey(c), shown: !c.hidden && getComputedStyle(c).display !== "none" || (ghost && !c.hidden), legend: tn ? srcText(tn).trim() : "", custom: c.classList.contains("bo-sec"),
        text: (c.innerText || "").replace(/\s+/g, " ").trim().slice(0, 60) }; }) };
}

/* ------------------------------------------------------------------ 6. cartes des listes : champs personnalisés affichés */
let itemsRef = null, itemsMap = new Map();
function cardValue(f, v) {
  if (v == null || v === "" || (Array.isArray(v) && !v.length)) return "";
  switch (f.type) {
    case "check": return v ? "✓ " + f.label : "";
    case "stars": return f.label + " : " + "★".repeat(+v || 0) + "☆".repeat(5 - (+v || 0));
    case "money": return f.label + " : " + (typeof money === "function" ? money(+v) : v + " €");
    case "date": return f.label + " : " + fmtDate(v);
    case "multi": return f.label + " : " + v.join(", ");
    case "item": return f.label + " : " + v.map(nameOf).join(", ");
    case "list": return f.label + " : " + (state.lists.find(l => l.id === v)?.name || "");
    case "url": return "";
    default: return f.label + " : " + v;
  }
}
function cards() {
  if (!app()) return;
  const box = D.getElementById("items");
  if (!box) return;
  const fs = allFields().filter(f => f.card && !f.off);
  if (!fs.length && !box.querySelector(".bo-meta")) return;
  if (itemsRef !== state.items) { itemsRef = state.items; itemsMap = new Map(state.items.map(i => [i.id, i])); }
  for (const c of all(".card[data-id]", box)) {
    const it = itemsMap.get(c.dataset.id);
    const html = it && fs.length ? fs.map(f => f.type === "calc" ? (W.BO.plus?.cardCalc(f, it) || "") : cardValue(f, (it.x || {})[f.id])).filter(Boolean).map(s => `<span>${esc(s)}</span>`).join("") : "";
    let m = c.querySelector(":scope > .body > .bo-meta");
    if (!html) { if (m) m.remove(); continue; }
    if (!m) { m = D.createElement("div"); m.className = "meta bo-meta bo-x"; const foot = c.querySelector(":scope > .body > .foot"); if (foot) foot.before(m); else (c.querySelector(".body") || c).append(m); }
    if (m._sig !== html) { m._sig = html; m.innerHTML = html; }
  }
}

/* ------------------------------------------------------------------ boucle : tout ce qui se réapplique quand la page change */
let pending = false, runs = 0, runT = 0;
function refresh() {
  pending = false;
  const now = Date.now();
  if (now - runT > 1000) { runT = now; runs = 0; }
  if (++runs > 60) return;   // garde-fou : jamais de boucle sans fin
  try { if (PAGE === "app") menu(); } catch (e) { console.warn("BO menu", e); }
  try { applyMoves(); } catch (e) { console.warn("BO déplacements", e); }
  try { applyAdds(); } catch (e) { console.warn("BO ajouts", e); }
  try { cards(); } catch (e) { console.warn("BO cartes", e); }
  try { if (app() && state.draft && !modal.hidden) { const f = D.getElementById("stepConfig"); if (f && !f.hidden) { for (const c of f.children) { const k = blockKey(c); if (c.dataset.boKey !== k) c.dataset.boKey = k; } autoLinks(sheetType()); } } } catch (e) { console.warn("BO fiche", e); }
  run("refresh");
}
const schedule = () => { if (!pending) { pending = true; setTimeout(refresh, 30); } };
new MutationObserver(list => {
  if (T.any) for (const m of list) {
    if (m.type === "characterData") trText(m.target);
    else if (m.type === "attributes") trAttrs(m.target);
    else for (const n of m.addedNodes) trTree(n);
  }
  schedule();
}).observe(D.documentElement, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });

function apply(next) {   // (ré)applique tous les réglages — au chargement, et à chaque changement dans le back office
  if (next) cfg = next;
  buildCss(); buildTexts(); run("apply");
  if (D.body) { trTree(D.documentElement); refresh(); try { if (app() && state.draft && !modal.hidden) sheet(false); } catch {} }
}
apply();

/* l'application est chargée : on se branche sur le remplissage et la lecture d'une fiche (fonctions globales de app.js) */
function hook(name, wrap) {
  const o = W[name];
  if (typeof o !== "function") return;
  W[name] = function (...a) { return wrap.call(this, o, a); };
}
D.addEventListener("DOMContentLoaded", () => {
  apply();
  hook("fillConfig", function (o, a) { const r = o.apply(this, a); try { sheet(true); } catch (e) { console.warn("BO fiche", e); } return r; });
  hook("readConfig", function (o, a) {   // la fiche enregistrée emporte les champs personnalisés (clé « x »)
    const b = o.apply(this, a);
    try {
      const form = D.getElementById("stepConfig");
      if (b && typeof b === "object" && !directSave() && (form.querySelector(".bo-sec") || state.draft?.item?.x)) b.x = readInputs(form);
    } catch (e) { console.warn("BO champs", e); }
    return b;
  });
  if (W.BO_COPIE && !ADMIN && !sessionStorage.getItem("boRibbon")) {   // copie de travail : petit rappel
    const r = D.createElement("div"); r.className = "bo-ribbon bo-ui";
    r.innerHTML = `🧪 Copie de travail${PUBLIC ? "" : ` · <a href="/backoffice">Back office</a>`}<button type="button" aria-label="Masquer">✕</button>`;
    r.querySelector("button").onclick = () => { r.remove(); try { sessionStorage.setItem("boRibbon", "1"); } catch {} };
    D.body.append(r);
  }
  if (ADMIN) try { ADMIN.onReady?.(W); } catch {}
});

/* ------------------------------------------------------------------ 7. aperçu du back office : « cliquer pour modifier » */
const pk = { on: false, hl: null, selBox: null, tip: null, el: null };
const VOLATILE = /^(on|open|active|picked|selected|invalid|hidden|sub|drag.*|is-.*|bo-.*|has-.*|show|shown|busy|loading|dirty|cur|current|focus|hover)$/;
const cls = el => [...el.classList].filter(c => !VOLATILE.test(c) && /^[a-zA-Z_][\w-]*$/.test(c));
const goodId = el => el.id && /^[a-zA-Z][\w-]*$/.test(el.id) && !/\d{3,}/.test(el.id) && D.querySelectorAll("#" + CSS.escape(el.id)).length === 1;
const step = el => el.tagName.toLowerCase() + cls(el).slice(0, 3).map(c => "." + c).join("");
function selOne(el) {   // sélecteur de CET élément précis
  const parts = [];
  for (let e = el; e && e !== D.body && e !== D.documentElement; e = e.parentElement) {
    if (goodId(e)) { parts.unshift("#" + CSS.escape(e.id)); break; }
    let s = step(e);
    for (const a of ["data-bo-mv", "data-id", "data-pub", "data-bo-key", "data-bo-id", "data-field", "data-secid", "name", "for"]) {
      const v = e.getAttribute(a);
      if (v && v.length < 60 && !(a === "name" && e.type === "radio")) { s += `[${a}="${CSS.escape(v)}"]`; break; }
    }
    const sibs = e.parentElement ? [...e.parentElement.children].filter(x => matches(x, s)) : [];
    if (sibs.length > 1) s += `:nth-of-type(${[...e.parentElement.children].filter(x => x.tagName === e.tagName).indexOf(e) + 1})`;
    parts.unshift(s);
    if (parts.length > 8) break;
  }
  return parts.join(" > ");
}
function selSim(el) {   // sélecteur de TOUS les éléments du même genre
  const parts = [step(el)];
  let anchor = "";
  for (let e = el.parentElement, n = 0; e && e !== D.body && e !== D.documentElement; e = e.parentElement) {
    if (goodId(e)) { anchor = "#" + CSS.escape(e.id); break; }
    if (cls(e).length && n < 3) { parts.unshift(e.tagName.toLowerCase() + "." + cls(e)[0]); n++; }
  }
  return (anchor ? anchor + " " : "") + parts.join(" ");
}
const NAMES = { button: "Bouton", a: "Lien", input: "Champ", select: "Liste déroulante", textarea: "Zone de texte", img: "Image", h1: "Titre", h2: "Titre", h3: "Titre", h4: "Titre",
  legend: "Titre de bloc", fieldset: "Bloc", label: "Libellé", nav: "Menu", article: "Carte", form: "Formulaire", header: "Barre du haut", aside: "Menu latéral", p: "Texte", span: "Texte", li: "Ligne", td: "Cellule", th: "En-tête", table: "Tableau" };
const ownText = el => [...el.childNodes].filter(n => n.nodeType === 3 && n.nodeValue.trim());
function describe(el) {
  const t = el.tagName.toLowerCase(), txt = (ownText(el)[0]?.nodeValue || el.getAttribute("aria-label") || el.getAttribute("placeholder") || el.getAttribute("title") || (el.innerText || "")).replace(/\s+/g, " ").trim();
  const nm = el.classList.contains("btn") ? "Bouton" : el.classList.contains("card") ? "Carte" : el.classList.contains("badge") ? "Étiquette" : el.classList.contains("modal-box") ? "Fenêtre" : NAMES[t] || (ownText(el).length ? "Texte" : "Zone");
  return nm + (txt ? ` « ${txt.slice(0, 38)}${txt.length > 38 ? "…" : ""} »` : "");
}
function place(box, el) {
  if (!box) return;
  if (!el || !el.isConnected) { box.style.display = "none"; return; }
  const r = el.getBoundingClientRect();
  Object.assign(box.style, { display: "block", left: r.left - 2 + "px", top: r.top - 2 + "px", width: r.width + 4 + "px", height: r.height + 4 + "px" });
}
function pickInfo(el) {
  const cs = getComputedStyle(el), one = selOne(el), sim = selSim(el), tn = ownText(el)[0], ps = el.parentElement ? getComputedStyle(el.parentElement) : null;
  const crumbs = [];
  for (let e = el.parentElement; e && e !== D.body && crumbs.length < 6; e = e.parentElement) crumbs.push(describe(e));
  return { desc: describe(el), one, sim, nOne: all(one).length, nSim: all(sim).length, page: PAGE, tag: el.tagName.toLowerCase(), href: el.tagName === "A" ? (el.dataset.boHref0 ?? el.getAttribute("href") ?? "") : "",
    text: tn ? srcText(tn).trim() : "", textNow: tn ? tn.nodeValue.trim() : "",
    placeholder: el.getAttribute("placeholder") != null ? (seenAttr.get(el)?.placeholder?.src ?? el.getAttribute("placeholder")) : null,
    title: el.getAttribute("title") != null ? (seenAttr.get(el)?.title?.src ?? el.getAttribute("title")) : null,
    flexParent: !!ps && /flex|grid/.test(ps.display), container: el.children.length > 0, crumbs,
    css: { color: cs.color, "background-color": cs.backgroundColor, "font-size": cs.fontSize, "font-weight": cs.fontWeight, "font-style": cs.fontStyle, "text-align": cs.textAlign,
      "border-radius": cs.borderTopLeftRadius, "border-width": cs.borderTopWidth, "border-color": cs.borderTopColor, padding: cs.paddingTop, margin: cs.marginTop, width: cs.width, height: cs.height, opacity: cs.opacity } };
}
function choose(el) {
  pk.el = el; place(pk.selBox, el);
  try { ADMIN.onPick(el ? pickInfo(el) : null); } catch (e) { console.warn(e); }
}
/* mode « déplacer » : on attrape un élément, une barre verte montre où il sera posé (avant / après l'élément survolé), on lâche */
const mv = { on: false, src: null, x: 0, y: 0, drag: false, dst: null, pos: "", bar: null };
function overlays() { for (const [o, k, c] of [[pk, "hl", "bo-hl"], [pk, "selBox", "bo-hl-sel"], [pk, "tip", "bo-tip"], [mv, "bar", "bo-mvbar"]]) if (!o[k]) { o[k] = D.createElement("div"); o[k].className = c + " bo-ui"; D.body.append(o[k]); } }
function mvStop() { mv.src = null; mv.drag = false; mv.dst = null; if (mv.bar) mv.bar.style.display = "none"; place(pk.selBox, null); if (pk.tip) pk.tip.style.display = "none"; }
function mvDown(e) {
  let el = target(e);
  if (el && el.tagName === "LEGEND" && el.parentElement?.parentElement?.id === "stepConfig") el = el.parentElement;   // le titre d'un bloc de fiche : c'est le bloc entier qu'on attrape
  mv.src = el && el.tagName !== "BO-MV" ? el : null; mv.x = e.clientX; mv.y = e.clientY; mv.drag = false; mv.dst = null;
}
function mvDrop(x, y) {   // où poser : l'élément sous le pointeur, au niveau des voisins de l'élément déplacé si possible
  let t = D.elementFromPoint(x, y);
  if (!t || t.closest(".bo-ui") || t === D.body || t === D.documentElement || mv.src.contains(t)) return null;
  const sp = mv.src.parentElement && mv.src.parentElement.tagName === "BO-MV" ? mv.src.parentElement.parentElement : mv.src.parentElement;
  let same = null;
  for (let e = t; e && e !== D.body; e = e.parentElement) if (e.parentElement === sp) { same = e; break; }
  if (same) t = same.tagName === "BO-MV" ? same.firstElementChild || same : same;
  else while (t.parentElement && t.parentElement !== D.body && getComputedStyle(t).display === "inline") t = t.parentElement;
  if (!t || t === mv.src || mv.src.contains(t)) return null;
  const r = t.getBoundingClientRect(), box = t.parentElement && t.parentElement.tagName === "BO-MV" ? t.parentElement : t;
  const sib = box.nextElementSibling || box.previousElementSibling, r2 = sib && sib.getClientRects().length ? sib.getBoundingClientRect() : null;
  const ps = t.parentElement ? getComputedStyle(box.parentElement || t.parentElement) : null;
  const horiz = r2 ? Math.abs(r2.top - r.top) < Math.min(r.height, r2.height) / 2 && Math.abs(r2.left - r.left) > 4 : !!ps && /flex/.test(ps.display) && !/column/.test(ps.flexDirection);
  return { t, r, horiz, pos: horiz ? (x < r.left + r.width / 2 ? "before" : "after") : (y < r.top + r.height / 2 ? "before" : "after") };
}
function mvMove(e) {
  if (!mv.drag && Math.hypot(e.clientX - mv.x, e.clientY - mv.y) < 6) return false;
  mv.drag = true;
  place(pk.selBox, mv.src);
  if (pk.hl) pk.hl.style.display = "none";
  const d = mvDrop(e.clientX, e.clientY);
  mv.dst = d ? d.t : null; mv.pos = d ? d.pos : "";
  if (d) Object.assign(mv.bar.style, d.horiz ? { display: "block", left: (d.pos === "before" ? d.r.left - 4 : d.r.right) + "px", top: d.r.top + "px", width: "4px", height: d.r.height + "px" }
    : { display: "block", left: d.r.left + "px", top: (d.pos === "before" ? d.r.top - 4 : d.r.bottom) + "px", width: d.r.width + "px", height: "4px" });
  else mv.bar.style.display = "none";
  pk.tip.textContent = d ? `${describe(mv.src)} → ${d.pos === "before" ? "avant" : "après"} ${describe(d.t)}` : "Déposez à côté d'un autre élément";
  Object.assign(pk.tip.style, { display: "block", left: Math.min(e.clientX + 14, innerWidth - 320) + "px", top: Math.min(e.clientY + 18, innerHeight - 30) + "px" });
  return true;
}
function moveDo(src, dst, pos) {   // déplacer src avant / après dst (glisser-déposer, ou clic droit : couper → coller, reculer / avancer)
  for (const m of cfg.moves || []) undoMove(m.id);   // les sélecteurs se lisent sur la page d'origine (comme applyMoves)
  const top = (el, id) => { for (let e = el; e && e !== D.body; e = e.parentElement) if (e.parentElement && e.parentElement.id === id) return e; return null; };   // l'entrée (du menu, de la fiche) qui contient l'élément
  const mS = top(src, "sidebar"), mD = top(dst, "sidebar"), menu = mS && mD && mS !== mD;   // d'une entrée du menu à une autre : c'est l'ordre du menu qui change
  const inf = (el, m) => ({ one: selOne(el), desc: describe(el), sheetKey: el.parentElement && el.parentElement.id === "stepConfig" ? blockKey(el) : "", menuKey: menu ? (m.dataset.boKey || "") : "" });
  let out = null;
  try { if (src.isConnected && dst.isConnected) out = { src: inf(src, mS), dst: inf(dst, mD), pos, page: PAGE, sheet: (D.getElementById("stepConfig") || {}).dataset?.boReal || "" }; } catch (e) { console.warn(e); }
  schedule();
  if (out) try { ADMIN.onMove(out); } catch (e) { console.warn(e); }
}
function mvUp() {
  const { src, dst, pos, drag } = mv;
  mvStop();
  if (!drag || !src || !dst) return;
  moveDo(src, dst, pos);
}
/* clic droit dans l'aperçu : les outils de l'élément (le back office fait le travail : BO_ADMIN.onContext) */
const cx = { menu: null, cut: null };
function ctxClose() { if (cx.menu) { cx.menu.remove(); cx.menu = null; place(pk.selBox, pk.el); } }
function ctxOpen(el, x, y) {
  ctxClose(); overlays(); place(pk.selBox, el);
  const m = D.createElement("div"); m.className = "bo-ctx bo-ui";
  const info = pickInfo(el), ask = (a, extra) => { try { return ADMIN.onContext && ADMIN.onContext(a, info, extra); } catch (e) { console.warn(e); } };
  const item = (ico, label, fn, off) => { const b = D.createElement("button"); b.type = "button"; b.disabled = !!off; b.innerHTML = `<span>${ico}</span>${esc(label)}`; b._run = fn; m.append(b); };
  const sep = () => m.append(D.createElement("hr"));
  const real = s => s && s.tagName === "BO-MV" ? s.firstElementChild : s, box = el.parentElement && el.parentElement.tagName === "BO-MV" ? el.parentElement : el;
  const ok = s => s && !s.closest(".bo-ui") && s.tagName !== "SCRIPT" && s.tagName !== "STYLE" ? s : null;
  const prev = ok(real(box.previousElementSibling)), next = ok(real(box.nextElementSibling)), par = el.parentElement && el.parentElement !== D.body ? (el.parentElement.tagName === "BO-MV" ? el.parentElement.parentElement : el.parentElement) : null;
  const canPaste = !!cx.cut && cx.cut.isConnected && cx.cut !== el && !cx.cut.contains(el) && !el.contains(cx.cut);
  const h = D.createElement("div"); h.className = "bo-ctx-h"; h.textContent = describe(el); m.append(h);
  item("✏️", "Modifier (texte, style, lien, action…)", () => { ask("edit"); choose(el); });
  item("👁", "Masquer", () => ask("hide"));
  sep();
  item("🎨", "Copier le style", () => ask("copystyle"));
  item("🖌️", "Coller le style", () => ask("pastestyle"), !(ADMIN.ctxHas && ADMIN.ctxHas("style")));
  item("🔤", "Copier le texte", () => ask("copytext", { text: (el.innerText || el.value || "").trim() }));
  item("🧷", "Copier le sélecteur", () => ask("copysel"));
  sep();
  item("✂️", "Couper (pour le déplacer)", () => { cx.cut = el; ask("cut"); });
  item("📌", "Coller avant", () => { const s = cx.cut; cx.cut = null; moveDo(s, el, "before"); }, !canPaste);
  item("📌", "Coller après", () => { const s = cx.cut; cx.cut = null; moveDo(s, el, "after"); }, !canPaste);
  item("⬅️", "Reculer d'un cran", () => moveDo(el, prev, "before"), !prev);
  item("➡️", "Avancer d'un cran", () => moveDo(el, next, "after"), !next);
  sep();
  item("⤴️", "Élément parent", () => ctxOpen(par, x, y), !par || par === D.documentElement);
  item("↩️", "Annuler ses modifications", () => ask("reset"));
  D.body.append(m); cx.menu = m;
  Object.assign(m.style, { left: Math.max(4, Math.min(x, innerWidth - m.offsetWidth - 6)) + "px", top: Math.max(4, Math.min(y, innerHeight - m.offsetHeight - 6)) + "px" });
}
function moveMode(on) { mv.on = !!on; if (mv.on) overlays(); D.documentElement.classList.toggle("bo-moving", mv.on); if (!mv.on) mvStop(); }
const target = e => { let el = e.target; if (el.nodeType !== 1) el = el.parentElement; return el && !el.closest(".bo-ui") && el !== D.body && el !== D.documentElement ? el : null; };
if (ADMIN) {
  /* clic droit : le menu des outils de l'élément, dans tous les modes (Maj + clic droit : le menu du navigateur) — posés AVANT les écouteurs des modes */
  D.addEventListener("contextmenu", e => {
    if (e.shiftKey) return;
    const el = target(e);
    e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
    if (el) ctxOpen(el, e.clientX, e.clientY); else ctxClose();
  }, true);
  D.addEventListener("click", e => {   // un outil du menu (les modes « cliquer » / « déplacer » avalent les clics : celui-ci passe avant eux)
    const b = e.target.closest ? e.target.closest(".bo-ctx button") : null;
    if (!b) { if (cx.menu) ctxClose(); return; }
    e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
    if (!b.disabled) { const run = b._run; ctxClose(); try { run(); } catch (err) { console.warn(err); } }
  }, true);
  D.addEventListener("keydown", e => { if (e.key === "Escape" && cx.menu) ctxClose(); }, true);
  W.addEventListener("scroll", () => ctxClose(), true);
  W.addEventListener("blur", () => ctxClose());
  for (const ev of ["click", "mousedown", "mouseup", "pointerdown", "pointerup", "dblclick", "contextmenu", "submit", "touchstart", "touchend", "keydown"]) {
    D.addEventListener(ev, e => {
      if (!pk.on && !mv.on) return;
      if (ev === "keydown") { if (e.key === "Escape") { if (pk.on) choose(null); mvStop(); } return; }
      e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
      if (mv.on) {   // (pointerdown : une fois neutralisé, le navigateur n'envoie plus de « mousedown » — c'est donc lui qui lance le glisser)
        if ((ev === "pointerdown" || ev === "mousedown") && e.button === 0 && !mv.src) mvDown(e); else if (ev === "pointerup" || ev === "mouseup") mvUp();
        return; }
      if (ev === "click") { const el = target(e); if (el) choose(el); }
    }, true);
  }
  D.addEventListener("mousemove", e => {
    if (mv.on && mv.src && mvMove(e)) return;
    if (!pk.on && !mv.on) return;
    const el = target(e);
    place(pk.hl, el);
    if (el) { pk.tip.textContent = describe(el); Object.assign(pk.tip.style, { display: "block", left: Math.min(e.clientX + 14, innerWidth - 260) + "px", top: Math.min(e.clientY + 18, innerHeight - 30) + "px" }); }
    else pk.tip.style.display = "none";
  }, true);
  D.addEventListener("pointermove", e => { if (mv.on && mv.src) mvMove(e); }, true);   // glisser en cours (selon le navigateur, « mousemove » peut ne plus arriver)
  D.addEventListener("mouseleave", () => { if (pk.hl) pk.hl.style.display = "none"; if (pk.tip) pk.tip.style.display = "none"; });
  W.addEventListener("scroll", () => { place(pk.selBox, pk.el); if (pk.hl) pk.hl.style.display = "none"; }, true);
  W.addEventListener("resize", () => place(pk.selBox, pk.el));
}
function pickMode(on) {
  pk.on = !!on;
  D.documentElement.classList.toggle("bo-picking", pk.on);
  if (pk.on) overlays();
  if (!pk.on) { pk.el = null; for (const k of ["hl", "selBox", "tip"]) if (pk[k]) pk[k].style.display = "none"; }
}

/* ------------------------------------------------------------------ ce que le back office peut demander à son aperçu */
W.BO = {
  apply, page: PAGE, tr,
  move: moveMode,   // aperçu : mode « déplacer à la souris »
  _: { HOOKS, cfg: () => cfg, esc, all, app, PAGE, PUBLIC, admin: () => ADMIN, itemType, ownItem, sheetType, xvals: () => xvals, fmtDate, nameOf, schedule, readInputs, openList, goItem },   // pour bo-plus.js et bo-max.js
  cfg: () => cfg,
  pick: pickMode,
  picked: () => pk.el && pk.el.isConnected ? pickInfo(pk.el) : null,
  pickParent() { if (pk.el?.parentElement && pk.el.parentElement !== D.body) choose(pk.el.parentElement); },
  pickSel(sel) { const el = all(sel)[0]; if (el) { el.scrollIntoView({ block: "center" }); choose(el); } return !!el; },
  unpick() { pk.el = null; place(pk.selBox, null); },
  replace() { place(pk.selBox, pk.el); },
  ghost(on) { ghost = !!on; buildCss(); },
  flash(sel) { const els = all(sel); els.forEach(e => e.classList.add("bo-flash")); els[0]?.scrollIntoView({ block: "center", behavior: "smooth" }); setTimeout(() => els.forEach(e => e.classList.remove("bo-flash")), 1400); return els.length; },
  count: sel => all(sel).length,
  sheetInfo,
  menuInfo() { const sb = D.getElementById("sidebar"); if (!sb) return null; menu();
    return [...sb.children].map(c => ({ key: c.dataset.boKey, custom: c.classList.contains("bo-link"), sep: c.classList.contains("side-sep"), empty: !c.classList.contains("side-sep") && !(c.innerText || "").trim(),
      text: (c.innerText || "").replace(/\s+/g, " ").trim().slice(0, 50) })); },
  types() { if (!app()) return {}; const o = {}; for (const i of state.items) { const t = itemType(i) + (["set", "fig"].includes(itemType(i)) && isWish(i.list_id) ? "_wish" : ""); o[t] = (o[t] || 0) + 1; } return o; },
  open(type) {   // ouvre une fiche d'exemple de ce type (panneau « Fiches »)
    if (!app()) return false;
    const base = type.replace("_wish", ""), wish = type.endsWith("_wish");
    const it = state.items.find(i => itemType(i) === base && !i._in && isWish(i.list_id) === wish) || state.items.find(i => itemType(i) === base && isWish(i.list_id) === wish);
    if (!it) return false;
    openEdit(it.id); return true;
  },
  close() { try { if (app() && !modal.hidden) modal.hidden = true; all("body > .modal:not(#modal)").forEach(m => m.remove()); } catch {} },
  lists: () => app() ? state.lists.map(l => ({ id: l.id, name: l.name, kind: l.kind || "collection" })) : [],
  items: () => app() ? state.items.filter(i => i.kind !== "part").map(i => ({ id: i.id, name: nameOf(i.id), type: itemType(i), x: i.x || null })) : [],
  texts() {   // tous les textes visibles à l'écran (panneau « Textes » : choisir dans la page)
    const out = new Map(), w = D.createTreeWalker(D.body, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) {
      const p = n.parentElement;
      if (!p || p.closest(SKIP + ",.bo-x") || !p.getClientRects().length) continue;
      const s = srcText(n).replace(/\s+/g, " ").trim();
      if (s.length >= 2 && s.length <= 120 && /\p{L}/u.test(s) && !out.has(s)) out.set(s, n.nodeValue.replace(/\s+/g, " ").trim());
    }
    return [...out].map(([from, now]) => ({ from, now }));
  },
  dark: () => matchMedia("(prefers-color-scheme: dark)").matches,
  vars() { const cs = getComputedStyle(D.documentElement), o = {}; for (const k of ["bg", "panel", "ink", "muted", "line", "red", "red-ink", "yellow", "green", "neg", "accent-bg"]) o[k] = cs.getPropertyValue("--" + k).trim(); o.radius = parseFloat(cs.getPropertyValue("--radius")) || 14; return o; },
};
})();

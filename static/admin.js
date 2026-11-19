/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
/* Briquothèque — BACK OFFICE : l'écran du back office, servi par /backoffice (personnaliser le site sans code).
   Tout ce que règle cette page tient dans UN objet « cfg » (voir backoffice.py pour sa forme) :
     - chaque changement passe par change() : annulable, enregistré en brouillon sur le serveur, montré tout de suite dans l'aperçu ;
     - « Publier » fait du brouillon la version du site ; l'historique garde chaque publication.
   L'aperçu (iframe) charge le vrai site : son script /bo.js lit le brouillon par window.BO_ADMIN et offre window.BO
   (sélection à la souris, blocs de la fiche ouverte, entrées du menu…). */
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const uid = () => Math.random().toString(36).slice(2, 9);
const clone = o => JSON.parse(JSON.stringify(o ?? null));
const slug = s => (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 24);

/* fabrique un élément : el("button", {class, onclick…}, enfants…) */
function el(tag, props, ...kids) {
  const n = document.createElement(tag);
  let val;
  for (const [k, v] of Object.entries(props || {})) {
    if (v == null || v === false) continue;
    if (k === "value") val = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k in n && k !== "list" && k !== "form") n[k] = v;
    else n.setAttribute(k, v === true ? "" : v);
  }
  n.append(...kids.flat(Infinity).filter(k => k != null && k !== false && k !== ""));
  if (val !== undefined) n.value = val;
  return n;
}
const btn = (label, onclick, cls = "", title) => el("button", { type: "button", class: "b " + cls, onclick, title }, label);
const head = (t, intro) => [el("h2", {}, t), el("p", { class: "intro" }, intro)];
const card = (title, ...kids) => el("section", { class: "card" }, title && el("h3", {}, title), kids);
const para = html => el("p", { html });
const hint = html => el("p", { class: "hint", html });
const note = (html, cls = "") => el("div", { class: "note " + cls, html });
const fld = (label, control, help) => el("div", { class: "f" }, el("div", { class: "fl" }, label), control, help && el("div", { class: "fh", html: help }));
const line = (...kids) => el("div", { class: "line" }, kids);
const chk = (label, checked, on, title) => el("label", { class: "chk", title }, el("input", { type: "checkbox", checked: !!checked, onchange: e => on(e.target.checked) }), el("span", {}, label));
const sel = (value, opts, on) => el("select", { value: value ?? "", onchange: e => on(e.target.value) }, opts.map(([v, l]) => el("option", { value: v }, l)));
const txt = (value, on, ph, o = {}) => el("input", { type: o.type || "text", value: value ?? "", placeholder: ph, title: o.title, oninput: e => on(e.target.value) });

/* ------------------------------------------------------------------ état */
let cfg = {}, published = {}, hist = [], copie = false;
const undo = [], redo = [];
let panel = "accueil", lastKey = "", lastT = 0, saveT = 0, saveState = "";
let mode = "use";    // aperçu : "use" (se comporte comme le site) | "pick" (un clic sélectionne un élément)
let ghost = false;   // aperçu : ce qui est masqué reste visible en transparence
let pick = null, scope = { sim: false, all: false }, addPos = "after";   // élément choisi à la souris
let shType = "set", shSig = "", noSample = false;   // rubrique « Fiches »
let dataItem = null, dataQ = "";   // rubrique « Données »
let themeTab = "light";
const frame = $("#preview");
const FW = () => { try { return frame.contentWindow; } catch { return null; } };
const BOF = () => { try { return frame.contentWindow.BO || null; } catch { return null; } };

const PANELS = [
  ["accueil", "🏠", "Accueil", ""],
  ["souris", "🖱️", "Modifier à la souris", "Cliquez sur n'importe quel élément du site pour le masquer, le renommer, le recolorer, le déplacer…"],
  ["apparence", "🎨", "Apparence", "Nom du site, logo, couleurs, arrondis, police, taille du texte."],
  ["textes", "🔤", "Textes", "Remplacer un mot ou une phrase partout sur le site."],
  ["fiches", "🧱", "Fiches", "Le squelette de chaque type de fiche : ordre des blocs, blocs masqués, titres."],
  ["champs", "🧩", "Champs personnalisés", "Vos propres informations sur les fiches : texte, date, note, liens vers d'autres fiches…"],
  ["liens", "🔗", "Liens automatiques", "Des boutons sur chaque fiche vers d'autres sites, calculés avec le numéro ou le nom."],
  ["cartes", "🃏", "Cartes des listes", "Taille des vignettes et informations affichées dessus."],
  ["menu", "☰", "Menu", "Ordre du menu, entrées masquées, raccourcis vers une liste, une fiche ou un site."],
  ["donnees", "🗃️", "Données", "Corriger à la main n'importe quelle information enregistrée dans une fiche."],
  ["modifs", "📋", "Mes modifications", "Tout ce que vous avez changé, au même endroit : retrouver, désactiver, supprimer."],
  ["historique", "🕘", "Historique et secours", "Revenir à une version publiée ou au site d'origine, exporter vos réglages."],
];
const PAGES = { "": "toutes les pages", app: "le site", public: "les pages publiques", nouveautes: "la page Nouveautés", partage: "les fiches partagées", connexion: "la page de connexion" };
const SHEETS = [["set", "Set"], ["fig", "Figurine"], ["moc", "MOC"], ["partial", "Set partiel"], ["mocfig", "Figurine personnalisée"], ["set_wish", "Set en liste de souhaits"], ["fig_wish", "Figurine en liste de souhaits"]];
const KINDS = SHEETS.slice(0, 5).map(([k, l]) => [k, l + "s"]).map(([k, l]) => [k, l.replace("Sets partiels", "Sets partiels").replace("Set partiels", "Sets partiels").replace("Figurine personnalisées", "Figurines personnalisées")]);
const BASE = t => t.replace("_wish", "");
const sheetName = t => SHEETS.find(s => s[0] === t)?.[1] || t;
const BLOCKS = {   // nom lisible des blocs d'une fiche
  newBanner: "Bandeau « Créer une nouvelle fiche »", sampleBanner: "Bandeau « Fiche de démo »",
  "cfg-top": "En-tête : photo, nom, numéro, prix, boutons", "list-pick": "Choix de la liste", "qty-row": "Quantité et options", addBar: "Barre « Ajouter »",
  altBox: "Apparences alternatives", customBox: "MOC", wishBox: "État souhaité", adjustMode: "Choix « tout le set / une partie »", figOnlyBox: "Figurines à ajouter",
  figBox: "Figurines", figExtra: "Figurines en plus", "fig-side": "Pièces et accessoires", accBox: "Accessoires", partOfBox: "Partie de", estBox: "Valeur estimée",
  addPrices: "Tarifs constatés", cfgPrices: "Tarifs", figHost: "Rangée dans le set", cfgInSets: "Présente dans mes sets", cfgCatSets: "Aussi dans ces sets (pas dans ma collection)",
  "links-row": "Liens du bas de fiche", estimate: "Barre du bas : Supprimer / Enregistrer",
};
const NATURAL = ["newBanner", "sampleBanner", "cfg-top", "list-pick", "qty-row", "addBar", "altBox", "customBox", "wishBox", "adjustMode", "figOnlyBox", "figBox", "figExtra", "fig-side", "accBox", "partOfBox",
  "estBox", "addPrices", "cfgPrices", "figHost", "cfgInSets", "cfgCatSets", "links-row", "estimate"];
const MENU = {   // nom lisible des entrées du menu
  "side-title": "Boutons du haut : nouvelle liste, ordre des listes", listNav: "Mes listes", todoNav: "📝 À faire", wishNav: "À construire, liste de souhaits, nouveautés", shareNav: "Fiches partagées",
  mocSection: "🧪 MOC à valider", partsNav: "Pièces à commander", invNav: "Inventaires", btnNewInv: "+ Nouvel inventaire", statsNav: "Statistiques, fiche au hasard",
  "side-bottom": "Réglages, mot de passe, déconnexion", pubSep: "Trait de séparation", pubNav: "Pages publiques (liens à copier)", "side-legal": "Mentions légales",
};
const FTYPES = [["text", "Texte court"], ["long", "Texte long"], ["number", "Nombre"], ["money", "Montant en €"], ["date", "Date"], ["check", "Case à cocher (oui / non)"],
  ["choice", "Liste de choix (un seul)"], ["multi", "Choix multiples"], ["stars", "Note en étoiles"], ["url", "Lien internet"], ["item", "Lien vers d'autres fiches"], ["list", "Lien vers une liste"]];
const ADDK = { texte: "Texte", titre: "Titre", bouton: "Bouton-lien", image: "Image", sep: "Trait de séparation" };
const DEF = {   // couleurs d'origine du site (style.css)
  both: { red: "#d01012", "red-ink": "#ffffff", yellow: "#ffcf00" },
  light: { bg: "#f4f5f7", panel: "#ffffff", ink: "#1b1d22", muted: "#6b7280", line: "#e4e6eb", "accent-bg": "#fff4f4", green: "#12805c", neg: "#c2410c" },
  dark: { bg: "#111317", panel: "#1b1e24", ink: "#eceef2", muted: "#9aa1ad", line: "#2b2f37", "accent-bg": "#2a1a1b", green: "#34d399", neg: "#fb923c" },
};
const COLORS = { red: "Couleur principale (boutons, sélection)", "red-ink": "Texte sur la couleur principale", yellow: "Couleur d'accent (étoiles, repères)",
  bg: "Fond de la page", panel: "Fond des blocs et des cartes", ink: "Texte", muted: "Texte secondaire", line: "Traits et bordures", "accent-bg": "Fond des éléments sélectionnés",
  green: "Couleur « positif »", neg: "Couleur « négatif »" };
const PRESETS = [["Rouge brique (origine)", null], ["Bleu", "#1d4ed8", "#eff4ff", "#172036"], ["Vert", "#15803d", "#effaf2", "#14261b"], ["Violet", "#7c3aed", "#f5f0ff", "#221a36"],
  ["Orange", "#c2410c", "#fff4ec", "#2c1c12"], ["Ardoise", "#475569", "#f1f5f9", "#1e2530"]];
const LINK_PRESETS = [["BrickLink", "https://www.bricklink.com/v2/search.page?q={numero}"], ["Rebrickable", "https://rebrickable.com/search/?q={numero}"],
  ["Brickset", "https://brickset.com/sets?query={numero}"], ["Notices LEGO", "https://www.lego.com/fr-fr/service/buildinginstructions/{numero}"],
  ["Images (Google)", "https://www.google.com/search?tbm=isch&q=LEGO+{numero}+{nom}"], ["Vidéos (YouTube)", "https://www.youtube.com/results?search_query=LEGO+{numero}+{nom}"]];
const CARDP = [["img", "L'image"], ["badges", "Les pastilles sur l'image"], ["sel", "La case de sélection"], ["num", "Le numéro"], ["qty", "La quantité (×2)"], ["todo", "L'étiquette « à faire »"],
  ["tags", "Les étiquettes sous le nom"], ["insets", "« Dans le set… »"], ["listtag", "Le nom de la liste"], ["meta", "Thème · année · pièces"], ["pcsunit", "Le prix à la pièce"],
  ["prices3", "Les trois prix"], ["value", "La valeur, en bas de carte"]];

/* ------------------------------------------------------------------ serveur, messages, fenêtres */
async function api(path, body) {
  const r = await fetch(path, body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (r.status === 401) { location.href = "/backoffice"; throw new Error("Connexion au back office requise"); }   // session finie : retour à la porte du back office
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.erreur || "Erreur " + r.status);
  return d;
}
let toastT = 0;
function toast(m) { const t = $("#toast"); t.textContent = m; t.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => { t.hidden = true; }, 3800); }
function modal(title, body, o = {}) {   // body : éléments, ou fonction(fermer) → éléments ; rend une promesse (null = annulé)
  return new Promise(res => {
    const close = v => { m.remove(); res(v); };
    const m = el("div", { class: "modal", onmousedown: e => { if (e.target === m) close(null); }, onkeydown: e => { if (e.key === "Escape") close(null); } },
      el("div", { class: "modal-box" + (o.wide ? " wide" : "") }, el("h3", {}, title), el("div", { class: "modal-body" }, typeof body === "function" ? body(close) : body),
        el("div", { class: "modal-foot" }, o.cancel !== false && btn(o.cancel || "Annuler", () => close(null)), o.ok !== false && btn(o.ok || "OK", () => close(o.value ? o.value() : true), "primary"))));
    document.body.append(m);
    (m.querySelector("input, textarea, select") || m.querySelector(".primary") || m.querySelector("button"))?.focus();
  });
}
const sure = (title, html, ok = "Oui") => modal(title, para(html), { ok });
function ask(title, html, label, o = {}) {   // une question avec une réponse à taper
  const inp = el("input", { type: "text", value: o.value || "", placeholder: o.ph || "", onkeydown: e => { if (e.key === "Enter") inp.closest(".modal").querySelector(".primary").click(); } });
  return modal(title, [html && para(html), fld(label, inp)], { ok: o.ok || "OK", value: () => inp.value.trim() });
}
function choose(title, rows, o = {}) {   // choisir dans une liste (avec recherche) : rows = [{v, label, sub}]
  return modal(title, close => {
    const list = el("div", { class: "pickl" });
    const fill = q => list.replaceChildren(...rows.filter(r => !q || (r.label + " " + (r.sub || "")).toLowerCase().includes(q)).slice(0, 5000)
      .map(r => el("button", { type: "button", onclick: () => close(r.v) }, r.label, r.sub && el("small", {}, r.sub))), rows.length ? "" : el("p", { class: "hint" }, o.empty || "Rien à choisir."));
    fill("");
    return [el("input", { type: "search", placeholder: "Rechercher…", oninput: e => fill(e.target.value.trim().toLowerCase()) }), list];
  }, { ok: false, cancel: "Fermer", wide: true });
}
function pickImage(max, done) {   // choisir une image sur l'ordinateur → réduite, rangée dans les réglages
  const inp = el("input", { type: "file", accept: "image/*", onchange: () => {
    const f = inp.files[0]; if (!f) return;
    const rd = new FileReader();
    rd.onload = () => { const im = new Image();
      im.onload = () => { const k = Math.min(1, max / Math.max(im.width, im.height)), c = el("canvas", { width: Math.max(1, Math.round(im.width * k)), height: Math.max(1, Math.round(im.height * k)) });
        c.getContext("2d").drawImage(im, 0, 0, c.width, c.height); done(c.toDataURL(max > 200 ? "image/webp" : "image/png", .86)); };
      im.onerror = () => toast("Image illisible"); im.src = rd.result; };
    rd.readAsDataURL(f); } });
  inp.click();
}
function toHex(c) {
  if (!c) return "";
  if (/^#[0-9a-f]{6}$/i.test(c)) return c.toLowerCase();
  if (/^#[0-9a-f]{3}$/i.test(c)) return "#" + [...c.slice(1)].map(x => x + x).join("").toLowerCase();
  const m = /rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)(?:[,\s/]+([\d.]+))?/.exec(c);
  if (!m || (m[4] !== undefined && +m[4] === 0)) return "";
  return "#" + [m[1], m[2], m[3]].map(x => (+x).toString(16).padStart(2, "0")).join("");
}
const fmtId = id => `${id.slice(6, 8)}/${id.slice(4, 6)}/${id.slice(0, 4)} à ${id.slice(9, 11)}:${id.slice(11, 13)}`;

/* ------------------------------------------------------------------ modifier, annuler, enregistrer, publier */
function canon(o) {   // forme comparable des réglages (sans les vides, clés triées)
  if (Array.isArray(o)) return o.map(canon);
  if (o && typeof o === "object") { const r = {};
    for (const k of Object.keys(o).sort()) { const v = canon(o[k]);   // (toutes les clés comptent : « v » est la variable d'une condition, la cible d'une action)
      if (v == null || v === "" || v === false || (Array.isArray(v) && !v.length) || (typeof v === "object" && !Array.isArray(v) && !Object.keys(v).length)) continue; r[k] = v; }
    return r; }
  return o;
}
const dirty = () => JSON.stringify(canon(cfg)) !== JSON.stringify(canon(published));
function prune(c) {   // ménage : ce qui ne règle plus rien disparaît
  if (c.rules) c.rules = c.rules.filter(r => r.hide || (r.order != null && r.order !== "") || Object.keys(r.css || {}).length);
  for (const k of ["rules", "texts", "adds", "fields", "links", "secs"]) if (c[k] && !c[k].length) delete c[k];
  if (c.theme) {
    for (const g of ["both", "light", "dark"]) if (c.theme[g] && !Object.keys(c.theme[g]).length) delete c.theme[g];
    for (const k of Object.keys(c.theme)) if (c.theme[k] == null || c.theme[k] === "") delete c.theme[k];
    if (!Object.keys(c.theme).length) delete c.theme;
  }
  for (const [t, s] of Object.entries(c.sheets || {})) {
    if (s.hidden && !s.hidden.length) delete s.hidden;
    for (const k of Object.keys(s.labels || {})) if (!s.labels[k]) delete s.labels[k];
    if (s.labels && !Object.keys(s.labels).length) delete s.labels;
    if (!t.endsWith("_wish") && !Object.keys(s).length) delete c.sheets[t];
  }
  if (c.sheets && !Object.keys(c.sheets).length) delete c.sheets;
  if (c.menu) { for (const k of ["order", "hidden", "items"]) if (c.menu[k] && !c.menu[k].length) delete c.menu[k]; if (!Object.keys(c.menu).length) delete c.menu; }
  if (c.cards) { if (c.cards.hide && !c.cards.hide.length) delete c.cards.hide; for (const k of Object.keys(c.cards)) if (c.cards[k] == null || c.cards[k] === "") delete c.cards[k]; if (!Object.keys(c.cards).length) delete c.cards; }
  if (!c.css) delete c.css;
  if (!c.secTitle) delete c.secTitle;
}
function change(fn, o = {}) {   // TOUTE modification des réglages passe par ici
  const before = JSON.stringify(cfg);
  fn(cfg); prune(cfg);
  if (JSON.stringify(cfg) === before) { if (o.redraw !== false) draw(); return; }
  const now = Date.now();
  if (!(o.key && o.key === lastKey && now - lastT < 1500)) { undo.push(before); if (undo.length > 150) undo.shift(); }   // une frappe continue = une seule étape d'annulation
  lastKey = o.key || ""; lastT = now; redo.length = 0;
  pushed();
  if (o.redraw !== false) draw();
}
function pushed() { status(); pushPreview(); clearTimeout(saveT); saveState = "attente"; saveT = setTimeout(saveDraft, 500); status(); }
function pushPreview() { try { const b = BOF(); if (b) { b.apply(clone(cfg)); b.replace(); } } catch (e) { console.warn(e); } }
async function saveDraft() {
  clearTimeout(saveT); saveT = 0;
  try { if (dirty()) await api("/api/bo/draft", { cfg }); else await api("/api/bo/discard", {}); saveState = "ok"; } catch (e) { saveState = "erreur"; toast("Brouillon non enregistré : " + e.message); }
  status();
}
function step(from, to) { if (!from.length) return; to.push(JSON.stringify(cfg)); cfg = JSON.parse(from.pop()); lastKey = ""; pushed(); draw(); }
function replaceAll(next) { change(c => { for (const k of Object.keys(c)) delete c[k]; Object.assign(c, clone(next || {})); }); }
function countAll() {   // même décompte que les lignes de « Mes modifications »
  const th = cfg.theme || {}, mn = cfg.menu || {};
  const nTh = Object.keys(th).filter(k => !["both", "light", "dark"].includes(k)).length + ["both", "light", "dark"].reduce((n, g) => n + Object.keys(th[g] || {}).length, 0);
  return (nTh ? 1 : 0) + (cfg.rules || []).length + (cfg.texts || []).length + (cfg.adds || []).length + Object.keys(cfg.sheets || {}).length + (cfg.fields || []).length + (cfg.links || []).length
    + (mn.order || mn.hidden ? 1 : 0) + (mn.items || []).length + (cfg.cards ? 1 : 0) + (cfg.css ? 1 : 0);
}
async function publish() {
  if (!dirty()) return toast("Rien à publier : le site est déjà à jour.");
  const n = await ask("Publier sur le site", "Vos modifications seront appliquées au site, pour tous ceux qui le consultent. Vous pourrez toujours revenir en arrière depuis « Historique et secours ».",
    "Un mot pour vous y retrouver plus tard (facultatif)", { ph: "ex. : nouvelles couleurs", ok: "✔ Publier" });
  if (n === null) return;
  clearTimeout(saveT); saveT = 0;
  try { const r = await api("/api/bo/publish", { cfg, note: n, count: countAll() }); published = clone(cfg); hist = r.history || hist; saveState = ""; status(); draw(); toast("✔ Publié : le site est à jour."); }
  catch (e) { toast("Publication impossible : " + e.message); }
}
async function discard() {
  if (!dirty()) return;
  if (!await sure("Abandonner le brouillon ?", "Tout ce qui n'est pas publié sera oublié : le back office reviendra à la version actuelle du site.<br>(« Annuler » ↶ permet encore de le récupérer tant que cette page reste ouverte.)", "Abandonner")) return;
  replaceAll(published);
}
function status() {
  const d = dirty(), s = $("#status");
  s.className = "status" + (d ? " dirty" : "");
  s.innerHTML = `<span class="dot"></span>${d ? "<b>Modifications non publiées</b>" : "Le site est à jour"}<small>${saveState === "attente" ? "enregistrement…" : saveState === "erreur" ? "⚠ brouillon non enregistré" : d ? "brouillon enregistré" : ""}</small>`;
  $("#btnUndo").disabled = !undo.length; $("#btnRedo").disabled = !redo.length; $("#btnDiscard").disabled = !d; $("#btnPublish").disabled = !d;
  const c = $("#nav .ct"); if (c) { c.textContent = countAll(); c.hidden = !countAll(); }
}

/* ------------------------------------------------------------------ aperçu */
function go(url) { pick = null; frame.src = url; }
function whenApp(fn) {   // exécute fn quand l'aperçu montre le site, données chargées (au besoin, l'y amène)
  if (BOF()?.page !== "app" && !/^\/(\?|$)/.test(new URL(frame.src || "/", location.href).pathname + "?")) go("/");
  else if (!BOF() && !frame.src) go("/");
  let n = 0;
  const t = setInterval(() => { const b = BOF(); let ok = false; try { ok = !!b && b.page === "app" && b.lists().length > 0; } catch {}
    if (ok) { clearInterval(t); fn(b); } else if (++n > 75) clearInterval(t); }, 200);
}
function setMode(m) {
  mode = m; if (m !== "pick") pick = null;
  try { BOF()?.pick(m === "pick"); } catch {}
  try { BOF()?.move?.(m === "move"); } catch {}   // mode « déplacer à la souris »
  for (const b of $("#pvMode").children) b.classList.toggle("on", b.dataset.mode === m);
  $(".prev").classList.toggle("picking", m !== "use");
  $("#pvNote").innerHTML = m === "move" ? "✋ <b>Déplacer à la souris</b> : attrapez un élément de l'aperçu et déposez-le ailleurs — une barre verte montre où il se posera (Échap : annuler)." : m === "pick" ? "🖱️ Cliquez sur un élément de l'aperçu pour le modifier. Pour naviguer (ouvrir une fiche, un menu…), repassez sur « Utiliser le site »."
    : "L'aperçu montre votre <b>brouillon</b> : vous seul le voyez tant que vous n'avez pas publié.";
  if (panel === "souris") draw();
}
function flash(s, page, hidden) {   // montre un élément dans l'aperçu
  const b = BOF(); if (!b) return;
  if (page && b.page !== page) return toast("Cet élément se trouve sur " + (PAGES[page] || page) + " : affichez d'abord cette page dans l'aperçu.");
  if (hidden && !ghost) { ghost = true; $("#pvGhost").checked = true; b.ghost(true); }
  if (!b.flash(s)) toast("Cet élément n'est pas à l'écran en ce moment : ouvrez dans l'aperçu l'endroit où il se trouve.");
}
window.BO_ADMIN = {   // ce que /bo.js (dans l'aperçu) appelle
  cfg: () => clone(cfg),
  onReady() {
    pick = null;
    const b = BOF(); if (b) { try { b.pick(mode === "pick"); b.move?.(mode === "move"); b.ghost(ghost); } catch {} }
    try { const p = FW().location.pathname, o = [...$("#pvPage").options].find(x => x.value.split("?")[0] === p); if (o) $("#pvPage").value = o.value; } catch {}
    if (panel === "souris") draw();
    if (b?.page === "app" && ["fiches", "menu", "donnees", "champs", "liens"].includes(panel)) whenApp(() => draw());
  },
  onPick(info) {
    pick = info;
    if (info) { const has = s => [cfg.rules, cfg.texts, cfg.adds].some(l => (l || []).some(r => r.sel === s));
      scope = { sim: !has(info.one) && info.sim !== info.one && has(info.sim), all: false };
      scope.all = [cfg.rules, cfg.texts, cfg.adds].some(l => (l || []).some(r => r.sel === (scope.sim ? info.sim : info.one) && !r.page)); }
    if (panel !== "souris") show("souris"); else draw();
  },
  onSheet(info) {
    const sig = info ? info.real + "|" + info.blocks.map(b => b.key + (b.shown ? 1 : 0)).join(",") : "";
    if (info && SHEETS.some(s => s[0] === info.real) && panel === "fiches" && !noSample) shType = info.real;
    if (sig !== shSig) { shSig = sig; if (panel === "fiches") draw(); }
  },
};

/* ------------------------------------------------------------------ rubriques : affichage */
function show(p) {
  if (!PANELS.some(x => x[0] === p)) p = "accueil";
  const was = panel; panel = p;
  if (location.hash.slice(1) !== p) history.replaceState(null, "", "#" + p);
  if (p === "souris") setMode("pick"); else if (was === "souris" && mode !== "use") setMode("use");
  $("#panel").scrollTop = 0;
  draw();
  if (p === "fiches") whenApp(b => { if (!b.sheetInfo()) openSample(); else draw(); });
  if (["menu", "cartes"].includes(p)) { try { BOF()?.close(); } catch {} }   // la fiche d'exemple ouverte cacherait le menu et les cartes
  if (["menu", "donnees", "champs", "liens"].includes(p)) whenApp(() => draw());
}
function draw() {
  const box = $("#panel"), y = box.scrollTop;
  let kids;
  try { kids = VIEW[panel](); } catch (e) { console.error(e); kids = [el("div", { class: "note warn" }, "Cette rubrique n'a pas pu s'afficher : " + e.message)]; }
  box.replaceChildren(...[kids].flat(Infinity).filter(k => k != null && k !== false && k !== ""));
  box.scrollTop = y;
  for (const b of $("#nav").children) b.classList?.toggle("on", b.dataset.p === panel);
}
function orderList(rows, onMove) {   // liste à ordonner : glisser la poignée, ou ▲ ▼
  let from = -1;
  // ▲ ▼ sautent les lignes « absentes » (blocs qui ne servent pas sur la fiche d'exemple) : chaque clic se voit dans l'aperçu
  const next = (i, d) => { if (rows[i].absent) return i + d; for (let j = i + d; j >= 0 && j < rows.length; j += d) if (!rows[j].absent) return j; return -1; };
  return el("div", { class: "ord" }, rows.map((r, i) => {
    const up = next(i, -1), down = next(i, 1);
    const it = el("div", { class: "it" + (r.off ? " off" : "") + (r.absent ? " absent" : ""),
      ondragover: e => { if (from < 0 || from === i) return; e.preventDefault(); it.classList.add("over"); },
      ondragleave: () => it.classList.remove("over"),
      ondrop: e => { e.preventDefault(); it.classList.remove("over"); const f = from; from = -1; if (f >= 0 && f !== i) onMove(f, f < i ? i - 1 : i); } },
      el("span", { class: "grip", draggable: true, title: "Faire glisser pour déplacer",
        ondragstart: e => { from = i; it.classList.add("dragging"); e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", r.key); try { e.dataTransfer.setDragImage(it, 12, 12); } catch {} },
        ondragend: () => it.classList.remove("dragging") }, "⠿"),
      el("span", { class: "mv" }, el("button", { type: "button", title: "Monter", disabled: up < 0, onclick: () => onMove(i, up) }, "▲"),
        el("button", { type: "button", title: "Descendre", disabled: down < 0 || down >= rows.length, onclick: () => onMove(i, down) }, "▼")),
      el("span", { class: "nm" }, el("b", { title: r.name }, r.name), r.sub && el("span", {}, r.sub), r.below),
      r.tools);
    return it;
  }));
}
const moved = (arr, from, to) => { const a = [...arr]; a.splice(to, 0, a.splice(from, 1)[0]); return a; };
const VIEW = {};

/* ---------- Accueil */
VIEW.accueil = () => [
  head("Bienvenue dans le back office", "Ici, vous changez l'apparence et l'organisation du site sans écrire une seule ligne de code."),
  copie && note("🧪 Vous êtes sur la <b>copie de travail</b> : rien de ce que vous faites ici ne touche le vrai site."),
  card("Comment ça marche",
    el("ol", { class: "steps" },
      el("li", { html: "<b>Vous modifiez</b> avec les rubriques ci-dessous, ou en cliquant directement dans l'aperçu (« Modifier à la souris »)." }),
      el("li", { html: "<b>L'aperçu à droite</b> montre le résultat tout de suite. C'est un brouillon : vous seul le voyez." }),
      el("li", { html: "<b>« ✔ Publier sur le site »</b>, en haut, l'applique pour de bon." })),
    hint("Rien n'est définitif : « ↶ Annuler », « Abandonner le brouillon » et la rubrique « Historique et secours » permettent toujours de revenir en arrière.")),
  el("div", { class: "tiles" }, PANELS.slice(1).map(([id, ic, nm, ds]) => el("button", { type: "button", onclick: () => show(id) }, el("b", {}, ic + " " + nm), el("span", {}, ds)))),
];

/* ---------- Modifier à la souris */
const pSel = () => scope.sim && pick.sim ? pick.sim : pick.one;
const pPage = () => scope.all ? "" : pick.page;
const sameT = o => o.sel === pSel() && (o.page || "") === pPage();
const getRule = (c, make) => { let r = (c.rules || []).find(sameT); if (!r && make) { r = { id: uid(), sel: pSel(), page: pPage(), label: pick.desc, css: {} }; (c.rules ||= []).push(r); } return r; };
function setCss(prop, val) {
  change(c => { const r = getRule(c, true); r.css ||= {};
    if (val == null || val === "") delete r.css[prop]; else r.css[prop] = val;
    if (prop === "border-width") { if (r.css[prop]) r.css["border-style"] = "solid"; else delete r.css["border-style"]; }
  }, { key: "css" + prop + pSel(), redraw: false });
}
function setText(attr, from, to) {
  change(c => { c.texts ||= [];
    const i = c.texts.findIndex(t => sameT(t) && (t.attr || "") === attr && t.from === from);
    if (to === from) { if (i >= 0) c.texts.splice(i, 1); return; }
    if (i >= 0) c.texts[i].to = to; else c.texts.push({ id: uid(), from, to, sel: pSel(), page: pPage(), attr: attr || undefined, label: pick.desc });
  }, { key: "txt" + attr + pSel(), redraw: false });
}
const STYLES = [
  ["color", "Couleur du texte", "color"], ["background", "Couleur de fond", "color", "background-color"], ["font-size", "Taille du texte", "px"],
  ["font-weight", "Gras", "sel", [["", "comme à l'origine"], ["800", "gras"], ["400", "pas gras"]]],
  ["font-style", "Italique", "sel", [["", "comme à l'origine"], ["italic", "italique"], ["normal", "droit"]]],
  ["text-transform", "Majuscules", "sel", [["", "comme à l'origine"], ["uppercase", "TOUT EN MAJUSCULES"], ["none", "normales"]]],
  ["text-align", "Alignement", "sel", [["", "comme à l'origine"], ["left", "à gauche"], ["center", "au centre"], ["right", "à droite"]]],
  ["border-radius", "Coins arrondis", "px"], ["border-width", "Bordure : épaisseur", "px"], ["border-color", "Bordure : couleur", "color"],
  ["padding", "Espace intérieur", "px"], ["margin", "Espace autour", "px"], ["width", "Largeur", "px"], ["height", "Hauteur", "px"], ["opacity", "Opacité", "pct"],
];
function styleRow([prop, label, kind, extra]) {
  const cur = getRule(cfg)?.css?.[prop] ?? "", comp = pick.css[kind === "color" && extra ? extra : prop] || "";
  let ctl;
  if (kind === "color") ctl = el("input", { type: "color", value: toHex(cur || comp) || "#ffffff", oninput: e => setCss(prop, e.target.value) });
  else if (kind === "px") ctl = [el("input", { type: "number", class: "num", min: 0, max: 3000, value: cur ? parseFloat(cur) : "", placeholder: comp && !isNaN(parseFloat(comp)) ? Math.round(parseFloat(comp)) : "",
    oninput: e => setCss(prop, e.target.value === "" ? "" : e.target.value + "px") }), el("span", { class: "u" }, "px")];
  else if (kind === "pct") ctl = [el("input", { type: "range", min: 5, max: 100, step: 5, value: cur ? Math.round(cur * 100) : 100, oninput: e => setCss(prop, +e.target.value >= 100 ? "" : String(e.target.value / 100)) })];
  else ctl = sel(cur, extra, v => setCss(prop, v));
  return [el("span", { class: "lab", style: cur ? "font-weight:700" : "" }, label), el("span", { class: "ctl" }, ctl),
    el("button", { type: "button", class: "x", title: "Remettre comme à l'origine", onclick: () => { setCss(prop, ""); draw(); } }, "↺")];
}
function addEditor(a) {   // un élément ajouté (texte, bouton, image…)
  const set = (k, v, redraw) => change(c => { const x = (c.adds || []).find(x => x.id === a.id); if (x) { if (v === "" || v == null || v === false) delete x[k]; else x[k] = v; } }, { key: "add" + a.id + k, redraw: !!redraw });
  return el("div", { class: "ed" + (a.off ? " offed" : "") },
    a.kind !== "sep" && a.kind !== "image" && fld(ADDK[a.kind], txt(a.text, v => set("text", v), a.kind === "bouton" ? "Texte du bouton" : "Votre texte")),
    a.kind === "bouton" && fld("Adresse ouverte par le bouton", txt(a.url, v => set("url", v), "https://…"), ""),
    a.kind === "bouton" && chk("Ouvrir dans le même onglet", a.same, v => set("same", v, true)),
    a.kind === "image" && fld("Image", line(txt(/^data:/.test(a.url || "") ? "" : a.url, v => set("url", v), /^data:/.test(a.url || "") ? "(image choisie sur l'ordinateur)" : "Adresse de l'image, https://…"),
      btn("Choisir un fichier…", () => pickImage(900, d => set("url", d, true)), "small"))),
    a.kind === "image" && line(el("span", { class: "lab" }, "Largeur de l'image"), el("input", { type: "number", class: "num", min: 10, max: 2000, value: a.w || "", placeholder: "auto", oninput: e => set("w", e.target.value === "" ? "" : +e.target.value) }), el("span", { class: "hint" }, "px")),
    el("div", { class: "ed-foot" }, el("span", { class: "hint" }, "Placé"), sel(a.pos || "after", POS, v => set("pos", v, true)),
      btn("Supprimer", () => change(c => { c.adds = (c.adds || []).filter(x => x.id !== a.id); }), "small danger")));
}
const POS = [["after", "juste après l'élément"], ["before", "juste avant l'élément"], ["end", "dans l'élément, à la fin"], ["start", "dans l'élément, au début"]];
VIEW.souris = () => {
  const top = head("Modifier à la souris", "Cliquez sur n'importe quel élément du site, dans l'aperçu à droite : vous pourrez le renommer, le masquer, changer son style, le déplacer ou ajouter quelque chose à côté.");
  if (mode !== "pick") return [top, el("div", { class: "empty" }, el("p", {}, "Le clic dans l'aperçu sert en ce moment à utiliser le site."), btn("🖱️ Activer « Cliquer pour modifier »", () => setMode("pick"), "primary big"))];
  if (!pick) return [top,
    el("div", { class: "empty" }, el("p", { html: "👉 <b>Cliquez sur un élément dans l'aperçu.</b>" }), el("p", { class: "hint" }, "Il s'entoure de bleu au survol, puis d'orange une fois choisi.")),
    card("Besoin d'aller ailleurs dans le site ?", para("Pour ouvrir une fiche, un menu ou une autre page avant de cliquer dessus :"),
      el("ol", { class: "steps" }, el("li", {}, "passez l'aperçu sur « 👆 Utiliser le site » ;"), el("li", {}, "allez à l'endroit voulu ;"), el("li", {}, "revenez sur « 🖱️ Cliquer pour modifier »."))),
    card("Bon à savoir", hint("Pour l'ordre des blocs d'une fiche ou du menu, les rubriques « Fiches » et « Menu » sont plus pratiques. Tout ce que vous faites ici se retrouve dans « Mes modifications »."))];
  const r = getRule(cfg), hasSim = pick.sim && pick.sim !== pick.one && pick.nSim > 1;
  const tr = attr => (cfg.texts || []).find(t => sameT(t) && (t.attr || "") === attr);
  const adds = (cfg.adds || []).filter(sameT);
  const textRow = (label, attr, from) => fld(label, line(txt(tr(attr) ? tr(attr).to : from, v => setText(attr, from, v), from),
    el("button", { type: "button", class: "x", title: "Remettre le texte d'origine", onclick: () => { setText(attr, from, from); draw(); } }, "↺")), "Texte d'origine : « " + from.replace(/</g, "&lt;") + " »");
  return [top,
    el("div", { class: "picked" }, el("b", {}, pick.desc), el("div", { class: "crumbs", title: pick.crumbs.join(" ‹ ") }, pick.crumbs.length ? "dans : " + pick.crumbs.join(" ‹ ") : ""),
      el("div", { class: "btns" }, btn("⬆ Sélectionner ce qui l'entoure", () => BOF()?.pickParent(), "small", "Choisir l'élément qui contient celui-ci"),
        btn("✕ Désélectionner", () => { BOF()?.unpick(); pick = null; draw(); }, "small"))),
    card("À quoi appliquer vos changements ?",
      hasSim ? sel(scope.sim ? "sim" : "one", [["one", "Seulement cet élément"], ["sim", `Tous les éléments du même genre (${pick.nSim} à l'écran)`]], v => { scope.sim = v === "sim"; draw(); }) : null,
      el("div", { style: "height:6px" }),
      sel(scope.all ? "all" : "page", [["page", "Seulement sur " + (PAGES[pick.page] || "cette page")], ["all", "Sur toutes les pages du site"]], v => { scope.all = v === "all"; draw(); })),
    card("Texte",
      pick.text ? textRow("Texte affiché", "", pick.text) : hint("Cet élément ne contient pas de texte directement. Pour changer un texte, cliquez précisément sur lui."),
      pick.placeholder ? textRow("Texte grisé dans le champ (avant de taper)", "placeholder", pick.placeholder) : null,
      pick.title ? textRow("Info-bulle (au survol)", "title", pick.title) : null),
    card("Afficher ou masquer",
      chk("Masquer cet élément", r?.hide, v => change(c => { const x = getRule(c, true); if (v) x.hide = true; else delete x.hide; })),
      r?.hide ? hint("Masqué. Pour le revoir dans l'aperçu, cochez « Montrer ce qui est masqué » au-dessus de l'aperçu ; il reste aussi listé dans « Mes modifications ».") : null),
    pick.flexParent ? card("Position", para("Par rapport aux éléments voisins :"),
      el("div", { class: "btns" }, btn("⏮ Mettre en premier", () => change(c => { getRule(c, true).order = -1; }), r?.order === -1 ? "on" : ""), btn("Mettre en dernier ⏭", () => change(c => { getRule(c, true).order = 99; }), r?.order === 99 ? "on" : ""),
        btn("↺ Place d'origine", () => change(c => { const x = getRule(c); if (x) delete x.order; })))) : null,
    card("Style", el("div", { class: "st" }, STYLES.map(styleRow)), hint("En gras : ce que vous avez changé. ↺ remet la valeur d'origine.")),
    card("Ajouter quelque chose à côté",
      fld("Où ?", sel(addPos, POS, v => { addPos = v; })),
      el("div", { class: "btns" }, Object.entries(ADDK).map(([k, l]) => btn("+ " + l, () => change(c => { (c.adds ||= []).push({ id: uid(), sel: pSel(), page: pPage(), pos: addPos, kind: k,
        text: k === "texte" ? "Votre texte" : k === "titre" ? "Votre titre" : k === "bouton" ? "Mon lien" : undefined, label: pick.desc }); }), "small"))),
      adds.length ? el("div", { style: "margin-top:10px" }, adds.map(addEditor)) : null),
    card("Tout annuler pour cet élément", btn("↺ Remettre cet élément comme à l'origine", () => change(c => { for (const k of ["rules", "texts", "adds"]) c[k] = (c[k] || []).filter(o => !sameT(o)); }), "danger")),
  ];
};

/* ---------- Apparence */
function setTheme(k, v, key, redraw) { change(c => { c.theme ||= {}; if (v == null || v === "") delete c.theme[k]; else c.theme[k] = v; }, { key: "th" + (key || k), redraw: !!redraw }); }
function setColor(g, k, v, redraw) { change(c => { c.theme ||= {}; c.theme[g] ||= {}; if (!v || v === DEF[g][k]) delete c.theme[g][k]; else c.theme[g][k] = v; }, { key: "col" + g + k, redraw: !!redraw }); }
const colorRow = (g, k) => line(el("span", { class: "lab", style: cfg.theme?.[g]?.[k] ? "font-weight:700" : "" }, COLORS[k]),
  el("input", { type: "color", value: cfg.theme?.[g]?.[k] || DEF[g][k], oninput: e => setColor(g, k, e.target.value) }),
  el("button", { type: "button", class: "x", title: "Remettre la couleur d'origine", onclick: () => setColor(g, k, "", true) }, "↺"));
VIEW.apparence = () => {
  const th = cfg.theme || {}, dark = (() => { try { return !!BOF()?.dark(); } catch { return false; } })();
  const isImg = /^data:image\//.test(th.logo || "");
  return [head("Apparence", "L'allure générale du site : son nom, son logo, ses couleurs, ses formes."),
    card("Nom et logo",
      fld("Nom du site", txt(th.brand, v => setTheme("brand", v), "Briquothèque"), "Remplace « Briquothèque » partout où il apparaît."),
      fld("Logo", line(txt(isImg ? "" : th.logo, v => setTheme("logo", v), isImg ? "(image choisie)" : "un emoji, ex. 🧱"), btn("Choisir une image…", () => pickImage(96, d => setTheme("logo", d, "", true)), "small"),
        btn("↺", () => setTheme("logo", "", "", true), "small", "Remettre la brique d'origine")), "Un emoji ou une petite image à la place de la brique rouge.")),
    card("Ambiances toutes prêtes", el("div", { class: "btns" }, PRESETS.map(([n, c, l, d]) => btn([el("span", { class: "sw", style: "background:" + (c || DEF.both.red) }), n], () => change(x => {
      x.theme ||= {}; for (const g of ["both", "light", "dark"]) x.theme[g] ||= {};
      if (!c) { delete x.theme.both.red; delete x.theme.light["accent-bg"]; delete x.theme.dark["accent-bg"]; } else { x.theme.both.red = c; x.theme.light["accent-bg"] = l; x.theme.dark["accent-bg"] = d; }
    }), "small"))), hint("Un clic change la couleur principale ; vous pouvez ensuite tout affiner ci-dessous.")),
    card("Couleurs communes", el("div", { class: "rowset" }, Object.keys(DEF.both).map(k => colorRow("both", k)))),
    card(el("span", {}, "Couleurs selon le mode de l'écran"),
      el("div", { class: "pills" }, [["light", "☀️ Mode clair"], ["dark", "🌙 Mode sombre"]].map(([k, l]) => el("button", { type: "button", class: themeTab === k ? "on" : "", onclick: () => { themeTab = k; draw(); } }, l))),
      (themeTab === "dark") !== dark ? note(`Votre écran est en mode ${dark ? "sombre" : "clair"} : ces couleurs-ci ne se verront pas dans l'aperçu (elles servent aux écrans en mode ${dark ? "clair" : "sombre"}).`, "warn") : null,
      el("div", { class: "rowset" }, Object.keys(DEF[themeTab]).map(k => colorRow(themeTab, k)))),
    card("Formes et texte",
      fld("Arrondi des coins", line(el("input", { type: "range", min: 0, max: 26, value: th.radius ?? 14, oninput: e => { setTheme("radius", +e.target.value === 14 ? "" : +e.target.value); e.target.nextSibling.textContent = e.target.value + " px"; } }), el("span", { class: "hint" }, (th.radius ?? 14) + " px"))),
      fld("Police d'écriture", sel(th.font || "", [["", "Celle d'origine"], ["arrondie", "Arrondie"], ["humaniste", "Large et lisible (Verdana)"], ["etroite", "Étroite"], ["serif", "À empattements (Georgia)"], ["mono", "Machine à écrire"]], v => setTheme("font", v, "", true))),
      fld("Taille générale", line(el("input", { type: "range", min: 80, max: 140, step: 5, value: th.zoom || 100, oninput: e => { setTheme("zoom", +e.target.value === 100 ? "" : +e.target.value); e.target.nextSibling.textContent = e.target.value + " %"; } }), el("span", { class: "hint" }, (th.zoom || 100) + " %")), "Grossit ou réduit tout le site d'un coup.")),
    card("", btn("↺ Remettre toute l'apparence d'origine", () => change(c => { delete c.theme; }), "danger")),
  ];
};

/* ---------- Textes */
function pickText() {
  const b = BOF(); if (!b) return;
  const used = new Set((cfg.texts || []).filter(t => !t.sel).map(t => t.from));
  choose("Choisir un texte affiché dans l'aperçu", b.texts().filter(t => !used.has(t.from)).map(t => ({ v: t.from, label: t.from })), { empty: "Aucun texte trouvé dans l'aperçu." })
    .then(v => { if (v) change(c => { (c.texts ||= []).push({ id: uid(), from: v, to: "", mode: "exact" }); }); });
}
VIEW.textes = () => {
  const glob = (cfg.texts || []).filter(t => !t.sel), loc = (cfg.texts || []).filter(t => t.sel);
  const set = (t, k, v, redraw) => change(c => { const x = (c.texts || []).find(x => x.id === t.id); if (x) { if (v === false || v == null) delete x[k]; else x[k] = v; } }, { key: "t" + t.id + k, redraw: !!redraw });
  const del = t => change(c => { c.texts = (c.texts || []).filter(x => x.id !== t.id); });
  return [head("Textes", "Remplacez n'importe quel mot ou phrase du site par le vôtre. Exemple : « Figurines » → « Personnages »."),
    card("Remplacements",
      glob.length ? glob.map(t => el("div", { class: "tx" },
        txt(t.from, v => set(t, "from", v), "Texte actuel"), el("span", {}, "→"), txt(t.to, v => set(t, "to", v), "Votre texte"),
        el("button", { type: "button", class: "x", title: "Supprimer ce remplacement", onclick: () => del(t) }, "✕"),
        el("div", { class: "opt" }, sel(t.mode === "mot" ? "mot" : "exact", [["mot", "partout, même au milieu d'une phrase"], ["exact", "seulement quand c'est le texte entier"]], v => set(t, "mode", v, true)),
          t.mode === "mot" ? chk("majuscules indifférentes", t.ci, v => set(t, "ci", v)) : null)))
        : el("p", { class: "hint" }, "Aucun remplacement pour l'instant."),
      el("div", { class: "btns" }, btn("+ Ajouter un remplacement", () => change(c => { (c.texts ||= []).push({ id: uid(), from: "", to: "", mode: "mot", ci: true }); }), "primary"),
        btn("🔍 Choisir un texte dans l'aperçu…", pickText)),
      hint("Pensez au pluriel : « Figurine » et « Figurines » sont deux remplacements différents.")),
    loc.length ? card("Textes changés à la souris", hint("Ils ne concernent qu'un élément précis."),
      loc.map(t => el("div", { class: "tx" }, el("span", { class: "hint", title: t.from }, "« " + t.from.slice(0, 40) + " »"), el("span", {}, "→"), txt(t.to, v => set(t, "to", v), "Votre texte"),
        el("button", { type: "button", class: "x", title: "Supprimer", onclick: () => del(t) }, "✕")))) : null,
    card("Autre façon de faire", para("Dans « 🖱️ Modifier à la souris », cliquez directement sur un texte du site pour le changer à cet endroit seulement."), btn("Ouvrir « Modifier à la souris »", () => show("souris"), "small")),
  ];
};

/* ---------- Fiches (squelettes) */
const secName = id => id === "_" ? (cfg.secTitle || "Informations personnelles") : (cfg.secs || []).find(s => s.id === id)?.label || "Bloc";
function customKeys(base) {   // blocs personnalisés qui apparaissent sur ce type de fiche
  const secs = cfg.secs || [], used = new Set((cfg.fields || []).filter(f => !f.off && (!(f.types || []).length || f.types.includes(base))).map(f => secs.some(s => s.id === f.sec) ? f.sec : "_"));
  return [...secs.map(s => s.id), "_"].filter(s => used.has(s)).map(s => "x-" + s);
}
function sheetKeys(live) {   // tous les blocs de ce type de fiche, dans l'ordre réglé (ou d'origine)
  const conf = cfg.sheets?.[shType] ?? cfg.sheets?.[BASE(shType)] ?? {}, custom = customKeys(BASE(shType));
  const nat = NATURAL.filter(k => !(BASE(shType) === "fig" && (k === "altBox" || k === "accBox")));
  nat.splice(nat.indexOf("links-row"), 0, ...custom);
  const dom = live ? live.blocks.map(b => b.key) : [];
  const ord = (conf.order || []).filter(k => !k.startsWith("x-") || custom.includes(k));
  const merge = src => src.forEach((k, i) => { if (ord.includes(k)) return; const prev = src.slice(0, i).reverse().find(p => ord.includes(p)); ord.splice(prev ? ord.indexOf(prev) + 1 : 0, 0, k); });
  if (!ord.length) ord.push(...(dom.length ? dom : nat));
  merge(dom); merge(nat);
  return ord;
}
const shConf = c => { c.sheets ||= {}; if (!c.sheets[shType]) c.sheets[shType] = clone(c.sheets[BASE(shType)] || {}); return c.sheets[shType]; };
function openSample() { noSample = false; whenApp(b => { let ok = false; try { ok = b.open(shType); } catch (e) { console.warn(e); } noSample = !ok; if (!ok) draw(); }); }
VIEW.fiches = () => {
  const b = BOF();
  let live = null, counts = {};
  try { live = b?.sheetInfo() || null; counts = b?.types() || {}; } catch {}
  const match = live && live.real === shType ? live : null, base = BASE(shType), wish = shType !== base, own = !!cfg.sheets?.[shType];
  const conf = cfg.sheets?.[shType] ?? cfg.sheets?.[base] ?? {}, keys = sheetKeys(match);
  const P = `#stepConfig > [data-bo-key="`;
  const rows = keys.map(k => {
    const i = match?.blocks.find(x => x.key === k), custom = k.startsWith("x-"), hid = (conf.hidden || []).includes(k);
    const absent = !!match && !hid && (!i || !i.shown);
    return { key: k, name: custom ? "🧩 " + secName(k.slice(2)) : BLOCKS[k] || i?.legend || k, off: hid, absent,
      sub: hid ? "masqué par vous" : absent ? "pas utilisé sur la fiche d'exemple" : conf.labels?.[k] ? "renommé" : i?.legend && BLOCKS[k] !== i.legend ? "« " + i.legend + " »" : "",
      below: i?.legend && !custom ? el("input", { type: "text", value: conf.labels?.[k] || "", placeholder: "Renommer « " + i.legend + " »…", title: "Nouveau titre du bloc (laisser vide pour garder le titre d'origine)",
        oninput: e => change(c => { const s = shConf(c); s.labels ||= {}; s.labels[k] = e.target.value.trim(); }, { key: "lab" + k, redraw: false }) }) : null,
      tools: [el("button", { type: "button", class: "eye", title: hid ? "Réafficher ce bloc" : "Masquer ce bloc", onclick: async () => {
          if (!hid && k === "estimate" && !await sure("Masquer la barre du bas ?", "Sans elle, on ne peut plus <b>enregistrer</b> ni <b>supprimer</b> une fiche de ce type. Masquer quand même ?", "Masquer")) return;
          change(c => { const s = shConf(c); s.hidden = hid ? (s.hidden || []).filter(x => x !== k) : [...(s.hidden || []), k]; }); } }, hid ? "🚫 Masqué" : "👁 Affiché"),
        btn("Voir", () => flash(P + k + '"]', "app", hid), "small", "Montrer ce bloc dans l'aperçu")] };
  });
  return [head("Fiches", "Le squelette d'une fiche : dans quel ordre viennent ses blocs, lesquels sont masqués, comment ils s'appellent. Chaque type de fiche a son propre squelette."),
    el("div", { class: "pills" }, SHEETS.map(([k, l]) => el("button", { type: "button", class: shType === k ? "on" : "", onclick: () => { shType = k; noSample = false; draw(); openSample(); } }, l, counts[k] ? el("span", { class: "n" }, counts[k]) : null))),
    noSample ? note("Vous n'avez aucune fiche de ce type : pas d'exemple à montrer dans l'aperçu, mais vous pouvez régler son squelette quand même.", "warn")
      : !match ? el("div", { class: "note" }, "Pour voir le résultat en direct : ", btn("Ouvrir une fiche d'exemple dans l'aperçu", openSample, "small")) : null,
    wish && !own ? note(`Tant que vous ne changez rien ici, cette fiche suit le squelette de « ${sheetName(base)} ».`) : null,
    orderList(rows, (f, t) => change(c => { shConf(c).order = moved(keys, f, t); })),
    hint("⠿ faites glisser, ou utilisez ▲ ▼. Les blocs grisés existent mais ne servent pas sur la fiche d'exemple (ils apparaissent sur d'autres fiches du même type)."),
    card("Aller plus loin",
      el("div", { class: "btns" }, btn("🧩 Ajouter mes propres champs et blocs", () => show("champs"), "small"), btn("🖱️ Modifier un détail à l'intérieur d'un bloc", () => show("souris"), "small"),
        cfg.sheets?.[shType] ? btn("↺ Remettre ce squelette d'origine", () => change(c => { delete c.sheets[shType]; }), "small danger") : null)),
  ];
};

/* ---------- Champs personnalisés */
async function newField() {
  const name = await ask("Nouveau champ", "Comment s'appelle cette information ?", "Nom du champ", { ph: "ex. : État de la boîte", ok: "Créer" });
  if (!name) return;
  let id = slug(name) || "champ"; const ids = new Set((cfg.fields || []).map(f => f.id));
  for (let n = 2; ids.has(id); n++) id = (slug(name) || "champ") + "_" + n;
  change(c => { (c.fields ||= []).push({ id, label: name, type: "text" }); });
  showFields();
}
function showFields() {   // montre, dans l'aperçu, les champs personnalisés sur une fiche d'exemple
  whenApp(b => { try { if (!b.sheetInfo()) b.open("set") || b.open("fig"); } catch {} setTimeout(() => { try { BOF()?.flash("#stepConfig .bo-x"); } catch {} }, 900); });
}
async function newSec(then) {
  const name = await ask("Nouveau bloc", "Un bloc regroupe plusieurs champs sous un même titre, sur la fiche.", "Titre du bloc", { ph: "ex. : Rangement", ok: "Créer" });
  if (!name) return;
  const id = uid();
  change(c => { (c.secs ||= []).push({ id, label: name }); if (then) then(c, id); });
}
VIEW.champs = () => {
  const fs = cfg.fields || [], secs = cfg.secs || [];
  const set = (f, k, v, redraw) => change(c => { const x = (c.fields || []).find(x => x.id === f.id); if (x) { if (v === "" || v == null || v === false || (Array.isArray(v) && !v.length)) delete x[k]; else x[k] = v; } }, { key: "f" + f.id + k, redraw: !!redraw });
  const secOpts = [["", secName("_")], ...secs.map(s => [s.id, s.label]), ["+", "+ Nouveau bloc…"]];
  return [head("Champs personnalisés", "Ajoutez vos propres informations aux fiches. Chaque champ apparaît sur la fiche, prêt à remplir ; il peut aussi s'afficher sur les cartes des listes."),
    fs.length ? fs.map((f, i) => el("div", { class: "ed" + (f.off ? " offed" : "") },
      el("div", { class: "cols" }, fld("Nom", txt(f.label, v => set(f, "label", v), "Nom du champ")), fld("Type", sel(f.type || "text", FTYPES, v => set(f, "type", v, true)))),
      ["choice", "multi"].includes(f.type) ? fld("Choix proposés", el("textarea", { rows: 3, value: (f.opts || []).join("\n"), placeholder: "Un choix par ligne", oninput: e => set(f, "opts", e.target.value.split("\n").map(s => s.trim()).filter(Boolean)) }), "Un choix par ligne.") : null,
      f.type === "item" ? hint("Sur la fiche : un bouton « + Relier une fiche » ; un clic sur une fiche reliée l'ouvre.") : null,
      fld("Sur quelles fiches ?", el("div", { class: "checks" }, KINDS.map(([k, l]) => chk(l, (f.types || []).includes(k), v => set(f, "types", v ? [...(f.types || []), k] : (f.types || []).filter(x => x !== k), true)))),
        (f.types || []).length ? "" : "Rien de coché = sur toutes les fiches."),
      el("div", { class: "cols" },
        fld("Rangé dans le bloc", sel(secs.some(s => s.id === f.sec) ? f.sec : "", secOpts, v => v === "+" ? newSec((c, id) => { const x = c.fields.find(x => x.id === f.id); if (x) x.sec = id; }).then(draw) : set(f, "sec", v, true))),
        fld("Aide (facultatif)", txt(f.help, v => set(f, "help", v), "Affichée sous le champ"))),
      chk("Afficher aussi sur les cartes des listes", f.card, v => set(f, "card", v, true)),
      el("div", { class: "ed-foot" }, el("span", { class: "hint", title: "Sert dans « Liens automatiques » : {" + f.id + "}" }, "identifiant : " + f.id),
        btn("▲", () => change(c => { c.fields = moved(c.fields, i, i - 1); }), "small", "Monter"), btn("▼", () => change(c => { c.fields = moved(c.fields, i, Math.min(fs.length - 1, i + 1)); }), "small", "Descendre"),
        btn("Supprimer", async () => { if (await sure("Supprimer le champ « " + f.label + " » ?", "Il disparaîtra des fiches. Les valeurs déjà saisies restent enregistrées dans les fiches (elles reviennent si vous recréez un champ du même nom).", "Supprimer")) change(c => { c.fields = c.fields.filter(x => x.id !== f.id); }); }, "small danger"))))
      : el("div", { class: "empty" }, "Aucun champ personnalisé pour l'instant."),
    el("div", { class: "btns", style: "margin-bottom:12px" }, btn("+ Ajouter un champ", newField, "primary big")),
    card("Blocs (groupes de champs)", hint("Sur la fiche, les champs sont regroupés en blocs. L'ordre des blocs dans la fiche se règle dans « Fiches »."),
      fld("Titre du bloc par défaut", txt(cfg.secTitle, v => change(c => { c.secTitle = v; }, { key: "secTitle", redraw: false }), "Informations personnelles")),
      secs.map(s => line(txt(s.label, v => change(c => { const x = c.secs.find(x => x.id === s.id); if (x) x.label = v; }, { key: "sec" + s.id, redraw: false }), "Titre du bloc"),
        el("button", { type: "button", class: "x", title: "Supprimer ce bloc (ses champs retournent dans le bloc par défaut)", onclick: () => change(c => { c.secs = c.secs.filter(x => x.id !== s.id); }) }, "✕"))),
      el("div", { class: "btns", style: "margin-top:8px" }, btn("+ Nouveau bloc", () => newSec(), "small"))),
    fs.length ? card("Où les voir ?", para("Ouvrez une fiche dans l'aperçu : vos champs sont en bas, avant les liens."), btn("Montrer mes champs sur une fiche d'exemple", showFields, "small")) : null,
  ];
};

/* ---------- Liens automatiques */
VIEW.liens = () => {
  const ls = cfg.links || [];
  const set = (l, k, v, redraw) => change(c => { const x = (c.links || []).find(x => x.id === l.id); if (x) { if (v === "" || v == null || (Array.isArray(v) && !v.length)) delete x[k]; else x[k] = v; } }, { key: "l" + l.id + k, redraw: !!redraw });
  const vars = [["numero", "numéro"], ["nom", "nom"], ["annee", "année"], ["theme", "thème"], ...(cfg.fields || []).map(f => [f.id, f.label])];
  return [head("Liens automatiques", "Un bouton ajouté en bas de chaque fiche, qui ouvre un autre site déjà positionné sur le bon set ou la bonne figurine."),
    ls.length ? ls.map(l => el("div", { class: "ed" + (l.off ? " offed" : "") },
      fld("Texte du bouton", txt(l.label, v => set(l, "label", v), "ex. : Notice")),
      fld("Adresse", txt(l.url, v => set(l, "url", v), "https://…{numero}"), "Cliquez sur une information ci-dessous pour l'ajouter à l'adresse : elle sera remplacée par celle de la fiche."),
      el("div", { class: "btns", style: "margin:-6px 0 10px" }, vars.map(([k, n]) => btn("{" + n + "}", e => { const inp = e.target.closest(".ed").querySelectorAll("input[type=text]")[1]; inp.value += "{" + k + "}"; set(l, "url", inp.value); inp.focus(); }, "small", "Sera remplacé par : " + n + " de la fiche"))),
      fld("Sur quelles fiches ?", el("div", { class: "checks" }, KINDS.map(([k, n]) => chk(n, (l.types || []).includes(k), v => set(l, "types", v ? [...(l.types || []), k] : (l.types || []).filter(x => x !== k), true)))), (l.types || []).length ? "" : "Rien de coché = sur toutes les fiches."),
      el("div", { class: "ed-foot" }, el("span", { class: "hint" }, "Le bouton n'apparaît que si la fiche a l'information demandée."), btn("Supprimer", () => change(c => { c.links = c.links.filter(x => x.id !== l.id); }), "small danger"))))
      : el("div", { class: "empty" }, "Aucun lien automatique pour l'instant."),
    el("div", { class: "btns", style: "margin-bottom:12px" }, btn("+ Ajouter un lien", () => change(c => { (c.links ||= []).push({ id: uid(), label: "Mon lien", url: "https://" }); }), "primary big")),
    card("Modèles tout prêts", el("div", { class: "btns" }, LINK_PRESETS.map(([n, u]) => btn("+ " + n, () => change(c => { (c.links ||= []).push({ id: uid(), label: n, url: u }); }), "small"))),
      hint("{numéro}, {nom}… sont remplacés par ceux de la fiche ouverte. Vos champs personnalisés peuvent servir aussi.")),
    card("Relier une fiche à une autre", para("Pour relier une fiche à d'autres fiches ou à une liste, créez un champ personnalisé de type « Lien vers d'autres fiches » ou « Lien vers une liste »."), btn("🧩 Champs personnalisés", () => show("champs"), "small")),
  ];
};

/* ---------- Cartes des listes */
VIEW.cartes = () => {
  const cd = cfg.cards || {};
  const set = (k, v, redraw) => change(c => { c.cards ||= {}; if (v === "" || v == null) delete c.cards[k]; else c.cards[k] = v; }, { key: "card" + k, redraw: !!redraw });
  const shown = (cfg.fields || []).filter(f => f.card);
  return [head("Cartes des listes", "Les vignettes qui représentent chaque set ou figurine dans une liste."),
    card("Taille",
      fld("Largeur des cartes", line(el("input", { type: "range", min: 130, max: 420, step: 10, value: cd.min || 220, oninput: e => { set("min", +e.target.value === 220 ? "" : +e.target.value); e.target.nextSibling.textContent = e.target.value + " px"; } }), el("span", { class: "hint" }, (cd.min || 220) + " px")), "Plus petit = plus de cartes par ligne."),
      el("div", { class: "cols" },
        fld("Format de l'image", sel(cd.ratio || "", [["", "4/3 (origine)"], ["1/1", "Carré"], ["3/4", "Portrait"], ["16/9", "Large"]], v => set("ratio", v, true))),
        fld("Nom du set", sel(cd.lines || "", [["", "en entier"], ["1", "1 ligne maximum"], ["2", "2 lignes maximum"], ["3", "3 lignes maximum"]], v => set("lines", v ? +v : "", true))))),
    card("Ce qui est affiché sur une carte", el("div", { class: "rowset" }, CARDP.map(([k, l]) => line(chk(l, !(cd.hide || []).includes(k), v => change(c => { c.cards ||= {}; c.cards.hide = v ? (c.cards.hide || []).filter(x => x !== k) : [...(c.cards.hide || []), k]; }))))),
      hint("Décochez pour retirer une information de toutes les cartes.")),
    card("Vos champs sur les cartes", shown.length ? para("Affichés : " + shown.map(f => "<b>" + f.label.replace(/</g, "&lt;") + "</b>").join(", ") + ".") : para("Aucun de vos champs n'est affiché sur les cartes."),
      hint("Dans « Champs personnalisés », cochez « Afficher aussi sur les cartes des listes »."), btn("🧩 Champs personnalisés", () => show("champs"), "small")),
    cfg.cards ? card("", btn("↺ Remettre les cartes d'origine", () => change(c => { delete c.cards; }), "danger")) : null,
  ];
};

/* ---------- Menu */
VIEW.menu = () => {
  const b = BOF();
  let info = null, lists = [], items = [];
  try { info = b?.menuInfo() || null; lists = b?.lists() || []; items = b?.items() || []; } catch {}
  const mn = cfg.menu || {}, its = mn.items || [];
  const dom = (info || []).map(x => x.key), ord = (mn.order || []).filter(k => !k.startsWith("bo-") || its.some(i => "bo-" + i.id === k));
  if (!ord.length) ord.push(...dom);
  dom.forEach((k, i) => { if (ord.includes(k)) return; const prev = dom.slice(0, i).reverse().find(p => ord.includes(p)); ord.splice(prev ? ord.indexOf(prev) + 1 : 0, 0, k); });
  for (const i of its) if (!ord.includes("bo-" + i.id)) ord.push("bo-" + i.id);
  const rows = ord.map(k => { const i = (info || []).find(x => x.key === k), hid = (mn.hidden || []).includes(k), cu = k.startsWith("bo-"), sep = i?.sep || k === "pubSep";
    const sepAdded = cu && its.find(x => "bo-" + x.id === k)?.kind === "sep";
    return { key: k, name: sepAdded ? "──── trait de séparation (ajouté)" : cu ? "⭐ " + (its.find(x => "bo-" + x.id === k)?.label || "Raccourci") : sep ? "──── trait de séparation" : MENU[k] || i?.text || k, off: hid, absent: !hid && !!i?.empty,
      sub: hid ? "masqué par vous" : i?.empty ? "vide pour l'instant" : cu || sep ? "" : (i?.text || "").slice(0, 46),
      tools: [el("button", { type: "button", class: "eye", onclick: () => change(c => { c.menu ||= {}; c.menu.hidden = hid ? (c.menu.hidden || []).filter(x => x !== k) : [...(c.menu.hidden || []), k]; }) }, hid ? "🚫 Masqué" : "👁 Affiché"),
        btn("Voir", () => flash(`.sidebar > [data-bo-key="${k}"]`, "app", hid), "small")] }; });
  const set = (it, k, v, redraw) => change(c => { const x = (c.menu?.items || []).find(x => x.id === it.id); if (x) { if (v === "" || v == null || v === false) delete x[k]; else x[k] = v; } }, { key: "m" + it.id + k, redraw: !!redraw });
  const nameOf = id => items.find(x => x.id === id)?.name || (id ? "(fiche introuvable)" : "aucune fiche choisie");
  return [head("Menu", "Le menu latéral du site : son ordre, ce qui est masqué, et vos propres raccourcis."),
    !info ? note("L'aperçu doit afficher le site (connecté) pour lister le menu.", "warn") : null,
    orderList(rows, (f, t) => change(c => { c.menu ||= {}; c.menu.order = moved(ord, f, t); })),
    hint("L'ordre des listes elles-mêmes se règle dans le site, avec le bouton ⇅ du menu. Sur un petit écran d'aperçu, ouvrez le menu (☰) pour le voir."),
    (() => { let ents = []; try { ents = b?.navEntries() || []; } catch {}   /* chaque entrée : renommée, masquée — une à une */
      const L = mn.labels || {}, OFF = new Set(mn.off || []);
      return card("Chaque entrée du menu", hint("Renommez (émoji compris) ou masquez chaque entrée, une à une. Vide : son texte d'origine. Les listes se renomment dans le site (✏️)."),
        ents.length ? ents.map(e => line(el("span", { class: "lab" }, e.text),
          txt(L[e.key] || "", v => change(c => { c.menu ||= {}; c.menu.labels ||= {}; if (v.trim()) c.menu.labels[e.key] = v; else delete c.menu.labels[e.key]; }, { key: "ml" + e.key }), e.text),
          el("button", { type: "button", class: "eye", onclick: () => change(c => { c.menu ||= {}; const o = new Set(c.menu.off || []); o.has(e.key) ? o.delete(e.key) : o.add(e.key); c.menu.off = [...o]; }) }, OFF.has(e.key) ? "🚫 Masquée" : "👁 Affichée")))
          : note("L'aperçu doit afficher le site (connecté) pour lister les entrées.", "warn")); })(),
    card("Mes raccourcis", hint("Une entrée de menu en plus, vers une liste, une fiche ou un autre site."),
      its.filter(it => it.kind !== "sep").map(it => el("div", { class: "ed" },
        el("div", { class: "cols" }, fld("Texte dans le menu", txt(it.label, v => set(it, "label", v), "ex. : ⭐ Mes préférés")),
          fld("Ouvre", sel(it.kind || "url", [["url", "une adresse internet"], ["liste", "une de mes listes"], ["fiche", "une de mes fiches"]], v => set(it, "kind", v, true)))),
        it.kind === "liste" ? fld("Quelle liste ?", sel(it.target || "", [["", "— choisir —"], ...lists.map(l => [l.id, l.name])], v => set(it, "target", v, true)))
          : it.kind === "fiche" ? fld("Quelle fiche ?", line(el("span", { class: "lab" }, nameOf(it.target)), btn("Choisir…", () => choose("Choisir une fiche", items.map(x => ({ v: x.id, label: x.name }))).then(v => { if (v) set(it, "target", v, true); }), "small")))
          : [fld("Adresse", txt(it.url, v => set(it, "url", v), "https://…")), chk("Ouvrir dans le même onglet", it.same, v => set(it, "same", v, true))],
        el("div", { class: "ed-foot" }, el("span", { class: "hint" }, ""), btn("Supprimer", () => change(c => { c.menu.items = c.menu.items.filter(x => x.id !== it.id); if (c.menu.order) c.menu.order = c.menu.order.filter(k => k !== "bo-" + it.id); }), "small danger")))),
      btn("+ Ajouter un raccourci", () => change(c => { c.menu ||= {}; (c.menu.items ||= []).push({ id: uid(), label: "⭐ Mon raccourci", kind: "url", url: "https://" }); }), "primary")),
    card("Traits de séparation", hint("Un trait de plus dans le menu, comme ceux d'origine : ajoutez-le, puis glissez-le à sa place dans la liste ci-dessus."),
      its.filter(it => it.kind === "sep").map((it, n) => line(el("span", { class: "lab" }, `──── trait ajouté n° ${n + 1}`), btn("Supprimer", () => change(c => { c.menu.items = c.menu.items.filter(x => x.id !== it.id); if (c.menu.order) c.menu.order = c.menu.order.filter(k => k !== "bo-" + it.id); }), "small danger"))),
      btn("+ Ajouter un trait de séparation", () => change(c => { c.menu ||= {}; (c.menu.items ||= []).push({ id: uid(), kind: "sep" }); }), "primary")),
    mn.order || mn.hidden || mn.labels || mn.off ? card("", btn("↺ Remettre le menu d'origine (ordre, noms et entrées masquées)", () => change(c => { delete c.menu.order; delete c.menu.hidden; delete c.menu.labels; delete c.menu.off; }), "danger")) : null,
  ];
};

/* ---------- Données (fiche brute) */
async function loadItem(id) {
  try { const r = await api("/api/bo/item?id=" + encodeURIComponent(id));
    dataItem = { id, rows: Object.entries(r.item).map(([k, v]) => ({ k, t: v === null ? "z" : typeof v === "boolean" ? "b" : typeof v === "number" ? "n" : typeof v === "string" ? "s" : "j", v: v !== null && typeof v === "object" ? JSON.stringify(v, null, 1) : v })) };
    draw();
  } catch (e) { toast(e.message); }
}
async function saveItem() {
  const item = {}; let bad = false;
  for (const r of dataItem.rows) {
    if (r.del) continue;
    let v = r.v;
    if (r.t === "n") { v = r.v === "" || r.v == null ? null : +r.v; if (Number.isNaN(v)) { bad = true; r.bad = true; continue; } }
    else if (r.t === "b") v = !!r.v;
    else if (r.t === "z") v = r.v === "" || r.v == null ? null : r.v;
    else if (r.t === "j") { try { v = JSON.parse(r.v); r.bad = false; } catch { bad = true; r.bad = true; continue; } }
    item[r.k] = v;
  }
  if (bad) { draw(); return toast("Une valeur est illisible (encadrée en rouge) : rien n'a été enregistré."); }
  if (!await sure("Enregistrer cette fiche ?", "Les informations de la fiche seront remplacées par celles affichées ici. Une sauvegarde de toute la collection est faite juste avant, automatiquement.", "Enregistrer")) return;
  try { await api("/api/bo/item", { id: dataItem.id, item }); toast("✔ Fiche enregistrée."); try { FW().location.reload(); } catch {} loadItem(dataItem.id); }
  catch (e) { toast("Enregistrement refusé : " + e.message); }
}
VIEW.donnees = () => {
  const top = head("Données", "Pour corriger à la main une information que le site ne permet pas de modifier. Ici, vous voyez une fiche telle qu'elle est enregistrée, ligne par ligne.");
  if (!dataItem) {
    let items = [];
    try { items = BOF()?.items() || []; } catch {}
    const list = el("div", { class: "pickl", style: "max-height:52vh" });
    const fill = () => { const q = dataQ.toLowerCase(); list.replaceChildren(...items.filter(i => !q || i.name.toLowerCase().includes(q)).slice(0, 5000).map(i => el("button", { type: "button", onclick: () => loadItem(i.id) }, i.name, el("small", {}, sheetName(i.type)))),
      items.length ? "" : el("p", { class: "hint" }, "L'aperçu doit afficher le site (connecté) pour lister vos fiches.")); };
    fill();
    return [top, note("Ces changements touchent directement la collection, <b>sans passer par « Publier »</b>. Une sauvegarde automatique est faite avant chaque enregistrement.", "warn"),
      card("Choisir une fiche", el("input", { type: "search", value: dataQ, placeholder: "Nom ou numéro…", oninput: e => { dataQ = e.target.value.trim(); fill(); } }), el("div", { style: "height:8px" }), list)];
  }
  const tname = { s: "texte", n: "nombre", b: "oui / non", z: "vide", j: "structure" };
  return [top,
    line(btn("← Choisir une autre fiche", () => { dataItem = null; draw(); }, "small"), el("span", { class: "grow" }), btn("✔ Enregistrer la fiche", saveItem, "primary")),
    el("div", { style: "height:10px" }),
    card("Informations enregistrées", el("div", { class: "kv" }, dataItem.rows.filter(r => !r.del).map(r => [
      el("span", { class: "k", title: r.k + " (" + tname[r.t] + ")" }, r.k),
      r.k === "id" ? el("input", { type: "text", value: r.v, disabled: true })
        : r.t === "b" ? chk("oui", r.v, v => { r.v = v; })
        : r.t === "n" ? el("input", { type: "number", step: "any", value: r.v, class: r.bad ? "bad" : "", oninput: e => { r.v = e.target.value; } })
        : r.t === "j" ? el("textarea", { rows: Math.min(8, String(r.v).split("\n").length), value: r.v, class: r.bad ? "bad" : "", spellcheck: false, oninput: e => { r.v = e.target.value; } })
        : String(r.v ?? "").length > 60 ? el("textarea", { rows: 3, value: r.v ?? "", oninput: e => { r.v = e.target.value; } })
        : el("input", { type: "text", value: r.v ?? "", placeholder: r.t === "z" ? "(vide)" : "", oninput: e => { r.v = e.target.value; } }),
      ["id", "list_id", "kind"].includes(r.k) ? el("span", {}) : el("button", { type: "button", class: "x", title: "Retirer cette information de la fiche", onclick: () => { r.del = true; draw(); } }, "✕"),
    ])),
      hint("Les cases « structure » (entre accolades ou crochets) regroupent plusieurs informations : gardez bien leur forme, guillemets et virgules compris.")),
    card("Ajouter une information", line(btn("+ Ajouter une ligne", async () => { const k = await ask("Nouvelle information", "", "Nom de l'information (sans espace)", { ph: "ex. : emplacement" });
      if (!k) return; const key = slug(k); if (!key || dataItem.rows.some(r => r.k === key && !r.del)) return toast("Nom déjà utilisé ou vide."); dataItem.rows.push({ k: key, t: "s", v: "" }); draw(); }, "small")),
      hint("Pour une information à remplir sur toutes les fiches, préférez un « champ personnalisé ».")),
  ];
};

/* ---------- Mes modifications */
VIEW.modifs = () => {
  const rows = [], th = cfg.theme || {};
  const nTh = Object.keys(th).filter(k => !["both", "light", "dark"].includes(k)).length + ["both", "light", "dark"].reduce((n, g) => n + Object.keys(th[g] || {}).length, 0);
  const listRow = (ic, name, sub, list, o, extra = {}) => rows.push({ ic, name, sub, obj: o, list, ...extra });
  if (nTh) rows.push({ ic: "🎨", name: "Apparence", sub: nTh + " réglage(s) : couleurs, nom, logo, formes", open: "apparence", del: c => { delete c.theme; } });
  for (const r of cfg.rules || []) listRow("🖱️", r.label || "Élément", [r.hide && "masqué", r.order != null && "déplacé", Object.keys(r.css || {}).length && "style modifié"].filter(Boolean).join(", ") + " — sur " + (PAGES[r.page || ""] || r.page), "rules", r, { sel: r.sel, page: r.page, hidden: r.hide });
  for (const t of cfg.texts || []) listRow("🔤", `« ${t.from.slice(0, 30)} » → « ${String(t.to).slice(0, 30)} »`, t.sel ? "sur un élément précis — " + (PAGES[t.page || ""] || "") : t.mode === "mot" ? "partout sur le site" : "quand c'est le texte entier", "texts", t, { sel: t.sel, page: t.page, open: t.sel ? null : "textes" });
  for (const a of cfg.adds || []) listRow("➕", "Ajout : " + ADDK[a.kind] + (a.text ? " « " + a.text.slice(0, 30) + " »" : ""), "près de : " + (a.label || "un élément") + " — sur " + (PAGES[a.page || ""] || ""), "adds", a, { sel: `[data-bo-add="${a.id}"]`, page: a.page });
  for (const [t, s] of Object.entries(cfg.sheets || {})) rows.push({ ic: "🧱", name: "Fiche « " + sheetName(t) + " »", sub: [s.order && "ordre des blocs changé", (s.hidden || []).length && s.hidden.length + " bloc(s) masqué(s)", Object.keys(s.labels || {}).length && Object.keys(s.labels).length + " bloc(s) renommé(s)"].filter(Boolean).join(", ") || "squelette propre à ce type",
    open: "fiches", before: () => { shType = t; }, del: c => { delete c.sheets[t]; } });
  for (const f of cfg.fields || []) listRow("🧩", "Champ « " + f.label + " »", FTYPES.find(x => x[0] === (f.type || "text"))?.[1], "fields", f, { open: "champs" });
  for (const l of cfg.links || []) listRow("🔗", "Lien « " + l.label + " »", l.url, "links", l, { open: "liens" });
  const mn = cfg.menu || {};
  if (mn.order || mn.hidden) rows.push({ ic: "☰", name: "Menu", sub: [mn.order && "ordre changé", (mn.hidden || []).length && mn.hidden.length + " entrée(s) masquée(s)"].filter(Boolean).join(", "), open: "menu", del: c => { delete c.menu.order; delete c.menu.hidden; } });
  for (const i of mn.items || []) rows.push({ ic: "⭐", name: "Raccourci « " + i.label + " »", sub: "dans le menu", open: "menu", del: c => { c.menu.items = c.menu.items.filter(x => x.id !== i.id); } });
  if (cfg.cards) rows.push({ ic: "🃏", name: "Cartes des listes", sub: "taille ou contenu modifiés", open: "cartes", del: c => { delete c.cards; } });
  if (cfg.css) rows.push({ ic: "⚙️", name: "Feuille de style libre", sub: "rubrique « Historique et secours », tout en bas", open: "historique", del: c => { delete c.css; } });
  return [head("Mes modifications", "Tout ce que vous avez changé, rassemblé ici. Chaque ligne peut être retrouvée, mise en pause ou supprimée."),
    rows.length ? el("div", { class: "ord" }, rows.map(r => el("div", { class: "it" + (r.obj?.off ? " off" : "") },
      el("span", {}, r.ic), el("span", { class: "nm" }, el("b", { title: r.name }, r.name), el("span", { title: r.sub }, (r.obj?.off ? "en pause — " : "") + (r.sub || ""))),
      r.sel ? btn("Voir", () => flash(r.sel, r.page, r.hidden), "small", "Montrer dans l'aperçu") : null,
      r.open ? btn("Ouvrir", () => { r.before?.(); show(r.open); }, "small", "Aller à la rubrique qui le règle") : null,
      r.list ? btn(r.obj.off ? "▶" : "⏸", () => change(c => { const x = (c[r.list] || []).find(x => x.id === r.obj.id); if (x) { if (x.off) delete x.off; else x.off = true; } }), "small", r.obj.off ? "Réactiver" : "Mettre en pause (sans supprimer)") : null,
      el("button", { type: "button", class: "x", title: "Supprimer cette modification", onclick: () => change(c => { if (r.del) r.del(c); else c[r.list] = (c[r.list] || []).filter(x => x.id !== r.obj.id); }) }, "✕"))))
      : el("div", { class: "empty" }, "Aucune modification : le site est comme à l'origine."),
    rows.length ? hint("Une suppression se rattrape avec « ↶ Annuler », en haut.") : null,
  ];
};

/* ---------- Historique et secours */
VIEW.historique = () => [
  head("Historique et secours", "Chaque publication est gardée. Vous pouvez reprendre n'importe laquelle : elle devient votre brouillon, à publier quand vous voulez."),
  card("Versions publiées", hist.length ? el("div", { class: "rowset" }, hist.map((h, i) => line(
    el("span", { class: "lab" }, el("b", {}, fmtId(h.id)), i === 0 ? " — en ligne" : "", el("div", { class: "hint" }, [h.note, h.count ? h.count + " modification(s)" : "aucune modification"].filter(Boolean).join(" · "))),
    btn("Reprendre", async () => { try { const r = await api("/api/bo/version?id=" + h.id); replaceAll(r.cfg); toast("Version reprise comme brouillon : vérifiez l'aperçu, puis publiez."); } catch (e) { toast(e.message); } }, "small"))))
    : el("p", { class: "hint" }, "Aucune publication pour l'instant.")),
  card("Revenir au site d'origine", para("Vide le brouillon de tous vos réglages : le site redevient comme avant le back office (après publication). Vos anciennes versions restent dans l'historique."),
    btn("↺ Tout remettre d'origine", async () => { if (await sure("Tout remettre d'origine ?", "Le brouillon sera vidé de tous vos réglages. Le site ne changera que lorsque vous publierez.", "Tout remettre d'origine")) replaceAll({}); }, "danger")),
  card("Garder une copie de mes réglages", para("Un fichier qui contient tous vos réglages (pas vos fiches). Utile avant un gros changement, ou pour les transférer."),
    el("div", { class: "btns" }, btn("⬇ Exporter dans un fichier", () => { const a = el("a", { href: URL.createObjectURL(new Blob([JSON.stringify(cfg, null, 1)], { type: "application/json" })), download: "briquotheque-backoffice-" + new Date().toISOString().slice(0, 10) + ".json" }); a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 5000); }),
      btn("⬆ Importer un fichier…", () => { const inp = el("input", { type: "file", accept: ".json,application/json", onchange: async () => { try { const o = JSON.parse(await inp.files[0].text()); if (!o || typeof o !== "object" || Array.isArray(o)) throw 0;
          const r = await api("/api/bo/normalize", { cfg: o });   // le serveur remet le fichier d'aplomb (types, adresses, tailles) avant qu'il n'entre dans le brouillon
          replaceAll(r.cfg || {}); toast("Réglages importés dans le brouillon : vérifiez l'aperçu, puis publiez."); } catch { toast("Ce fichier n'est pas un export du back office."); } } }); inp.click(); }))),
  card("En cas de problème", para("Si un réglage rend le site inutilisable : cette page <code>/backoffice</code> reste toujours accessible pour le défaire. Et en ajoutant <code>?bo=off</code> à la fin de l'adresse du site, il s'affiche sans aucune personnalisation.")),
  el("details", { class: "card" }, el("summary", { style: "cursor:pointer;font-weight:600" }, "Avancé (facultatif) : feuille de style libre"),
    hint("Réservé à qui connaît le CSS ; tout le reste du back office s'en passe. Ce texte est ajouté tel quel aux styles du site."),
    el("textarea", { rows: 8, value: cfg.css || "", spellcheck: false, style: "font-family:ui-monospace,Consolas,monospace;font-size:12px", placeholder: ".card { … }", oninput: e => change(c => { c.css = e.target.value; }, { key: "css", redraw: false }) })),
];

/* ------------------------------------------------------------------ menu des rubriques (admin-plus.js le remplace par un menu en groupes) */
function buildNav() {
  $("#nav").append(...PANELS.flatMap(([id, ic, nm]) => [id === "donnees" || id === "souris" ? el("div", { class: "sep" }) : null,
    el("button", { type: "button", "data-p": id, onclick: () => show(id) }, el("span", { class: "ic" }, ic), el("span", {}, nm), id === "modifs" ? el("span", { class: "ct", hidden: true }) : null)]).filter(Boolean));
}

/* ------------------------------------------------------------------ démarrage */
function startAdmin() {   // appelée en fin de admin-max.js (sinon de admin-plus.js, sinon ci-dessous) — une seule fois
if (window.BO_STARTED) return;
window.BO_STARTED = true;
buildNav();
$("#btnUndo").onclick = () => step(undo, redo);
$("#btnRedo").onclick = () => step(redo, undo);
$("#btnDiscard").onclick = discard;
$("#btnPublish").onclick = publish;
$("#pvPage").onchange = e => go(e.target.value);
$("#pvMode").onclick = e => { const m = e.target.closest("[data-mode]")?.dataset.mode; if (!m) return; if ((m === "pick" || m === "move") && panel !== "souris") { show("souris"); if (m === "move") setMode("move"); } else setMode(m); };
$("#pvSize").onclick = e => { const b = e.target.closest("[data-w]"); if (!b) return; frame.style.maxWidth = b.dataset.w ? b.dataset.w + "px" : ""; $(".prev-wrap").classList.toggle("narrow", !!b.dataset.w);
  for (const x of $("#pvSize").children) x.classList.toggle("on", x === b); };
$("#pvGhost").onchange = e => { ghost = e.target.checked; try { BOF()?.ghost(ghost); } catch {} if (panel === "fiches") draw(); };
$("#pvReload").onclick = () => { try { FW().location.reload(); } catch { frame.src = frame.src; } };
$("#pvSize").firstElementChild.classList.add("on");
/* zoom de l'aperçu (CSS zoom dans la page de l'aperçu) : − / 100 % / +, retenu sur l'appareil, remis à chaque chargement de l'aperçu */
let pvZoom = (() => { try { return +localStorage.getItem("bo-pv-zoom") || 1; } catch { return 1; } })();
const ZOOMS = [0.5, 0.67, 0.75, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2];
const applyZoom = () => { try { FW().document.documentElement.style.zoom = pvZoom === 1 ? "" : String(pvZoom); } catch {} $("#pvZoomN").textContent = Math.round(pvZoom * 100) + " %"; };
$("#pvZoom").onclick = e => { const b = e.target.closest("[data-z]"); if (!b) return; const d = +b.dataset.z;
  if (!d) pvZoom = 1; else { const k = ZOOMS.indexOf(ZOOMS.reduce((a, z) => Math.abs(z - pvZoom) < Math.abs(a - pvZoom) ? z : a, 1)); pvZoom = ZOOMS[Math.max(0, Math.min(ZOOMS.length - 1, k + d))]; }
  try { localStorage.setItem("bo-pv-zoom", pvZoom); } catch {} applyZoom(); };
frame.addEventListener("load", applyZoom); applyZoom();
addEventListener("keydown", e => {
  if (!(e.ctrlKey || e.metaKey) || /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || "")) return;
  const k = e.key.toLowerCase();
  if (k === "z" && !e.shiftKey) { e.preventDefault(); step(undo, redo); } else if (k === "y" || (k === "z" && e.shiftKey)) { e.preventDefault(); step(redo, undo); }
});
addEventListener("hashchange", () => { const h = location.hash.slice(1); if (h && h !== panel) show(h); });
addEventListener("pagehide", () => { if (saveT) { clearTimeout(saveT); try { fetch(dirty() ? "/api/bo/draft" : "/api/bo/discard", { method: "POST", keepalive: true, headers: { "Content-Type": "application/json" }, body: JSON.stringify(dirty() ? { cfg } : {}) }); } catch {} } });
(async () => {
  try { const s = await api("/api/bo/state"); published = s.published || {}; cfg = clone(s.draft || {}) || {}; hist = s.history || []; copie = !!s.copie; }
  catch (e) { $("#panel").append(el("div", { class: "note warn" }, "Le back office n'a pas pu se charger : " + e.message)); return; }
  $("#copyTag").hidden = !copie;
  setMode("use"); status();
  frame.src = "/";
  show(location.hash.slice(1) || "accueil");
})();
}
window.addEventListener("load", () => { if (!window.BO_STARTED) startAdmin(); });   // admin-plus.js absent ou en panne : le back office de base démarre quand même

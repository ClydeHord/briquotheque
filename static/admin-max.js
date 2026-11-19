/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
/* Briquothèque — BACK OFFICE : rubriques « tout modifier » (chargé après admin.js et admin-plus.js).
   Ajoute à l'écran du back office :
     - 🏷️ Étiquettes et pastilles (cfg.tags) · 🔘 Boutons et tailles (cfg.btn, cfg.sizes) · 📄 Pages (cfg.pages)
     - ⚙️ Page « Réglages » de l'appli (cfg.settings) · 🎮 Comportements (cfg.behav) — brouillon puis « Publier », appliqués par /bo-max.js ;
     - 🖼️ Images (envoyées au serveur : /api/bo/x/image…) · 🔐 Mots de passe et sécurité (/api/bo/password…) — effet immédiat ;
     - dans « Modifier à la souris » : icône ou image d'un élément, lien et action au clic, décalage / échelle / rotation.
   S'appuie sur admin.js (el, btn, card, change, VIEW…) et sur ce que admin-plus.js expose dans window.BOX (xapi, condBox, fxBox…). */
(() => {
"use strict";
const X0 = window.BOX;
if (!X0) { window.addEventListener("load", () => { if (!window.BO_STARTED) startAdmin(); }); return; }
const { GROUPS, WIDE, xapi, act, got, reload, wait, X, condBox, fxBox, P, needPreview, esc, sz, dt, xbtn, colorIn, foot, typesRow, upd, del } = X0;
const M = () => { try { return BOF()?.max || null; } catch { return null; } };   // moteur bo-max.js, dans l'aperçu
const empty = v => v == null || v === "" || (Array.isArray(v) && !v.length) || (typeof v === "object" && !Array.isArray(v) && !Object.keys(v).length);
function tidy(o) { if (o && typeof o === "object" && !Array.isArray(o)) for (const k of Object.keys(o)) { tidy(o[k]); if (empty(o[k])) delete o[k]; } else if (Array.isArray(o)) o.forEach(tidy); return o; }
const setIn = (path, v, o) => change(c => { let t = c; for (const k of path.slice(0, -1)) t = (t[k] ||= {}); const k = path[path.length - 1]; if (v === "" || v == null) delete t[k]; else t[k] = v; }, o);
const getIn = (path, c = cfg) => path.reduce((t, k) => (t && typeof t === "object" ? t[k] : undefined), c);
const numIn = (path, ph, o = {}) => [el("input", { type: "number", class: "num", min: o.min ?? 0, max: o.max ?? 4000, step: o.step || 1, value: getIn(path) ?? "", placeholder: ph,
  oninput: e => setIn(path, e.target.value === "" ? "" : +e.target.value, { key: path.join("."), redraw: false }) }), el("span", { class: "u" }, o.unit ?? "px")];
const flag = (label, path, title) => chk(label, getIn(path) === true, v => setIn(path, v ? true : ""), title);
const colIn = (path, label) => { const v = getIn(path);
  return el("span", { class: "colset" }, el("input", { type: "color", value: /^#[0-9a-f]{6}$/i.test(v || "") ? v : "#888888", title: label, oninput: e => setIn(path, e.target.value, { key: path.join("."), redraw: false }) }),
    el("span", { class: "hint" }, label), v ? el("button", { type: "button", class: "x", title: "Couleur d'origine", onclick: () => setIn(path, "") }, "↺") : null); };
const row3 = (label, ...ctl) => [el("span", { class: "lab" }, label), el("span", { class: "ctl" }, ctl), el("span", {})];
const emoji = (value, on, ph = "🙂") => el("input", { type: "text", class: "emo", value: value ?? "", placeholder: ph, maxLength: 8, title: "Un émoji ou un texte très court (facultatif)", oninput: e => on(e.target.value) });

/* ------------------------------------------------------------------ rubriques ajoutées */
const MORE = [
  ["boutons", "🔘", "Boutons et tailles", "L'allure de tous les boutons ; les grandes dimensions du site."],
  ["etiquettes", "🏷️", "Étiquettes et pastilles", "Renommer, recolorer, masquer les étiquettes (Modifié, MOC, Neuf…) ; créer les vôtres."],
  ["pages", "📄", "Pages", "Créer vos propres pages : textes, images, boutons, listes de fiches, totaux, tableaux."],
  ["reglages", "⚙️", "Page « Réglages » de l'appli", "L'ordre, les titres et la visibilité des sections de la page Réglages."],
  ["comportements", "🎮", "Comportements", "Page de départ, tri et vue par défaut, raccourcis clavier, action au clic."],
  ["images", "🖼️", "Images", "Vos images (boutons, pages, logo) : envoyer, réutiliser, supprimer."],
  ["securite", "🔐", "Mots de passe et sécurité", "Changer le mot de passe du back office ou celui de la Briquothèque ; sessions."],
];
for (const p of MORE) PANELS.push(p);
const grp = t => GROUPS.find(g => g[0] === t)?.[1];
grp("Personnaliser")?.splice(1, 0, "boutons");
grp("Personnaliser")?.splice(3, 0, "etiquettes");
grp("Personnaliser")?.push("pages", "reglages", "comportements", "images");
grp("Serveur")?.splice(2, 0, "securite");
WIDE.push("images", "securite");

/* ------------------------------------------------------------------ ménage et décompte des réglages ajoutés */
const hasMax = r => !!(r.ico?.t || r.img?.url || !empty(r.tx) || r.href || r.blank || r.click?.k);
const baseRule = r => r.hide || (r.order != null && r.order !== "") || Object.keys(r.css || {}).length > 0;
const prune2 = prune, count2 = countAll;
prune = function (c) {
  for (const r of c.rules || []) {   // compléments d'une règle : ce qui est vide disparaît
    if (r.ico && !String(r.ico.t || "").trim()) delete r.ico;
    if (r.img && !String(r.img.url || "").trim()) delete r.img;
    if (r.tx) { for (const k of Object.keys(r.tx)) if (!+r.tx[k] || (k === "s" && +r.tx[k] === 100)) delete r.tx[k]; if (empty(r.tx)) delete r.tx; }
    if (r.click && !r.click.k) delete r.click;
    if (!r.href) delete r.href;
    if (!r.blank) delete r.blank;
  }
  const keep = (c.rules || []).filter(r => hasMax(r) && !baseRule(r));   // (admin.js ne garde que les règles de style : celles-ci sont remises après)
  prune2(c);
  if (keep.length) c.rules = [...(c.rules || []), ...keep];
  if (c.tags) { for (const k of Object.keys(c.tags.over || {})) { tidy(c.tags.over[k]); if (c.tags.over[k].hide === false) delete c.tags.over[k].hide; if (empty(c.tags.over[k])) delete c.tags.over[k]; } }
  for (const k of ["tags", "btn", "sizes", "settings", "behav"]) if (c[k]) { tidy(c[k]); if (empty(c[k])) delete c[k]; }
  if (c.btn) for (const k of Object.keys(c.btn)) if (c.btn[k] === false) delete c.btn[k];
  if (c.behav) for (const k of ["noAnim", "noMerge", "noOffer", "noTrend", "noVariations", "editFirst", "partZoom", "noPubNav"]) if (c.behav[k] === false) delete c.behav[k];
  if (c.js != null && !String(c.js).trim()) delete c.js;
  if (c.pages && !c.pages.length) delete c.pages;
};
countAll = function () {
  const t = cfg.tags || {};
  return count2() + Object.keys(t.over || {}).length + (t.add || []).length + (t.badges ? 1 : 0) + (cfg.btn ? 1 : 0) + (cfg.sizes ? 1 : 0) + (cfg.settings ? 1 : 0) + (cfg.behav ? 1 : 0) + (cfg.pages || []).length;
};
const modifs2 = VIEW.modifs;
VIEW.modifs = () => { const t = cfg.tags || {}, n = Object.keys(t.over || {}).length + (t.add || []).length + (t.badges ? 1 : 0);
  const rows = [[n, "🏷️", n + " étiquette(s) modifiée(s) ou créée(s)", "etiquettes", "tags"], [cfg.btn, "🔘", "Allure des boutons", "boutons", "btn"], [cfg.sizes, "🔘", "Tailles générales", "boutons", "sizes"],
    [(cfg.pages || []).length, "📄", (cfg.pages || []).length + " page(s) créée(s)", "pages", "pages"], [cfg.settings, "⚙️", "Page « Réglages » réorganisée", "reglages", "settings"], [cfg.behav, "🎮", "Comportements", "comportements", "behav"]].filter(r => r[0]);
  return [modifs2(), rows.length ? card("Étiquettes, boutons, pages, comportements", el("div", { class: "rowset" }, rows.map(([, ic, nm, to, key]) => line(el("span", { class: "lab" }, ic + " ", el("b", {}, nm)),
    btn("Ouvrir", () => show(to), "small"), xbtn("Tout remettre d'origine", async () => { if (await sure("Remettre d'origine ?", "« " + esc(nm) + " » : ces réglages seront retirés du brouillon.", "Retirer")) change(c => { delete c[key]; }); }))))) : null];
};

/* ------------------------------------------------------------------ images : envoi, bibliothèque, choix */
function shrink(file, max) {   // image trop lourde : réduite avant l'envoi
  return new Promise((ok, ko) => { const u = URL.createObjectURL(file), im = new Image();
    im.onload = () => { const k = Math.min(1, max / Math.max(im.width, im.height)), c = el("canvas", { width: Math.max(1, Math.round(im.width * k)), height: Math.max(1, Math.round(im.height * k)) });
      c.getContext("2d").drawImage(im, 0, 0, c.width, c.height); URL.revokeObjectURL(u); c.toBlob(b => b ? ok(b) : ko(new Error("Image illisible")), file.type === "image/png" ? "image/png" : "image/jpeg", .86); };
    im.onerror = () => { URL.revokeObjectURL(u); ko(new Error("Image illisible")); }; im.src = u; });
}
async function upload(file) {
  let body = file;
  if (file.size > 3.5e6 && /^image\/(png|jpeg|webp)$/.test(file.type)) body = await shrink(file, 1800);
  const r = await xapi("image?label=" + encodeURIComponent(file.name.replace(/\.[a-z0-9]+$/i, "").slice(0, 60)), body, true);
  X.imgs = { images: r.images };
  return r.url;
}
const pickFiles = (done, multiple) => { const i = el("input", { type: "file", accept: "image/*,.svg,.ico", multiple: !!multiple, onchange: () => { if (i.files.length) done([...i.files]); } }); i.click(); };
async function imgPick() {   // choisir une image : dans la bibliothèque, ou en envoyer une — rend son adresse (null : annulé)
  let list = [];
  try { list = (await xapi("images")).images; } catch (e) { toast(e.message); }
  return modal("Choisir une image", close => [
    el("div", { class: "btns", style: "margin-bottom:10px" }, btn("⬆ Envoyer une image depuis l'ordinateur…", () => pickFiles(async fs => { const u = await act(() => upload(fs[0]), "✔ Image envoyée."); if (u) close(u); }), "primary")),
    list.length ? el("div", { class: "imgs" }, list.map(i => el("button", { type: "button", class: "imgc", title: i.label || i.name, onclick: () => close(i.url) }, el("img", { src: i.url, alt: "", loading: "lazy" }), el("span", {}, i.label || sz(i.size)))))
      : el("p", { class: "hint" }, "Aucune image pour l'instant : envoyez-en une.")], { ok: false, cancel: "Fermer", wide: true });
}
const imgField = (value, on) => line(txt(/^data:/.test(value || "") ? "" : value, v => on(v, false), /^data:/.test(value || "") ? "(image intégrée aux réglages)" : "Adresse de l'image (https://… ou /bo-img/…)"),
  btn("🖼️ Choisir…", async () => { const u = await imgPick(); if (u) on(u, true); }, "small", "Choisir dans vos images, ou en envoyer une"));
let imgBusy = false;
VIEW.images = () => {
  const d = got("imgs", "images"), w = wait(d, "imgs"), used = JSON.stringify(cfg) + JSON.stringify(published);
  const send = fs => (async () => { imgBusy = true; draw(); let n = 0; for (const f of fs.slice(0, 500)) if (await act(() => upload(f))) n++; imgBusy = false; if (n) toast("✔ " + n + " image(s) envoyée(s)."); draw(); })();
  return [head("Images", "Vos images, gardées sur le serveur : elles servent aux boutons, aux pages, aux éléments ajoutés. Une image envoyée ici a une adresse (/bo-img/…) à coller où vous voulez — ou à choisir avec « 🖼️ Choisir… »."),
    card("Envoyer", el("div", { class: "btns" }, btn(imgBusy ? "Envoi en cours…" : "⬆ Envoyer des images…", () => pickFiles(send, true), "primary")),
      hint("PNG, JPEG, WebP, GIF, SVG (sans script), ICO, AVIF — 4 Mo au plus (une photo plus lourde est réduite toute seule). Effet immédiat : pas besoin de publier.")),
    w || card("Bibliothèque (" + d.images.length + ")", d.images.length ? el("div", { class: "imgs big" }, d.images.map(i => { const on = used.includes(i.url);
      return el("div", { class: "imgc" }, el("a", { href: i.url, target: "_blank", rel: "noopener" }, el("img", { src: i.url, alt: "", loading: "lazy" })),
        el("span", { title: i.name }, (i.label || i.name) + " · " + sz(i.size)), el("span", { class: "hint" }, on ? "✔ utilisée" : "pas utilisée"),
        el("div", { class: "btns" }, btn("Copier l'adresse", () => { navigator.clipboard?.writeText(i.url).then(() => toast("Adresse copiée : " + i.url), () => toast(i.url)); }, "small"),
          btn("Supprimer", async () => { if (!await sure("Supprimer cette image ?", on ? "Elle est <b>utilisée</b> dans vos réglages : là où elle sert, il n'y aura plus d'image." : "Elle n'est utilisée nulle part.", "Supprimer")) return;
            const r = await act(() => xapi("image-delete", { name: i.name }), "Image supprimée."); if (r) { X.imgs = { images: r.images }; draw(); } }, "small danger"))); }))
      : el("p", { class: "hint" }, "Aucune image pour l'instant."))];
};

/* ------------------------------------------------------------------ choix d'une action (bouton d'une page, clic sur un élément, raccourci clavier) */
const ACTS = [["url", "Ouvrir une adresse (site, page, e-mail…)"], ["list", "Ouvrir une liste"], ["all", "Ouvrir « Toute la collection »"], ["view", "Ouvrir une vue enregistrée"], ["page", "Ouvrir une page créée"],
  ["item", "Ouvrir une fiche"], ["new", "Ajouter une fiche (« + Nouveau »)"], ["search", "Aller à la recherche"], ["settings", "Ouvrir les Réglages"], ["top", "Remonter en haut de la page"], ["back", "Revenir en arrière"]];
const appLists = () => { try { return BOF()?.lists() || []; } catch { return []; } };
const appItems = () => { try { return BOF()?.items() || []; } catch { return []; } };
function actBox(a, set, extra = []) {   // a : l'action {k, v, same} ; set(fn, redessiner) la modifie
  a = a || {};
  const k = a.k || "", target = () => {
    if (k === "url") return [txt(a.v, v => set(x => { x.v = v; }, false), "https://… ou /collection ou mailto:…"), chk("dans le même onglet", a.same === true, v => set(x => { if (v) x.same = true; else delete x.same; }, true))];
    if (k === "list") { const ls = appLists(); return ls.length || a.v ? sel(a.v || "", [["", "— choisir une liste —"], ...ls.map(l => [l.id, l.name]), ...(a.v && !ls.some(l => l.id === a.v) ? [[a.v, "(liste introuvable)"]] : [])], v => set(x => { x.v = v; }, true)) : hint("L'aperçu doit afficher le site pour choisir une liste."); }
    if (k === "view") return (cfg.views || []).length ? sel(a.v || "", [["", "— choisir une vue —"], ...(cfg.views || []).map(v => [v.id, v.label || "vue"])], v => set(x => { x.v = v; }, true)) : hint("Aucune vue enregistrée (rubrique « Vues, tris et filtres »).");
    if (k === "page") return (cfg.pages || []).length ? sel(a.v || "", [["", "— choisir une page —"], ...(cfg.pages || []).map(p => [p.id, p.title || "page"])], v => set(x => { x.v = v; }, true)) : hint("Aucune page créée (rubrique « Pages »).");
    if (k === "item") { const its = appItems(), cur = its.find(i => i.id === a.v);
      return line(el("span", { class: "lab" }, cur ? cur.name : a.v ? "(fiche introuvable)" : "Aucune fiche choisie"), btn("Choisir une fiche…", async () => { const v = await choose("Choisir une fiche", its.map(i => ({ v: i.id, label: i.name })), { empty: "L'aperçu doit afficher le site." }); if (v) set(x => { x.v = v; }, true); }, "small")); }
    return null; };
  return el("div", { class: "actb" }, sel(k, [...extra, ...ACTS], v => set(x => { x.k = v; delete x.v; delete x.same; delete x.msg; }, true)), target());
}
const actText = a => { a = a || {}; const n = ACTS.find(x => x[0] === a.k)?.[1] || ""; if (!a.k) return "";
  const v = a.k === "list" ? appLists().find(l => l.id === a.v)?.name : a.k === "view" ? (cfg.views || []).find(x => x.id === a.v)?.label : a.k === "page" ? (cfg.pages || []).find(x => x.id === a.v)?.title : a.k === "item" ? appItems().find(i => i.id === a.v)?.name : a.v;
  return n.replace(/ \(.*/, "") + (v ? " : " + v : ""); };

/* ------------------------------------------------------------------ « Modifier à la souris » : icône ou image, lien et clic, décalage */
const ruleSet = (fn, o) => change(c => { fn(getRule(c, true)); }, o);
let kindSel = "", kindFor = "";   // « icône » ou « image » : le choix en cours pour l'élément sélectionné (l'image n'entre dans les réglages qu'une fois choisie)
function sourisCards() {
  const r = getRule(cfg) || {}, ic = r.ico || {}, im = r.img || {}, tx = r.tx || {}, kind = (kindFor === pSel() && kindSel) || (r.img ? "img" : r.ico ? "ico" : "");
  const isLink = pick.tag === "a";
  const txIn = (k, ph, min, max, unit) => [el("input", { type: "number", class: "num", min, max, value: tx[k] ?? "", placeholder: ph, oninput: e => ruleSet(x => { x.tx ||= {}; if (e.target.value === "") delete x.tx[k]; else x.tx[k] = +e.target.value; }, { key: "tx" + k + pSel(), redraw: false }) }), el("span", { class: "u" }, unit)];
  const imgSet = (fn, o) => ruleSet(x => { x.img = { mode: "before", w: 20, ...(x.img || {}) }; fn(x.img); }, o);
  const dim = (k, ph) => el("input", { type: "number", class: "num", min: 4, max: 2000, value: im[k] ?? "", placeholder: ph, oninput: e => imgSet(x => { if (e.target.value === "") delete x[k]; else x[k] = +e.target.value; }, { key: "img" + k + pSel(), redraw: false }) });
  return [
    card("Icône ou image",
      sel(kind, [["", "Aucune (comme à l'origine)"], ["ico", "Une icône (émoji ou petit texte)"], ["img", "Une image"]], v => { kindSel = v; kindFor = pSel();
        change(c => { const x = getRule(c, v === "ico"); if (!x) return; delete x.ico; delete x.img; if (v === "ico") x.ico = { t: "⭐", pos: "before" }; }); draw(); }),
      kind === "ico" ? el("div", { class: "st", style: "margin-top:8px" },
        row3("Icône", emoji(ic.t, v => ruleSet(x => { (x.ico ||= { pos: "before" }).t = v; }, { key: "icot" + pSel(), redraw: false }), "⭐")),
        row3("Place", sel(ic.pos || "before", [["before", "avant le texte"], ["after", "après le texte"], ["only", "à la place du texte"]], v => ruleSet(x => { (x.ico ||= {}).pos = v; }))),
        ic.pos === "only" ? row3("Taille", el("input", { type: "number", class: "num", min: 8, max: 200, value: ic.size ?? "", placeholder: 18, oninput: e => ruleSet(x => { if (!x.ico) return; if (e.target.value === "") delete x.ico.size; else x.ico.size = +e.target.value; }, { key: "icos" + pSel(), redraw: false }) }), el("span", { class: "u" }, "px")) : null) : null,
      kind === "img" ? [el("div", { style: "height:8px" }), imgField(im.url, (v, rd) => imgSet(x => { x.url = v; }, { key: "imgu" + pSel(), redraw: !!rd })),
        el("div", { class: "st", style: "margin-top:8px" },
          row3("Place", sel(im.mode || "before", [["before", "avant le texte"], ["after", "après le texte"], ["only", "à la place du texte"], ["bg", "en fond (remplit l'élément)"], ["bgc", "en fond (image entière)"]], v => imgSet(x => { x.mode = v; }))),
          ["bg", "bgc"].includes(im.mode) ? null : row3("Largeur", dim("w", 20), el("span", { class: "u" }, "px")),
          ["bg", "bgc"].includes(im.mode) ? null : row3("Hauteur", dim("h", "= largeur"), el("span", { class: "u" }, "px"))),
        hint(im.url ? "« À la place du texte » : seul le dessin se voit. Pour une image de fond, réglez aussi Largeur / Hauteur dans « Style »." : "Choisissez d'abord l'image : « 🖼️ Choisir… » (vos images, ou en envoyer une), ou collez son adresse.")] : null),
    card("Lien et action au clic",
      isLink ? [fld("Adresse du lien", line(txt(r.href ?? "", v => ruleSet(x => { x.href = v; }, { key: "href" + pSel(), redraw: false }), pick.href || "https://…"),
        el("button", { type: "button", class: "x", title: "Remettre l'adresse d'origine", onclick: () => ruleSet(x => { delete x.href; }) }, "↺")), pick.href ? "Adresse d'origine : " + esc(pick.href) : ""),
        chk("Ouvrir dans un nouvel onglet", r.blank === true, v => ruleSet(x => { if (v) x.blank = true; else delete x.blank; }))] : null,
      fld("Quand on clique dessus", actBox(r.click, (fn, rd) => ruleSet(x => { x.click ||= {}; fn(x.click); }, { key: "click" + pSel(), redraw: !!rd }),
        [["", "Comme à l'origine"], ["none", "Ne rien faire (clic désactivé)"], ["confirm", "Demander d'abord une confirmation"]]),
        "Remplace ce que fait l'élément. « Comme à l'origine » retire ce réglage."),
      r.click?.k === "confirm" ? fld("Question posée", txt(r.click.msg, v => ruleSet(x => { x.click.msg = v; }, { key: "cmsg" + pSel(), redraw: false }), "Continuer ?")) : null),
    card("Décalage, échelle, rotation", el("div", { class: "st" },
      row3("Vers la droite", txIn("x", 0, -3000, 3000, "px")), row3("Vers le bas", txIn("y", 0, -3000, 3000, "px")), row3("Échelle", txIn("s", 100, 10, 500, "%")), row3("Rotation", txIn("r", 0, -360, 360, "°"))),
      hint("Un nombre négatif décale vers la gauche ou vers le haut. Pour changer un élément de place parmi ses voisins, préférez « ✋ Déplacer ».")),
  ];
}
const souris0 = VIEW.souris;
VIEW.souris = () => { const out = [souris0()].flat(Infinity).filter(n => n != null && n !== false && n !== "");
  if (mode !== "pick" || !pick) return out;
  const i = out.findIndex(n => n.querySelector && (n.matches?.(".card") ? n : null)?.querySelector("h3")?.textContent.startsWith("Tout annuler"));   // juste avant « Tout annuler pour cet élément »
  out.splice(i < 0 ? out.length : i, 0, ...sourisCards());
  return out; };

/* ------------------------------------------------------------------ Boutons et tailles */
VIEW.boutons = () => [
  head("Boutons et tailles", "L'allure de tous les boutons du site d'un coup, et les grandes dimensions (menu, fiches, espace entre les cartes)."),
  card("Tous les boutons", el("div", { class: "st" },
    row3("Coins arrondis", numIn(["btn", "radius"], 10, { max: 60 })), row3("Hauteur (espace en haut et en bas)", numIn(["btn", "padY"], 9, { max: 40 })), row3("Largeur (espace à gauche et à droite)", numIn(["btn", "padX"], 14, { max: 80 })),
    row3("Taille du texte", numIn(["btn", "size"], 14, { min: 9, max: 32 })),
    row3("Graisse du texte", sel(getIn(["btn", "weight"]) || "", [["", "comme à l'origine"], ["400", "normale"], ["600", "demi-grasse"], ["800", "grasse"]], v => setIn(["btn", "weight"], v))),
    row3("Bordure", numIn(["btn", "border"], 1, { max: 8 }))),
    el("div", { class: "checks", style: "margin-top:8px" }, flag("TEXTE EN MAJUSCULES", ["btn", "upper"]), flag("Ombre sous les boutons", ["btn", "shadow"]))),
  card("Couleurs des boutons",
    fld("Boutons ordinaires", el("div", { class: "cols" }, colIn(["btn", "bg"], "fond"), colIn(["btn", "ink"], "texte"), colIn(["btn", "line"], "bordure"))),
    fld("Boutons principaux (« + Nouveau », « Enregistrer »)", el("div", { class: "cols" }, colIn(["btn", "primBg"], "fond"), colIn(["btn", "primInk"], "texte")), "Sans réglage ici, ils suivent la couleur principale (rubrique « Apparence »)."),
    fld("Boutons de suppression", el("div", { class: "cols" }, colIn(["btn", "dangBg"], "fond"), colIn(["btn", "dangInk"], "texte")))),
  card("Un bouton en particulier", para("Son texte, ses couleurs, <b>son icône ou son image</b>, son lien, ce qu'il fait au clic : cliquez-le dans l'aperçu."),
    btn("🖱️ Cliquer un bouton dans l'aperçu", () => show("souris"), "primary")),
  card("Tailles générales", el("div", { class: "st" },
    row3("Largeur du menu latéral", numIn(["sizes", "menu"], 320, { min: 160, max: 600 })), row3("Largeur de la fenêtre d'une fiche", numIn(["sizes", "sheet"], 680, { min: 420, max: 1800 })),
    row3("Largeur maximale du contenu", numIn(["sizes", "content"], "aucune", { min: 600, max: 4000 })), row3("Espace entre les cartes", numIn(["sizes", "gap"], 16, { max: 60 })),
    row3("Taille du titre de la liste", numIn(["sizes", "title"], 26, { min: 12, max: 80 }))),
    hint("Sur ordinateur (le téléphone garde sa mise en page). La taille du texte et des cartes : rubriques « Apparence » et « Cartes des listes ».")),
  cfg.btn || cfg.sizes ? card("Revenir en arrière", btn("↺ Boutons et tailles d'origine", () => change(c => { delete c.btn; delete c.sizes; }), "danger")) : null,
];

/* ------------------------------------------------------------------ Étiquettes et pastilles */
let tagOpen = "";
const TAG_PRESETS = [["💰", "Plus de 100 €", { rows: [{ v: "valeur", op: ">", val: "100" }] }, "#15803d"], ["🕰️", "Avant 2000", { rows: [{ v: "annee", op: "<", val: "2000" }] }, "#7c3aed"],
  ["📦", "Avec sa boîte", { rows: [{ v: "boite", op: "vrai" }] }, "#b45309"], ["🚧", "À construire", { rows: [{ v: "a_construire", op: "vrai" }] }, "#c2410c"], ["⭐", "Coup de cœur", null, "#d97706"]];
const TAGDEF = [["t-moc", "MOC", "tg"], ["t-mod", "Modifié / Modifiée", "tg"], ["t-imp", "Amélioré / Améliorée", "tg"], ["t-part", "Set partiel", "tg"], ["t-add", "+ N figurines ajoutées", "tg"], ["t-rep", "N figurines remplacées", "tg"],
  ["t-complet", "Complet (étiquette posée à la main)", "tg"], ["t-pieces", "Pièces ajoutées", "tg"], ["t-nofig", "Sans figurines", "tg"], ["t-prix", "Prix par les pièces", "tg"], ["b-moc", "MOC", "badge"], ["b-partial", "🧩 Set partiel", "badge"], ["b-scan", "Scan en cours / à valider", "badge"],
  ["b-upcoming", "Bientôt disponible", "badge"], ["b-soon", "Bientôt retiré", "badge"], ["b-onsale", "En vente", "badge"], ["b-retired", "Retiré", "badge"], ["b-inset", "Dans un set / Dans N sets", "badge"], ["b-neuf", "Neuf", "badge"],
  ["b-nofig", "Sans figurines", "badge"], ["b-qty", "×N (plusieurs exemplaires)", "badge"], ["b-plans", "Sans plans", "badge"], ["b-partiel", "Partiel", "badge"], ["b-attente", "En Attente 🚧", "badge"], ["b-boite", "📦 Avec boîte", "badge"]].map(([key, label, kind]) => ({ key, label, kind }));
const chip = (t, kind) => el("span", { class: "chip " + (kind === "badge" ? "bdg" : ""), style: [t.color && "color:" + t.color, t.bg && "background:" + t.bg, t.border && "border-color:" + t.border].filter(Boolean).join(";") }, (t.icon ? t.icon + " " : "") + (t.text || t.label || "étiquette"));
const tagUpd = (id, fn, o) => change(c => { const t = (c.tags?.add || []).find(x => x.id === id); if (t) fn(t); }, o);
function tagEditor(t) {
  const setc = k => v => tagUpd(t.id, x => { x[k] = v; }, { key: "tag" + t.id + k, redraw: false });
  const colr = (k, lab) => el("span", { class: "colset" }, el("input", { type: "color", value: /^#[0-9a-f]{6}$/i.test(t[k] || "") ? t[k] : "#888888", oninput: e => setc(k)(e.target.value), onchange: () => draw() }), el("span", { class: "hint" }, lab),
    t[k] ? el("button", { type: "button", class: "x", title: "Sans couleur", onclick: () => tagUpd(t.id, x => { delete x[k]; }) }, "↺") : null);
  return el("div", { class: "ed" + (t.off ? " offed" : "") },
    line(emoji(t.icon, setc("icon")), txt(t.label, setc("label"), "Texte de l'étiquette"), chip(t, t.kind)),
    hint("Le texte peut reprendre une valeur de la fiche : <code>{annee}</code>, <code>{theme}</code>, un de vos champs…"),
    fld("Genre", sel(t.kind || "tg", [["tg", "Étiquette, sous le nom (comme « Modifié »)"], ["badge", "Pastille, sur l'image (comme « Retiré »)"]], v => tagUpd(t.id, x => { x.kind = v; }))),
    fld("Couleurs", el("div", { class: "cols" }, colr("color", "texte"), colr("bg", "fond"), colr("border", "bordure"))),
    el("div", { class: "fl" }, "AFFICHÉE SI LA FICHE REMPLIT…"),
    condBox(() => (cfg.tags?.add || []).find(x => x.id === t.id)?.cond, (fn, rd) => tagUpd(t.id, x => { x.cond ||= {}; fn(x.cond); }, { key: "tagc" + t.id, redraw: !!rd })),
    typesRow0(t),
    el("div", { class: "checks" }, chk("Sur les cartes", t.card !== false, v => tagUpd(t.id, x => { if (v) delete x.card; else x.card = false; })), chk("En haut de la fiche", t.sheet !== false, v => tagUpd(t.id, x => { if (v) delete x.sheet; else x.sheet = false; })),
      chk("Proposer dans le menu ⚙️ Filtres", t.filter === true, v => tagUpd(t.id, x => { if (v) x.filter = true; else delete x.filter; }), "Une case de plus dans « Filtres » : ne montrer que les fiches qui portent cette étiquette")),
    el("div", { class: "ed-foot" }, el("span", { class: "hint" }, t.off ? "En pause : n'apparaît plus, sans être supprimée." : ""),
      btn(t.off ? "▶ Réactiver" : "⏸ Pause", () => tagUpd(t.id, x => { if (x.off) delete x.off; else x.off = true; }), "small"), btn("Supprimer", () => change(c => { c.tags.add = (c.tags.add || []).filter(x => x.id !== t.id); }), "small danger")));
}
const typesRow0 = t => fld("Sur quelles fiches ?", el("div", { class: "checks" }, KINDS.map(([k, n]) => chk(n, (t.types || []).includes(k), v => tagUpd(t.id, x => { x.types = v ? [...(x.types || []), k] : (x.types || []).filter(y => y !== k); if (!x.types.length) delete x.types; })))),
  (t.types || []).length ? "" : "Rien de coché = toutes les fiches.");
function overEditor(d) {
  const o = cfg.tags?.over?.[d.key] || {}, set = (k, v, rd) => setIn(["tags", "over", d.key, k], v, { key: "ov" + d.key + k, redraw: !!rd });
  const colr = (k, lab) => el("span", { class: "colset" }, el("input", { type: "color", value: /^#[0-9a-f]{6}$/i.test(o[k] || "") ? o[k] : "#888888", oninput: e => set(k, e.target.value), onchange: () => draw() }), el("span", { class: "hint" }, lab),
    o[k] ? el("button", { type: "button", class: "x", title: "Couleur d'origine", onclick: () => set(k, "", true) }, "↺") : null);
  return el("div", { class: "ed" },
    fld("Nouveau texte", line(emoji(o.icon, v => set("icon", v)), txt(o.text, v => set("text", v), d.label)), /N/.test(d.label) ? "Écrivez <code>{n}</code> là où le nombre doit apparaître (ex. : « {n} fig. en plus »). Vide = texte d'origine." : "Vide = texte d'origine."),
    fld("Couleurs", el("div", { class: "cols" }, colr("color", "texte"), colr("bg", "fond"), colr("border", "bordure"))),
    chk("Masquer complètement cette étiquette", o.hide === true, v => set("hide", v ? true : "", true)),
    o.hide ? null : [el("div", { class: "fl", style: "margin-top:8px" }, "L'AFFICHER SEULEMENT SI LA FICHE REMPLIT… (facultatif)"),
      condBox(() => cfg.tags?.over?.[d.key]?.cond, (fn, rd) => change(c => { const x = (((c.tags ||= {}).over ||= {})[d.key] ||= {}); x.cond ||= {}; fn(x.cond); }, { key: "ovc" + d.key, redraw: !!rd })),
      hint("La condition vaut sur le site connecté ; les pages publiques gardent l'affichage normal (texte, couleurs et masquage s'y appliquent).")],
    el("div", { class: "ed-foot" }, el("span", { class: "hint" }, ""), btn("↺ Comme à l'origine", () => change(c => { if (c.tags?.over) delete c.tags.over[d.key]; }), "small")));
}
VIEW.etiquettes = () => {
  const m = M(), seen = (() => { try { return m ? m.tagsSeen() : {}; } catch { return {}; } })(), mine = cfg.tags?.add || [], over = cfg.tags?.over || {};
  const newTag = (icon = "", label = "Nouvelle étiquette", cond = null, color = "") => change(c => { ((c.tags ||= {}).add ||= []).push({ id: uid(), label, ...(icon ? { icon } : {}), ...(cond ? { cond: clone(cond) } : {}), ...(color ? { color, border: color } : {}) }); });
  const grp = (kind, title, intro) => card(title, hint(intro), el("div", { class: "rowset" }, TAGDEF.filter(d => d.kind === kind).map(d => { const o = over[d.key], open = tagOpen === d.key;
    return [line(el("span", { class: "lab" }, chip({ ...(o || {}), label: o?.text ? o.text : d.label }, kind), " ", o?.hide ? el("span", { class: "hint" }, "masquée") : o ? el("span", { class: "hint" }, "modifiée") : null,
      seen[d.key] ? el("span", { class: "hint" }, " · " + seen[d.key] + " à l'écran") : null),
      btn(open ? "Fermer" : "Modifier", () => { tagOpen = open ? "" : d.key; draw(); }, "small"), o ? xbtn("Remettre comme à l'origine", () => change(c => { delete c.tags.over[d.key]; })) : null), open ? overEditor(d) : null]; })));
  return [head("Étiquettes et pastilles", "Les petits mots posés sur les cartes et les fiches. Renommez-les, recolorez-les, masquez-les, montrez-les seulement dans certains cas — et créez les vôtres, affichées selon vos conditions."),
    P() ? null : needPreview(),
    card("Vos étiquettes", mine.length ? mine.map(tagEditor) : el("p", { class: "hint" }, "Aucune pour l'instant. Une étiquette à vous apparaît sur les fiches qui remplissent sa condition."),
      el("div", { class: "btns" }, btn("+ Nouvelle étiquette", () => newTag(), "primary"), TAG_PRESETS.map(([ic, lb, cond, col]) => btn(ic + " " + lb, () => newTag(ic, lb, cond, col), "small", "Exemple prêt à adapter")))),
    grp("tg", "Étiquettes de l'application (sous le nom)", "Celles que l'application pose d'elle-même."),
    grp("badge", "Pastilles de l'application (sur l'image)", "Posées sur l'image : dans la liste de souhaits, les nouveautés, la recherche, les pages publiques. Sur les cartes de la collection, l'application les masque — sauf si vous cochez la case ci-dessous."),
    card("Pastilles sur les cartes de la collection", flag("Montrer aussi les pastilles de l'application sur les cartes de la collection", ["tags", "badges"]),
      hint("Vos propres pastilles (genre « Pastille, sur l'image ») s'affichent toujours, en bas à gauche de l'image.")),
    card("Bon à savoir", hint("Une étiquette qui dépend d'une case ou d'une note à vous ? Créez d'abord un champ personnalisé (rubrique « Champs personnalisés », par ex. une case « Coup de cœur »), puis utilisez-le dans la condition."))];
};

/* ------------------------------------------------------------------ Pages */
let pgSel = "";
const BLOCKS = [["titre", "🔠", "Titre"], ["texte", "📝", "Texte"], ["note", "💡", "Encadré coloré"], ["image", "🖼️", "Image"], ["bouton", "🔘", "Bouton"], ["fiches", "🧱", "Liste de fiches"], ["total", "🔢", "Total (tuile)"],
  ["tableau", "📋", "Tableau"], ["sep", "➖", "Trait de séparation"], ["espace", "↕️", "Espace vide"], ["html", "🧩", "HTML libre"], ["cadre", "🪟", "Page d'un autre site (cadre)"]];
const PUBLIC_OK = ["titre", "texte", "note", "image", "bouton", "sep", "espace", "html", "cadre"];
const blkName = k => BLOCKS.find(b => b[0] === k)?.[2] || k;
const NEWBLK = { titre: { text: "Mon titre" }, texte: { text: "Mon texte. **Gras**, *italique*, [un lien](https://exemple.fr).\n\n- une liste\n- à puces" }, note: { text: "Une information à mettre en avant.", color: "#2563eb" }, image: { url: "" },
  bouton: { text: "Mon bouton", act: { k: "all" } }, fiches: { limit: 12, sort: "valeur" }, total: { text: "Nombre de fiches", agg: "count" }, tableau: { cols: ["numero", "nom", "valeur"], limit: 50, sort: "valeur" }, sep: {}, espace: { h: 24 }, html: { html: "<p>Votre HTML…</p>" }, cadre: { url: "", h: 480 } };
const pgUpd = (id, fn, o) => change(c => { const p = (c.pages || []).find(x => x.id === id); if (p) fn(p); }, o);
const blkUpd = (pid, bid, fn, o) => pgUpd(pid, p => { const b = (p.blocks || []).find(x => x.id === bid); if (b) fn(b); }, o);
const showPage = id => whenApp(b => { try { b.max?.openPage(id); } catch {} });
const SCOPES = () => [["", "Toute la collection"], ["wish", "Les listes de souhaits"], ["all", "Tout (collection et souhaits)"], ...appLists().map(l => ["list:" + l.id, "Liste : " + l.name])];
const varOpts = () => { const p = P(); return p ? p.vars().map(v => [v.id, v.label]) : [["numero", "Numéro"], ["nom", "Nom"], ["valeur", "Valeur estimée"], ["annee", "Année"], ["date_ajout", "Date d'ajout"]]; };
function dataRows(pid, b) {   // réglages communs aux blocs de données : quelles fiches, condition, tri, nombre
  const set = (k, rd) => v => blkUpd(pid, b.id, x => { if (v === "" || v == null) delete x[k]; else x[k] = v; }, { key: "blk" + b.id + k, redraw: !!rd });
  return [fld("Quelles fiches ?", sel(b.scope || "", SCOPES(), set("scope", true))),
    el("div", { class: "fl" }, "SEULEMENT CELLES QUI REMPLISSENT… (facultatif)"),
    condBox(() => cfg.pages?.find(p => p.id === pid)?.blocks?.find(x => x.id === b.id)?.cond, (fn, rd) => blkUpd(pid, b.id, x => { x.cond ||= {}; fn(x.cond); }, { key: "blkc" + b.id, redraw: !!rd })),
    b.k === "total" ? null : [fld("Triées par", line(sel(b.sort || "", [["", "(sans tri)"], ...varOpts()], set("sort", true)), sel(b.dir || "desc", [["desc", "du plus grand au plus petit"], ["asc", "du plus petit au plus grand"]], set("dir", true)))),
      line(el("span", { class: "lab" }, "Nombre maximum de fiches"), el("input", { type: "number", class: "num", min: 1, max: 1000, value: b.limit ?? "", placeholder: 60, oninput: e => set("limit")(e.target.value === "" ? "" : +e.target.value) }))]];
}
function blockEditor(pg, b) {
  const set = (k, rd) => v => blkUpd(pg.id, b.id, x => { if (v === "" || v == null) delete x[k]; else x[k] = v; }, { key: "blk" + b.id + k, redraw: !!rd }), k = b.k;
  const area = (key, rows, ph) => el("textarea", { rows, value: b[key] || "", placeholder: ph, spellcheck: key !== "html", oninput: e => set(key)(e.target.value) });
  const body = k === "titre" ? [txt(b.text, set("text"), "Votre titre"), fld("Taille", sel(String(b.level || 2), [["2", "Grand"], ["3", "Moyen"], ["4", "Petit"]], v => set("level", true)(+v)))]
    : k === "texte" ? [area("text", 6, "Votre texte"), hint("<code>**gras**</code>, <code>*italique*</code>, <code>[texte du lien](https://…)</code> ; une ligne vide = nouveau paragraphe ; des lignes qui commencent par <code>- </code> = liste.")]
    : k === "note" ? [area("text", 3, "Votre message"), line(el("span", { class: "hint" }, "Couleur"), colorIn(b.color, set("color")))]
    : k === "image" ? [imgField(b.url, (v, rd) => set("url", rd)(v)), line(el("span", { class: "hint" }, "Largeur"), el("input", { type: "number", class: "num", min: 10, max: 3000, value: b.width ?? "", placeholder: "auto", oninput: e => set("width")(e.target.value === "" ? "" : +e.target.value) }), el("span", { class: "u" }, "px")),
        fld("Légende (facultatif)", txt(b.text, set("text"), "")), fld("Lien ouvert au clic (facultatif)", txt(b.link, set("link"), "https://…"))]
    : k === "bouton" ? [txt(b.text, set("text"), "Texte du bouton"), el("div", { class: "checks" }, chk("Bouton principal (coloré)", b.primary === true, v => set("primary", true)(v ? true : ""))),
        fld("Alignement", sel(b.align || "left", [["left", "à gauche"], ["center", "au centre"], ["right", "à droite"]], set("align", true))),
        fld("Quand on clique", actBox(b.act, (fn, rd) => blkUpd(pg.id, b.id, x => { x.act ||= {}; fn(x.act); }, { key: "blka" + b.id, redraw: !!rd })))]
    : k === "fiches" ? [dataRows(pg.id, b), fld("Texte s'il n'y en a aucune", txt(b.empty, set("empty"), "Aucune fiche ne correspond."))]
    : k === "total" ? [txt(b.text, set("text"), "Titre de la tuile"), fld("Calcul", sel(b.agg || "count", [["count", "Nombre de fiches"], ["sum", "Somme de…"], ["avg", "Moyenne de…"], ["min", "Plus petite valeur de…"], ["max", "Plus grande valeur de…"]], set("agg", true))),
        (b.agg || "count") === "count" ? null : [fxBox(b.expr, v => set("expr")(v), b.fmt, "ex. : {valeur}"), fld("Affichage", sel(b.fmt || "", [["", "Automatique"], ["euros", "Prix"], ["nombre", "Nombre"], ["entier", "Nombre entier"], ["pourcent", "Pourcentage"]], set("fmt", true)))], dataRows(pg.id, b)]
    : k === "tableau" ? [fld("Colonnes", el("div", { class: "checks" }, varOpts().map(([id, lab]) => chk(lab, (b.cols || []).includes(id), v => blkUpd(pg.id, b.id, x => { x.cols = v ? [...(x.cols || []), id] : (x.cols || []).filter(c => c !== id); }))))), dataRows(pg.id, b)]
    : k === "espace" ? [line(el("span", { class: "hint" }, "Hauteur"), el("input", { type: "number", class: "num", min: 2, max: 600, value: b.h ?? "", placeholder: 24, oninput: e => set("h")(e.target.value === "" ? "" : +e.target.value) }), el("span", { class: "u" }, "px"))]
    : k === "html" ? [area("html", 7, "<p>…</p>"), hint("Pour qui connaît le HTML. Par sécurité, les scripts, formulaires, cadres et styles « flottants » sont retirés à l'affichage.")]
    : k === "cadre" ? [txt(b.url, set("url"), "https://… (adresse de la page à montrer)"), line(el("span", { class: "hint" }, "Hauteur"), el("input", { type: "number", class: "num", min: 80, max: 3000, value: b.h ?? "", placeholder: 480, oninput: e => set("h")(e.target.value === "" ? "" : +e.target.value) }), el("span", { class: "u" }, "px")),
        hint("Certains sites refusent d'être montrés dans un cadre : la zone reste alors vide.")] : [];
  return [body, k === "sep" ? null : fld("Largeur du bloc", sel(String(b.w || 1), [["1", "toute la largeur"], ["2", "la moitié"], ["3", "un tiers"]], v => set("w", true)(v === "1" ? "" : +v)), "Deux blocs « la moitié » qui se suivent se placent côte à côte (sur un écran assez large)."),
    pg.pub && !PUBLIC_OK.includes(k) ? hint("🔒 Bloc de données : visible seulement dans le site connecté, jamais sur la page publique.") : null];
}
let blkOpen = "";
function pageEditor(pg) {
  const set = (k, rd) => v => pgUpd(pg.id, x => { if (v === "" || v == null) delete x[k]; else x[k] = v; }, { key: "pg" + pg.id + k, redraw: !!rd }), blocks = pg.blocks || [];
  return [btn("← Toutes les pages", () => { pgSel = ""; try { M()?.closePage(); } catch {} draw(); }, "small"), el("div", { style: "height:8px" }),
    card("La page", line(emoji(pg.icon, set("icon"), "📄"), txt(pg.title, set("title"), "Titre de la page")),
      el("div", { class: "checks", style: "margin:8px 0" }, chk("Dans le menu latéral", pg.menu !== false, v => pgUpd(pg.id, x => { if (v) delete x.menu; else x.menu = false; })), chk("Afficher son titre en haut", pg.head !== false, v => pgUpd(pg.id, x => { if (v) delete x.head; else x.head = false; })),
        chk("Publique (visible sans connexion)", pg.pub === true, v => pgUpd(pg.id, x => { if (v) x.pub = true; else delete x.pub; }), "Une adresse à donner à qui vous voulez")),
      pg.pub ? note(`Adresse publique (après publication) : <a href="/p/${esc(pg.slug || "")}" target="_blank" rel="noopener"><b>${esc(location.origin)}/p/${esc(pg.slug || "")}</b></a><br>Les visiteurs ne voient que les blocs sans données (titres, textes, images, boutons vers une adresse, HTML, cadres) — jamais vos fiches ni vos prix.`) : null,
      fld("Adresse de la page (lettres, chiffres, tirets)", txt(pg.slug, v => set("slug")(v.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+/, "").slice(0, 120)), "ma-page")),
      line(el("span", { class: "lab" }, "Largeur maximale de la page"), el("input", { type: "number", class: "num", min: 320, max: 4000, value: pg.width ?? "", placeholder: "toute", oninput: e => set("width")(e.target.value === "" ? "" : +e.target.value) }), el("span", { class: "u" }, "px"))),
    card("Les blocs de la page (" + blocks.length + ")", blocks.length ? orderList(blocks.map(b => ({ key: b.id, name: (BLOCKS.find(x => x[0] === b.k)?.[1] || "") + " " + blkName(b.k), off: !!b.off,
      sub: String(b.text || b.url || b.html || "").replace(/\s+/g, " ").slice(0, 44),
      tools: el("span", { class: "tools" }, btn(blkOpen === b.id ? "Fermer" : "Modifier", () => { blkOpen = blkOpen === b.id ? "" : b.id; draw(); }, "small"),
        btn("Copier", () => pgUpd(pg.id, x => { const i = x.blocks.findIndex(y => y.id === b.id); x.blocks.splice(i + 1, 0, { ...clone(b), id: uid() }); }), "small", "Dupliquer ce bloc (la copie se place juste en dessous)"),
        xbtn("Supprimer ce bloc", () => pgUpd(pg.id, x => { x.blocks = x.blocks.filter(y => y.id !== b.id); }))),
      below: blkOpen === b.id ? el("div", { class: "blk" }, blockEditor(pg, b)) : null })), (f, t) => pgUpd(pg.id, x => { x.blocks = moved(x.blocks, f, t); })) : el("p", { class: "hint" }, "Page vide : ajoutez un premier bloc."),
      el("div", { class: "fl", style: "margin-top:10px" }, "AJOUTER UN BLOC"),
      el("div", { class: "btns" }, BLOCKS.map(([k, ic, nm]) => btn(ic + " " + nm, () => { const id = uid(); blkOpen = id; pgUpd(pg.id, x => { (x.blocks ||= []).push({ id, k, ...clone(NEWBLK[k] || {}) }); }); }, "small")))),
    card("Voir le résultat", el("div", { class: "btns" }, btn("👁 Afficher cette page dans l'aperçu", () => showPage(pg.id), "primary"), btn(pg.off ? "▶ Réactiver la page" : "⏸ Mettre en pause", () => pgUpd(pg.id, x => { if (x.off) delete x.off; else x.off = true; })),
      btn("Supprimer la page", async () => { if (await sure("Supprimer cette page ?", "« " + esc(pg.title || "Page") + " » et ses blocs seront retirés du brouillon.", "Supprimer")) { pgSel = ""; change(c => { c.pages = c.pages.filter(x => x.id !== pg.id); }); } }, "danger")),
      hint("L'aperçu se met à jour à chaque changement. Les listes de fiches, totaux et tableaux se calculent sur votre collection.")),
  ];
}
const PAGE_PRESETS = {
  vide: () => ({ title: "Nouvelle page", icon: "📄", blocks: [{ id: uid(), k: "texte", text: "Écrivez ici." }] }),
  bord: () => ({ title: "Tableau de bord", icon: "📊", blocks: [{ id: uid(), k: "total", text: "Fiches", agg: "count", w: 3 }, { id: uid(), k: "total", text: "Valeur totale", agg: "sum", expr: "{valeur}", fmt: "euros", w: 3 },
    { id: uid(), k: "total", text: "Valeur moyenne", agg: "avg", expr: "{valeur}", fmt: "euros", w: 3 }, { id: uid(), k: "titre", text: "Les 12 fiches les plus chères", level: 3 }, { id: uid(), k: "fiches", sort: "valeur", limit: 12 },
    { id: uid(), k: "titre", text: "Derniers ajouts", level: 3 }, { id: uid(), k: "tableau", cols: ["numero", "nom", "date_ajout", "valeur"], sort: "date_ajout", limit: 15 }] }),
  notes: () => ({ title: "Mes notes", icon: "📝", blocks: [{ id: uid(), k: "note", text: "Une page à vous : idées, liens utiles, choses à faire.", color: "#2563eb" }, { id: uid(), k: "texte", text: "- première idée\n- deuxième idée" },
    { id: uid(), k: "bouton", text: "Retour à la collection", act: { k: "all" } }] }),
};
VIEW.pages = () => {
  const pages = cfg.pages || [], pg = pages.find(p => p.id === pgSel);
  const create = kind => { const p = { id: uid(), ...PAGE_PRESETS[kind]() }; p.slug = slug(p.title).replace(/_/g, "-") || "page"; let n = 2; const b = p.slug; while (pages.some(x => x.slug === p.slug)) p.slug = b + "-" + n++;
    pgSel = p.id; change(c => { (c.pages ||= []).push(p); }); showPage(p.id); };
  if (pg) return [head("Page « " + (pg.title || "Page") + " »", "Une page se compose de blocs, empilés dans l'ordre. Chaque bloc peut prendre toute la largeur, la moitié ou un tiers."), P() ? null : needPreview(), pageEditor(pg)];
  return [head("Pages", "Créez vos propres pages dans le site : un tableau de bord, une liste de sets à vendre, une page de notes, une page publique à partager… Elles apparaissent dans le menu latéral."),
    card("Vos pages", pages.length ? orderList(pages.map(p => ({ key: p.id, name: (p.icon || "📄") + " " + (p.title || "Page"), off: !!p.off, sub: (p.blocks || []).length + " bloc(s)" + (p.pub ? " · publique : /p/" + (p.slug || "") : "") + (p.menu === false ? " · hors menu" : "") + (p.off ? " · en pause" : ""),
      tools: el("span", { class: "tools" }, btn("Modifier", () => { pgSel = p.id; blkOpen = ""; draw(); showPage(p.id); }, "small primary"), btn("👁", () => showPage(p.id), "small", "Voir dans l'aperçu")) })), (f, t) => change(c => { c.pages = moved(c.pages, f, t); }))
      : el("p", { class: "hint" }, "Aucune page pour l'instant.")),
    card("Créer une page", el("div", { class: "tiles" }, el("button", { type: "button", onclick: () => create("vide") }, el("b", {}, "📄 Page vide"), el("span", {}, "Vous ajoutez les blocs un à un.")),
      el("button", { type: "button", onclick: () => create("bord") }, el("b", {}, "📊 Tableau de bord"), el("span", {}, "Totaux, fiches les plus chères, derniers ajouts.")),
      el("button", { type: "button", onclick: () => create("notes") }, el("b", {}, "📝 Page de notes"), el("span", {}, "Un encadré, un texte, un bouton.")))),
    card("Bon à savoir", hint("L'ordre des pages dans le menu, et leur place parmi les autres entrées : rubrique « Menu ». Un bouton ou un raccourci clavier peut ouvrir une page (« Comportements »). Une page « publique » reçoit une adresse /p/… ; ses blocs de données n'y sont jamais montrés."))];
};

/* ------------------------------------------------------------------ Page « Réglages » de l'application */
const SETDEF = [["prix", "💶 Prix"], ["estimations", "🧮 Estimations"], ["reseaux_sociaux", "💬 Réseaux sociaux"], ["bricklink", "🧱 BrickLink"], ["rebrickable", "🔑 Rebrickable"], ["public", "🌐 Public"], ["securite", "🔒 Sécurité"], ["docs", "📚 Docs"], ["back_office", "🛠 Back office"], ["aide", "❓ Aide"]];
VIEW.reglages = () => {
  let live = null; try { live = M()?.settings() || null; } catch {}
  const s = cfg.settings || {}, base = (live || SETDEF.map(([key, label]) => ({ key, label }))), order = s.order || [], hidden = s.hidden || [];
  const rows = [...base].sort((a, b) => { const i = order.indexOf(a.key), j = order.indexOf(b.key); return (i < 0 ? 999 : i) - (j < 0 ? 999 : j); });
  const open = () => whenApp(b => { try { b.max?.openSettings(); } catch {} setTimeout(draw, 900); });
  return [head("Page « Réglages » de l'appli", "La page ⚙️ Réglages du site : choisissez l'ordre de ses sections, renommez-les, masquez celles dont vous ne vous servez pas."),
    live ? null : note("Pour voir le résultat en direct, ouvrez la page Réglages dans l'aperçu.", "warn"),
    el("div", { class: "btns", style: "margin-bottom:12px" }, btn("⚙️ Ouvrir la page Réglages dans l'aperçu", open, live ? "" : "primary"), live ? btn("Refermer", () => { try { M()?.closeSettings(); } catch {} setTimeout(draw, 300); }) : null),
    card("Sections", orderList(rows.map(r => ({ key: r.key, name: s.titles?.[r.key] || r.label, off: hidden.includes(r.key), sub: hidden.includes(r.key) ? "masquée" : s.titles?.[r.key] ? "à l'origine : " + r.label : "",
      below: el("input", { type: "text", class: "ren", value: s.titles?.[r.key] || "", placeholder: "Renommer cette section…", title: "Nouveau titre de la section (vide = titre d'origine)", oninput: e => setIn(["settings", "titles", r.key], e.target.value, { key: "sett" + r.key, redraw: false }) }),
      tools: el("span", { class: "tools" }, chk("visible", !hidden.includes(r.key), v => change(c => { const st = (c.settings ||= {}); st.hidden = (st.hidden || []).filter(k => k !== r.key); if (!v) st.hidden.push(r.key); }))) })),
      (f, t) => change(c => { (c.settings ||= {}).order = moved(rows.map(r => r.key), f, t); })),
      hint("Glissez ⠿ ou utilisez ▲ ▼. Une section masquée garde ses réglages : elle est seulement cachée.")),
    hidden.includes("securite") || hidden.includes("back_office") ? note("ℹ️ Section masquée : le back office reste accessible par son adresse <b>/backoffice</b>, et le mot de passe de la Briquothèque se change aussi dans « Mots de passe et sécurité ».") : null,
    card("Une option en particulier", para("Pour masquer, renommer ou restyler <b>une ligne, un bouton, un texte</b> de la page Réglages — ou y ajouter un texte, un lien, une image : ouvrez-la dans l'aperçu, puis « 🖱️ Cliquer pour modifier »."),
      btn("🖱️ Cliquer pour modifier", () => { open(); setTimeout(() => show("souris"), 1200); })),
    cfg.settings ? card("Revenir en arrière", btn("↺ Page Réglages d'origine", () => change(c => { delete c.settings; }), "danger")) : null];
};

/* ------------------------------------------------------------------ Comportements */
const SORTS0 = [["modified", "Dernière modification"], ["added", "Ajout récent"], ["value", "Valeur"], ["variation", "Variation de prix (%)"], ["hausse", "Augmentation / baisse (%)"], ["ecart", "Variation de prix (€)"], ["name", "Nom"], ["number", "Numéro"], ["year", "Année"], ["qty", "Nombre d'exemplaires"],
  ["pieces", "Nombre de pièces"], ["figs", "Nombre de figurines"], ["theme", "Thème"], ["random", "Aléatoire"]];
VIEW.comportements = () => {
  const b = cfg.behav || {}, st = String(b.start || ""), sk = st.slice(0, Math.max(0, st.indexOf(":"))), sv = st.slice(st.indexOf(":") + 1), lists = appLists();
  const sortOpts = [["", "comme à l'origine"], ...SORTS0, ...(cfg.sorts || []).map(s => ["bo:" + s.id, "★ " + (s.label || "tri")])];
  const keys = b.keys || [], kUpd = (id, fn, o) => change(c => { const k = (c.behav?.keys || []).find(x => x.id === id); if (k) fn(k); }, o);
  const clicks = (cfg.rules || []).filter(r => r.click?.k || r.href || r.blank);
  return [head("Comportements", "Ce que fait le site : par quoi il s'ouvre, comment il trie, les raccourcis clavier, ce qui se passe quand on clique sur un élément."),
    lists.length ? null : needPreview(),
    card("À l'ouverture du site",
      fld("Page de départ", line(sel(sk, [["", "Comme d'habitude (toute la collection)"], ["list", "Une liste…"], ["view", "Une vue enregistrée…"], ["page", "Une page créée…"]], v => setIn(["behav", "start"], v ? v + ":" : "")),
        sk === "list" ? sel(sv, [["", "— choisir —"], ...lists.map(l => [l.id, l.name])], v => setIn(["behav", "start"], "list:" + v)) : sk === "view" ? sel(sv, [["", "— choisir —"], ...(cfg.views || []).map(v => [v.id, v.label || "vue"])], v => setIn(["behav", "start"], "view:" + v))
          : sk === "page" ? sel(sv, [["", "— choisir —"], ...(cfg.pages || []).map(p => [p.id, p.title || "page"])], v => setIn(["behav", "start"], "page:" + v)) : null)),
      fld("Ce qui est montré", sel(b.view || "", [["", "Comme la dernière fois"], ["all", "Tout (sets et figurines)"], ["sets", "Les sets"], ["figs", "Les figurines"]], v => setIn(["behav", "view"], v))),
      hint("Appliqué à chaque ouverture du site (pas dans cet aperçu : utilisez « Ouvrir le site ↗ » pour l'essayer).")),
    card("Tri par défaut", el("div", { class: "st" },
      row3("« Toute la collection »", sel(b.sorts?.all || "", sortOpts, v => setIn(["behav", "sorts", "all"], v))), row3("Une liste de la collection", sel(b.sorts?.collection || "", sortOpts, v => setIn(["behav", "sorts", "collection"], v))),
      row3("Une liste de souhaits", sel(b.sorts?.wishlist || "", sortOpts, v => setIn(["behav", "sorts", "wishlist"], v)))),
      hint("Vaut tant que vous n'avez pas choisi un autre tri pour la liste (le site retient votre choix, liste par liste).")),
    card("Raccourcis clavier", keys.length ? keys.map(k => el("div", { class: "ed" }, line(el("span", { class: "hint" }, "Touche"),
      el("input", { type: "text", class: "emo", maxLength: 12, value: k.key || "", placeholder: "n", title: "Une lettre, un chiffre, ou le nom d'une touche (F2, Enter, ArrowUp…)", oninput: e => kUpd(k.id, x => { x.key = e.target.value; }, { key: "key" + k.id, redraw: false }) }),
      chk("Ctrl", k.ctrl === true, v => kUpd(k.id, x => { if (v) x.ctrl = true; else delete x.ctrl; })), chk("Alt", k.alt === true, v => kUpd(k.id, x => { if (v) x.alt = true; else delete x.alt; })), el("span", { class: "grow" }),
      xbtn("Supprimer ce raccourci", () => change(c => { c.behav.keys = c.behav.keys.filter(x => x.id !== k.id); }))),
      actBox(k.act, (fn, rd) => kUpd(k.id, x => { x.act ||= {}; fn(x.act); }, { key: "keya" + k.id, redraw: !!rd }), [["", "— que fait ce raccourci ? —"]]))) : el("p", { class: "hint" }, "Aucun raccourci pour l'instant."),
      btn("+ Raccourci", () => change(c => { ((c.behav ||= {}).keys ||= []).push({ id: uid(), key: "", act: { k: "new" } }); }), "small"),
      hint("Un raccourci n'agit pas pendant que vous tapez dans une case. Évitez les touches déjà prises par le navigateur (Ctrl + T, Ctrl + W…).")),
    card("Clics et liens modifiés (" + clicks.length + ")", clicks.length ? el("div", { class: "rowset" }, clicks.map(r => line(el("span", { class: "lab" }, el("b", {}, r.label || r.sel), el("div", { class: "hint" },
        [r.click?.k === "none" ? "clic désactivé" : r.click?.k === "confirm" ? "confirmation demandée" : actText(r.click), r.href ? "lien → " + r.href : "", r.blank ? "nouvel onglet" : ""].filter(Boolean).join(" · "))),
      btn("Montrer", () => flash(r.sel, r.page), "small"), xbtn("Retirer ce comportement", () => change(c => { const x = c.rules.find(y => y.id === r.id); if (x) { delete x.click; delete x.href; delete x.blank; } })))))
      : el("p", { class: "hint" }, "Aucun pour l'instant."),
      para("Pour changer ce que fait <b>un bouton, un lien, une image, une carte</b> : cliquez-le dans l'aperçu, carte « Lien et action au clic »."), btn("🖱️ Cliquer un élément dans l'aperçu", () => show("souris"), "small")),
    card("Figurines identiques",
      flag("Ne pas regrouper en une seule carte une figurine que vous avez à la fois seule et dans un set (ou dans plusieurs sets)", ["behav", "noMerge"]),
      flag("Ne pas demander « est-ce celle de ce set ? » quand vous ajoutez un set dont vous avez déjà une figurine seule", ["behav", "noOffer"]),
      hint("D'origine : une même figurine n'a qu'une carte (« ×N », seule et dans vos sets), et l'application propose de ranger dans le set ajouté la figurine seule que vous aviez déjà. La tâche automatique « Photo à faire » se règle dans <b>Paramètres du serveur</b> ; la décote « modifié », dans les Réglages de l'application.")),
    card("Prix et variations",
      flag("Ne pas afficher les flèches de variation (↑ ↓ ~) à côté des prix", ["behav", "noTrend"]),
      flag("Masquer le bouton « 🔍 Comprendre les variations » des statistiques", ["behav", "noVariations"]),
      (() => {   // apparence des flèches : valeurs en vigueur (celles choisies, ou celles du brouillon) ; l'aperçu les montre en direct
        if (X.trend === undefined) { X.trend = null; api("/api/settings").then(s => { X.trend = s.trend || {}; draw(); }).catch(() => { X.trend = {}; draw(); }); }
        const base = X.trend || {}, tv = k => getIn(["behav", "trend", k]) ?? base[k], tset = (k, v, o) => setIn(["behav", "trend", k], v, o);
        return [el("div", { style: "height:8px" }), el("b", {}, "Apparence des flèches"),
          chk("Variations affichées d'office dans la vue générale (le bouton 📈 les montre ou les cache à la volée)", tv("on") !== false, v => tset("on", v)),
          chk("Afficher « ~ » quand le prix est stable (entre les deux seuils)", tv("stable") !== false, v => tset("stable", v)),
          chk("Afficher le pourcentage", tv("pct") === true, v => tset("pct", v)),
          fld("Taille des flèches", line(el("input", { type: "range", min: 60, max: 220, step: 5, value: tv("size") || 100, oninput: e => { tset("size", +e.target.value, { key: "trendsize", redraw: false }); e.target.nextSibling.textContent = e.target.value + " %"; } }),
            el("span", { class: "u" }, (tv("size") || 100) + " %"))),
          cfg.behav?.trend ? btn("↺ Revenir aux valeurs enregistrées", () => change(c => { delete c.behav.trend; }), "small") : null];
      })(),
      hint("Dans une fiche (prix, estimation, détail des prix), la variation est toujours affichée. Les seuils de hausse et de baisse se règlent dans l'application : Réglages → 🧮 Estimations. Le minimum de ventes pour retenir un prix : Réglages → 💶 Prix.")),
    card("Fiches et pièces",
      flag("Ouvrir les fiches directement en modification (sans passer par la clé 🔧)", ["behav", "editFirst"]),
      flag("Toucher une pièce l'agrandit (au lieu d'ouvrir sa fiche : où la trouver, prix…)", ["behav", "partZoom"])),
    card("Pages publiques",
      flag("Ne pas garder les listes dans la barre collée en haut (elles défilent avec la page)", ["behav", "noPubNav"]),
      hint("D'origine : en défilant, les listes principales et « ↩ Toute la collection » restent à portée, en haut de la page.")),
    card("Divers", fld("Titre de l'onglet du navigateur", txt(b.title, v => setIn(["behav", "title"], v, { key: "bhtitle", redraw: false }), "Briquothèque")),
      flag("Réduire les animations et les transitions", ["behav", "noAnim"])),
    el("details", { class: "card", open: !!cfg.js }, el("summary", { style: "cursor:pointer;font-weight:600" }, "Avancé (facultatif) : script libre"),
      hint("Réservé à qui connaît le JavaScript. Ce script est exécuté une fois, au chargement de l'application (jamais sur les pages publiques). Il reçoit « BO » (les outils du back office) et voit tout ce que voit l'application. " +
        "S'il casse l'affichage : ajoutez « ?bo=off » à l'adresse du site, puis videz cette case."),
      el("textarea", { rows: 8, value: cfg.js || "", spellcheck: false, style: "font-family:ui-monospace,Consolas,monospace;font-size:12px", placeholder: "// ex. : console.log(state.items.length + \" fiches\");",
        oninput: e => change(c => { c.js = e.target.value; }, { key: "js", redraw: false }) }),
      hint("Pris en compte au prochain chargement de la page (dans l'aperçu : ↻ recharger).")),
    cfg.behav ? card("Revenir en arrière", btn("↺ Comportements d'origine", () => change(c => { delete c.behav; }), "danger")) : null];
};

/* ------------------------------------------------------------------ Mots de passe et sécurité (effet immédiat) */
const pwIn = (ph, auto) => el("input", { type: "password", placeholder: ph, autocomplete: auto || "new-password" });
VIEW.securite = () => {
  if (X.acc === undefined) { X.acc = null; api("/api/bo/acces").then(v => { X.acc = v; draw(); }).catch(e => { X.acc = { erreur: e.message }; draw(); }); }
  const d = X.acc, w = wait(d, "acc");
  if (w) return [head("Mots de passe et sécurité", ""), w];
  const cur = pwIn("Mot de passe actuel du back office", "current-password"), n1 = pwIn("Nouveau mot de passe (" + d.min + " caractères au moins)"), n2 = pwIn("Le même, une seconde fois");
  const bo = pwIn("Mot de passe du back office", "current-password"), a1 = pwIn("Nouveau mot de passe de la Briquothèque (" + d.min + " caractères au moins)"), a2 = pwIn("Le même, une seconde fois");
  const same = (a, b) => { if (a.value.length < d.min) { toast("Le mot de passe doit faire au moins " + d.min + " caractères."); return false; } if (a.value !== b.value) { toast("Les deux mots de passe ne sont pas identiques."); return false; } return true; };
  const opt = async body => { const r = await act(() => api("/api/bo/options", body)); if (r) { X.acc = { ...X.acc, ...r }; draw(); } return r; };
  return [head("Mots de passe et sécurité", "Le back office a son propre mot de passe. Il ouvre aussi la Briquothèque : gardez-le précieusement."),
    note("🔑 <b>Ne perdez pas le mot de passe du back office</b> : il ne peut pas être retrouvé depuis l'application. Perdu, il faut supprimer le fichier <code>data/backoffice_auth.json</code> sur le serveur, puis rouvrir /backoffice pour en créer un nouveau.", "warn"),
    card("État", el("div", { class: "rowset" },
      line(el("span", { class: "lab" }, "Mot de passe du back office"), el("b", {}, d.same ? "le même que celui de la Briquothèque" : "différent de celui de la Briquothèque")),
      line(el("span", { class: "lab" }, "Créé le"), el("span", {}, dt(d.created)), el("span", { class: "hint" }, "· changé le " + dt(d.changed))),
      line(el("span", { class: "lab" }, "Sessions ouvertes du back office"), el("b", {}, String(d.sessions)), d.sessions > 1 ? btn("Fermer les autres", () => opt({ logout_all: true }).then(r => r && toast("✔ Les autres appareils sont déconnectés du back office.")), "small") : null),
      line(el("span", { class: "lab" }, "Durée d'une session"), el("span", {}, d.session_hours + " h (ou " + d.remember_days + " jours avec « Rester connecté »)")),
      line(el("span", { class: "lab" }, "Vous êtes connecté depuis"), el("b", {}, d.local ? "le réseau local" : "Internet"))),
      el("div", { class: "btns", style: "margin-top:8px" }, btn("Se déconnecter du back office", async () => { await act(() => api("/api/bo/logout", {})); location.href = "/"; }))),
    card("Changer le mot de passe du back office", fld("Actuel", cur), fld("Nouveau", n1), fld("Confirmation", n2),
      btn("✔ Changer le mot de passe du back office", async () => { if (!same(n1, n2)) return; const r = await act(() => api("/api/bo/password", { current: cur.value, new: n1.value }), "✔ Mot de passe du back office changé. Les autres appareils sont déconnectés.");
        if (r) { delete X.acc; draw(); } }, "primary")),
    card("Changer le mot de passe de la Briquothèque", para("Celui qui protège la collection. Utile aussi s'il a été <b>oublié</b> : l'ancien n'est pas demandé, seulement celui du back office."),
      fld("Mot de passe du back office (pour confirmer)", bo), fld("Nouveau mot de passe de la Briquothèque", a1), fld("Confirmation", a2),
      btn("✔ Changer le mot de passe de la Briquothèque", async () => { if (!same(a1, a2)) return;
        if (!await sure("Changer le mot de passe de la Briquothèque ?", "Tous les appareils connectés à la Briquothèque devront se reconnecter avec le nouveau mot de passe.", "Changer")) return;
        const r = await act(() => api("/api/bo/app-password", { bo: bo.value, new: a1.value }), "✔ Mot de passe de la Briquothèque changé."); if (r) { delete X.acc; draw(); } }, "primary"),
      hint("Astuce : pour que les deux mots de passe soient identiques, donnez ici le même que celui du back office.")),
    card("Outils sensibles depuis Internet", para("Le <b>code de l'application</b>, les réglages de démarrage, la restauration d'un .zip et la page de secours peuvent casser le serveur : ils ne répondent que depuis le <b>réseau local</b> (chez vous)."),
      chk("Les permettre aussi depuis Internet", d.remote_tools === true, async v => { if (v && !await sure("Permettre les outils sensibles depuis Internet ?", "Quiconque connaîtrait le mot de passe du back office pourrait alors modifier le code du serveur depuis n'importe où. À n'activer que si vous en avez besoin, avec un mot de passe long.", "Permettre")) return draw(); await opt({ remote_tools: v }); draw(); }),
      hint(d.local ? "Vous êtes sur le réseau local : vous pouvez changer ce réglage." : "Ce réglage ne se change que depuis le réseau local (vous êtes vu comme venant d'Internet). Tout le reste du back office marche de partout.")),
    card("En cas de problème", el("ul", { class: "steps" },
      el("li", { html: "Le site s'affiche mal après un réglage : ajoutez <code>?bo=off</code> à son adresse (il s'affiche sans personnalisation), puis corrigez ici." }),
      el("li", { html: "Le site ne répond plus après une modification du code : <a href=\"/backoffice/secours\" target=\"_blank\" rel=\"noopener\">🛟 page de secours</a> (remettre une version, redémarrer)." }),
      el("li", { html: "Après 10 mots de passe faux, l'adresse est bloquée 15 minutes (bannie 4 h si elle vient d'Internet) : les adresses bannies se gèrent dans Réglages → Sécurité du site." })))];
};

/* ------------------------------------------------------------------ barre du haut : notice, déconnexion ; écran trop petit */
const grow = $(".top .grow");
$(".top").append(el("a", { class: "b", href: "/backoffice/guide", target: "_blank", rel: "noopener", title: "La notice du back office : exemples, captures, pas à pas" }, "❓ Notice"),
  el("button", { type: "button", class: "b", title: "Se déconnecter du back office", onclick: async () => { try { await api("/api/bo/logout", {}); } catch {} location.href = "/"; } }, "⎋ Quitter"));
let small = false;
try { small = matchMedia("(max-width: 1000px)").matches || /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || (navigator.maxTouchPoints > 1 && innerWidth < 1100); } catch {}
if (small && !sessionStorage.getItem("bo-small")) {
  const b = el("div", { class: "devwarn" }, el("span", { html: "📱 <b>Le back office est pensé pour un ordinateur</b> (grand écran, souris). Sur tablette ou téléphone il est déconseillé : « cliquer pour modifier » et « déplacer » y sont peu pratiques." }),
    el("button", { type: "button", class: "b small", onclick: () => { b.remove(); try { sessionStorage.setItem("bo-small", "1"); } catch {} } }, "J'ai compris"));
  document.body.prepend(b);
}
/* chaque rubrique porte un lien vers son chapitre de la notice */
const draw3 = draw;
draw = function () { draw3(); const h = $("#panel h2"); if (h && !h.querySelector(".helpl")) h.append(el("a", { class: "helpl", href: "/backoffice/guide#" + panel, target: "_blank", rel: "noopener", title: "Ouvrir la notice à ce chapitre (nouvel onglet)" }, "❓ Aide")); };
/* pour les captures de la notice et les essais : ouvrir directement un éditeur (page, bloc, étiquette d'origine) */
X0.ui = { page: id => { pgSel = id || ""; }, block: id => { blkOpen = id || ""; }, tag: k => { tagOpen = k || ""; }, showPage };
window.BO_MAX = true;
startAdmin();

/* ------------------------------------------------------------------ 🧩 Éléments d'origine : modifier l'existant (tris, filtres, tuiles, calculs) */
PANELS.push(["origine", "🧩", "Éléments d'origine", "Renommer, masquer, réordonner les tris, filtres et tuiles de l'appli ; régler les calculs d'origine."]);
grp("Avancé")?.unshift("origine");
PANELS.push(["tout", "🗂️", "Tous les éléments", "Chaque bouton, lien, menu, titre, option de l'appli — même caché : le modifier, le masquer, l'afficher."]);
grp("Avancé")?.unshift("tout");
try { buildNav(); } catch {}
const obj = v => v && typeof v === "object" && !Array.isArray(v) ? v : {}, arr = v => Array.isArray(v) ? v : [];
const FILT0 = [["complet", "Complet"], ["ameliore", "Amélioré"], ["modifie", "Modifié"], ["partiel", "Set partiel"], ["moc", "MOC"], ["cardLogo", "Logo de la liste (cartes)"], ["cardName", "Nom de la liste (cartes)"]];
const tilesSeen = () => { try { const d = frame.contentDocument; return [...d.querySelectorAll("#stats .stat")].map(t => [t.dataset.natOrig || t.querySelector(".lbl")?.textContent.trim() || "", t.dataset.natOrig || t.querySelector(".lbl")?.textContent.trim() || ""]).filter(x => x[0]); } catch { return []; } };
let calc0 = null;
function natEditor(kind, base) {   // une ligne par élément : ↑ ↓, nom (vide = d'origine), masquer
  const c = obj(getIn(["native", kind])), lab = obj(c.labels), hid = arr(c.hidden);
  const seen = new Set(), list = [];
  for (const k of arr(c.order)) { const b = base.find(x => x[0] === k); if (b && !seen.has(k)) { seen.add(k); list.push(b); } }
  for (const b of base) if (!seen.has(b[0])) { seen.add(b[0]); list.push(b); }
  for (const k of [...Object.keys(lab), ...hid]) if (!seen.has(k)) { seen.add(k); list.push([k, k]); }   /* (réglé, mais pas visible maintenant) */
  const move = (k, d) => { const o = list.map(x => x[0]), i = o.indexOf(k), j = i + d; if (j < 0 || j >= o.length) return; [o[i], o[j]] = [o[j], o[i]]; setIn(["native", kind, "order"], o); };
  return el("div", { class: "rowset" }, list.map(([k, nm], i) => line(
    el("span", { class: "lab" }, el("input", { type: "text", value: lab[k] || "", placeholder: nm, title: "Nouveau nom (vide : « " + nm + " »)", style: "width:100%",
      oninput: e => setIn(["native", kind, "labels", k], e.target.value.trim(), { key: "nat" + kind + k, redraw: false }) })),
    chk("masquer", hid.includes(k), v => setIn(["native", kind, "hidden"], v ? [...new Set([...hid, k])] : hid.filter(x => x !== k))),
    xbtn ? el("span", {}, btn("↑", () => move(k, -1), "small", "Monter"), btn("↓", () => move(k, 1), "small", "Descendre")) : null)));
}
VIEW.origine = () => {
  const ta = tilesSeen();
  if (!calc0) { calc0 = "…"; fetch("/api/settings", { credentials: "include" }).then(r => r.json()).then(j => { calc0 = j; draw(); }).catch(() => { calc0 = { err: true }; draw(); }); }
  const app = async (u, body, msg) => { try { const r = await fetch(u, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || "Erreur " + r.status); toast(msg); } catch (e) { toast(e.message); } };
  const pct = (val, on, max = 100, step = 1) => [el("input", { type: "number", class: "num", min: 0, max, step, value: val ?? "", onchange: e => on(+e.target.value) }), el("span", { class: "u" }, "%")];
  const C = typeof calc0 === "object" ? calc0 : null;
  return [head("🧩 Éléments d'origine", "Ce qui existe déjà dans l'appli : le renommer, le masquer, changer son ordre (brouillon puis « Publier »). Les calculs d'origine : leur formule et leurs pourcentages (effet immédiat)."),
    P() ? null : needPreview(),
    card("Tris — « Trier par »", natEditor("sorts", SORTS0), hint("Vide : le nom d'origine. Un tri masqué disparaît du menu « Trier par » (s'il était choisi, il reste actif jusqu'au prochain choix). Vos propres tris (★) se règlent dans « Vues, tris et filtres ».")),
    card("Filtres — « ⚙️ Filtres »", natEditor("filters", FILT0), hint("Les étiquettes et les options des cartes du menu Filtres.")),
    card("Tuiles du haut", ta.length || Object.keys(obj(getIn(["native", "tiles"]))).length ? natEditor("tiles", ta) : hint("Aucune tuile dans l'aperçu."),
      hint("Les tuiles changent selon la page : ouvrez dans l'aperçu celle à régler (Toute la collection, une liste, une liste de souhaits, À construire…), puis ⟳ ci-dessous."),
      el("div", { class: "btns" }, btn("⟳ Relire les tuiles de l'aperçu", () => draw(), "small"))),
    card("Calculs d'origine", !C ? hint("Chargement…") : C.err ? note("Impossible de lire les réglages de l'appli (ouvrez l'appli connecté dans ce navigateur).", "warn") : [
      fld("📦 Set d'occasion avec sa boîte", pct(C.box_bonus ?? 6, v => app("/api/settings/box", { pct: v }, "✔ Boîte : enregistré")), "Valeur = cote d'occasion + prix d'une <b>boîte vide</b> de ce set (BrickOwl, chaque mois) ; sans prix de boîte : cote × (1 + ce pourcentage)."),
      fld("📘 Avec son livret de plans", pct(C.plan_cut ?? 5, v => app("/api/settings/plan", { pct: v }, "✔ Livret : enregistré"), 90), "Valeur = cote + prix des <b>plans seuls</b> de ce set (BrickOwl) ; sinon : cote × (1 + ce pourcentage)."),
      fld("🔧 Exemplaire modifié", pct(C.mod_discount ?? 5, v => app("/api/settings/discount", { pct: v }, "✔ Décote : enregistré"), 90), "Seulement si une figurine d'<b>origine</b> est modifiée : valeur = cote × (1 − ce pourcentage). Pièces échangées, ajouts : leur écart de prix, pas de décote."),
      fld("↑ ↓ Seuils des flèches de variation", [el("span", { class: "hint" }, "hausse ≥ "), ...pct(C.trend?.up ?? 3, v => { C.trend = { ...(C.trend || {}), up: v }; app("/api/settings/trend", { up: v, down: C.trend.down ?? 3 }, "✔ Seuil de hausse : enregistré"); }, 100, .5),
        el("span", { class: "hint" }, " baisse ≥ "), ...pct(C.trend?.down ?? 3, v => { C.trend = { ...(C.trend || {}), down: v }; app("/api/settings/trend", { up: C.trend.up ?? 3, down: v }, "✔ Seuil de baisse : enregistré"); }, 100, .5)],
        "Écart depuis le dernier relevé : au-delà, flèche ↑ ou ↓ ; en dessous, « ~ » (stable)."),
      hint("Ces pourcentages s'appliquent tout de suite (sans « Publier ») : ce sont les réglages du serveur, les mêmes que dans l'appli (Réglages → 🧮 Estimations).")]),
  ];
};

})();

/* ------------------------------------------------------------------ clic droit dans l'aperçu : les outils de l'élément (bo.js ouvre le menu, le travail se fait ici) */
let ctxStyle = null;   // style copié : {propriété CSS: valeur}
const CTX_STYLE = ["color", "background-color", "font-size", "font-weight", "font-style", "text-align", "border-radius", "border-width", "border-color", "opacity"];
/* ------------------------------------------------------------------ 🗂️ Tous les éléments : l'inventaire de l'aperçu, cherchable, avec ✏️ Modifier et 🙈 Masquer / 👁 Afficher */
let invQ = "", invZone = "", invData = null;
VIEW.tout = () => {
  const B = BOF();
  if (!B || !B.inventory) return [head("🗂️ Tous les éléments", "Tout ce que l'appli affiche, même caché."), note("L'aperçu n'est pas prêt : attendez qu'il soit chargé, puis rouvrez ce panneau.", "warn")];
  try { if (!invData) invData = B.inventory(); } catch (e) { invData = []; }
  const mine = x => (cfg.rules || []).some(r => r.sel === x.one && r.hide && (!r.page || r.page === B.page));
  const zones = [...new Set(invData.map(x => x.area))];
  const list = el("div", { class: "rowset" }), count = el("p", { class: "hint", style: "margin:0 0 6px" });
  const fill = () => {
    const q = invQ.trim().toLowerCase(), rows = invData.filter(x => (!invZone || x.area === invZone) && (!q || (x.text + " " + x.desc + " " + x.area).toLowerCase().includes(q)));
    count.textContent = rows.length + " élément(s)" + (rows.length > 3000 ? " — les 3 000 premiers affichés : précisez la recherche" : "");
    list.replaceChildren(...rows.slice(0, 3000).map(x => { const hid = mine(x);
      return line(el("span", { class: "lab", style: "min-width:0" }, el("b", {}, x.text || "(sans texte)"), el("br"), el("small", { class: "hint" }, x.area + " · " + x.desc + (hid ? " · 🙈 masqué par vous" : x.hidden ? " · caché pour l'instant (menu fermé, autre page…)" : ""))),
        el("span", { style: "display:flex;gap:6px;flex:none" },
          btn("✏️ Modifier", () => { if (typeof setMode === "function" && mode !== "pick") setMode("pick"); if (!B.invPick(x.i)) { toast("Élément introuvable : ⟳ Relire l'aperçu."); } }, "small", "Ouvrir l'éditeur de cet élément (texte, style, lien, action, icône…)"),
          hid ? btn("👁 Afficher", () => change(c => { for (const r of c.rules || []) if (r.sel === x.one && (!r.page || r.page === B.page)) delete r.hide; }), "small", "Ne plus le masquer")
            : btn("🙈 Masquer", () => { const info = B.invInfo(x.i); if (!info) return toast("Élément introuvable : ⟳ Relire l'aperçu."); window.BO_ADMIN.onContext("hide", info); }, "small", "Le masquer (« Afficher » le remet)"))); }));
  };
  fill();
  return [head("🗂️ Tous les éléments", "Chaque bouton, lien, menu, titre, étiquette, option et champ de la page affichée dans l'aperçu — y compris ce qu'on ne peut pas atteindre en cliquant (menus Trier / Filtres fermés, fenêtres, éléments masqués). « ✏️ Modifier » ouvre l'éditeur complet de l'élément ; rien n'est verrouillé."),
    card("Chercher", el("input", { type: "search", value: invQ, placeholder: "Un mot du bouton, du menu, du titre…", style: "width:100%", oninput: e => { invQ = e.target.value; fill(); } }),
      el("div", { class: "pills", style: "margin-top:8px" }, [["", "Toutes les zones"], ...zones.map(z => [z, z])].map(([k, l]) => el("button", { type: "button", class: invZone === k ? "on" : "", onclick: () => { invZone = k; draw(); } }, l))),
      el("div", { class: "btns" }, btn("⟳ Relire l'aperçu", () => { invData = null; draw(); }, "small")),
      hint("L'inventaire est celui de la page affichée dans l'aperçu : ouvrez-y une fiche, les Réglages ou une autre page, puis ⟳ Relire l'aperçu pour en lister les éléments.")),
    card("Éléments", count, list)];
};

window.BO_ADMIN.ctxHas = k => k === "style" && !!ctxStyle;
window.BO_ADMIN.onContext = (a, info, extra) => {
  const same = r => r.sel === info.one && (r.page || "") === (info.page || "");
  const rule = (c, make) => { let r = (c.rules || []).find(same); if (!r && make) { r = { id: uid(), sel: info.one, page: info.page, label: info.desc, css: {} }; (c.rules ||= []).push(r); } return r; };
  const clip = t => { if (!t) return toast("Rien à copier ici."); (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(() => toast("Copié : " + t.slice(0, 60)), () => prompt("Copiez ce texte :", t)); };
  if (a === "edit") { if (mode !== "pick") setMode("pick"); return; }
  if (a === "hide") { change(c => { rule(c, true).hide = true; }); return toast("Masqué : " + info.desc + " — « Montrer ce qui est masqué » (au-dessus de l'aperçu) le retrouve."); }
  if (a === "copystyle") {
    const r = (cfg.rules || []).find(same);
    ctxStyle = r && Object.keys(r.css || {}).length ? clone(r.css) : Object.fromEntries(CTX_STYLE.map(k => [k, info.css[k]]).filter(([k, v]) => v != null && v !== "" && !(k === "border-width" && parseFloat(v) === 0)));
    if (!ctxStyle["border-width"]) delete ctxStyle["border-color"];
    return toast("Style copié : clic droit sur un autre élément → « Coller le style ».");
  }
  if (a === "pastestyle") { if (!ctxStyle) return; change(c => { const r = rule(c, true); r.css = { ...(r.css || {}), ...clone(ctxStyle) }; if (r.css["border-width"]) r.css["border-style"] = "solid"; }); return toast("Style collé sur : " + info.desc); }
  if (a === "copytext") return clip((extra && extra.text) || info.textNow || "");
  if (a === "copysel") return clip(info.one);
  if (a === "cut") return toast("Coupé : clic droit sur un autre élément → « Coller avant » ou « Coller après ».");
  if (a === "reset") {
    const before = JSON.stringify(cfg);
    change(c => { for (const k of ["rules", "texts", "adds", "moves"]) if (c[k]) c[k] = c[k].filter(r => !((r.sel === info.one || r.sel === info.sim) && (!r.page || r.page === info.page))); });
    return toast(JSON.stringify(cfg) === before ? "Aucune modification sur cet élément." : "Modifications de cet élément annulées (↶ les remet).");
  }
};

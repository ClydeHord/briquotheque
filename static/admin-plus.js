/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
/* Briquothèque — BACK OFFICE : rubriques avancées et outils du serveur (chargé après admin.js).
   Tout ce qui suit s'appuie sur admin.js (el, btn, card, change, modal, VIEW, PANELS…) :
     - personnalisation avancée (réglages « cfg », brouillon puis « Publier ») : calculs et variables, règles « si… alors »,
       tuiles, vues / tris / filtres, éléments déplacés à la souris — appliqués sur le site par /bo-plus.js ;
     - outils du serveur (/api/bo/x/…, voir backoffice_outils.py — effet immédiat, pas de brouillon) : corrections du catalogue,
       tableur, sauvegardes, état et journal, fichiers de données, paramètres, code de l'application.
   L'interrupteur « Fonctions avancées » (en haut) montre ou cache les rubriques marquées « avancé ».
   La session du back office (son mot de passe) ouvre tous les outils ; les plus sensibles ne répondent que depuis le réseau local. */
(() => {
"use strict";
const ls = (k, v) => { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch {} return null; };
let expertUI = ls("bo-expert") === "1";
const P = () => { try { return BOF()?.plus || null; } catch { return null; } };   // moteur des fonctions avancées, dans l'aperçu
const needPreview = () => note("L'aperçu doit afficher <b>le site (connecté)</b> pour lister vos variables et essayer vos formules : choisissez « Le site (connecté) » au-dessus de l'aperçu.", "warn");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const sz = n => n >= 1e9 ? (n / 1e9).toFixed(1).replace(".", ",") + " Go" : n >= 1e6 ? (n / 1e6).toFixed(1).replace(".", ",") + " Mo" : Math.max(1, Math.round(n / 1e3)) + " Ko";
const dt = t => t ? new Date(t * 1000).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" }) : "—";
const xbtn = (title, onclick) => el("button", { type: "button", class: "x", title, onclick }, "✕");

/* ------------------------------------------------------------------ rubriques ajoutées (dernier élément : 1 = « fonctions avancées ») */
const NEW = [
  ["calculs", "🧮", "Calculs et variables", "Des champs calculés par une formule (plus-value, prix par pièce…) et vos propres variables.", 1],
  ["regles", "⚡", "Règles « si… alors »", "Si une fiche remplit une condition : étiquette, pastille, couleur de carte, message, bloc masqué.", 1],
  ["tuiles", "📊", "Tuiles et totaux", "Vos propres totaux, à côté de Sets / Figurines / Pièces.", 1],
  ["vues", "🔎", "Vues, tris et filtres", "Des listes filtrées prêtes à ouvrir depuis le menu, vos propres tris et filtres.", 1],
  ["catalogue", "📚", "Corrections du catalogue", "Corriger un nom, un thème, une année, une image ou un prix venus du catalogue.", 1],
  ["tableur", "📑", "Tableur (CSV)", "Exporter vos fiches vers un tableur ; remplir vos champs en masse depuis un tableur.", 1],
  ["sauvegardes", "💾", "Sauvegardes", "Sauvegarder, télécharger, restaurer la collection ; tout emporter dans un .zip.", 0],
  ["serveur", "🩺", "État et journal", "Santé du serveur, place disponible, journal, redémarrage.", 0],
  ["fichiers", "🗂️", "Fichiers de données", "Voir et corriger n'importe quelle donnée enregistrée, ligne par ligne.", 1],
  ["parametres", "🎛️", "Paramètres du serveur", "Durées, quotas, tailles ; port, proxy, démonstration.", 1],
  ["code", "🧾", "Code de l'application", "Modifier les fichiers du programme, avec vérification et retour arrière.", 1],
];
for (const p of NEW) PANELS.push(p);
const isX = id => !!NEW.find(p => p[0] === id)?.[4];
const WIDE = ["fichiers", "code", "serveur", "sauvegardes", "parametres", "tableur", "catalogue"];   // rubriques en pleine largeur (sans l'aperçu)
const GROUPS = [[null, ["accueil", "souris"]], ["Personnaliser", ["apparence", "textes", "fiches", "champs", "liens", "cartes", "menu"]], ["Avancé", ["calculs", "regles", "tuiles", "vues"]],
  ["Données", ["donnees", "catalogue", "tableur"]], ["Suivi", ["modifs", "historique"]], ["Serveur", ["sauvegardes", "serveur", "fichiers", "parametres", "code"]]];
buildNav = function () {   // menu en groupes ; les rubriques avancées n'apparaissent que si l'interrupteur est allumé
  const nav = $("#nav"); nav.replaceChildren();
  for (const [title, ids] of GROUPS) {
    const vis = ids.filter(id => !isX(id) || expertUI);
    if (!vis.length) continue;
    nav.append(title ? el("div", { class: "gt" }, title) : "");
    for (const id of vis) { const [, ic, nm] = PANELS.find(p => p[0] === id);
      nav.append(el("button", { type: "button", "data-p": id, onclick: () => show(id) }, el("span", { class: "ic" }, ic), el("span", {}, nm), id === "modifs" ? el("span", { class: "ct", hidden: true }) : null)); }
  }
};
const LISTS = ["moves", "vars", "calcs", "auto", "tiles", "sorts", "filters", "views"];   // réglages ajoutés par ce fichier
const prune0 = prune, count0 = countAll, draw0 = draw;
prune = function (c) { prune0(c); for (const k of LISTS) if (c[k] && !c[k].length) delete c[k]; };
countAll = function () { return count0() + LISTS.reduce((n, k) => n + (cfg[k] || []).length, 0); };
draw = function () { draw0(); $(".main").classList.toggle("wide", WIDE.includes(panel)); };

/* ------------------------------------------------------------------ serveur : appels, mode expert, données des rubriques */
async function askExpert() {
  const inp = el("input", { type: "password", placeholder: "Votre mot de passe", autocomplete: "current-password", onkeydown: e => { if (e.key === "Enter") inp.closest(".modal").querySelector(".primary").click(); } });
  const pw = await modal("🔐 Mode expert", [para("Cette partie touche directement au serveur. Par sécurité, redonnez votre mot de passe (valable 2 heures)."), fld("Mot de passe", inp)], { ok: "Continuer", value: () => inp.value });
  if (!pw) return false;
  try { await api("/api/bo/x/expert", { password: pw }); return true; } catch (e) { toast(e.message); return false; }
}
async function xapi(name, body, raw) {   // GET si body est absent ; raw : corps binaire (fichier)
  const opt = body === undefined ? {} : raw ? { method: "POST", body } : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  for (let k = 0; k < 2; k++) {
    const r = await fetch("/api/bo/x/" + name, opt);
    if (r.status === 401) { location.href = "/backoffice"; throw new Error("Connexion au back office requise"); }
    const d = await r.json().catch(() => ({}));
    if (r.ok) return d;
    if (d.besoin === "expert" && k === 0 && await askExpert()) continue;
    throw new Error(d.erreur || "Erreur " + r.status);
  }
}
const X = {};   // données du serveur, par rubrique (chargées une fois ; reload les redemande)
function got(key, name) {
  if (X[key] === undefined) { X[key] = null; xapi(name).then(v => { X[key] = v; draw(); }).catch(e => { X[key] = { erreur: e.message }; draw(); }); }
  return X[key];
}
const reload = (...keys) => { for (const k of keys) delete X[k]; draw(); };
const wait = (d, key) => !d ? el("p", { class: "hint" }, "Chargement…") : d.erreur ? el("div", {}, note("⚠ " + esc(d.erreur), "warn"), btn("Réessayer", () => reload(key))) : null;
const act = async (f, okMsg) => { try { const r = await f(); if (okMsg) toast(okMsg); return r; } catch (e) { toast(e.message); return null; } };
const pvReload = () => { try { FW().location.reload(); } catch {} };
async function waitBack() {   // le serveur redémarre : on attend son retour
  toast("Le serveur redémarre…");
  await new Promise(r => setTimeout(r, 2500));
  for (let k = 0; k < 40; k++) { try { const r = await fetch("/api/ping", { cache: "no-store" }); if (r.ok) { toast("✔ Le serveur est revenu."); for (const key of Object.keys(X)) delete X[key]; pvReload(); draw(); return true; } } catch {} await new Promise(r => setTimeout(r, 1500)); }
  toast("Le serveur ne répond pas encore : patientez, puis rechargez la page (au besoin : /backoffice/secours).");
  return false;
}
const restart = async () => { if (!await sure("Redémarrer le serveur ?", "Le site sera indisponible une dizaine de secondes.", "Redémarrer")) return; if (await act(() => xapi("restart", {}))) waitBack(); };
const pickFile = (accept, done) => { const i = el("input", { type: "file", accept, onchange: () => { if (i.files[0]) done(i.files[0]); } }); i.click(); };

/* ------------------------------------------------------------------ outils d'écriture des réglages */
const upd = (list, id, fn, o) => change(c => { const x = (c[list] || []).find(x => x.id === id); if (x) fn(x); }, o);
const del = (list, id) => change(c => { c[list] = (c[list] || []).filter(x => x.id !== id); });
const add = (list, obj) => change(c => { (c[list] ||= []).push({ id: uid(), ...obj }); });
const typing = (list, o, k, pre = "") => v => upd(list, o.id, x => { x[k] = v; }, { key: pre + list + o.id + k, redraw: false });
const opt = (list, o, k) => v => upd(list, o.id, x => { if (v === "" || v == null || v === false) delete x[k]; else x[k] = v; });
const condSet = (list, id) => (fn, rd) => upd(list, id, x => { x.cond ||= {}; fn(x.cond); }, { key: list + id + "cond", redraw: !!rd });
const condGet = (list, id) => () => (cfg[list] || []).find(x => x.id === id)?.cond;
const typesRow = (list, o) => fld("Sur quelles fiches ?", el("div", { class: "checks" }, KINDS.map(([k, n]) => chk(n, (o.types || []).includes(k),
  v => upd(list, o.id, x => { x.types = v ? [...(x.types || []), k] : (x.types || []).filter(t => t !== k); if (!x.types.length) delete x.types; })))), (o.types || []).length ? "" : "Rien de coché = toutes les fiches.");
const foot = (list, o, info) => el("div", { class: "ed-foot" }, el("span", { class: "hint" }, info || (o.off ? "En pause : n'agit plus, sans être supprimé." : "")),
  btn(o.off ? "▶ Réactiver" : "⏸ Pause", () => upd(list, o.id, x => { if (x.off) delete x.off; else x.off = true; }), "small"), btn("Supprimer", () => del(list, o.id), "small danger"));
const colorIn = (v, on) => el("input", { type: "color", value: /^#[0-9a-f]{6}$/i.test(v || "") ? v : "#2563eb", oninput: e => on(e.target.value), title: "Couleur" });
const BUILTIN = ["numero", "nom", "type", "liste", "quantite", "valeur", "valeur_unitaire", "prix_achat", "prix_neuf", "prix_occasion", "prix_magasin", "annee", "theme", "pieces", "figurines", "etat", "boite", "plan",
  "a_construire", "retire", "souhait", "modifie", "taches", "notes", "date_ajout", "date_modif"];
function freeId(label) {   // identifiant de variable, unique parmi tout ce qui existe déjà
  const taken = new Set([...BUILTIN, ...["fields", "calcs", "vars"].flatMap(k => (cfg[k] || []).map(x => x.id))]), base = slug(label) || "valeur";
  let id = base; for (let n = 2; taken.has(id); n++) id = base.slice(0, 21) + "_" + n;
  return id;
}

/* ------------------------------------------------------------------ zone de formule et éditeur de condition */
const FMT = [["", "Automatique"], ["euros", "Prix (12,50 €)"], ["nombre", "Nombre"], ["entier", "Nombre entier"], ["pourcent", "Pourcentage"], ["date", "Date"], ["ouinon", "Oui / Non"], ["etoiles", "Étoiles"], ["texte", "Texte"]];
function fxBox(value, on, fmt, ph) {   // saisie d'une formule, boutons « variable » / « fonction », résultat en direct sur une fiche d'exemple
  const out = el("div", { class: "fx-out" });
  const ta = el("textarea", { rows: 2, class: "fx", spellcheck: false, placeholder: ph || "ex. : {valeur} - {prix_achat}", value: value || "", oninput: () => { on(ta.value); res(); } });
  const res = () => { const p = P(), v = ta.value.trim();
    if (!v) { out.textContent = ""; out.className = "fx-out"; return; }
    if (!p) { out.textContent = "(aperçu indisponible : résultat non calculé)"; out.className = "fx-out"; return; }
    const r = p.try(v, typeof fmt === "function" ? fmt() : fmt);
    out.className = "fx-out " + (r.ok ? "ok" : "bad");
    out.textContent = r.ok ? `= ${r.text}   (sur « ${r.on} »)` : "⚠ " + r.error; };
  const ins = (s, back = 0) => { const a = ta.selectionStart ?? ta.value.length, b = ta.selectionEnd ?? a; ta.value = ta.value.slice(0, a) + s + ta.value.slice(b); ta.focus(); ta.selectionStart = ta.selectionEnd = a + s.length - back; on(ta.value); res(); };
  const pickVar = async () => { const p = P(); if (!p) return toast("L'aperçu doit afficher le site.");
    const v = await choose("Insérer une variable", p.vars().map(v => ({ v: v.id, label: v.label, sub: v.group + " · {" + v.id + "}" }))); if (v) ins("{" + v + "}"); };
  const pickFn = async () => { const p = P(); if (!p) return toast("L'aperçu doit afficher le site.");
    const v = await choose("Insérer une fonction", p.fns().map(f => ({ v: f.sig, label: f.sig, sub: f.doc }))); if (v) ins(v.replace(/\(.*$/, "") + "()", 1); };
  setTimeout(res, 0);
  return el("div", { class: "fxb" }, ta, el("div", { class: "btns" }, btn("+ Variable", pickVar, "small", "Choisir une information de la fiche, un de vos champs, un de vos calculs"), btn("ƒ Fonction", pickFn, "small", "si, arrondi, min, max, jours_depuis…"),
    ["+", "-", "*", "/", "&", "(", ")"].map(o => btn(o, () => ins(o === "(" || o === ")" ? o : " " + o + " "), "small", o === "&" ? "Coller deux textes bout à bout" : ""))), out);
}
const OPS = [["=", "est égal à"], ["<>", "est différent de"], [">", "est plus grand que"], ["<", "est plus petit que"], [">=", "est au moins"], ["<=", "est au plus"], ["contient", "contient"], ["sans", "ne contient pas"],
  ["rempli", "est rempli"], ["vide", "est vide"], ["vrai", "est « oui »"], ["faux", "est « non »"]];
const NOVAL = ["rempli", "vide", "vrai", "faux"];
function condBox(get, set) {   // get() → la condition ; set(fn, redessiner) la modifie dans les réglages
  const c = get() || {}, p = P(), vars = p ? p.vars() : [];
  const cnt = el("div", { class: "hint" });
  const count = () => { const pp = P(); if (!pp) return; const r = pp.count(get() || null); cnt.textContent = r ? `→ ${r.n} fiche${r.n > 1 ? "s" : ""} sur ${r.total} ${r.n > 1 ? "remplissent" : "remplit"} cette condition` : ""; };
  setTimeout(count, 0);
  if (c.expr != null) return el("div", { class: "cond" }, fxBox(c.expr, v => { set(x => { x.expr = v; }, false); count(); }, "ouinon", "ex. : {valeur} > 100 et {retire}"),
    line(cnt, el("span", { class: "grow" }), btn("← Conditions simples", () => set(x => { delete x.expr; }, true), "small")));
  const rows = c.rows || [];
  return el("div", { class: "cond" },
    rows.length > 1 && line(el("span", { class: "hint" }, "La fiche doit remplir"), sel(c.mode || "all", [["all", "toutes les conditions"], ["any", "au moins une condition"]], v => set(x => { x.mode = v; }, true))),
    rows.map((r, i) => el("div", { class: "crow" },
      sel(r.v || "", [["", "— choisir —"], ...vars.map(v => [v.id, v.label]), ...(r.v && !vars.some(v => v.id === r.v) ? [[r.v, r.v]] : [])], v => set(x => { x.rows[i].v = v; }, true)),
      sel(r.op || "=", OPS, v => set(x => { x.rows[i].op = v; }, true)),
      NOVAL.includes(r.op) ? el("span", {}) : txt(r.val, v => { set(x => { x.rows[i].val = v; }, false); count(); }, "valeur"),
      xbtn("Retirer cette condition", () => set(x => { x.rows.splice(i, 1); }, true)))),
    line(btn("+ Condition", () => set(x => { (x.rows ||= []).push({ v: "", op: "=", val: "" }); }, true), "small"),
      btn("ƒ Formule", () => set(x => { x.expr = ""; }, true), "small", "Écrire la condition comme une formule (pour les cas compliqués)"), el("span", { class: "grow" })),
    rows.some(r => r.v) ? cnt : el("div", { class: "hint" }, "Sans condition : toutes les fiches."));
}
const helpCard = () => { const p = P(); return el("details", { class: "card help" }, el("summary", {}, "Aide-mémoire : écrire une formule"),
  para("Une <b>variable</b> s'écrit entre accolades : <code>{valeur}</code>. Un <b>texte</b>, entre guillemets : <code>\"Neuf\"</code>. Les nombres s'écrivent <code>12,5</code> ou <code>12.5</code>.<br>" +
    "Calculs : <code>+ - * /</code> ; comparaisons : <code>= &lt;&gt; &gt; &lt; &gt;= &lt;=</code> ; logique : <code>et</code>, <code>ou</code>, <code>non</code> ; coller des textes : <code>&amp;</code>.<br>" +
    "Dans une fonction, les valeurs se séparent par <code>;</code>. Une valeur vide donne un résultat vide : <code>sivide({prix_achat} ; 0)</code> la compte pour 0."),
  p ? [el("h3", {}, "Variables"), el("dl", {}, p.vars().map(v => [el("dt", {}, "{" + v.id + "}"), el("dd", {}, v.label + " — " + v.group)])),
    el("h3", {}, "Fonctions"), el("dl", {}, p.fns().map(f => [el("dt", {}, f.sig), el("dd", {}, f.doc)]))] : hint("La liste des variables et des fonctions s'affiche quand l'aperçu montre le site.")); };

/* ------------------------------------------------------------------ Calculs et variables */
const CALC_PRESETS = [["Plus-value", "{valeur} - {prix_achat}", "euros"], ["Plus-value en %", "pourcent({valeur} - {prix_achat} ; {prix_achat})", "pourcent"], ["Prix par pièce", "{valeur} / {pieces}", "euros"],
  ["Âge du set", "annee(aujourdhui()) - {annee}", "entier"], ["Jours depuis l'ajout", "jours_depuis({date_ajout})", "entier"]];
const newCalc = (label = "", expr = "", fmt = "") => change(c => { (c.calcs ||= []).push({ id: freeId(label || "calcul"), label: label || "Nouveau calcul", expr, ...(fmt ? { fmt } : {}) }); });
VIEW.calculs = () => {
  const secs = [["", secName("_")], ...(cfg.secs || []).map(s => [s.id, s.label])];
  return [head("Calculs et variables", "Un champ calculé affiche le résultat d'une formule sur chaque fiche (et sur les cartes, si vous voulez). Il se recalcule tout seul ; rien n'est enregistré dans vos données."),
    P() ? null : needPreview(),
    (cfg.calcs || []).map(f => el("div", { class: "ed" + (f.off ? " offed" : "") },
      fld("Nom affiché", txt(f.label, typing("calcs", f, "label"), "ex. : Plus-value"), `Pour l'utiliser dans une autre formule : <code>{${f.id}}</code>`),
      fld("Formule", fxBox(f.expr, typing("calcs", f, "expr"), () => (cfg.calcs || []).find(x => x.id === f.id)?.fmt)),
      el("div", { class: "cols" }, fld("Affiché comme", sel(f.fmt || "", FMT, opt("calcs", f, "fmt"))), fld("Dans le bloc", sel(f.sec || "", secs, opt("calcs", f, "sec")))),
      chk("Afficher aussi sur les cartes des listes", f.card, opt("calcs", f, "card")),
      typesRow("calcs", f), foot("calcs", f))),
    card((cfg.calcs || []).length ? "" : "Ajouter un calcul", el("div", { class: "btns" }, btn("+ Nouveau calcul", () => newCalc(), "primary"), CALC_PRESETS.map(([n, e, f]) => btn(n, () => newCalc(n, e, f), "small", e))),
      hint("Les boutons de droite sont des exemples tout prêts. Le calcul apparaît sur la fiche, dans le bloc « " + esc(secName("_")) + " » (ou celui choisi).")),
    card("Mes variables", para("Une valeur que vous fixez une fois et réutilisez dans vos formules : un taux, un seuil, un budget…"),
      (cfg.vars || []).map(v => el("div", { class: "crow v" }, txt(v.label, typing("vars", v, "label"), "Nom"), el("code", {}, "{" + v.id + "}"), txt(v.value, typing("vars", v, "value"), "Valeur"), xbtn("Supprimer", () => del("vars", v.id)))),
      btn("+ Nouvelle variable", async () => { const n = await ask("Nouvelle variable", "", "Son nom", { ph: "ex. : Taux de revente" }); if (n) change(c => { (c.vars ||= []).push({ id: freeId(n), label: n, value: "" }); }); })),
    helpCard()];
};

/* ------------------------------------------------------------------ Règles « si… alors » */
const ACTS = [["tag", "Étiquette sous le nom (carte)"], ["badge", "Pastille sur la photo (carte)"], ["card", "Couleur de la carte"], ["msg", "Message en haut de la fiche"], ["hide", "Masquer un bloc de la fiche"]];
const blockOpts = () => [...Object.entries(BLOCKS), ["x-_", "Bloc « " + secName("_") + " »"], ...(cfg.secs || []).map(s => ["x-" + s.id, "Bloc « " + s.label + " »"])];
function actEd(r, a, i) {
  const set = (fn, rd) => upd("auto", r.id, x => fn(x.acts[i]), { key: "act" + r.id + i, redraw: !!rd });
  return el("div", { class: "act" }, sel(a.k, ACTS, v => set(x => { x.k = v; }, true)),
    ["tag", "badge", "msg"].includes(a.k) ? [txt(a.text, v => set(x => { x.text = v; }), a.k === "msg" ? "Texte du message ({variables} possibles)" : "Texte — ex. : 💎 Précieux"), colorIn(a.color, v => set(x => { x.color = v; }))] : null,
    a.k === "card" ? [el("span", { class: "hint" }, "fond"), colorIn(a.bg, v => set(x => { x.bg = v; })), el("span", { class: "hint" }, "bordure"), colorIn(a.border, v => set(x => { x.border = v; })), el("span", { class: "grow" })] : null,
    a.k === "hide" ? sel(a.block || "", [["", "— quel bloc ? —"], ...blockOpts()], v => set(x => { x.block = v; }, true)) : null,
    xbtn("Retirer cette action", () => upd("auto", r.id, x => { x.acts.splice(i, 1); })));
}
const RULE_PRESETS = [
  ["💎 Valeur de plus de 100 €", { label: "Fiches précieuses", cond: { rows: [{ v: "valeur", op: ">", val: "100" }] }, acts: [{ k: "tag", text: "💎 Précieux", color: "#7c3aed" }] }],
  ["⚠ Prix d'achat manquant", { label: "Prix d'achat à remplir", cond: { rows: [{ v: "prix_achat", op: "vide", val: "" }] }, acts: [{ k: "msg", text: "Prix d'achat non renseigné pour {nom}.", color: "#f59e0b" }] }],
  ["🟢 Bonne affaire (+50 %)", { label: "Bonnes affaires", cond: { expr: "{valeur} > {prix_achat} * 1,5" }, acts: [{ k: "badge", text: "+50 %", color: "#15803d" }] }],
];
VIEW.regles = () => [head("Règles « si… alors »", "Quand une fiche remplit une condition, le site réagit : une étiquette ou une pastille sur sa carte, une couleur, un message sur sa fiche, un bloc masqué."),
  P() ? null : needPreview(),
  (cfg.auto || []).map(r => el("div", { class: "ed" + (r.off ? " offed" : "") },
    fld("Nom de la règle", txt(r.label, typing("auto", r, "label"), "ex. : Sets précieux")),
    el("div", { class: "fl" }, "SI LA FICHE…"), condBox(condGet("auto", r.id), condSet("auto", r.id)),
    el("div", { class: "fl" }, "ALORS…"), (r.acts || []).map((a, i) => actEd(r, a, i)),
    btn("+ Action", () => upd("auto", r.id, x => { (x.acts ||= []).push({ k: "tag", text: "", color: "#2563eb" }); }), "small"),
    el("div", { style: "height:8px" }), typesRow("auto", r), foot("auto", r))),
  card((cfg.auto || []).length ? "" : "Ajouter une règle", el("div", { class: "btns" }, btn("+ Nouvelle règle", () => add("auto", { label: "", cond: { rows: [{ v: "", op: "=", val: "" }] }, acts: [{ k: "tag", text: "", color: "#2563eb" }] }), "primary"),
    RULE_PRESETS.map(([n, o]) => btn(n, () => add("auto", clone(o)), "small"))),
    hint("Les règles ne changent jamais vos données : seulement ce qui s'affiche. Dans un texte, <code>{nom}</code>, <code>{valeur}</code>… sont remplacés par ceux de la fiche.")),
];

/* ------------------------------------------------------------------ Tuiles et totaux */
const AGG = [["sum", "Somme"], ["avg", "Moyenne"], ["count", "Nombre de fiches"], ["min", "Plus petite valeur"], ["max", "Plus grande valeur"]];
const TILE_PRESETS = [["Total payé", { label: "Total payé", agg: "sum", expr: "{prix_achat}", fmt: "euros" }], ["Plus-value", { label: "Plus-value", agg: "sum", expr: "{valeur} - {prix_achat}", fmt: "euros" }],
  ["Sets retirés", { label: "Retirés de la vente", agg: "count", cond: { rows: [{ v: "retire", op: "vrai", val: "" }] } }], ["Valeur moyenne", { label: "Valeur moyenne", agg: "avg", expr: "{valeur}", fmt: "euros" }]];
VIEW.tuiles = () => [head("Tuiles et totaux", "Vos propres chiffres, à côté de « Sets / Figurines / Pièces ». Ils se calculent sur la liste affichée."),
  P() ? null : needPreview(),
  (cfg.tiles || []).map(t => el("div", { class: "ed" + (t.off ? " offed" : "") },
    el("div", { class: "cols" }, fld("Titre de la tuile", txt(t.label, typing("tiles", t, "label"), "ex. : Total payé")), fld("Calcul", sel(t.agg || "sum", AGG, v => upd("tiles", t.id, x => { x.agg = v; })))),
    fld(t.agg === "count" ? "De quoi ? (laissez vide pour compter les fiches)" : "De quoi ?", fxBox(t.expr, typing("tiles", t, "expr"), () => (cfg.tiles || []).find(x => x.id === t.id)?.fmt, "ex. : {prix_achat}")),
    fld("Affiché comme", sel(t.fmt || "", FMT, opt("tiles", t, "fmt"))),
    el("div", { class: "fl" }, "SEULEMENT LES FICHES QUI… (facultatif)"), condBox(condGet("tiles", t.id), condSet("tiles", t.id)),
    foot("tiles", t))),
  card((cfg.tiles || []).length ? "" : "Ajouter une tuile", el("div", { class: "btns" }, btn("+ Nouvelle tuile", () => add("tiles", { label: "", agg: "sum", expr: "" }), "primary"), TILE_PRESETS.map(([n, o]) => btn(n, () => add("tiles", clone(o)), "small")))),
];

/* ------------------------------------------------------------------ Vues, tris et filtres */
const SORTS = [["", "(ne pas changer le tri)"], ["modified", "Dernière modification"], ["added", "Ajout récent"], ["added_old", "Ajout le plus ancien"], ["value", "Valeur décroissante"], ["variation", "Variation de prix (%)"], ["ecart", "Variation de prix (€)"], ["name", "Nom (A → Z)"], ["number", "Numéro"],
  ["year", "Année"], ["qty", "Nombre d'exemplaires"], ["pieces", "Nombre de pièces"], ["figs", "Nombre de figurines"], ["theme", "Thème"]];
VIEW.vues = () => {
  let lists = []; try { lists = (BOF()?.lists() || []).filter(l => l.kind === "collection"); } catch {}
  const sortOpts = [...SORTS, ...(cfg.sorts || []).map(s => ["bo:" + s.id, "★ " + (s.label || "tri")])];
  return [head("Vues, tris et filtres", "Une vue est une liste filtrée, prête à ouvrir d'un clic depuis le menu. Vos tris s'ajoutent à la liste « Trier par » ; vos filtres, au menu « ⚙️ Filtres »."),
    P() ? null : needPreview(),
    el("h3", {}, "Vues enregistrées"),
    (cfg.views || []).map(v => el("div", { class: "ed" },
      fld("Nom de la vue", txt(v.label, typing("views", v, "label"), "ex. : Sets à plus de 100 €")),
      el("div", { class: "cols" }, fld("Dans la liste", sel(v.list || "", [["", "Toute la collection"], ...lists.map(l => [l.id, l.name])], opt("views", v, "list"))),
        fld("Afficher", sel(v.view || "", [["", "Sets et figurines"], ["sets", "Les sets"], ["figs", "Les figurines"]], opt("views", v, "view")))),
      el("div", { class: "fl" }, "SEULEMENT LES FICHES QUI…"), condBox(condGet("views", v.id), condSet("views", v.id)),
      fld("Triées par", sel(v.sort || "", sortOpts, opt("views", v, "sort"))),
      chk("Afficher cette vue dans le menu latéral", v.menu !== false, x => upd("views", v.id, o => { if (x) delete o.menu; else o.menu = false; })),
      el("div", { class: "ed-foot" }, el("span", { class: "hint" }, ""), btn("Ouvrir dans l'aperçu", () => { try { P().openView(v.id); } catch { toast("L'aperçu doit afficher le site."); } }, "small"), btn("Supprimer", () => del("views", v.id), "small danger")))),
    btn("+ Nouvelle vue", () => add("views", { label: "", cond: { rows: [{ v: "", op: "=", val: "" }] } }), "primary"),
    el("h3", { style: "margin-top:22px" }, "Mes tris"),
    (cfg.sorts || []).map(s => el("div", { class: "ed" },
      el("div", { class: "cols" }, fld("Nom du tri", txt(s.label, typing("sorts", s, "label"), "ex. : Plus-value")), fld("Ordre", sel(s.dir || "desc", [["desc", "Du plus grand au plus petit"], ["asc", "Du plus petit au plus grand"]], v => upd("sorts", s.id, x => { x.dir = v; })))),
      fld("Trier selon", fxBox(s.expr, typing("sorts", s, "expr"), "", "ex. : {valeur} - {prix_achat}")),
      el("div", { class: "ed-foot" }, el("span", { class: "hint" }, "Les fiches sans valeur vont à la fin."), btn("Supprimer", () => del("sorts", s.id), "small danger")))),
    btn("+ Nouveau tri", () => add("sorts", { label: "", expr: "", dir: "desc" })),
    el("h3", { style: "margin-top:22px" }, "Mes filtres"),
    (cfg.filters || []).map(f => el("div", { class: "ed" },
      fld("Nom du filtre", txt(f.label, typing("filters", f, "label"), "ex. : Avec boîte")),
      condBox(condGet("filters", f.id), condSet("filters", f.id)),
      el("div", { class: "ed-foot" }, el("span", { class: "hint" }, "Une case de plus dans « ⚙️ Filtres »."), btn("Supprimer", () => del("filters", f.id), "small danger")))),
    btn("+ Nouveau filtre", () => add("filters", { label: "", cond: { rows: [{ v: "", op: "=", val: "" }] } }))];
};

/* ------------------------------------------------------------------ Modifier à la souris : mode « déplacer » */
const movesCard = () => (cfg.moves || []).length ? card("Éléments déplacés", el("div", { class: "rowset" }, cfg.moves.map(m => line(
    el("span", { class: "lab" }, el("b", {}, m.label || "Élément"), el("div", { class: "hint" }, (m.pos === "before" ? "posé avant " : "posé après ") + (m.toLabel || "un autre élément") + " — sur " + (PAGES[m.page || ""] || ""))),
    btn("Voir", () => flash(`bo-mv[data-bo-mv="${m.id}"] > *`, m.page), "small"), xbtn("Remettre à sa place d'origine", () => change(c => { c.moves = c.moves.filter(x => x.id !== m.id); }))))),
  el("div", { style: "height:8px" }), btn("↺ Tout remettre à sa place", () => change(c => { delete c.moves; }), "small danger")) : null;
const souris0 = VIEW.souris;
VIEW.souris = () => mode === "move" ? [head("Déplacer à la souris", "Attrapez n'importe quel élément dans l'aperçu et déposez-le ailleurs : avant ou après un autre élément."),
  card("Mode d'emploi", el("ol", { class: "steps" },
    el("li", { html: "Allez d'abord à l'endroit voulu avec « 👆 Utiliser le site » (ouvrir une fiche, le menu…)." }),
    el("li", { html: "Revenez sur « ✋ Déplacer », puis <b>cliquez-glissez</b> l'élément : une <b>barre verte</b> montre où il se posera. Lâchez." }),
    el("li", { html: "Les blocs d'une fiche et les entrées du menu changent d'<b>ordre</b> ; tout le reste est <b>déplacé</b> là où vous le posez, même dans une autre zone." })),
    hint("Un déplacement raté ? « ↶ Annuler », en haut. Les éléments que le site redessine sans cesse (cartes, tuiles) se règlent mieux dans « Cartes » et « Tuiles ».")),
  movesCard()] : [souris0(), movesCard()];
window.BO_ADMIN.onMove = info => {
  const b = BOF(); if (!b) return;
  if (info.src.sheetKey && info.dst.sheetKey && SHEETS.some(s => s[0] === info.sheet)) {   // blocs d'une fiche : c'est le squelette de ce type de fiche qui change
    shType = info.sheet;
    const ord = sheetKeys(b.sheetInfo()).filter(k => k !== info.src.sheetKey), i = ord.indexOf(info.dst.sheetKey);
    if (i < 0) return;
    ord.splice(info.pos === "before" ? i : i + 1, 0, info.src.sheetKey);
    change(c => { shConf(c).order = ord; });
    return toast("Bloc déplacé : ordre de la fiche « " + sheetName(shType) + " » (rubrique « Fiches »).");
  }
  if (info.src.menuKey && info.dst.menuKey) {   // entrées du menu : c'est l'ordre du menu qui change
    const ord = [...(cfg.menu?.order || [])];
    for (const x of b.menuInfo() || []) if (!ord.includes(x.key)) ord.push(x.key);
    const rest = ord.filter(k => k !== info.src.menuKey), i = rest.indexOf(info.dst.menuKey);
    if (i < 0) return;
    rest.splice(info.pos === "before" ? i : i + 1, 0, info.src.menuKey);
    change(c => { c.menu ||= {}; c.menu.order = rest; });
    return toast("Entrée du menu déplacée (rubrique « Menu »).");
  }
  change(c => { c.moves = (c.moves || []).filter(m => !(m.sel === info.src.one && (m.page || "") === (info.page || "")));
    c.moves.push({ id: uid(), sel: info.src.one, to: info.dst.one, pos: info.pos, page: info.page, label: info.src.desc, toLabel: info.dst.desc }); });
  toast("Déplacé : " + info.src.desc);
};
const ready0 = window.BO_ADMIN.onReady;
window.BO_ADMIN.onReady = function (...a) { ready0.apply(this, a); if (["calculs", "regles", "tuiles", "vues", "tableur"].includes(panel)) whenApp(() => draw()); };

/* ------------------------------------------------------------------ Corrections du catalogue (effet immédiat, côté serveur) */
let catQ = "", catHits = null;
const CATF = [["name", "Nom"], ["theme", "Thème"], ["subtheme", "Sous-thème"], ["year", "Année"], ["pieces", "Nombre de pièces"], ["image", "Image (adresse https://…)"], ["retail", "Prix magasin (€)"]];
const CATP = { set: [["new_value", "Cote neuf (€)"], ["used_value", "Cote occasion (€)"]], fig: [["value", "Cote neuf (€)"], ["used", "Cote occasion (€)"]] };
async function catEdit(key, base, cur) {   // base : ce que dit le catalogue ; cur : la correction déjà faite
  const fields = [...CATF, ...CATP[key.startsWith("fig:") ? "fig" : "set"]], inp = {};
  const ok = await modal("Corriger « " + (base?.name || cur?.label || key) + " »", [para("Remplissez seulement ce qui est faux : le reste continue de venir du catalogue. Videz une case pour retirer sa correction."),
    fields.map(([k, l]) => fld(l, inp[k] = el("input", { type: "text", value: cur?.[k] ?? "", placeholder: base?.[k] != null ? "catalogue : " + base[k] : "" })))], { ok: "Enregistrer", wide: true });
  if (!ok) return;
  const f = {}; for (const [k] of fields) if (inp[k].value.trim()) f[k] = inp[k].value.trim();
  const r = await act(() => xapi("fix", { key, fields: Object.keys(f).length ? f : null, label: base?.name || cur?.label || "" }), "✔ Correction enregistrée.");
  if (r) { X.fixes = { fixes: r.fixes }; pvReload(); draw(); }
}
VIEW.catalogue = () => {
  const d = got("fixes", "fixes"), w = wait(d, "fixes");
  const search = async () => { if (catQ.length < 2) return toast("Tapez au moins deux caractères."); const r = await act(() => xapi("catalog?q=" + encodeURIComponent(catQ))); if (r) { catHits = r.hits; draw(); } };
  return [head("Corrections du catalogue", "Le nom, le thème, l'année, l'image ou un prix d'un set ou d'une figurine sont faux ? Corrigez-les ici : votre correction passe par-dessus le catalogue, partout sur le site, et y reste même quand le catalogue est relu."),
    note("Ces corrections s'appliquent <b>tout de suite</b> (pas de brouillon ni de « Publier »)."),
    card("Chercher un set ou une figurine", line(el("input", { type: "search", value: catQ, placeholder: "Numéro ou nom…", oninput: e => { catQ = e.target.value.trim(); }, onkeydown: e => { if (e.key === "Enter") search(); } }), btn("Chercher", search, "primary")),
      catHits && (catHits.length ? el("div", { class: "pickl", style: "max-height:40vh;margin-top:8px" }, catHits.map(h => el("button", { type: "button", onclick: () => catEdit(h.key, h, d?.fixes?.[h.key]) }, h.name || h.key, el("small", {}, h.key.replace(/^fig:/, "figurine ")))))
        : el("p", { class: "hint" }, "Rien dans le catalogue du serveur pour cette recherche (seules les fiches déjà vues y sont)."))),
    card("Mes corrections", w || (Object.keys(d.fixes).length ? el("div", { class: "rowset" }, Object.entries(d.fixes).map(([k, f]) => line(
      el("span", { class: "lab" }, el("b", {}, f.label || k), el("div", { class: "hint" }, k.replace(/^fig:/, "figurine ") + " · " + Object.keys(f).filter(x => x !== "label").map(x => [...CATF, ...CATP.set, ...CATP.fig].find(c => c[0] === x)?.[1] || x).join(", "))),
      btn("Modifier", () => catEdit(k, null, f), "small"), xbtn("Retirer cette correction", async () => { const r = await act(() => xapi("fix", { key: k, fields: null })); if (r) { X.fixes = { fixes: r.fixes }; pvReload(); draw(); } }))))
      : el("p", { class: "hint" }, "Aucune correction pour l'instant.")))];
};

/* ------------------------------------------------------------------ Tableur (CSV) */
let csvCols = null;
const csvCell = v => { const s = typeof v === "number" ? String(v).replace(".", ",") : typeof v === "boolean" ? (v ? "oui" : "non") : String(v ?? ""); return /[;"\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
function csvParse(text) {   // texte CSV → lignes de cellules (séparateur ; ou , deviné sur la 1re ligne)
  text = text.replace(/^﻿/, "");
  const first = text.split(/\r?\n/, 1)[0], sep = (first.match(/;/g) || []).length >= (first.match(/,/g) || []).length ? ";" : ",";
  const rows = []; let row = [], cur = "", q = false;
  for (let i = 0; i < text.length; i++) { const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; }
    else if (c === '"') q = true; else if (c === sep) { row.push(cur); cur = ""; } else if (c === "\n") { row.push(cur); rows.push(row); row = []; cur = ""; } else if (c !== "\r") cur += c; }
  if (cur !== "" || row.length) { row.push(cur); rows.push(row); }
  return rows.filter(r => r.some(c => c.trim() !== ""));
}
const nrm = s => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
function csvValue(f, s) {   // cellule → valeur d'un champ personnalisé (selon son type)
  s = String(s ?? "").trim(); if (s === "") return "";
  if (["number", "money", "stars"].includes(f.type)) { const n = parseFloat(s.replace(/[\s€]/g, "").replace(",", ".")); return isNaN(n) ? "" : f.type === "stars" ? Math.max(0, Math.min(5, Math.round(n))) : n; }
  if (f.type === "check") return /^(oui|vrai|true|1|x)$/i.test(s);
  if (f.type === "multi") return s.split(/\s*,\s*/).filter(Boolean);
  if (f.type === "date") { const m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(s); return m ? `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}` : s; }
  return s;
}
VIEW.tableur = () => {
  const p = P(); if (!p) return [head("Tableur (CSV)", ""), needPreview()];
  const vars = p.vars(); csvCols ||= new Set(["numero", "nom", "type", "liste", "quantite", "valeur", "prix_achat", ...(cfg.fields || []).map(f => f.id), ...(cfg.calcs || []).map(f => f.id)]);
  const exp = () => { const t = p.table(vars.filter(v => csvCols.has(v.id)).map(v => v.id)); if (!t) return;
    const a = el("a", { href: URL.createObjectURL(new Blob(["﻿" + [t.head, ...t.rows].map(r => r.map(csvCell).join(";")).join("\r\n")], { type: "text/csv" })), download: "briquotheque-" + new Date().toISOString().slice(0, 10) + ".csv" });
    a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 5000); };
  const imp = file => file.text().then(async text => {
    const rows = csvParse(text), headR = rows.shift() || [], idc = headR.findIndex(h => nrm(h) === "id");
    if (idc < 0) return toast("Il faut une colonne « id » (celle de l'export) pour reconnaître les fiches.");
    const fs = (cfg.fields || []).filter(f => f.type !== "item" && f.type !== "list"), map = headR.map(h => fs.find(f => f.id === nrm(h) || nrm(f.label) === nrm(h)) || null);
    const used = map.filter(Boolean);
    if (!used.length) return toast("Aucune colonne ne porte le nom d'un de vos champs personnalisés.");
    const out = rows.map(r => ({ id: (r[idc] || "").trim(), x: Object.fromEntries(map.map((f, i) => f ? [f.id, csvValue(f, r[i])] : null).filter(Boolean)) })).filter(r => r.id);
    if (!await sure("Importer ces valeurs ?", `${out.length} ligne(s). Champs reconnus : <b>${used.map(f => esc(f.label)).join(", ")}</b>.<br>Une case vide efface la valeur du champ. Une sauvegarde de la collection est faite juste avant.`, "Importer")) return;
    const r = await act(() => xapi("values-bulk", { rows: out })); if (r) { toast(`✔ ${r.changed} fiche(s) mise(s) à jour.`); pvReload(); } });
  return [head("Tableur (CSV)", "Travaillez vos fiches dans un tableur (Excel, LibreOffice, Google Sheets) : exportez-les, puis réimportez vos champs personnalisés remplis en masse."),
    card("1. Exporter", para("Cochez les colonnes voulues. Le fichier s'ouvre directement dans un tableur."),
      el("div", { class: "checks" }, vars.map(v => chk(v.label, csvCols.has(v.id), on => { on ? csvCols.add(v.id) : csvCols.delete(v.id); }))),
      el("div", { style: "height:10px" }), btn("⬇ Exporter (.csv)", exp, "primary")),
    card("2. Importer des valeurs", para("Gardez la colonne <b>id</b> de l'export. Les colonnes qui portent le nom d'un de vos <b>champs personnalisés</b> sont importées ; les autres sont ignorées (le nom, la valeur… ne se modifient pas ici)."),
      btn("⬆ Importer un fichier .csv…", () => pickFile(".csv,text/csv", imp)),
      (cfg.fields || []).length ? null : hint("Vous n'avez pas encore de champ personnalisé : créez-en d'abord dans « Champs personnalisés »."))];
};

/* ------------------------------------------------------------------ Sauvegardes */
VIEW.sauvegardes = () => {
  const d = got("bk", "backups"), w = wait(d, "bk");
  const up = f => f.text().then(async t => { if (await act(() => xapi("backup-upload", { content: t }), "✔ Sauvegarde déposée : elle est dans la liste, prête à être restaurée.")) reload("bk"); });
  const rest = async b => { if (!await sure("Restaurer cette sauvegarde ?", `La collection redeviendra celle du <b>${dt(b.t)}</b>. L'état actuel est d'abord sauvegardé : vous pourrez y revenir.`, "Restaurer")) return;
    if (await act(() => xapi("restore", { name: b.name }), "✔ Collection restaurée.")) { pvReload(); reload("bk"); } };
  const zip = f => (async () => { if (!await sure("Restaurer cet export .zip ?", "Les données du serveur seront remplacées par celles du fichier (les fichiers remplacés sont gardés dans les sauvegardes), puis le serveur redémarrera.", "Restaurer")) return;
    if (await act(() => xapi("import-zip", f, true))) waitBack(); })();
  return [head("Sauvegardes", "La collection est sauvegardée automatiquement chaque jour et avant chaque opération risquée. Ici, vous faites une copie quand vous voulez, vous la téléchargez, vous revenez en arrière."),
    card("Maintenant", el("div", { class: "btns" }, btn("💾 Sauvegarder la collection", async () => { if (await act(() => xapi("backup", {}), "✔ Sauvegarde faite.")) reload("bk"); }, "primary"),
      btn("⬆ Déposer une sauvegarde (.json)…", () => pickFile(".json,application/json", up)))),
    card("Sauvegardes gardées sur le serveur", w || (d.backups.length ? el("div", { class: "rowset" }, d.backups.map(b => line(
      el("span", { class: "lab" }, el("b", {}, dt(b.t)), el("div", { class: "hint" }, b.name + " · " + sz(b.size))),
      el("a", { class: "b small", href: "/api/bo/x/backup-file?name=" + encodeURIComponent(b.name), download: b.name, title: "Télécharger" }, "⬇"), btn("Restaurer", () => rest(b), "small"),
      xbtn("Supprimer cette sauvegarde", async () => { if (await sure("Supprimer cette sauvegarde ?", esc(b.name), "Supprimer") && await act(() => xapi("backup-delete", { name: b.name }))) reload("bk"); }))))
      : el("p", { class: "hint" }, "Aucune sauvegarde pour l'instant."))),
    card("Tout emporter ailleurs", para("Un fichier .zip avec <b>toutes</b> vos données (collection, réglages, back office), à ranger hors du serveur : c'est votre assurance en cas de panne."),
      el("div", { class: "btns" }, el("a", { class: "b", href: "/api/bo/x/export", download: "" }, "⬇ Exporter les données (.zip)"), el("a", { class: "b", href: "/api/bo/x/export?photos=1", download: "" }, "⬇ Données + mes photos (.zip)")),
      expertUI ? [el("div", { style: "height:10px" }), btn("⬆ Restaurer un export .zip…", () => pickFile(".zip,application/zip", zip), "danger"),
        hint("Depuis le réseau local (ou de partout si « Outils sensibles depuis Internet » est permis). Les mots de passe ne sont jamais dans l'export : ceux du serveur restent en place.")] : null)];
};

/* ------------------------------------------------------------------ État et journal */
let logQ = "", logErr = false;
const up = s => s >= 86400 ? Math.floor(s / 86400) + " j " + Math.floor(s % 86400 / 3600) + " h" : s >= 3600 ? Math.floor(s / 3600) + " h " + Math.floor(s % 3600 / 60) + " min" : Math.floor(s / 60) + " min";
VIEW.serveur = () => {
  const d = got("st", "status"), w = wait(d, "st"), lg = got("log", "log?n=600");
  const bad = /erreur|error|traceback|exception|impossible|refus/i;
  const lines = lg && !lg.erreur ? lg.lines.filter(l => (!logQ || l.toLowerCase().includes(logQ.toLowerCase())) && (!logErr || bad.test(l))).slice(-300) : [];
  return [head("État et journal", "Comment va le serveur, la place qu'il lui reste, ce qu'il a fait."),
    w || [d.restored.length ? note("🛟 Au dernier démarrage, le serveur ne démarrait plus : la version précédente de <b>" + d.restored.map(esc).join(", ") + "</b> a été remise automatiquement.", "warn") : null,
      card("Santé", el("div", { class: "facts" },
        el("div", {}, el("span", {}, "En marche depuis"), el("b", {}, up(d.uptime))), el("div", {}, el("span", {}, "Disque libre"), el("b", {}, sz(d.disk.free) + " sur " + sz(d.disk.total))),
        el("div", {}, el("span", {}, "Mémoire libre"), el("b", {}, sz(d.mem.free) + " sur " + sz(d.mem.total))), el("div", {}, el("span", {}, "Charge du processeur"), el("b", {}, d.load.toFixed(2).replace(".", ","))),
        el("div", {}, el("span", {}, "Fiches · listes"), el("b", {}, d.items + " · " + d.lists)), el("div", {}, el("span", {}, "Dernière sauvegarde"), el("b", {}, dt(d.last_backup))),
        el("div", {}, el("span", {}, "Port · Python"), el("b", {}, d.port + " · " + d.python)), el("div", {}, el("span", {}, "Données (fichiers .json)"), el("b", {}, sz(d.json))),
        d.folders.map(f => el("div", {}, el("span", {}, f.name), el("b", {}, sz(f.size) + " · " + f.files + " fichiers")))),
        el("div", { style: "height:10px" }), el("div", { class: "btns" }, btn("⟳ Actualiser", () => reload("st", "log")), btn("↻ Redémarrer le serveur", restart, "danger"),
          el("a", { class: "b", href: "/backoffice/secours", target: "_blank", rel: "noopener", title: "Page indépendante : remettre une version précédente du code, redémarrer" }, "🛟 Page de secours")),
        d.disk.free < 5e8 ? note("⚠ Il reste peu de place sur le disque : supprimez d'anciennes sauvegardes, ou baissez la limite des images dans « Paramètres du serveur ».", "warn") : null),
      card("Actions faites depuis le back office", d.journal.length ? el("div", { class: "logbox", style: "max-height:22vh" }, d.journal.map(l => { const [t, a, x] = l.split("\t"); return el("div", {}, t.slice(5, 16) + "  " + a + (x ? " — " + x : "")); }))
        : el("p", { class: "hint" }, "Rien pour l'instant."))],
    card("Journal du serveur", line(el("input", { type: "search", value: logQ, placeholder: "Filtrer…", oninput: e => { logQ = e.target.value; draw(); } }), chk("Erreurs seulement", logErr, v => { logErr = v; draw(); }), btn("⟳", () => reload("log"), "small")),
      el("div", { style: "height:8px" }), !lg ? el("p", { class: "hint" }, "Chargement…") : lg.erreur ? note("⚠ " + esc(lg.erreur), "warn")
        : el("div", { class: "logbox" }, lines.length ? lines.map(l => el("div", { class: bad.test(l) ? "er" : "" }, l)) : "Aucune ligne."),
      hint("Une ligne rouge signale un souci. Copiez-la telle quelle si vous demandez de l'aide."))];
};

/* ------------------------------------------------------------------ Fichiers de données */
let fFile = "", fPath = [], fQ = "", fStart = 0;
const TY = { dict: "groupe", list: "liste", str: "texte", num: "nombre", bool: "oui / non", "null": "vide" };
async function valueEdit(title, cur, withKey) {   // fenêtre : type + valeur (→ { key, value }) ; null si annulé
  const t0 = cur === undefined ? "str" : cur === null ? "null" : typeof cur === "boolean" ? "bool" : typeof cur === "number" ? "num" : typeof cur === "string" ? "str" : "json";
  const key = el("input", { type: "text", placeholder: "nom de la ligne" });
  const ty = el("select", {}, [["str", "Texte"], ["num", "Nombre"], ["bool", "Oui / Non"], ["null", "Vide"], ["json", "Groupe ou liste (JSON)"]].map(([v, l]) => el("option", { value: v }, l))); ty.value = t0;
  const ta = el("textarea", { rows: 6, spellcheck: false, style: "font-family:ui-monospace,Consolas,monospace;font-size:12.5px", value: cur === undefined || cur === null ? "" : typeof cur === "object" ? JSON.stringify(cur, null, 1) : String(cur) });
  for (;;) {
    const ok = await modal(title, [withKey && fld("Nom de la ligne", key), fld("Type", ty), fld("Valeur", ta, "Oui / Non : écrivez « oui » ou « non ». Groupe ou liste : au format JSON, ex. <code>{}</code> ou <code>[]</code>.")], { ok: "Enregistrer", wide: true });
    if (!ok) return null;
    const s = ta.value; let v;
    if (ty.value === "num") { v = parseFloat(s.replace(",", ".")); if (isNaN(v)) { toast("Ce n'est pas un nombre."); continue; } }
    else if (ty.value === "bool") v = /^(oui|vrai|true|1)$/i.test(s.trim());
    else if (ty.value === "null") v = null;
    else if (ty.value === "json") { try { v = JSON.parse(s || "{}"); } catch { toast("JSON illisible : vérifiez les accolades, crochets et guillemets."); continue; } }
    else v = s;
    return { key: key.value.trim(), value: v };
  }
}
VIEW.fichiers = () => {
  if (!fFile) { const d = got("files", "files"), w = wait(d, "files");
    return [head("Fichiers de données", "Tout ce que l'application enregistre est ici, fichier par fichier. Vous pouvez tout voir et tout corriger, ligne par ligne : une copie du fichier est gardée avant chaque écriture."),
      note("À utiliser quand aucune autre rubrique ne permet la correction. Une valeur fausse ici peut dérégler l'application : en cas de doute, faites d'abord une sauvegarde.", "warn"),
      w || el("table", { class: "tb" }, el("tr", {}, el("th", {}, "Fichier"), el("th", {}, "Contenu"), el("th", {}, "Taille"), el("th", {}, "Modifié"), el("th", {})),
        d.files.map(f => el("tr", {}, el("td", {}, el("b", {}, f.name)), el("td", {}, f.doc), el("td", {}, sz(f.size)), el("td", {}, dt(f.t)),
          el("td", { class: "a" }, btn("Ouvrir", () => { fFile = f.name; fPath = []; fQ = ""; fStart = 0; draw(); }, "small"), " ", el("a", { class: "b small", href: "/api/bo/x/file-raw?file=" + encodeURIComponent(f.name), download: f.name }, "⬇")))))];
  }
  const key = "node", name = "json?file=" + encodeURIComponent(fFile) + "&path=" + encodeURIComponent(JSON.stringify(fPath)) + "&q=" + encodeURIComponent(fQ) + "&start=" + fStart;
  if (X.nodeFor !== name) { delete X.node; X.nodeFor = name; }
  const d = got(key, name), w = wait(d, key), goto = p => { fPath = p; fQ = ""; fStart = 0; draw(); };
  const edit = async (op, k, cur) => { const r = await valueEdit(op === "add" ? "Ajouter une ligne" : "Modifier « " + k + " »", cur, op === "add" && d.t === "dict"); if (!r) return;
    if (await act(() => xapi("json-edit", op === "add" ? { file: fFile, path: fPath, op, key: r.key, value: r.value } : { file: fFile, path: [...fPath, k], op: "set", value: r.value }), "✔ Enregistré (copie de l'ancien fichier gardée).")) { pvReload(); reload(key); } };
  const full = async k => { const r = await act(() => xapi("json?file=" + encodeURIComponent(fFile) + "&path=" + encodeURIComponent(JSON.stringify([...fPath, k])))); if (r) edit("set", k, r.v); };
  const find = async () => { const q = await ask("Chercher dans tout le fichier", "", "Texte à trouver (nom, numéro, valeur…)"); if (!q) return;
    const r = await act(() => xapi("json-find?file=" + encodeURIComponent(fFile) + "&q=" + encodeURIComponent(q))); if (!r) return;
    const p = await choose("Résultats pour « " + q + " »", r.hits.map(h => ({ v: h.path, label: h.path.join(" › "), sub: h.v })), { empty: "Rien trouvé." }); if (p) goto(p.slice(0, -1)); };
  return [head("Fichiers de données", ""),
    el("div", { class: "crumb" }, el("button", { type: "button", onclick: () => { fFile = ""; delete X.node; draw(); } }, "← Tous les fichiers"), "·", el("button", { type: "button", onclick: () => goto([]) }, fFile),
      fPath.map((k, i) => ["›", el("button", { type: "button", onclick: () => goto(fPath.slice(0, i + 1)) }, String(k))])),
    line(el("input", { type: "search", value: fQ, placeholder: "Filtrer ces lignes…", onkeydown: e => { if (e.key === "Enter") { fQ = e.target.value.trim(); fStart = 0; draw(); } }, title: "Entrée pour filtrer" }),
      btn("🔎 Chercher dans tout le fichier", find, "small"), btn("+ Ajouter une ligne", () => edit("add"), "small")),
    el("div", { style: "height:8px" }),
    w || (d.rows ? [el("p", { class: "hint" }, `${TY[d.t]} · ${d.n} ligne(s)` + (fQ ? ` · ${d.found} correspondent à « ${fQ} »` : "")),
      el("table", { class: "tb" }, d.rows.map(r => el("tr", {}, el("td", {}, el("b", {}, String(r.k))),
        r.t === "dict" || r.t === "list" ? el("td", { class: "v" }, el("button", { type: "button", class: "b small", onclick: () => goto([...fPath, r.k]) }, "Ouvrir ›"), ` ${TY[r.t]}, ${r.n} ligne(s)` + (r.hint ? " — " + r.hint : ""))
          : el("td", { class: "v" }, r.t === "null" ? "(vide)" : r.t === "bool" ? (r.v ? "oui" : "non") : String(r.v)),
        el("td", { class: "a" }, r.t === "dict" || r.t === "list" ? null : btn("Modifier", () => r.long ? full(r.k) : edit("set", r.k, r.v), "small"), " ",
          xbtn("Supprimer cette ligne", async () => { if (await sure("Supprimer « " + esc(String(r.k)) + " » ?", "Cette ligne (et tout ce qu'elle contient) sera retirée du fichier. Une copie de l'ancien fichier est gardée.", "Supprimer") && await act(() => xapi("json-edit", { file: fFile, path: [...fPath, r.k], op: "del" }))) { pvReload(); reload(key); } }))))),
      d.found > d.start + d.rows.length || d.start ? line(d.start ? btn("← Précédentes", () => { fStart = Math.max(0, fStart - 200); draw(); }, "small") : null, d.found > d.start + d.rows.length ? btn("Suivantes →", () => { fStart += 200; draw(); }, "small") : null) : null]
      : card("Valeur", el("p", { class: "v" }, String(d.v))))];
};

/* ------------------------------------------------------------------ Paramètres du serveur */
VIEW.parametres = () => {
  const d = got("pa", "params"), w = wait(d, "pa");
  const set = async (key, value) => { const r = await act(() => xapi("param", { key, value }), value === null ? "Valeur d'origine remise." : "✔ Appliqué tout de suite."); if (r) { X.pa = { ...X.pa, ...r }; draw(); } };
  const env = async (key, value) => { const r = await act(() => xapi("env", { key, value }), "✔ Enregistré : sera appliqué au prochain redémarrage."); if (r) { X.pa = { ...X.pa, ...r, dirty: true }; draw(); } };
  return [head("Paramètres du serveur", "Les réglages de fond de l'application : à quelle fréquence elle relit ses prix, combien de place elle garde, combien de temps on reste connecté…"),
    w || [card("Réglages appliqués tout de suite", el("div", { class: "rowset" }, d.params.map(p => { const inp = el("input", { type: "number", class: "num", step: "any", value: p.value, min: p.min, max: p.max, onchange: () => set(p.key, inp.value) });
        return line(el("span", { class: "lab" }, el("b", {}, p.label), el("div", { class: "hint" }, (p.doc ? p.doc + " " : "") + "D'origine : " + String(p.default).replace(".", ",") + " " + p.unit)), inp, el("span", { class: "hint", style: "width:62px" }, p.unit),
          p.changed ? btn("↺", () => set(p.key, null), "small", "Remettre la valeur d'origine") : el("span", { style: "width:30px" })); }))),
      card("Réglages de démarrage", para("Ceux-ci ne changent qu'au <b>redémarrage</b> du serveur. Laissez vide pour garder le réglage de l'installation."),
        el("div", { class: "rowset" }, d.env.map(e => { const inp = el("input", { type: "text", value: e.value ?? "", placeholder: e.now ? "actuel : " + e.now : "(non réglé)" });
          return line(el("span", { class: "lab" }, el("b", {}, e.label), el("div", { class: "hint" }, e.doc)), inp, btn("Enregistrer", () => env(e.key, inp.value.trim() === "" ? null : inp.value.trim()), "small")); })),
        d.dirty ? [el("div", { style: "height:8px" }), note("Un réglage de démarrage a changé : redémarrez pour l'appliquer.", "warn"), btn("↻ Redémarrer le serveur", restart, "danger")] : null,
        hint("Depuis le réseau local (ou de partout si « Outils sensibles depuis Internet » est permis). Si vous changez le port, l'adresse du site change : notez-la avant de redémarrer."))]];
};

/* ------------------------------------------------------------------ Code de l'application */
let cFile = "", cDoc = null, cRestart = false;
VIEW.code = () => {
  if (!cFile) { const d = got("cf", "code-files"), w = wait(d, "cf");
    return [head("Code de l'application", "Les fichiers du programme lui-même. À n'ouvrir que pour une correction précise — par exemple un morceau de code qu'on vous a fourni."),
      note("<b>Trois filets de sécurité</b> : la syntaxe est vérifiée avant d'enregistrer ; chaque version précédente est gardée et peut être remise d'un clic ; si le serveur ne redémarre plus après une modification, " +
        "l'ancienne version est remise toute seule. En dernier recours : la <a href=\"/backoffice/secours\" target=\"_blank\" rel=\"noopener\">🛟 page de secours</a> (notez son adresse : <code>/admin/secours</code>).", "warn"),
      cRestart ? [note("Un fichier <code>.py</code> a été modifié : il ne sera pris en compte qu'après un redémarrage.", "warn"), btn("↻ Redémarrer le serveur", async () => { await restart(); cRestart = false; }, "danger"), el("div", { style: "height:10px" })] : null,
      w || el("table", { class: "tb" }, el("tr", {}, el("th", {}, "Fichier"), el("th", {}, "Rôle"), el("th", {}, "Taille"), el("th", {}, "Modifié"), el("th", {}, "Versions gardées"), el("th", {})),
        d.files.map(f => el("tr", {}, el("td", {}, el("b", {}, f.file)), el("td", {}, ROLE[f.file] || ""), el("td", {}, sz(f.size)), el("td", {}, dt(f.t)), el("td", {}, f.versions || "—"),
          el("td", { class: "a" }, btn("Ouvrir", async () => { const r = await act(() => xapi("code?file=" + encodeURIComponent(f.file))); if (r) { cFile = f.file; cDoc = r; draw(); } }, "small")))))];
  }
  const ta = el("textarea", { class: "code", spellcheck: false, wrap: "off", value: cDoc.content, oninput: () => { save.disabled = ta.value === cDoc.content; }, onkeydown: e => { if (e.key === "Tab") { e.preventDefault(); const a = ta.selectionStart; ta.setRangeText("  ", a, ta.selectionEnd, "end"); save.disabled = false; } } });
  const reopen = async () => { const r = await act(() => xapi("code?file=" + encodeURIComponent(cFile))); if (r) { cDoc = r; delete X.cf; draw(); } };
  const save = btn("✔ Enregistrer", async () => { const r = await act(() => xapi("code-save", { file: cFile, content: ta.value }));
    if (!r) return; toast(r.same ? "Rien n'a changé." : "✔ Enregistré. L'ancienne version est gardée."); if (r.restart) cRestart = true; reopen(); if (!cFile.endsWith(".py")) pvReload(); }, "primary");
  save.disabled = true;
  const gotoLine = n => { const lines = ta.value.split("\n"), pos = lines.slice(0, Math.max(0, n - 1)).reduce((a, l) => a + l.length + 1, 0); ta.focus(); ta.setSelectionRange(pos, pos + (lines[n - 1] || "").length); ta.scrollTop = Math.max(0, (n - 8) * 18.1); };
  const findNext = q => { if (!q) return; const i = ta.value.toLowerCase().indexOf(q.toLowerCase(), ta.selectionEnd); const j = i < 0 ? ta.value.toLowerCase().indexOf(q.toLowerCase()) : i; if (j < 0) return toast("Introuvable.");
    ta.focus(); ta.setSelectionRange(j, j + q.length); ta.scrollTop = Math.max(0, (ta.value.slice(0, j).split("\n").length - 8) * 18.1); };
  const ver = el("select", {}, [el("option", { value: "" }, cDoc.versions.length ? "Versions précédentes (" + cDoc.versions.length + ")…" : "Aucune version précédente"), ...cDoc.versions.map(v => el("option", { value: v.id }, fmtId(v.id) + " · " + sz(v.size)))]);
  const back = async () => { if (!ver.value) return toast("Choisissez d'abord une version."); if (!await sure("Remettre cette version ?", `« ${esc(cFile)} » redeviendra tel qu'il était le <b>${fmtId(ver.value)}</b>. La version actuelle est gardée, vous pourrez y revenir.`, "Remettre")) return;
    const r = await act(() => xapi("code-restore", { file: cFile, id: ver.value }), "✔ Version remise."); if (r) { if (r.restart) cRestart = true; reopen(); } };
  const see = async () => { if (!ver.value) return toast("Choisissez d'abord une version."); const r = await act(() => xapi("code-version?file=" + encodeURIComponent(cFile) + "&id=" + ver.value));
    if (r) modal(cFile + " — version du " + fmtId(ver.value), el("textarea", { class: "code", style: "height:60vh", readOnly: true, wrap: "off", value: r.content }), { ok: false, cancel: "Fermer", wide: true }); };
  return [head("Code de l'application", ""),
    el("div", { class: "crumb" }, el("button", { type: "button", onclick: async () => { if (ta.value !== cDoc.content && !await sure("Quitter sans enregistrer ?", "Vos modifications de ce fichier seront perdues.", "Quitter")) return; cFile = ""; cDoc = null; draw(); } }, "← Tous les fichiers"), "·", el("b", {}, cFile),
      el("span", { class: "hint" }, ROLE[cFile] || "")),
    cRestart ? note("Un fichier <code>.py</code> a été modifié : redémarrez le serveur (liste des fichiers, ou « État et journal ») pour l'appliquer.", "warn") : null,
    line(save, el("input", { type: "search", placeholder: "Chercher… (Entrée)", style: "max-width:220px", onkeydown: e => { if (e.key === "Enter") findNext(e.target.value); } }),
      el("input", { type: "number", class: "num", placeholder: "ligne", min: 1, onkeydown: e => { if (e.key === "Enter") gotoLine(+e.target.value); }, title: "Aller à la ligne (Entrée)" }), el("span", { class: "grow" }), ver, btn("Voir", see, "small"), btn("Remettre", back, "small")),
    el("div", { style: "height:8px" }), ta,
    hint(cFile.endsWith(".py") ? "Fichier du serveur : après l'enregistrement, il faut redémarrer. S'il empêche le serveur de démarrer, l'ancienne version revient toute seule."
      : "Fichier de l'écran : pris en compte dès l'enregistrement (rechargez la page du site).")];
};
const ROLE = { "server.py": "Le serveur : toutes les routes, les prix, les calculs", "sources.py": "Catalogues et sites extérieurs (API)", "auth.py": "Mot de passe et sessions", "backoffice.py": "Back office : réglages et injection",
  "backoffice_outils.py": "Back office : outils du serveur", "detourage.py": "Détourage des photos", "static/app.js": "L'application (écran privé)", "static/style.css": "Styles du site", "static/index.html": "Page de l'application",
  "static/guest.html": "Pages publiques", "static/share.html": "Fiche partagée", "static/nouveautes.html": "Page Nouveautés", "static/login.html": "Page de connexion", "static/sw.js": "Mode hors ligne",
  "static/bo.js": "Back office : moteur (sur le site)", "static/bo-plus.js": "Back office : fonctions avancées (sur le site)", "static/admin.js": "Back office : cet écran", "static/admin-plus.js": "Back office : rubriques avancées",
  "static/admin.css": "Back office : styles", "static/admin.html": "Back office : page", "static/bo-max.js": "Back office : étiquettes, boutons, pages (sur le site)", "static/admin-max.js": "Back office : rubriques « tout modifier »",
  "backoffice_acces.py": "Back office : mot de passe et sessions", "static/page.html": "Gabarit des pages publiques créées", "docs/wiki.py": "Moteur des guides en wiki (docs/wiki/*.html)", "static/help.js": "Aide « ? » de l'application", "static/setup.html": "Première installation", "static/manifest.json": "Icône et nom de l'appli installée" };

/* ------------------------------------------------------------------ Accueil et « Mes modifications » complétés */
VIEW.accueil = () => [
  head("Bienvenue dans le back office", "Ici, vous changez l'apparence et l'organisation du site — et, si besoin, vous l'entretenez — sans ligne de commande."),
  copie && note("🧪 Vous êtes sur la <b>copie de travail</b> : rien de ce que vous faites ici ne touche le vrai site."),
  card("Comment ça marche", el("ol", { class: "steps" },
    el("li", { html: "<b>Vous modifiez</b> avec les rubriques de gauche, ou directement dans l'aperçu : « 🖱️ Cliquer pour modifier » et « ✋ Déplacer »." }),
    el("li", { html: "<b>L'aperçu à droite</b> montre le résultat tout de suite. C'est un brouillon : vous seul le voyez." }),
    el("li", { html: "<b>« ✔ Publier sur le site »</b>, en haut, l'applique pour de bon." })),
    hint("Rien n'est définitif : « ↶ Annuler », « Abandonner le brouillon » et « Historique et secours » permettent toujours de revenir en arrière.")),
  card("Fonctions avancées", para(expertUI ? "L'interrupteur <b>Fonctions avancées</b> (en haut) est allumé : calculs, règles « si… alors », tuiles, vues, corrections du catalogue, tableur, fichiers de données, paramètres et code sont dans le menu."
      : "Besoin d'aller plus loin ? Allumez <b>Fonctions avancées</b> (en haut) : calculs et variables, règles « si… alors », tuiles, vues, corrections du catalogue, tableur, fichiers de données, paramètres du serveur, code."),
    hint("Les outils du serveur agissent tout de suite (pas de brouillon). Les plus sensibles — code, démarrage, restauration .zip — ne répondent que depuis le réseau local, sauf réglage contraire dans « Mots de passe et sécurité ».")),
  GROUPS.slice(1).map(([title, ids]) => { const vis = ids.filter(id => !isX(id) || expertUI); return vis.length ? [el("h3", { style: "margin:16px 0 8px" }, title),
    el("div", { class: "tiles" }, vis.map(id => { const [, ic, nm, ds] = PANELS.find(p => p[0] === id); return el("button", { type: "button", onclick: () => show(id) }, el("b", {}, ic + " " + nm), el("span", {}, ds)); }))] : null; }),
];
const modifs0 = VIEW.modifs;
VIEW.modifs = () => { const rows = [["calcs", "🧮", "champ(s) calculé(s)", "calculs"], ["vars", "🧮", "variable(s)", "calculs"], ["auto", "⚡", "règle(s) « si… alors »", "regles"], ["tiles", "📊", "tuile(s)", "tuiles"],
    ["views", "🔎", "vue(s) enregistrée(s)", "vues"], ["sorts", "🔎", "tri(s)", "vues"], ["filters", "🔎", "filtre(s)", "vues"], ["moves", "✋", "élément(s) déplacé(s) à la souris", "souris"]].filter(r => (cfg[r[0]] || []).length);
  return [modifs0(), rows.length ? card("Fonctions avancées", el("div", { class: "rowset" }, rows.map(([k, ic, nm, to]) => line(el("span", { class: "lab" }, ic + " ", el("b", {}, cfg[k].length + " " + nm)),
    btn("Ouvrir", () => { if (isX(to) && !expertUI) setExpert(true); show(to); if (k === "moves") setMode("move"); }, "small"), xbtn("Tout supprimer", () => change(c => { delete c[k]; }))))) ) : null];
};

/* ------------------------------------------------------------------ interrupteur « Fonctions avancées », démarrage */
function setExpert(on) { expertUI = !!on; ls("bo-expert", on ? "1" : "0"); const box = $("#expert"); if (box) box.checked = expertUI; buildNav(); status(); if (isX(panel) && !expertUI) show("accueil"); else draw(); }
$(".top .grow").before(el("label", { class: "chk xp", title: "Montre les rubriques avancées : calculs, règles, tuiles, vues, catalogue, tableur, fichiers de données, paramètres, code" },
  el("input", { type: "checkbox", id: "expert", checked: expertUI, onchange: e => setExpert(e.target.checked) }), el("span", {}, "Fonctions avancées")));
const hash = location.hash.slice(1);
if (isX(hash) && !expertUI) { expertUI = true; ls("bo-expert", "1"); $("#expert").checked = true; }   // lien direct vers une rubrique avancée
window.BO_PLUS = true;
/* ce que admin-max.js réutilise (rubriques « tout modifier ») */
window.BOX = { GROUPS, WIDE, LISTS, NEW, xapi, act, got, reload, wait, X, condBox, fxBox, helpCard, P, needPreview, esc, sz, dt, xbtn, colorIn, foot, typesRow, upd, del, add, pickFile, restart, waitBack };
if (!document.querySelector('script[src="/admin-max.js"]')) startAdmin();   // (sinon c'est admin-max.js qui démarre l'écran, une fois ses rubriques ajoutées)
})();

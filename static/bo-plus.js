/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
/* Briquothèque — BACK OFFICE, fonctions avancées.
   Chargé après bo.js, seulement sur le site connecté. Rien ici ne modifie les données : tout est calculé à l'affichage.
     1. FORMULES : un petit langage de calcul, en français, sans risque (aucun code exécuté) — ex. : {valeur} - {prix_achat}
        variables : celles d'une fiche ({valeur}, {annee}, {theme}…), vos champs personnalisés, vos champs calculés, vos variables
     2. CHAMPS CALCULÉS (cfg.calcs) : une formule affichée sur la fiche et, au choix, sur les cartes
     3. RÈGLES « si… alors » (cfg.auto) : étiquette ou pastille sur la carte, couleur de carte, message ou bloc masqué sur la fiche
     4. TUILES (cfg.tiles) : totaux personnalisés à côté de « Sets / Figurines / Pièces »
     5. TRIS (cfg.sorts), FILTRES (cfg.filters), VUES enregistrées (cfg.views)
   Une condition (cond) : { mode: "all" | "any", rows: [{ v: variable, op, val }] } ou { expr: "formule" }. */
(() => {
"use strict";
const W = window, D = document, B = W.BO;
if (!B || !B._ || B.plus || B.page !== "app") return;
const { HOOKS, esc, all, app, itemType, ownItem, fmtDate, schedule } = B._;
const cfg = () => B._.cfg() || {};
let stamp = 0;   // change à chaque relecture des réglages : tout ce qui est gardé en mémoire est recalculé

/* ------------------------------------------------------------------ 1. formules */
class Err extends Error {}
const norm = s => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
const key = s => norm(s).replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
const nf2 = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 });
const eur = v => typeof money === "function" ? money(v) : new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(v);
const isZ = v => v == null || v === "" || (Array.isArray(v) && !v.length);
const isDate = v => typeof v === "string" && /^\d{4}-\d{2}-\d{2}/.test(v);
const num = v => typeof v === "number" ? (isFinite(v) ? v : null) : typeof v === "boolean" ? (v ? 1 : 0) : isZ(v) || isDate(v) ? null
  : (x => isNaN(x) ? null : x)(parseFloat(String(v).replace(/[\s €%]/g, "").replace(",", ".")));
const toBool = v => typeof v === "boolean" ? v : typeof v === "number" ? v !== 0 : /^(oui|vrai|true|1|x)$/.test(norm(v)) ? true : /^(non|faux|false|0)$/.test(norm(v)) ? false : !isZ(v);
const truthy = v => !(isZ(v) || v === false || v === 0);
const str = v => isZ(v) ? "" : Array.isArray(v) ? v.join(", ") : typeof v === "boolean" ? (v ? "oui" : "non") : typeof v === "number" ? nf2.format(v) : isDate(v) ? fmtDate(v.slice(0, 10)) : String(v);
const iso = d => d && !isNaN(d) ? `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}` : null;
function toDate(v) {
  if (isZ(v)) return null;
  if (typeof v === "number") return new Date(v > 1e11 ? v : v * 1000);
  let m = /^(\d{4})-(\d{2})-(\d{2})/.exec(v); if (m) return new Date(+m[1], +m[2] - 1, +m[3]);
  m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})/.exec(v); if (m) return new Date(+m[3], +m[2] - 1, +m[1]);
  m = /^(\d{4})$/.exec(String(v).trim()); return m ? new Date(+m[1], 0, 1) : null;
}
function compare(o, a, b) {
  if (Array.isArray(a) && !Array.isArray(b)) { const has = a.some(x => norm(x) === norm(str(b))); return o === "=" ? has : o === "<>" ? !has : false; }   // choix multiples : « = » veut dire « contient »
  if (isZ(a) || isZ(b)) { const both = isZ(a) && isZ(b); return o === "=" ? both : o === "<>" ? !both : false; }
  let c;
  if (typeof a === "boolean" || typeof b === "boolean") c = +toBool(a) - +toBool(b);
  else if (isDate(a) || isDate(b)) { const x = toDate(a), y = toDate(b); if (!x || !y) return o === "<>"; c = x - y; }
  else { const x = num(a), y = num(b); c = x != null && y != null ? x - y : norm(str(a)).localeCompare(norm(str(b)), "fr", { numeric: true }); }
  return o === "=" ? c === 0 : o === "<>" ? c !== 0 : o === "<" ? c < 0 : o === ">" ? c > 0 : o === "<=" ? c <= 0 : c >= 0;
}
function tokens(src) {
  const s = String(src ?? ""), out = [];
  for (let i = 0; i < s.length;) {
    const c = s[i];
    if (/\s/.test(c)) { i++; continue; }
    if (c === "{") { const j = s.indexOf("}", i); if (j < 0) throw new Err("Il manque « } » pour fermer le nom d'une variable"); out.push({ t: "var", v: s.slice(i + 1, j) }); i = j + 1; continue; }
    if (c === '"' || c === "'" || c === "«" || c === "“") { const end = c === "«" ? "»" : c === "“" ? "”" : c, j = s.indexOf(end, i + 1);
      if (j < 0) throw new Err("Il manque le guillemet qui ferme le texte"); out.push({ t: "str", v: c === "«" ? s.slice(i + 1, j).trim() : s.slice(i + 1, j) }); i = j + 1; continue; }
    let m = /^\d+(?:[.,]\d+)?/.exec(s.slice(i));
    if (m) { out.push({ t: "num", v: parseFloat(m[0].replace(",", ".")) }); i += m[0].length; continue; }
    m = /^(<=|>=|<>|!=|≤|≥|≠|[-+*\/^&=<>();,×÷])/.exec(s.slice(i));
    if (m) { out.push({ t: "op", v: { "!=": "<>", "≠": "<>", "≤": "<=", "≥": ">=", "×": "*", "÷": "/", ",": ";" }[m[0]] || m[0] }); i += m[0].length; continue; }
    m = /^[\p{L}_][\p{L}\p{N}_]*/u.exec(s.slice(i));
    if (m) { out.push({ t: "id", v: key(m[0]), raw: m[0] }); i += m[0].length; continue; }
    throw new Err(`Le signe « ${c} » n'est pas compris`);
  }
  return out;
}
function parse(src) {
  const tk = tokens(src); let p = 0;
  if (!tk.length) throw new Err("La formule est vide");
  const eat = (t, v) => { const k = tk[p]; if (k && k.t === t && (v === undefined || k.v === v)) { p++; return k; } return null; };
  const word = v => { const k = tk[p]; if (k && k.t === "id" && k.v === v && !(tk[p + 1] && tk[p + 1].t === "op" && tk[p + 1].v === "(")) { p++; return true; } return false; };
  const or = () => { let a = and(); while (word("ou")) a = { o: "ou", a, b: and() }; return a; };
  const and = () => { let a = not(); while (word("et")) a = { o: "et", a, b: not() }; return a; };
  const not = () => word("non") || word("pas") ? { o: "non", a: not() } : cmp();
  const cmp = () => { const a = cat(), k = tk[p]; if (k && k.t === "op" && ["=", "<>", "<", ">", "<=", ">="].includes(k.v)) { p++; return { o: k.v, a, b: cat() }; } return a; };
  const cat = () => { let a = add(); while (eat("op", "&")) a = { o: "&", a, b: add() }; return a; };
  const add = () => { let a = mul(); for (;;) { if (eat("op", "+")) a = { o: "+", a, b: mul() }; else if (eat("op", "-")) a = { o: "-", a, b: mul() }; else return a; } };
  const mul = () => { let a = una(); for (;;) { if (eat("op", "*")) a = { o: "*", a, b: una() }; else if (eat("op", "/")) a = { o: "/", a, b: una() }; else return a; } };
  const una = () => eat("op", "-") ? { o: "neg", a: una() } : eat("op", "+") ? una() : pow();
  const pow = () => { const a = prim(); return eat("op", "^") ? { o: "^", a, b: una() } : a; };
  const prim = () => {
    const k = tk[p];
    if (!k) throw new Err("La formule s'arrête trop tôt : il manque une valeur à la fin");
    p++;
    if (k.t === "num") return { n: k.v };
    if (k.t === "str") return { s: k.v };
    if (k.t === "var") return { v: k.v };
    if (k.t === "op" && k.v === "(") { const a = or(); if (!eat("op", ")")) throw new Err("Il manque une parenthèse fermante « ) »"); return a; }
    if (k.t === "id") {
      if (eat("op", "(")) { const args = [];
        if (!eat("op", ")")) for (;;) { args.push(or()); if (eat("op", ")")) break; if (!eat("op", ";")) throw new Err(`Dans ${k.raw}(…) : séparez les valeurs par « ; » et fermez la parenthèse`); }
        if (!FN[k.v]) throw new Err(`La fonction « ${k.raw} » n'existe pas`);
        return { f: k.v, args }; }
      if (k.v === "vrai" || k.v === "oui") return { bool: true };
      if (k.v === "faux") return { bool: false };
      if (k.v === "vide" || k.v === "rien") return { z: 1 };
      if (FN[k.v]) return { f: k.v, args: [] };
      throw new Err(`« ${k.raw} » n'est pas reconnu. Une variable s'écrit entre accolades : {${k.raw}} ; un texte, entre guillemets : "${k.raw}"`);
    }
    throw new Err(`« ${k.v} » n'est pas à sa place`);
  };
  const ast = or();
  if (p < tk.length) throw new Err(`« ${tk[p].raw ?? tk[p].v} » est en trop : il manque peut-être un signe (+, -, &, ;) juste avant`);
  return ast;
}
const need = (a, n, name) => { if (a.length < n) throw new Err(`${name}(…) attend ${n} valeur${n > 1 ? "s" : ""}, séparées par « ; »`); };
const nums = a => a.flat().map(num).filter(x => x != null);
const FN = {   // sig et doc : affichés dans le back office (liste des fonctions)
  si: { lazy: 1, sig: "si(condition ; alors ; sinon)", doc: "Choisit une valeur selon une condition. Ex. : si({valeur} > 100 ; \"💎\" ; \"\")",
    run: (a, e) => { need(a, 2, "si"); return truthy(ev(a[0], e)) ? ev(a[1], e) : a[2] ? ev(a[2], e) : null; } },
  sivide: { lazy: 1, sig: "sivide(valeur ; remplacement)", doc: "La valeur, ou le remplacement si elle est vide. Ex. : sivide({prix_achat} ; 0)",
    run: (a, e) => { need(a, 2, "sivide"); const v = ev(a[0], e); return isZ(v) ? ev(a[1], e) : v; } },
  estvide: { sig: "estvide(valeur)", doc: "Vrai si rien n'est rempli.", run: a => isZ(a[0]) },
  arrondi: { sig: "arrondi(nombre ; décimales)", doc: "Arrondit. Ex. : arrondi({valeur} / {pieces} ; 2)", run: a => { const x = num(a[0]), n = num(a[1]) || 0; return x == null ? null : Math.round(x * 10 ** n) / 10 ** n; } },
  entier: { sig: "entier(nombre)", doc: "Retire les décimales.", run: a => { const x = num(a[0]); return x == null ? null : Math.trunc(x); } },
  abs: { sig: "abs(nombre)", doc: "Le nombre sans son signe.", run: a => { const x = num(a[0]); return x == null ? null : Math.abs(x); } },
  min: { sig: "min(a ; b ; …)", doc: "La plus petite valeur.", run: a => { const n = nums(a); return n.length ? Math.min(...n) : null; } },
  max: { sig: "max(a ; b ; …)", doc: "La plus grande valeur.", run: a => { const n = nums(a); return n.length ? Math.max(...n) : null; } },
  somme: { sig: "somme(a ; b ; …)", doc: "Additionne (les valeurs vides sont ignorées).", run: a => nums(a).reduce((s, x) => s + x, 0) },
  moyenne: { sig: "moyenne(a ; b ; …)", doc: "La moyenne des valeurs remplies.", run: a => { const n = nums(a); return n.length ? n.reduce((s, x) => s + x, 0) / n.length : null; } },
  pourcent: { sig: "pourcent(partie ; total)", doc: "La part en %. Ex. : pourcent({valeur} - {prix_achat} ; {prix_achat})", run: a => { const x = num(a[0]), y = num(a[1]); return x == null || !y ? null : x / y * 100; } },
  euros: { sig: "euros(nombre)", doc: "Le nombre écrit comme un prix : 12,50 €.", run: a => { const x = num(a[0]); return x == null ? "" : eur(x); } },
  texte: { sig: "texte(valeur)", doc: "Transforme en texte.", run: a => str(a[0]) },
  nombre: { sig: "nombre(texte)", doc: "Transforme en nombre.", run: a => num(a[0]) },
  majuscules: { sig: "majuscules(texte)", doc: "TOUT EN MAJUSCULES.", run: a => str(a[0]).toUpperCase() },
  minuscules: { sig: "minuscules(texte)", doc: "tout en minuscules.", run: a => str(a[0]).toLowerCase() },
  longueur: { sig: "longueur(texte)", doc: "Nombre de caractères.", run: a => str(a[0]).length },
  contient: { sig: "contient(texte ; morceau)", doc: "Vrai si le texte contient le morceau (sans tenir compte des majuscules ni des accents).", run: a => { need(a, 2, "contient"); return Array.isArray(a[0]) ? a[0].some(x => norm(x).includes(norm(str(a[1])))) : norm(str(a[0])).includes(norm(str(a[1]))); } },
  commence: { sig: "commence(texte ; début)", doc: "Vrai si le texte commence par ce début.", run: a => { need(a, 2, "commence"); return norm(str(a[0])).startsWith(norm(str(a[1]))); } },
  remplace: { sig: "remplace(texte ; ancien ; nouveau)", doc: "Remplace un morceau du texte.", run: a => { need(a, 3, "remplace"); return str(a[0]).split(str(a[1])).join(str(a[2])); } },
  gauche: { sig: "gauche(texte ; n)", doc: "Les n premiers caractères.", run: a => str(a[0]).slice(0, num(a[1]) || 0) },
  droite: { sig: "droite(texte ; n)", doc: "Les n derniers caractères.", run: a => { const n = num(a[1]) || 0; return n ? str(a[0]).slice(-n) : ""; } },
  nb: { sig: "nb(liste)", doc: "Nombre d'éléments cochés ou reliés (choix multiples, fiches liées).", run: a => Array.isArray(a[0]) ? a[0].length : isZ(a[0]) ? 0 : 1 },
  aujourdhui: { sig: "aujourdhui()", doc: "La date du jour.", run: () => iso(new Date()) },
  annee: { sig: "annee(date)", doc: "L'année d'une date.", run: a => toDate(a[0])?.getFullYear() ?? null },
  mois: { sig: "mois(date)", doc: "Le mois (1 à 12).", run: a => { const d = toDate(a[0]); return d ? d.getMonth() + 1 : null; } },
  jour: { sig: "jour(date)", doc: "Le jour du mois.", run: a => toDate(a[0])?.getDate() ?? null },
  jours_entre: { sig: "jours_entre(date1 ; date2)", doc: "Nombre de jours de la première à la seconde date.", run: a => { need(a, 2, "jours_entre"); const x = toDate(a[0]), y = toDate(a[1]); return x && y ? Math.round((y - x) / 864e5) : null; } },
  jours_depuis: { sig: "jours_depuis(date)", doc: "Nombre de jours écoulés depuis cette date. Ex. : jours_depuis({date_ajout})", run: a => { const x = toDate(a[0]); return x ? Math.floor((Date.now() - x) / 864e5) : null; } },
};
function ev(n, env) {
  if ("n" in n) return n.n;
  if ("s" in n) return n.s;
  if ("bool" in n) return n.bool;   // (pas « b » : les opérations rangent déjà leur 2e valeur sous ce nom)
  if ("z" in n) return null;
  if ("v" in n) return env(n.v);
  if ("f" in n) { const f = FN[n.f]; return f.lazy ? f.run(n.args, env) : f.run(n.args.map(a => ev(a, env))); }
  switch (n.o) {
    case "ou": return truthy(ev(n.a, env)) || truthy(ev(n.b, env));
    case "et": return truthy(ev(n.a, env)) && truthy(ev(n.b, env));
    case "non": return !truthy(ev(n.a, env));
    case "neg": { const a = num(ev(n.a, env)); return a == null ? null : -a; }
    case "&": return str(ev(n.a, env)) + str(ev(n.b, env));
    case "+": case "-": case "*": case "/": case "^": {
      const a = num(ev(n.a, env)), b = num(ev(n.b, env));
      if (a == null || b == null) return null;   // une valeur vide : résultat vide (utiliser sivide(… ; 0) pour compter 0)
      const r = n.o === "+" ? a + b : n.o === "-" ? a - b : n.o === "*" ? a * b : n.o === "/" ? (b === 0 ? null : a / b) : a ** b;
      return r == null || !isFinite(r) ? null : Math.round(r * 1e6) / 1e6; }
    default: return compare(n.o, ev(n.a, env), ev(n.b, env));
  }
}
const asts = new Map();
function ast(expr) {
  let a = asts.get(expr);
  if (a === undefined) { try { a = parse(expr); } catch (e) { a = e instanceof Err ? e : new Err("Formule illisible"); } if (asts.size > 500) asts.clear(); asts.set(expr, a); }
  if (a instanceof Err) throw a;
  return a;
}

/* ------------------------------------------------------------------ variables d'une fiche */
const TYPE_FR = { set: "Set", fig: "Figurine", moc: "MOC", partial: "Set partiel", mocfig: "Figurine personnalisée", part: "Pièce" };
const APPFN = {   // fonctions de l'application utilisées ici (lues au moment de l'appel : si l'une manque, la valeur reste vide)
  itemName: i => itemName(i), figCount: i => figCount(i), isRetired: x => isRetired(x), isWish: x => isWish(x), isModified: i => isModified(i),
  todosOf: i => todosOf(i), isPartsList: x => isPartsList(x), toast: m => toast(m), setMenu: v => setMenu(v),
  itemStatus: i => itemStatus(i), handTags: i => handTags(i), tagWord: (k, f) => tagWord(k, f),
};
const g = (name, ...a) => { try { return APPFN[name](...a); } catch { return undefined; } };
const BUILT = {   // identifiant : [libellé, format conseillé, lecture]
  numero: ["Numéro", "texte", i => i.number && i.number !== "custom" ? i.number : ""],
  nom: ["Nom", "texte", i => g("itemName", i) || i.display_name || i.info?.name || ""],
  type: ["Type de fiche", "texte", i => TYPE_FR[itemType(i)] || ""],
  liste: ["Liste", "texte", i => state.lists.find(l => l.id === i.list_id)?.name || ""],
  quantite: ["Quantité", "nombre", i => i.quantity || 1],
  valeur: ["Valeur estimée (total)", "euros", i => i.total_value ?? null],
  valeur_unitaire: ["Valeur estimée (à l'unité)", "euros", i => i.total_value != null ? i.total_value / (i.quantity || 1) : null],
  prix_achat: ["Prix d'achat", "euros", i => i.purchase_price ?? null],
  prix_neuf: ["Cote neuf (catalogue)", "euros", i => (i.kind === "fig" ? i.info?.value : i.info?.new_value) ?? null],
  prix_occasion: ["Cote occasion (catalogue)", "euros", i => (i.kind === "fig" ? i.info?.used ?? i.info?.value : i.info?.used_value) ?? null],
  prix_magasin: ["Prix magasin", "euros", i => i.info?.retail ?? null],
  annee: ["Année", "entier", i => parseInt(i.info?.year || i.info?.years) || null],
  theme: ["Thème", "texte", i => i.info?.theme || ""],
  pieces: ["Nombre de pièces", "entier", i => i.info?.pieces ?? null],
  figurines: ["Nombre de figurines", "entier", i => g("figCount", i) ?? null],
  etat: ["État (Neuf / Occasion)", "texte", i => i.condition === "neuf" ? "Neuf" : i.condition === "occasion" ? "Occasion" : ""],
  boite: ["A sa boîte", "ouinon", i => !!i.has_box],
  plan: ["A son plan", "ouinon", i => !i.no_plan],
  a_construire: ["À construire", "ouinon", i => !!i.unbuilt],
  retire: ["Retiré de la vente", "ouinon", i => !!g("isRetired", i.info)],
  souhait: ["Dans une liste de souhaits", "ouinon", i => !!g("isWish", i.list_id)],
  modifie: ["Modifié (pièces retirées ou remplacées)", "ouinon", i => !!g("isModified", i)],
  statut: ["État de la fiche (Complet, Amélioré, Modifié, Set partiel, MOC)", "texte", i => ({ complet: "Complet", ameliore: "Amélioré", modifie: "Modifié", partiel: "Set partiel", moc: "MOC" })[g("itemStatus", i)?.status] || ""],
  etiquettes: ["Étiquettes posées à la main", "texte", i => (g("handTags", i) || []).map(k => g("tagWord", k, i.kind === "fig") || k).join(", ")],
  exemplaires: ["Exemplaires en tout (seuls et dans mes sets)", "entier", i => (i.quantity || 1) + (i._withSetN || 0)],
  dans_un_set: ["Rangée dans un set", "ouinon", i => !!i._in],
  accessoires: ["Valeur des accessoires (liste de pièces)", "euros", i => i.acc_value ?? null],
  taches: ["Nombre de tâches à faire", "entier", i => (g("todosOf", i) || []).length],
  notes: ["Notes", "texte", i => i.notes || ""],
  date_ajout: ["Date d'ajout", "date", i => i.added_at ? iso(new Date(i.added_at * 1000)) : null],
  date_modif: ["Dernière modification", "date", i => i.updated_at ? iso(new Date(i.updated_at * 1000)) : null],
};
const FFMT = { number: "nombre", money: "euros", date: "date", check: "ouinon", stars: "etoiles" };   // format conseillé d'un champ personnalisé
function envOf(it, x, depth = 0) {   // lecture d'une variable pour cette fiche (x : valeurs en cours de saisie sur la fiche ouverte)
  const c = cfg(), xv = x || it.x || {};
  return name => {
    const k = key(name);
    if (BUILT[k]) return BUILT[k][2](it);
    const f = (c.fields || []).find(f => f.id === k);
    if (f) { const v = xv[f.id]; return f.type === "list" ? state.lists.find(l => l.id === v)?.name || "" : f.type === "check" ? !!v : v ?? null; }
    const ca = (c.calcs || []).find(f => f.id === k);
    if (ca) { if (depth > 8) throw new Err(`Les calculs tournent en rond autour de {${k}}`); return ev(ast(ca.expr || ""), envOf(it, x, depth + 1)); }
    const v = (c.vars || []).find(v => v.id === k);
    if (v) return num(v.value) ?? (isZ(v.value) ? null : v.value);
    throw new Err(`La variable {${name.trim()}} n'existe pas`);
  };
}
function calc(expr, it, x) {   // → { ok, value } ou { ok: false, error }
  try { return { ok: true, value: ev(ast(String(expr ?? "")), envOf(it, x)) }; }
  catch (e) { return { ok: false, error: e instanceof Err ? e.message : "Calcul impossible" }; }
}
function show(v, fmt) {   // valeur → texte affiché
  if (isZ(v)) return "";
  switch (fmt) {
    case "euros": { const x = num(v); return x == null ? str(v) : eur(x); }
    case "entier": { const x = num(v); return x == null ? str(v) : nf2.format(Math.round(x)); }
    case "nombre": { const x = num(v); return x == null ? str(v) : nf2.format(x); }
    case "pourcent": { const x = num(v); return x == null ? str(v) : nf2.format(Math.round(x * 10) / 10) + " %"; }
    case "date": { const d = toDate(v); return d ? fmtDate(iso(d)) : str(v); }
    case "ouinon": return toBool(v) ? "Oui" : "Non";
    case "etoiles": { const x = Math.max(0, Math.min(5, Math.round(num(v) || 0))); return "★".repeat(x) + "☆".repeat(5 - x); }
    default: return typeof v === "boolean" ? (v ? "Oui" : "Non") : str(v);
  }
}
const fill = (text, it, x) => String(text ?? "").replace(/\{([^{}]+)\}/g, (m, n) => { try { const k = key(n), c = cfg();   // texte avec {variables}
  const fmt = BUILT[k]?.[1] || FFMT[(c.fields || []).find(f => f.id === k)?.type] || (c.calcs || []).find(f => f.id === k)?.fmt; return show(envOf(it, x)(n), fmt); } catch { return m; } });

/* ------------------------------------------------------------------ conditions */
const lit = b => { const s = String(b ?? "").trim(); return s === "" ? null : s; };
const OPS = {
  "=": (a, b) => compare("=", a, lit(b)), "<>": (a, b) => compare("<>", a, lit(b)), ">": (a, b) => compare(">", a, lit(b)), "<": (a, b) => compare("<", a, lit(b)),
  ">=": (a, b) => compare(">=", a, lit(b)), "<=": (a, b) => compare("<=", a, lit(b)),
  contient: (a, b) => norm(str(a)).includes(norm(b)), sans: (a, b) => !norm(str(a)).includes(norm(b)),
  vide: a => isZ(a) || a === false, rempli: a => !(isZ(a) || a === false), vrai: a => truthy(a) && toBool(a), faux: a => !(truthy(a) && toBool(a)),
};
function test(cond, it, x) {   // la fiche remplit-elle la condition ? (pas de condition : oui)
  if (!cond || typeof cond !== "object") return true;
  if (typeof cond.expr === "string" && cond.expr.trim()) { const r = calc(cond.expr, it, x); return r.ok && truthy(r.value); }
  const rows = (Array.isArray(cond.rows) ? cond.rows : []).filter(r => r && typeof r === "object" && typeof r.v === "string" && r.v);   // (une ligne mal formée ne compte pas)
  if (!rows.length) return true;
  const env = envOf(it, x);
  const one = r => { try { return !!(OPS[r.op] || OPS["="])(env(r.v), r.val); } catch { return false; } };
  return cond.mode === "any" ? rows.some(one) : rows.every(one);
}
const hasCond = c => !!c && typeof c === "object" && ((typeof c.expr === "string" && !!c.expr.trim()) || (Array.isArray(c.rows) ? c.rows : []).some(r => r && typeof r === "object" && r.v));

/* ------------------------------------------------------------------ style */
const st = D.createElement("style");
st.id = "bo-plus-style";
st.textContent = `
.bo-out{display:none!important}
#stepConfig>[data-bo-rule="hide"]{display:none!important}
.card .bo-tags{display:flex;flex-wrap:wrap;gap:4px;margin:2px 0}
.bo-tag{display:inline-block;padding:0 7px;border-radius:99px;font-size:11px;font-weight:700;line-height:1.6;border:1px solid var(--c,var(--line));color:var(--c,var(--muted));background:color-mix(in srgb,var(--c,transparent) 12%,transparent)}
.card .badges .bo-badge{background:var(--c,#2563eb);color:#fff}
.bo-msgs{display:flex;flex-direction:column;gap:6px;margin:0 0 10px}
.bo-msg{padding:9px 12px;border-radius:10px;font-weight:600;font-size:13.5px;border:1px solid var(--c,var(--line));background:color-mix(in srgb,var(--c,var(--yellow)) 16%,transparent)}
.stat.bo-tile .sub{font-size:11.5px;color:var(--muted);margin-top:2px}
.bo-viewbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 12px;padding:8px 12px;border:1px solid var(--red);border-radius:12px;background:var(--accent-bg);font-weight:600;font-size:13.5px}
.bo-viewbar button{margin-left:auto;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:99px;padding:4px 12px;font:inherit;font-size:12.5px;cursor:pointer}
.bo-filt{border-top:1px solid var(--line);margin-top:6px;padding-top:6px;display:flex;flex-direction:column;gap:2px}
.bo-filt-t{font-size:11.5px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.sidebar .bo-vlink.on{background:var(--accent-bg);color:var(--red);font-weight:700}`;
(D.head || D.documentElement).append(st);
const col = c => /^#[0-9a-f]{3,8}$/i.test(c || "") ? `style="--c:${c}"` : "";

/* ------------------------------------------------------------------ 2 et 3. sur les cartes : règles (étiquettes, pastilles, couleur) */
const memo = new WeakMap();   // fiche → { stamp, acts } (les fiches sont recréées à chaque rechargement des données)
const rulesFor = t => (cfg().auto || []).filter(r => r && !r.off && (r.acts || []).length && (!(r.types || []).length || r.types.includes(t)));
function actsOf(it) {
  let m = memo.get(it);
  if (!m || m.stamp !== stamp) { const acts = []; for (const r of rulesFor(itemType(it))) if (test(r.cond, it)) acts.push(...r.acts.map(a => ({ ...a, text: a.text != null ? fill(a.text, it) : "" }))); m = { stamp, acts }; memo.set(it, m); }
  return m.acts;
}
let byId = new Map(), byRef = null;
const itemOf = id => { if (byRef !== state.items) { byRef = state.items; byId = new Map(state.items.map(i => [i.id, i])); } return byId.get(id); };
function cardRules() {
  const box = D.getElementById("items");
  if (!box) return;
  const any = (cfg().auto || []).some(r => !r.off);
  if (!any && !box.querySelector(".bo-tags,.bo-badge,[data-bo-card]")) return;
  for (const c of all(".card[data-id]", box)) {
    const it = itemOf(c.dataset.id), acts = it && any ? actsOf(it) : [];
    const tags = acts.filter(a => a.k === "tag" && a.text).map(a => `<span class="bo-tag" ${col(a.color)}>${esc(a.text)}</span>`).join("");
    let tb = c.querySelector(":scope > .body > .bo-tags");
    if (!tags) tb?.remove();
    else { if (!tb) { tb = D.createElement("div"); tb.className = "bo-tags bo-x"; (c.querySelector(":scope > .body > .name") || c.querySelector(".body"))?.after(tb); }
      if (tb._sig !== tags) { tb._sig = tags; tb.innerHTML = tags; } }
    const bd = acts.filter(a => a.k === "badge" && a.text).map(a => `<span class="badge bo-badge bo-x" ${col(a.color)}>${esc(a.text)}</span>`).join(""), bx = c.querySelector(".pic .badges");
    if (bx && (bx._boSig || "") !== bd) { bx._boSig = bd; all(".bo-badge", bx).forEach(n => n.remove()); if (bd) bx.insertAdjacentHTML("beforeend", bd); }
    const cs = acts.filter(a => a.k === "card").pop(), sig = cs ? (cs.bg || "") + "|" + (cs.border || "") : "";
    if ((c.dataset.boCard || "") !== sig) { c.style.background = cs?.bg || ""; c.style.borderColor = cs?.border || ""; if (sig) c.dataset.boCard = sig; else delete c.dataset.boCard; }
  }
}

/* ------------------------------------------------------------------ 2 et 3. sur la fiche : champs calculés, messages, blocs masqués */
function draftItem() {   // la fiche ouverte (enregistrée) ; sinon ce qu'on sait de celle qu'on est en train d'ajouter
  const own = ownItem(); if (own) return own;
  const d = state.draft; if (!d) return null;
  return { kind: d.kind || "set", number: d.info?.number || "", quantity: 1, info: d.info || {}, list_id: D.getElementById("cfgList")?.value || "", _new: true };
}
function sheetPlus() {
  const form = D.getElementById("stepConfig");
  if (!form || form.hidden || !app() || !state.draft || modal.hidden) return;
  const it = draftItem(); if (!it) return;
  const x = B._.xvals(), c = cfg();
  for (const o of all("[data-calc]", form)) {
    const f = (c.calcs || []).find(f => f.id === o.dataset.calc), r = f ? calc(f.expr, it, x) : { ok: false, error: "Calcul supprimé" };
    const t = r.ok ? show(r.value, f.fmt) || "—" : "⚠ " + r.error;
    if (o.textContent !== t) o.textContent = t;
  }
  const acts = [];
  if (!it._new) for (const r of rulesFor(itemType(it))) if (test(r.cond, it, x)) acts.push(...r.acts.map(a => ({ ...a, text: a.text != null ? fill(a.text, it, x) : "" })));
  const msgs = acts.filter(a => a.k === "msg" && a.text).map(a => `<div class="bo-msg" ${col(a.color)}>${esc(a.text)}</div>`).join("");
  let mb = form.querySelector(":scope > .bo-msgs");
  if (!msgs) mb?.remove();
  else { if (!mb) { mb = D.createElement("div"); mb.className = "bo-msgs bo-x"; mb.dataset.boKey = "bo-msgs"; form.prepend(mb); } if (mb._sig !== msgs) { mb._sig = msgs; mb.innerHTML = msgs; } }
  const hide = new Set(acts.filter(a => a.k === "hide" && a.block).map(a => a.block));
  for (const b of form.children) { const on = hide.has(b.dataset.boKey); if ((b.dataset.boRule === "hide") !== on) { if (on) b.dataset.boRule = "hide"; else delete b.dataset.boRule; } }
}
let inT = 0;
D.addEventListener("input", e => { if (!e.target.closest?.("#stepConfig")) return; clearTimeout(inT);   // une saisie sur la fiche : calculs et règles suivent
  inT = setTimeout(() => { try { B._.readInputs(D.getElementById("stepConfig")); sheetPlus(); } catch (er) { console.warn("BO+ fiche", er); } }, 150); }, true);
D.addEventListener("change", e => { if (e.target.closest?.("#stepConfig")) setTimeout(() => { try { sheetPlus(); } catch {} }, 60); }, true);
function cardCalc(f, it) {   // ligne d'un champ calculé sur une carte
  const r = calc(f.expr, it); if (!r.ok) return "";
  const t = show(r.value, f.fmt); return t ? (f.label ? f.label + " : " : "") + t : "";
}

/* ------------------------------------------------------------------ 4. tuiles : totaux personnalisés */
let shownSig = "", shownList = [];
function shown() {   // les fiches de la liste affichée (comme les tuiles d'origine)
  const sig = stamp + "|" + state.current + "|" + (state.subDirect || "") + "|" + state.items.length;
  if (byRef !== state.items || sig !== shownSig) { itemOf(""); shownSig = sig; try { shownList = shownOf(state.current).filter(i => i.kind !== "part"); } catch { shownList = []; } }
  return shownList;
}
const special = () => [STATS, NOV].includes(state.current) || !!g("isPartsList", state.current);
let tileSig = "", tileHtml = "";
function tiles() {
  const box = D.getElementById("stats");
  if (!box) return;
  const want = (cfg().tiles || []).filter(t => t && !t.off && t.label);
  if (!want.length || special() || box.hidden) { all(".bo-tile", box).forEach(n => n.remove()); return; }
  const list = shown(), sig = shownSig + "|" + list.length;
  if (sig !== tileSig) {
    tileSig = sig;
    tileHtml = want.map(t => {
      const its = hasCond(t.cond) ? list.filter(i => test(t.cond, i)) : list;
      let val, n = its.length;
      if (t.agg === "count" && !String(t.expr || "").trim()) val = its.reduce((s, i) => s + (i.quantity || 1), 0);
      else { const vs = its.map(i => calc(t.expr || "{valeur}", i)).filter(r => r.ok && num(r.value) != null).map(r => num(r.value)); n = vs.length;
        val = !vs.length ? null : t.agg === "avg" ? vs.reduce((s, v) => s + v, 0) / vs.length : t.agg === "min" ? Math.min(...vs) : t.agg === "max" ? Math.max(...vs) : t.agg === "count" ? vs.length : vs.reduce((s, v) => s + v, 0); }
      return `<div class="stat bo-tile bo-x" data-bo-tile="${esc(t.id)}"><div class="lbl">${esc(t.label)}</div><div class="val">${esc(val == null ? "—" : show(val, t.fmt || (t.agg === "count" ? "entier" : "nombre")))}</div><div class="sub">${n} fiche${n > 1 ? "s" : ""}</div></div>`;
    }).join("");
  }
  const have = all(".bo-tile", box);
  if (have.length !== want.length || box._boTiles !== tileSig) { have.forEach(n => n.remove()); box.insertAdjacentHTML("beforeend", tileHtml); box._boTiles = tileSig; }
}

/* ------------------------------------------------------------------ 5. tris, filtres, vues */
let filtOn = new Set();
try { filtOn = new Set(JSON.parse(localStorage.getItem("bo-filt") || "[]")); } catch {}
let view = null, viewFor = "";   // vue enregistrée ouverte (et la liste où elle l'a été)
const cardItem = c => c.dataset.id ? itemOf(c.dataset.id) : c.dataset.altof ? itemOf(c.dataset.altof) : null;
function sorts() {
  const sel = D.getElementById("sort"); if (!sel) return;
  const want = (cfg().sorts || []).filter(s => s && s.id && s.label && String(s.expr || "").trim());
  all("option[data-bo]", sel).forEach(o => { if (!want.some(s => "bo:" + s.id === o.value)) o.remove(); });
  for (const s of want) { let o = all("option[data-bo]", sel).find(o => o.value === "bo:" + s.id);
    if (!o) { o = D.createElement("option"); o.value = "bo:" + s.id; o.dataset.bo = "1"; sel.append(o); }
    const t = "★ " + s.label; if (o.textContent !== t) o.textContent = t; }
  const saved = state.sortBy?.[state.current];   // tri personnalisé retenu pour cette liste (l'application ne le connaissait pas encore au chargement)
  if (saved && String(saved).startsWith("bo:") && sel.value !== saved && want.some(s => "bo:" + s.id === saved) && !g("isWish", state.current)) sel.value = saved;
  try {   // le menu « ⇅ Tri » de l'application (rempli depuis cette liste) : tenu à jour quand vos tris changent (une seule tentative par état)
    const pop = D.getElementById("sortPop");
    if (pop && typeof syncSortMenu === "function") {
      const want2 = [...sel.options].filter(o => !o.hidden && !o.disabled).map(o => o.value + "\n" + o.textContent.trim()).join("|") + "||" + sel.value;
      const have = [...pop.querySelectorAll("input")].map(i => i.value + "\n" + i.parentElement.textContent.trim()).join("|") + "||" + (pop.querySelector("input:checked")?.value ?? "");
      if (want2 !== have && pop._boTried !== want2) { pop._boTried = want2; syncSortMenu(); }
    }
  } catch {}
  const cur = want.find(s => "bo:" + s.id === sel.value), grid = D.querySelector("#items .grid");
  if (!cur || !grid) return;
  const sig = cur.id + "|" + stamp + "|" + grid.children.length + "|" + (cur.dir || "");
  if (grid.dataset.boSort === sig) return;
  const rows = [...grid.children].map((c, k) => { const it = cardItem(c), r = it ? calc(cur.expr, it) : null; return { c, k, v: r && r.ok && !isZ(r.value) ? r.value : null }; });
  const dir = cur.dir === "asc" ? 1 : -1;
  rows.sort((a, b) => a.v == null || b.v == null ? (a.v == null) - (b.v == null) || a.k - b.k : (compare("<", a.v, b.v) ? -1 : compare(">", a.v, b.v) ? 1 : 0) * dir || a.k - b.k);   // les vides à la fin
  rows.forEach(r => grid.append(r.c));
  grid.dataset.boSort = sig;
}
function filters() {
  const want = [...(cfg().filters || []).filter(f => f && f.id && f.label),   // vos filtres, puis vos étiquettes cochées « proposer dans ⚙️ Filtres »
    ...((cfg().tags || {}).add || []).filter(t => t && t.id && t.label && t.filter && !t.off).map(t => ({ id: "tag-" + t.id, label: (t.icon ? t.icon + " " : "") + t.label, cond: t.cond }))], pop = D.getElementById("filtPop"), box = D.getElementById("items");
  for (const id of [...filtOn]) if (!want.some(f => f.id === id)) filtOn.delete(id);
  if (pop) {   // cases « Mes filtres » dans le menu ⚙️ Filtres (redessiné par l'application à chaque affichage)
    const have = pop.querySelector(".bo-filt");
    if (!want.length) have?.remove();
    else { const list = shown(), html = `<div class="bo-filt-t">Mes filtres</div>` + want.map(f => `<label class="moc-chk"><input type="checkbox" data-bo-filt="${esc(f.id)}" ${filtOn.has(f.id) ? "checked" : ""}> ${esc(f.label)}
        <span class="muted small">${list.filter(i => test(f.cond, i)).length}</span></label>`).join(""), sig = shownSig + "|" + [...filtOn].join(",");
      if (!have || have._sig !== sig) { have?.remove(); const d = D.createElement("div"); d.className = "bo-filt bo-x"; d._sig = sig; d.innerHTML = html; pop.append(d); } }
  }
  if (view && state.current !== viewFor) view = null;   // on a changé de liste : la vue est quittée
  const v = view && (cfg().views || []).find(x => x.id === view);
  if (view && !v) view = null;
  const conds = [...want.filter(f => filtOn.has(f.id)).map(f => f.cond), ...(v && hasCond(v.cond) ? [v.cond] : [])];
  let n = 0;
  if (box) for (const c of all(".grid > .card", box)) { const it = cardItem(c), out = conds.length > 0 && !(it && conds.every(k => test(k, it)));
    if (c.classList.contains("bo-out") !== out) c.classList.toggle("bo-out", out); if (!out && c.dataset.id) n++; }
  D.getElementById("filtMenu")?.classList.toggle("bo-on", filtOn.size > 0);
  let bar = D.querySelector(".bo-viewbar");   // bandeau de la vue ouverte
  if (!v || !box) bar?.remove();
  else { if (!bar) { bar = D.createElement("div"); bar.className = "bo-viewbar bo-x"; bar.innerHTML = `<span></span><button type="button">✕ Quitter la vue</button>`; bar.querySelector("button").onclick = () => { view = null; schedule(); }; box.before(bar); }
    const t = `🔎 Vue « ${v.label} » — ${n} fiche${n > 1 ? "s" : ""}`; if (bar.firstChild.textContent !== t) bar.firstChild.textContent = t; }
}
D.addEventListener("change", e => { const c = e.target.closest?.("[data-bo-filt]"); if (!c) return;
  c.checked ? filtOn.add(c.dataset.boFilt) : filtOn.delete(c.dataset.boFilt);
  try { localStorage.setItem("bo-filt", JSON.stringify([...filtOn])); } catch {}
  schedule(); });
function openView(id) {
  const v = (cfg().views || []).find(x => x.id === id);
  if (!v) return g("toast", "Cette vue n'existe plus");
  g("setMenu", false);
  state.current = v.list && state.lists.some(l => l.id === v.list) ? v.list : ALL; state.subDirect = null; try { state.selected.clear(); } catch {}
  view = v.id; viewFor = state.current;
  try { toggleView(["sets", "figs"].includes(v.view) ? v.view : "all"); } catch { render(); }   // (réaffiche la liste)
  viewFor = state.current;
  const sel = D.getElementById("sort");
  if (v.sort && sel && [...sel.options].some(o => o.value === v.sort) && sel.value !== v.sort) { sel.value = v.sort; sel.dispatchEvent(new Event("change", { bubbles: true })); }
  scrollTo(0, 0); schedule();
}
function viewLinks() {   // les vues dans le menu de gauche
  const sb = D.getElementById("sidebar"); if (!sb) return;
  const want = (cfg().views || []).filter(v => v && v.id && v.label && v.menu !== false);
  all(":scope > .bo-vlink", sb).forEach(a => { if (!want.some(v => v.id === a.dataset.boView)) a.remove(); });
  for (const v of want) { let a = all(":scope > .bo-vlink", sb).find(x => x.dataset.boView === v.id);
    if (!a) { a = D.createElement("button"); a.type = "button"; a.className = "nav-item bo-vlink bo-x"; a.dataset.boView = v.id; a.dataset.boKey = "bo-vue-" + v.id; a.innerHTML = `<span class="nm"></span>`;
      a.onclick = () => openView(a.dataset.boView); (D.getElementById("shareNav") || D.getElementById("wishNav") || sb.lastElementChild).after(a); }
    const t = "🔎 " + v.label; if (a.firstChild.textContent !== t) a.firstChild.textContent = t;
    a.classList.toggle("on", view === v.id); }
}

/* ------------------------------------------------------------------ 📝 règles « si… alors » → tâches à faire (vraies tâches, marquées par leur règle) */
let rtSent = "", rtTimer = 0;
function ruleTodos() {
  if (!app() || B._.admin() || B._.PUBLIC || W.BQ_DEMO || !Array.isArray(state.items) || !state.items.length) return;   /* (jamais dans l'aperçu du back office : son brouillon) */
  const want = {}, rules = (cfg().auto || []).filter(r => r && !r.off && (r.acts || []).some(a => a.k === "todo"));
  for (const it of state.items) {
    if (it.kind === "part") continue;
    const t = itemType(it), out = [];
    for (const r of rules) {
      if ((r.types || []).length && !r.types.includes(t)) continue;
      let ok = false; try { ok = test(r.cond, it); } catch {}
      if (ok) for (const a of r.acts) if (a.k === "todo") out.push({ rule: r.id, cat: a.cat || "Autres", note: (a.text != null ? fill(a.text, it) : "") || r.label || "À faire" });
    }
    if (out.length) want[it.id] = out;
  }
  const have = {}; for (const it of state.items) { const ts = (it.todos || []).filter(t => t && t.rule).map(t => ({ rule: t.rule, cat: t.cat, note: t.note })); if (ts.length) have[it.id] = ts; }
  const sig = JSON.stringify(want);
  if (sig === JSON.stringify(have) || sig === rtSent) return;   /* (déjà à jour, ou déjà envoyé) */
  rtSent = sig;
  fetch("/api/rule-todos", { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ items: want }) })
    .then(r => r.json()).then(r => { if (r && r.changed && typeof load === "function") load(); }).catch(() => { rtSent = ""; });
}
HOOKS.refresh.push(() => { clearTimeout(rtTimer); rtTimer = setTimeout(() => { try { ruleTodos(); } catch (e) { console.warn("BO+ tâches", e); } }, 2500); });

/* ------------------------------------------------------------------ branchement sur bo.js */
HOOKS.apply.push(() => { stamp++; asts.clear(); tileSig = ""; shownSig = ""; });
HOOKS.refresh.push(() => {
  if (!app()) return;
  const step = (name, f) => { try { f(); } catch (e) { console.warn("BO+ " + name, e); } };
  step("vues", viewLinks); step("règles", cardRules); step("tuiles", tiles); step("filtres", filters); step("tris", sorts); step("fiche", sheetPlus);
});
HOOKS.sheet.push(() => sheetPlus());

/* ------------------------------------------------------------------ pour le back office (aperçu) et le reste du site */
const sample = id => (id && itemOf(id)) || ownItem() || state.items.find(i => i.kind !== "part" && !i._in) || state.items[0] || null;
B.plus = {
  cardCalc, openView, calc, show, test, fill, itemOf,
  vars() {   // toutes les variables utilisables dans une formule
    const c = cfg();
    return [...Object.entries(BUILT).map(([id, [label, fmt]]) => ({ id, label, fmt, group: "La fiche" })),
      ...(c.fields || []).filter(f => f.id).map(f => ({ id: f.id, label: f.label || f.id, fmt: FFMT[f.type] || "texte", group: "Mes champs", opts: f.opts, type: f.type })),
      ...(c.calcs || []).filter(f => f.id).map(f => ({ id: f.id, label: f.label || f.id, fmt: f.fmt || "", group: "Mes calculs" })),
      ...(c.vars || []).filter(f => f.id).map(f => ({ id: f.id, label: f.label || f.id, fmt: "", group: "Mes variables" }))];
  },
  fns: () => Object.values(FN).map(f => ({ sig: f.sig, doc: f.doc })),
  blocks: () => { const f = D.getElementById("stepConfig"); return f && !f.hidden ? [...f.children].map(c => c.dataset.boKey).filter(Boolean) : []; },
  try(expr, fmt, id) {   // essai d'une formule sur une fiche d'exemple (celle qui est ouverte, sinon la première)
    if (!app()) return { ok: false, error: "L'aperçu doit afficher le site" };
    const it = sample(id); if (!it) return { ok: false, error: "Aucune fiche pour essayer" };
    const r = calc(expr, it, it === ownItem() ? B._.xvals() : undefined);
    return r.ok ? { ok: true, value: r.value, text: show(r.value, fmt) || "(vide)", on: B._.nameOf(it.id) } : { ...r, on: B._.nameOf(it.id) };
  },
  count(cond) {   // combien de fiches remplissent la condition (toute la collection)
    if (!app()) return null;
    const its = state.items.filter(i => i.kind !== "part");
    return { n: its.filter(i => test(cond, i)).length, total: its.length };
  },
  table(cols) {   // tableau de toutes les fiches (export CSV) : cols = identifiants de variables
    if (!app()) return null;
    const vs = this.vars(), its = state.items.filter(i => i.kind !== "part");
    return { head: ["id", ...cols.map(c => vs.find(v => v.id === c)?.label || c)],
      rows: its.map(i => { const env = envOf(i); return [i.id, ...cols.map(c => { try { const v = env(c); return Array.isArray(v) ? v.join(", ") : v ?? ""; } catch { return ""; } })]; }) };
  },
};
schedule();
})();

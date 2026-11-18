// Captures d'écran de la NOTICE DU BACK OFFICE, prises sur une instance TEMPORAIRE : données d'exemple (seed/data), mots de passe jetables,
// port local 8767, dossier de données effacé à la fin. Jamais la vraie collection.
// Usage : node docs/captures_bo.js   → docs/captures/bo-*.jpg        (ONLY=bo-pages,bo-images : refaire seulement celles-là)
const { launch, connect, tab } = require("./cdp.js"), fs = require("fs"), path = require("path"), os = require("os"), http = require("http"), crypto = require("crypto"), { spawn } = require("child_process");
const ROOT = path.dirname(__dirname), OUT = path.join(__dirname, "captures"), PORT = 8767, BASE = "http://127.0.0.1:" + PORT;
const sleep = ms => new Promise(r => setTimeout(r, ms)), J = JSON.stringify;
const ping = () => new Promise(ok => http.get(BASE + "/api/ping", r => { r.resume(); ok(r.statusCode > 0); }).on("error", () => ok(false)));   // (installation neuve : le serveur répond 401 tant que le mot de passe n'est pas créé — il est là, c'est ce qui compte)
fs.mkdirSync(OUT, { recursive: true });

/* réglages d'exemple montrés dans les captures (étiquettes, calcul, règle, tuile, vue, page, champ, lien, raccourci) */
const CFG = {
  tags: { add: [{ id: "t1", label: "Plus de 10 €", icon: "💰", color: "#15803d", border: "#15803d", cond: { rows: [{ v: "valeur", op: ">", val: "10" }] }, filter: true },
    { id: "t2", label: "Avant 2024", icon: "🕰️", kind: "badge", bg: "#7c3aed", color: "#ffffff", cond: { rows: [{ v: "annee", op: "<", val: "2024" }] } }], over: { "t-moc": { text: "Création", icon: "🎨" } } },
  fields: [{ id: "emplacement", label: "Emplacement", type: "text", help: "Où le set est rangé ou exposé" }],
  links: [{ id: "l1", label: "BrickLink", url: "https://www.bricklink.com/v2/search.page?q={numero}" }],
  calcs: [{ id: "plus_value", label: "Plus-value", expr: "{valeur} - sivide({prix_achat}; 0)", fmt: "euros", card: true }],
  auto: [{ id: "r1", label: "Fiche précieuse", cond: { rows: [{ v: "valeur", op: ">", val: "100" }] }, acts: [{ k: "msg", text: "Fiche précieuse : pensez à l'assurer.", color: "#b45309" }, { k: "card", border: "#b45309" }] }],
  tiles: [{ id: "ti1", label: "Valeur moyenne", agg: "avg", expr: "{valeur}", fmt: "euros" }],
  views: [{ id: "v1", label: "Précieux", cond: { rows: [{ v: "valeur", op: ">", val: "100" }] } }],
  sorts: [{ id: "s1", label: "Prix par pièce", expr: "{valeur} / {pieces}", dir: "asc" }],
  pages: [{ id: "p1", title: "Tableau de bord", icon: "📊", slug: "tableau-de-bord", blocks: [{ id: "a", k: "total", text: "Fiches", agg: "count", w: 3 }, { id: "b", k: "total", text: "Valeur totale", agg: "sum", expr: "{valeur}", fmt: "euros", w: 3 },
    { id: "c", k: "total", text: "Valeur moyenne", agg: "avg", expr: "{valeur}", fmt: "euros", w: 3 }, { id: "d", k: "note", text: "Bienvenue ! Cette page est **la vôtre** : ajoutez-y ce que vous voulez.", color: "#2563eb" },
    { id: "e", k: "titre", text: "Les fiches les plus chères", level: 3 }, { id: "f", k: "fiches", sort: "valeur", limit: 8 }, { id: "g", k: "titre", text: "Derniers ajouts", level: 3 },
    { id: "h", k: "tableau", cols: ["numero", "nom", "annee", "valeur"], sort: "date_ajout", limit: 10 }] }],
  behav: { keys: [{ id: "k1", key: "n", act: { k: "new" } }, { id: "k2", key: "t", act: { k: "page", v: "p1" } }] },
};
const pick = sel => `BO.pickSel(${J(sel)})`;
const scrollTo = title => `[...document.querySelectorAll("#panel .card h3, #panel h2")].find(h => h.innerText.trim() === ${J(title)})?.scrollIntoView({ block: "start" })`;
const clickBtn = (txt, root = "#panel") => `[...document.querySelectorAll(${J(root + " button")})].find(b => b.innerText.includes(${J(txt)}))?.click()`;
/* les étapes : name (fichier), panel (rubrique), js (dans l'écran du back office), pjs (dans l'aperçu), wait (ms), puis (js joué après l'attente) */
const STEPS = [
  { name: "bo-accueil", panel: "accueil" },
  { name: "bo-souris", panel: "souris", pjs: pick("#btnAdd"), wait: 1200 },
  { name: "bo-souris-icone", panel: "souris", pjs: pick("#btnAdd"), wait: 900, puis: `(() => { const s = [...document.querySelectorAll("#panel .card")].find(c => c.querySelector("h3")?.innerText === "Icône ou image").querySelector("select"); s.value = "ico"; s.dispatchEvent(new Event("change")); })(); await sleep(700); ${scrollTo("Icône ou image")}`,
    after: `change(c => { delete c.rules; })` },
  { name: "bo-deplacer", panel: "souris", js: `setMode("move")`, wait: 900, after: `setMode("use")` },
  { name: "bo-apparence", panel: "apparence" },
  { name: "bo-boutons", panel: "boutons" },
  { name: "bo-textes", panel: "textes" },
  { name: "bo-etiquettes", panel: "etiquettes", pjs: `toggleView("all"); document.querySelector("#items").scrollIntoView()`, wait: 1500 },
  { name: "bo-etiquettes-origine", panel: "etiquettes", js: `BOX.ui.tag("t-moc"); draw()`, wait: 700, puis: scrollTo("Étiquettes de l'application (sous le nom)"), after: `BOX.ui.tag("")` },
  { name: "bo-fiches", panel: "fiches", wait: 3500 },
  { name: "bo-champs", panel: "champs", wait: 1500 },
  { name: "bo-liens", panel: "liens", wait: 1200 },
  { name: "bo-cartes", panel: "cartes", pjs: `BO.close(); document.querySelector("#items").scrollIntoView()`, wait: 1200 },
  { name: "bo-menu", panel: "menu", pjs: `scrollTo(0, 0)`, wait: 1200 },
  { name: "bo-pages", panel: "pages", js: `BOX.ui.page(""); draw()` },
  { name: "bo-page-edition", panel: "pages", js: `BOX.ui.page("p1"); BOX.ui.block("f"); draw(); BOX.ui.showPage("p1")`, wait: 2500, puis: scrollTo("Les blocs de la page (8)"), after: `BOX.ui.page(""); BOX.ui.block("")`, pafter: `BO.max.closePage()` },
  { name: "bo-reglages", panel: "reglages", js: clickBtn("Ouvrir la page Réglages"), wait: 4000, pafter: `BO.max.closeSettings()` },
  { name: "bo-comportements", panel: "comportements" },
  { name: "bo-comportements-figurines", panel: "comportements", puis: scrollTo("Figurines identiques") },
  { name: "bo-images", panel: "images", wait: 1800 },
  { name: "bo-calculs", panel: "calculs", wait: 1200 },
  { name: "bo-regles", panel: "regles", wait: 1200 },
  { name: "bo-tuiles", panel: "tuiles", pjs: `scrollTo(0, 0)`, wait: 1200 },
  { name: "bo-vues", panel: "vues", wait: 1200 },
  { name: "bo-donnees", panel: "donnees", wait: 1500 },
  { name: "bo-catalogue", panel: "catalogue", wait: 1500 },
  { name: "bo-tableur", panel: "tableur", wait: 1200 },
  { name: "bo-modifs", panel: "modifs" },
  { name: "bo-historique", panel: "historique" },
  { name: "bo-sauvegardes", panel: "sauvegardes", wait: 1800 },
  { name: "bo-serveur", panel: "serveur", wait: 2200 },
  { name: "bo-securite", panel: "securite", wait: 1800 },
  { name: "bo-fichiers", panel: "fichiers", wait: 1800 },
  { name: "bo-parametres", panel: "parametres", wait: 1800 },
  { name: "bo-code", panel: "code", wait: 1800 },
  { name: "bo-publier", panel: "modifs", js: `document.querySelector("#btnPublish").click()`, wait: 900, after: `document.querySelector(".modal .modal-foot button")?.click()` },
];

(async () => {
  const data = fs.mkdtempSync(path.join(os.tmpdir(), "bq-notice-")), pwApp = "notice-" + crypto.randomBytes(9).toString("hex"), pwBo = "office-" + crypto.randomBytes(9).toString("hex");
  fs.cpSync(path.join(ROOT, "seed", "data"), data, { recursive: true });
  const srv = spawn("python3", ["-u", "server.py"], { cwd: ROOT, stdio: "ignore", env: { ...process.env, BQ_DATA: data, PORT: String(PORT), HOST: "127.0.0.1", BQ_NO_DEMO: "1", BQ_COPIE: "1", BQ_COOKIE: "bq_notice", PYTHONDONTWRITEBYTECODE: "1" } });
  let chrome = null;
  const stop = () => { try { srv.kill(); } catch {} try { chrome?.kill(); } catch {} try { fs.rmSync(data, { recursive: true, force: true }); } catch {} };
  process.on("exit", stop); for (const s of ["SIGINT", "SIGTERM", "SIGHUP"]) process.on(s, () => process.exit(1));
  for (let k = 0; k < 60 && !(await ping()); k++) await sleep(300);
  if (!(await ping())) throw new Error("Le serveur temporaire ne démarre pas");
  const { proc, ws } = await launch(9346); chrome = proc;
  const b = await connect(ws), S = await tab(b), errors = [];
  b.on(m => { if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description?.split("\n")[0]); });
  await S("Runtime.enable"); await S("Page.enable"); await S("Network.enable");
  await S("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await S("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
  // (instance temporaire lancée sans tâches de fond : son repère « copie de travail » et le rappel des clés API sont retirés des captures)
  await S("Page.addScriptToEvaluateOnNewDocument", { source: `document.addEventListener("DOMContentLoaded", () => { const s = document.createElement("style"); s.textContent = ".bo-ribbon, #copyTag, #keysBanner { display: none !important; }"; document.head.append(s); });` });
  const ev = async js => { const r = await S("Runtime.evaluate", { expression: `(async () => { const sleep = ms => new Promise(r => setTimeout(r, ms)); ${js} })()`, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; };
  const fev = js => ev(`const W = document.querySelector("#preview").contentWindow; return W.eval(${J(js)});`);
  const go = async (u, ms = 3000) => { await S("Page.navigate", { url: BASE + u }); await sleep(ms); };
  const ONLY = (process.env.ONLY || "").split(",").filter(Boolean), want = n => !ONLY.length || ONLY.includes(n);
  const shot = async name => { if (!want(name)) return; const r = await S("Page.captureScreenshot", { format: "jpeg", quality: 80 }); fs.writeFileSync(path.join(OUT, name + ".jpg"), Buffer.from(r.data, "base64")); console.log("✓", name); };
  const post = (u, body) => ev(`const r = await fetch(${J(u)}, { method: "POST", headers: { "Content-Type": "application/json" }, body: ${J(J(body))} }); if (!r.ok) throw new Error(${J(u)} + " → " + r.status + " " + await r.text()); return true;`);

  // installation neuve : mot de passe de l'application, puis porte du back office
  await go("/setup", 1500); await post("/api/setup", { password: pwApp });
  await go("/backoffice", 1500); await shot("bo-premiere-visite");
  await post("/api/bo/setup", { password: pwBo, compris: true });
  await S("Network.deleteCookies", { name: "bq_notice_office", url: BASE });
  await go("/backoffice", 1500); await shot("bo-connexion");
  await post("/api/bo/login", { password: pwBo });
  await go("/backoffice/secours", 1200); await shot("bo-secours");
  await go("/backoffice", 6000);
  await ev(`if (!document.querySelector("#expert").checked) document.querySelector("#expert").click(); replaceAll(${J(CFG)}); await sleep(1200);`);
  // deux images d'exemple dans la bibliothèque (dessinées ici même)
  await ev(`for (const [bg, t] of [["#d01012", "🧱"], ["#1d4ed8", "⭐"]]) { const c = document.createElement("canvas"); c.width = c.height = 160; const x = c.getContext("2d"); x.fillStyle = bg; x.beginPath(); x.roundRect(0, 0, 160, 160, 36); x.fill();
      x.font = "96px sans-serif"; x.textAlign = "center"; x.textBaseline = "middle"; x.fillText(t, 80, 88); const blob = await new Promise(r => c.toBlob(r, "image/png")); await BOX.xapi("image?label=" + encodeURIComponent(t === "🧱" ? "logo brique" : "étoile"), blob, true); } delete BOX.X.imgs;`);
  for (const st of STEPS.filter(s => want(s.name))) {
    try {
      await ev(`show(${J(st.panel)}); await sleep(500); ${st.js || ""}`);
      if (st.pjs) { await sleep(300); await fev(st.pjs); }
      await sleep(st.wait || 800);
      if (st.puis) { await ev(st.puis); await sleep(600); }
      await shot(st.name);
      if (st.after) await ev(st.after);
      if (st.pafter) await fev(st.pafter);
    } catch (e) { console.log("✗", st.name, String(e.message).split("\n")[0]); }
  }
  // le site lui-même, une fois les réglages publiés : page créée, étiquettes, lien « Back office » dans Réglages
  try {
    await ev(`await api("/api/bo/publish", { cfg, note: "notice", count: countAll() });`);
    await go("/", 6000); await ev(`toggleView("all"); await sleep(600); document.querySelector("#items").scrollIntoView(); window.scrollBy(0, -80);`); await sleep(900); await shot("bo-site-etiquettes");
    await ev(`BO.max.openPage("p1"); await sleep(1500);`); await shot("bo-site-page");
    await ev(`BO.max.closePage(); document.querySelector("#btnSettings").click(); await sleep(3500); document.querySelector('.settings-page [data-bo-set="back_office"]')?.scrollIntoView({ block: "center" });`); await sleep(700); await shot("bo-site-reglages");
  } catch (e) { console.log("✗ site", String(e.message).split("\n")[0]); }
  if (errors.length) console.log("Erreurs JS :", [...new Set(errors)].join(" | "));
  b.close(); process.exit(0);
})().catch(e => { console.error(e.message); process.exit(1); });

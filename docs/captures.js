// Captures d'écran du guide utilisateur, prises dans la DÉMO (jamais dans la vraie collection).
// Usage : node docs/captures.js [http://localhost:8765]   → docs/captures/*.jpg
// Chaque étape : du JavaScript joué dans la page (ouvrir une fenêtre, remplir une recherche…), puis une capture.
const { launch, connect, tab } = require("./cdp.js"), fs = require("fs"), path = require("path");
const BASE = process.argv[2] || "http://localhost:8765";
const OUT = path.join(__dirname, "captures");
fs.mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Remise à plat entre deux étapes : fenêtres fermées, liste « Toute la collection », menu replié, en haut de page
const RESET = `(() => { document.querySelectorAll("body > .modal:not(#modal)").forEach(m => m.remove()); modal.hidden = true;   // (#modal : la fenêtre des fiches, réutilisée)
  document.querySelectorAll(".act-menu, .action-menu").forEach(m => m.remove()); state.selected.clear();
  if (typeof setMenu === "function") setMenu(false); $("#filter").value = ""; toggleView("sets"); state.current = ALL; render(); scrollTo(0, 0); })()`;
const first = sel => `document.querySelector(${JSON.stringify(sel)})`;
const SUPRA_ID = "a00969b7593c";   // set de la démo (77260, figurine modifiée)

/* Les étapes : nom du fichier, script préparatoire, attente, défilement éventuel de la fenêtre ouverte */
// raccourcis utilisés dans les étapes
const SCROLL = (sel, y) => `document.querySelector(${JSON.stringify(sel)})?.scrollBy(0, ${y})`;   // faire défiler une fenêtre
const SHEET = "#modal .modal-box";   // la fenêtre des fiches
const TOP = "body > .modal:not(#modal):last-of-type .modal-box";   // la dernière fenêtre ouverte par-dessus
const CLICK = sel => `document.querySelector(${JSON.stringify(sel)})?.click()`;
const MENU = re => `[...document.querySelectorAll(".act-menu button, .action-menu button")].find(b => ${re}.test(b.textContent))?.click()`;

/* Les étapes : nom du fichier, script préparatoire, attente ; keep : sans remise à plat (suite de l'étape précédente) */
const STEPS = [
  // --- écran principal et menu
  { name: "accueil", js: `` },
  { name: "accueil-cartes", js: `scrollTo(0, 520)`, wait: 1200 },
  { name: "menu", js: `setMenu(true)` },
  { name: "menu-bas", js: `setMenu(true); await sleep(400); $("#sidebar").scrollTop = 99999`, wait: 800 },
  { name: "liste-actions", js: `state.current = "demosets"; render()` },
  { name: "liste-nouvelle", js: `${CLICK("#btnNewList")}`, wait: 1200 },
  { name: "selection", js: `const c = [...document.querySelectorAll("#items .card [data-sel]")].slice(0, 2); c.forEach(x => x.click()); await sleep(300); scrollTo(0, 400)`, wait: 1200 },
  { name: "recherche", js: `$("#filter").value = "Supra"; $("#filter").dispatchEvent(new Event("input"))`, wait: 1200 },
  // --- ajouter
  { name: "ajout-recherche", js: `openAdd(); $("#searchInput").value = "77256"; $("#searchForm").requestSubmit()`, wait: 6500 },
  { name: "ajout-fiche", js: `openAdd(); $("#searchInput").value = "77256"; $("#searchForm").requestSubmit(); await sleep(5000);
      [...document.querySelectorAll("#results *")].find(e => e.onclick && /77256-1/.test(e.textContent))?.click()`, wait: 6000 },
  { name: "ajout-fiche-bas", js: SCROLL(SHEET, 650), wait: 800, keep: true },
  { name: "ajout-figurine", js: `openAdd(); $("#searchInput").value = "Dark Vador"; $("#searchForm").requestSubmit()`, wait: 6000 },
  { name: "ajout-moc", js: `openCustom({})`, wait: 2000 },
  // --- la fiche d'un set
  { name: "fiche", js: `openEdit(SUPRA)`, wait: 3500 },
  { name: "fiche-milieu", js: SCROLL(SHEET, 650), wait: 900, keep: true },
  { name: "fiche-bas", js: SCROLL(SHEET, 1400), wait: 900, keep: true },
  { name: "fiche-figurine-menu", js: `openEdit(SUPRA); await sleep(3000); ${SCROLL(SHEET, 650)}; await sleep(500); ${CLICK("#figList [data-figmenu]")}`, wait: 1000 },
  { name: "fiche-apparence", js: `openEdit(SUPRA); await sleep(3000); ${SCROLL(SHEET, 300)}; await sleep(400); ${CLICK('#addBar [data-add="alt"]')}`, wait: 1000 },
  { name: "fiche-etiquette", js: `openEdit(SUPRA); await sleep(3000); ${CLICK("#cfgStatus [data-tagadd]")}`, wait: 1000 },   // menu « + Étiquette »
  { name: "accessoire-pieces", js: `openEdit(SUPRA); await sleep(3000); (state.draft.accessories ||= []).push({ name: "Mini-vaisseau", photo: "" }); drawAccessories(); await sleep(300);
      [...document.querySelectorAll("#accList [data-acc]")].pop()?.click(); await sleep(400); ${MENU("/Liste de pièces/")}; await sleep(500);
      const t = document.querySelector("body > .modal.over [data-t]"); if (t) t.value = "<INVENTORY><ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>3023</ITEMID><COLOR>11</COLOR><MINQTY>4</MINQTY></ITEM></INVENTORY>"`, wait: 900 },   // (brouillon : rien n'est enregistré)
  { name: "fiche-pieces", js: `openEdit(SUPRA); await sleep(3000); ${CLICK("#btnShowParts")}`, wait: 5000 },
  { name: "tarifs", js: `openEdit(SUPRA); await sleep(3000); ${CLICK("#btnTarifs")}`, wait: 2500 },
  { name: "evolution", js: `openEdit(SUPRA); await sleep(3000); ${CLICK("#btnEvo")}`, wait: 3500 },
  { name: "partage", js: `openEdit(SUPRA); await sleep(3000); ${CLICK("#modalShare")}`, wait: 2000 },
  { name: "tache-ajout", js: `openEdit(SUPRA); await sleep(3000); ${CLICK("#modalTodo")}`, wait: 1500 },
  // --- figurines et MOC
  { name: "figurines", js: `state.current = "demofigs"; toggleView("figs"); render()`, wait: 1500 },
  { name: "figurine-fiche", js: `for (const f of state.items.filter(i => i.kind === "fig").slice(0, 10)) {   // la 1re figurine (seule) dont toutes les images s'affichent
      modal.hidden = true; openEdit(f.id); await sleep(8000); document.querySelector("#modal .modal-box").scrollBy(0, 330); await sleep(1500);
      if (![...document.querySelectorAll("#modal img")].some(i => i.classList.contains("img-retry") || i.classList.contains("img-missing") || (i.complete && !i.naturalWidth))) break; }
      document.querySelector("#modal .modal-box").scrollTo(0, 0)`, wait: 1500 },
  { name: "figurine-pieces", js: SCROLL(SHEET, 330), wait: 1200, keep: true },
  { name: "figurine-copier", js: `document.querySelector("#modal .modal-box").scrollTo(0, 0); await sleep(400); ${CLICK("#btnDupFig")}`, wait: 900, keep: true },   // (la même fiche : menu « Copier ou déplacer »)
  // une figurine seule ET dans un set : une fiche d'essai (2 exemplaires seuls d'une figurine d'un set), retirée aussitôt la capture faite
  { name: "figurine-exemplaires", js: `const o = state.items.find(i => i.set_orig && i._in && kindOf(i.list_id) === "collection" && !(i._mods?.fig_swaps || []).length && !(i._mods?.accessories || []).length && !i._mods?.name);
      const a = await api("/api/items", { method: "POST", body: { kind: "fig", number: o.number, list_id: o.list_id, quantity: 2, condition: "occasion", no_price_ok: true, name_hint: itemName(o) } });
      window.__capTmp = a.id; await load(); openEdit(a.id); await sleep(6000); document.querySelector("#cfgInSets")?.scrollIntoView({ block: "center" })`, wait: 1500,
    after: `if (window.__capTmp) { const id = window.__capTmp; window.__capTmp = null; modal.hidden = true; await api("/api/items/delete", { method: "POST", body: { ids: [id] } }); await load(); }` },
  { name: "figurine-lot", js: `const lot = state.items.filter(i => i.kind === "fig" && !i.attached_to && !i.set_orig && kindOf(i.list_id) === "collection").sort((x, y) => (y.quantity || 1) - (x.quantity || 1))[0];
      openEdit(lot.id); await sleep(9000); document.querySelector("#figPartsBox")?.scrollIntoView({ block: "start" }); await sleep(600);
      document.querySelector("#figPartsList [data-menu]")?.click(); await sleep(600); ${MENU("/Modifier la quantité/")}`, wait: 1200 },   // « 🔢 Modifier la quantité » d'une pièce du lot
  { name: "moc", js: `state.current = "demomocs"; render()`, wait: 1500 },
  { name: "moc-fiche", js: `openEdit((state.items.find(i => i.kind === "custom" && i.custom_type !== "fig") || state.items.find(i => i.kind === "custom")).id)`, wait: 3500 },   // (un set MOC, sinon un MOC)
  { name: "moc-fiche-pieces", js: SCROLL(SHEET, 700), wait: 900, keep: true },
  // --- inventaires
  { name: "inventaire-nouveau", js: `${CLICK("#btnNewInv")}; await sleep(800); document.querySelector("body > .modal:last-of-type [data-q]").value = "Honda S2000";
      document.querySelector("body > .modal:last-of-type [data-f]").requestSubmit()`, wait: 12000 },
  { name: "inventaire-xml", js: `${CLICK("#btnNewInv")}; await sleep(800); ${CLICK("body > .modal:last-of-type [data-xmlbtn]")}`, wait: 1000 },
  { name: "inventaire", js: `${CLICK("#invNav [data-inv]")}`, wait: 5500 },
  { name: "inventaire-lignes", js: SCROLL(TOP, 760), wait: 1200, keep: true },
  { name: "inventaire-couleur", js: `${CLICK("#invNav [data-inv]")}; await sleep(5000); ${CLICK("body > .modal:last-of-type [data-swapbtn]")}`, wait: 2000 },
  // --- souhaits, à commander
  { name: "souhaits", js: `state.current = "demowish"; render()`, wait: 1500 },
  { name: "souhait-fiche", js: `openEdit(state.items.find(i => i.list_id === "demowish").id); await sleep(3000); ${SCROLL(SHEET, 380)}`, wait: 1200 },
  { name: "a-commander", js: `state.current = "demoparts"; render()`, wait: 2000 },
  { name: "piece-fiche", js: `openEdit(state.items.find(i => i.kind === "part").id)`, wait: 4000 },
  { name: "piece-ajout", js: `openPart({ list_id: "demoparts" })`, wait: 1500 },
  { name: "piece-ajout-resultats", js: `openPart({ list_id: "demoparts" }); await sleep(800); const m = document.querySelector("body > .modal:last-of-type");
      const q = m.querySelector("input[data-q]") || m.querySelector("input:not([type=file]):not([type=checkbox])"); q.value = "3001"; q.closest("form")?.requestSubmit()`, wait: 6000 },
  // --- autres pages
  { name: "nouveautes", js: `state.current = NOV; render()`, wait: 5000 },
  { name: "nouveautes-themes", js: `state.current = NOV; render(); await sleep(4000); ${CLICK("#novView [data-exth]")}`, wait: 2000 },
  { name: "a-construire", js: `state.current = UNBUILT; render()`, wait: 1500 },
  { name: "statistiques", js: `state.current = STATS; render()`, wait: 3000 },
  { name: "statistiques-courbe", js: `scrollTo(0, 700)`, wait: 1500, keep: true },
  { name: "taches", js: `openTodos()`, wait: 2000 },
  { name: "partagees", js: `openShares()`, wait: 2000 },
  // --- pages publiques
  { name: "page-publique", url: "/collection", wait: 4000 },
  { name: "page-publique-souhaits", url: "/wishlist", wait: 4000 },
  { name: "page-nouveautes", url: "/nouveautes", wait: 4000 },
];

// écrans annotés de la documentation technique (annotations.json) : capture + position de chaque zone
const ANNOT_FILE = path.join(__dirname, "annotations.json");   // (documentation technique, privée : absente de la version publiée)
const ANNOT = fs.existsSync(ANNOT_FILE) ? JSON.parse(fs.readFileSync(ANNOT_FILE, "utf8")).screens : [];
for (const a of ANNOT) STEPS.push({ name: a.name, js: a.setup || "", url: a.url || "/", wait: a.wait, marks: a.marks.map(m => m.sel) });   // (écran de l'appli : on y revient d'abord)

(async () => {
  const { proc, ws } = await launch(); const b = await connect(ws); const S = await tab(b);
  const errors = [];
  b.on(m => { if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description?.split("\n")[0]); });
  await S("Runtime.enable"); await S("Page.enable"); await S("Network.enable");
  // téléphone, thème sombre (celui de l'appli)
  await S("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 2, mobile: true });
  await S("Emulation.setTouchEmulationEnabled", { enabled: true });
  await S("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
  const host = new URL(BASE).hostname;
  await S("Network.setCookie", { name: "bq_demo", value: "d2", domain: host, path: "/" });   // la démo, pas ma collection
  const ev = async js => { const r = await S("Runtime.evaluate", { expression: `(async () => { const sleep = ms => new Promise(r => setTimeout(r, ms)); const SUPRA = window.__supra || (typeof state === "undefined" ? null : (window.__supra = __capPick(${JSON.stringify(SUPRA_ID)})));   /* pages publiques : pas de « state » */ ${js} })()`, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; };
  // la démo change ses fiches à chaque remise à zéro : la Supra si elle y est, sinon un set (modifié de préférence) qui a des figurines
  await S("Page.addScriptToEvaluateOnNewDocument", { source: `window.__capPick = id => { const ok = i => (i.kind || "set") === "set" && (i.info?.minifigs || []).length;
    const it = state.items.find(i => i.id === id) || state.items.find(i => ok(i) && i.set_mod) || state.items.find(ok); return it?.id; };
    window.__capFig = id => (state.items.find(i => i.id === id)?.info?.minifigs || [])[0]?.id;` });
  const go = async u => { await S("Page.navigate", { url: BASE + u }); await sleep(4500); };
  await go("/");
  if (!(await ev(`return typeof DEMO !== "undefined" && DEMO`))) throw new Error("Pas dans la démo : captures annulées");
  const ONLY = (process.env.ONLY || "").split(",").filter(Boolean);   // ONLY=fiche,tarifs : refaire seulement ces captures
  for (const st of STEPS.filter(x => !ONLY.length || ONLY.includes(x.name))) {
    try {
      if (st.url) await go(st.url);   // une page (publique, ou l'appli), puis éventuellement son script
      else if (!st.keep) { await ev(RESET + ";"); await sleep(300); }
      if (st.js) await ev(st.js);
      await sleep(st.wait ?? 1500);
      // pas de capture « cassée » : on attend que les images visibles soient chargées (10 s au plus)
      await ev(`for (let k = 0; k < 40; k++) {
        const imgs = [...document.querySelectorAll("img")].filter(i => { const b = i.getBoundingClientRect(); return b.width > 0 && b.bottom > 0 && b.top < innerHeight; });
        if (imgs.every(i => i.complete && (i.naturalWidth > 0 || i.classList.contains("img-missing")))) break;
        await sleep(250); }`);
      const r = await S("Page.captureScreenshot", { format: "jpeg", quality: 72 });
      fs.writeFileSync(path.join(OUT, st.name + ".jpg"), Buffer.from(r.data, "base64"));
      if (st.marks) {   // position (en pixels CSS de l'écran) de la première zone visible de chaque sélecteur
        const boxes = await ev(`return ${JSON.stringify(st.marks)}.map(sel => { const e = [...document.querySelectorAll(sel)].find(x => { const b = x.getBoundingClientRect(); return b.width > 0 && b.height > 0 && b.bottom > 0 && b.top < innerHeight; });
          if (!e) return null; const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height].map(Math.round); })`);
        fs.writeFileSync(path.join(OUT, st.name + ".json"), JSON.stringify({ w: 412, h: 915, boxes }));
      }
      console.log("✓", st.name);
    } catch (e) { console.log("✗", st.name, String(e.message).split("\n")[0]); }
    if (st.after) try { await ev(st.after); } catch {}   // ménage de l'étape (fiche d'essai retirée de la démo), même si elle a échoué
  }
  if (errors.length) console.log("Erreurs JS :", errors.join(" | "));
  b.close(); proc.kill(); process.exit(0);
})().catch(e => { console.error(e.message); process.exit(1); });

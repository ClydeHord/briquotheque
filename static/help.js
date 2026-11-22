/* © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver) */
/* ============================================================ « ? » : aide de la page (ou de la fenêtre) en cours
   Un petit « ? » entouré, discret, à côté de la flèche ↑ (toujours visible, partout). Il ouvre un calque : les boutons
   présents à l'écran sont entourés et numérotés, et la liste numérotée en bas explique chacun. Fenêtre sans aide écrite :
   les explications viennent des bulles (title) de ses boutons. Fichier à part (chargé après app.js). */
(() => {
  const H = {   // aide par page : [sélecteur, nom, explication]
    liste: ["Une liste de la collection", [
      ["#btnMenu", "Menu", "Les listes, À faire, inventaires, statistiques, réglages."],
      ["#topTotal", "Valeur totale", "La valeur estimée de toute la collection."],
      ["#topViews", "Raccourcis", "Tout, Sets, Figurines, Pièces… : changer de vue d'un appui."],
      ["#btnAdd", "+ (ajouter)", "Ajouter un set, une figurine ou un MOC : numéro, nom, photo, code-barres, ou un post Instagram."],
      ["#stats", "Tuiles", "Valeur, nombre de sets, de figurines, de pièces de cette liste."],
      ["#filter", "Filtre", "Ne montrer que ce qui contient ce texte : nom, numéro, thème."],
      ["#mocChkRow", "MOC uniquement", "Ne montrer que les MOC."],
      ["#modChkRow", "Modifiés uniquement", "Ne montrer que les sets et figurines dont des pièces ont été retirées ou remplacées."],
      ["#sort", "Tri", "Dernière modification, ajout, valeur, nom, numéro, année, vu sur Instagram…"],
      ["#items .card", "Une fiche", "Un appui l'ouvre. La case en haut à gauche la sélectionne (déplacer, copier, supprimer en lot). On peut la glisser sur une liste du menu."],
      ["#btnRename", "Renommer", "Changer le nom de cette liste."],
      ["#btnMoveList", "Ranger dans…", "Mettre cette liste dans une autre (sous-liste)."],
      ["#btnDeleteList", "Supprimer la liste", "La liste disparaît (ce qu'elle contient est demandé avant)."],
      ["#lnkPublic", "Version publique", "La page publique (lecture seule) de cette liste."],
    ]],
    souhaits: ["Liste de souhaits", [
      ["#btnAdd", "+ (ajouter)", "Ajouter un set ou une figurine souhaité."],
      ["#btnNovelties", "✨ Nouveautés", "Les sets à venir et les sorties récentes de LEGO.com."],
      ["#btnGiftList", "👀 À surveiller", "Les sets surveillés (prix, retrait prévu)."],
      ["#btnGiftLink", "Lien public", "Copier le lien de la page publique « À surveiller »."],
      ["#filter", "Filtre", "Ne montrer que ce qui contient ce texte."],
      ["#sort", "Tri", "Ordre d'affichage des souhaits."],
      ["#items .card", "Un souhait", "Prix magasin, neuf, occasion (drapeau : zone du prix). Un appui ouvre la fiche ; « ✔ Acquis » le passe dans la collection."],
    ]],
    commander: ["Commandes", [
      ["#btnAdd", "+", "Ajouter une pièce (référence, nom, photo) ou une figurine à commander."],
      ["#btnOrderBL", "Exporter en XML", "Copie dans le presse-papier, au format XML de BrickLink, les pièces encore à commander."],
      ["#btnCleanParts", "🧹 Nettoyer", "Retire de la liste ce qui est marqué reçu (✔ OK)."],
      ["#stats", "Tuiles", "Coût estimé (selon l'état voulu de chaque ligne), éléments, références, sets concernés."],
      ["#items .bl-cond", "État voulu", "N'importe, Neuf ou Occasion (any / new / used de BrickLink). N'importe : le neuf de France d'abord, sinon le moins cher."],
      ["#items .bl-go", "BrickLink ↗", "Les annonces de cet élément, dans la zone d'où vient le prix, à l'état voulu."],
      ["#items .pp-line", "Prix", "Neuf et occasion ; en gras : celui retenu pour le coût. Drapeau : Europe 🇪🇺 ou monde 🇺🇳 (sans drapeau : France)."],
      ["#items .bl-for", "Pour …", "Ouvre la fiche du set pour lequel la pièce est commandée."],
      ["#items .bl-q", "Quantité", "− / + : enregistré aussitôt (tant qu'elle n'est pas commandée)."],
      ["#items .inv-ok", "✔ OK", "Reçue (après l'export). « 🧹 Nettoyer » la retire ensuite."],
      ["#items .bl-del", "🗑️", "Retirer la ligne de la liste."],
    ]],
    fiche: ["La fiche", [
      ["#modalBack", "←", "Revenir à la recherche."],
      ["#modalRename", "✏️", "Changer le nom affiché de la fiche."],
      ["#modalShare", "🔗", "Lien de partage public de cette fiche (lecture seule)."],
      ["#modalTodo", "✅", "Tâches de la fiche (photo à refaire, pièce à trouver…)."],
      ["#modalSave", "💾", "Enregistrer et rester sur la fiche."],
      ["#modalClose", "✕", "Fermer (ce qui n'est pas enregistré est demandé)."],
      ["#btnTarifs", "💶 Tarifs", "Prix magasin, neuf, occasion et le détail BrickLink (ventes des 6 derniers mois, zone)."],
      ["#btnShowParts", "🔶 Pièces", "Toutes les pièces, avec leur prix."],
      ["#btnPlans", "📘 Plan", "La notice de montage LEGO."],
      ["#btnSwapParts", "🔁 Échanger des pièces", "Noter les pièces retirées ou remplacées (décote « modifié »)."],
      ["#btnAsPartial", "🧩 Set partiel", "Une partie du set seulement."],
      ["#btnIsMoc", "🛠️ Enregistrer comme MOC", "La photo n'est pas ce set : la garder comme MOC."],
      ["#cfgList", "Liste", "Dans quelle liste ranger cette fiche (figurine : aussi « Commandes »)."],
      ["#btnCfgNewList", "+", "Créer une liste sans quitter la fiche."],
      ["#cfgStatus .tag-add", "+ Étiquette", "Poser une étiquette sur la fiche (Complet, Amélioré, Modifié, Set partiel, MOC). Le ✕ à côté d'une étiquette la retire de cette fiche."],
      ["#cfgQty", "Quantité", "Nombre d'exemplaires identiques. Figurine aussi présente dans des sets : le total, sets compris."],
      ["#btnDupFig", "⧉ Copier / Déplacer", "Set, set partiel, MOC : une copie de la fiche. Figurine : copier un exemplaire, le ranger dans un set, le déplacer vers un autre set ou l'en sortir."],
      ['#addBar [data-add="acc"]', "+ 🗡️ Accessoire", "Une mini-construction (nom, photo). Sa liste de pièces (XML), facultative, lui donne un prix, ajouté à la valeur de la fiche."],
      ["#figList .fq-more", "⋯ (figurine du set)", "Quantité, voir la fiche, échanger des pièces, copier, déplacer, supprimer (pas dans la collection)."],
      ["#figPartsList .fq-more", "⋯ (pièce)", "Détail, commander, échanger, 🔢 modifier la quantité (lot de figurines), retirer."],
      ["#cfgInSets .in-set-row .set-step", "− / + d'un set", "Combien d'exemplaires de cette figurine sont dans ce set."],
      ["#cfgInSets .in-sets-solo", "Seules (sans set)", "Combien d'exemplaires de cette figurine ne sont dans aucun set."],
      ["#btnSeparate", "+ Exemplaire séparé", "Un autre exemplaire avec son propre état (boîte, pièces, notes)."],
      ["#cfgBox", "📦 Boîte", "Le set a sa boîte (plus-value)."],
      ["#cfgPlan", "📘 Plan", "Le set a son livret de plans."],
      ["#cfgUnbuilt", "🚧 À construire", "Le set n'est pas encore monté."],
      ["#btnEvo", "📈 Évolution", "L'historique du prix."],
      ["#modalGift", "👀", "À surveiller (souhait)."],
      ["#btnAcquired", "✔ Acquis", "Le souhait passe dans la collection."],
      ["#btnDeleteItem", "Supprimer", "Retirer la fiche (confirmation demandée)."],
      ["#btnSave", "Enregistrer / Ajouter", "Enregistrer la fiche dans la liste choisie."],
    ]],
    recherche: ["Ajouter", [
      ["#searchInput", "Recherche", "Numéro (75192, sw0001…) ou nom, en français ou en anglais."],
      ["#modal .find-photo", "Photo", "📷 photo de la boîte, du set monté ou d'une figurine ; 📁 fichier ; elle est reconnue automatiquement."],
      ["#btnIgAdd", "📸 Instagram", "Coller le lien d'un post Instagram : ses fiches sont repérées photo par photo."],
      ["#btnNoImage", "Ajouter sans rechercher", "Créer une fiche à la main (MOC, élément introuvable)."],
    ]],
    afaire: ["À faire", [
      ["[data-addfree]", "📌 Note libre", "Une tâche rattachée à aucune fiche."],
      [".todo-open", "Une tâche", "Un appui ouvre sa fiche."],
      ["[data-done], [data-fdone]", "✔ Fait", "La tâche est faite (« Annuler » possible un instant)."],
      ["[data-newcat]", "+ Catégorie", "Créer une catégorie de tâches."],
      ["[data-mgcat]", "⚙️ Gérer les catégories", "Renommer ou supprimer une catégorie (ses tâches vont dans « Autres »)."],
    ]],
    inventaire: ["Inventaire", [
      ["[data-s=\"ok\"]", "✔ OK", "La pièce est là."],
      ["[data-s=\"order\"]", "🛒 À commander", "Elle manque : elle partira dans « Commandes » (quantité avec − / +)."],
      ["[data-color]", "🎨", "Changer la couleur de cette pièce."],
      ["[data-otherpart]", "🔁", "La remplacer par une autre pièce (équivalents, recherche, photo)."],
      ["[data-s=\"x\"]", "✕", "Exclure la pièce (ne compte pas)."],
      ["[data-rowreset]", "↺", "Remettre la pièce comme au départ."],
    ]],
  };
  const TXT = {   // pages sans boutons à montrer : une explication
    stats: ["Statistiques", "Valeur et évolution de la collection, répartition par thème, année, état ; un appui sur une barre liste les sets concernés. En bas : les visites des pages publiques."],
    nov: ["Nouveautés", "Les sets à venir et les sorties récentes de LEGO.com, sans ceux déjà dans la collection. Un appui ouvre la fiche ; « 👀 » pour surveiller, « ⭐ » pour la liste de souhaits. Les thèmes suivis se choisissent en haut."],
    reglages: ["Réglages", "Chaque section se règle à part : prix (BrickLink), estimations (boîte, plan, décote « modifié »), codes API, Instagram, pages publiques, sécurité, documentation. Les changements s'enregistrent avec le bouton de la section."],
  };
  const vis = el => { if (!el) return null; const r = el.getBoundingClientRect(); return r.width > 2 && r.height > 2 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth && getComputedStyle(el).visibility !== "hidden" ? r : null; };
  const label = b => (b.getAttribute("title") || b.getAttribute("aria-label") || b.textContent || "").replace(/\s+/g, " ").trim();

  const MEMO = { liste: "collection", souhaits: "souhaits", commander: "commander", fiche: "modifier", recherche: "collection", inventaire: "inventaire", stats: "prix" };   // « ? » → sa fiche de l'aide-mémoire (21/11)
  function pageOf(btn) {   // quelle aide : la fenêtre du « ? » touché, sinon la page
    const m = [...document.querySelectorAll("body > .modal")].filter(x => !x.hidden && getComputedStyle(x).display !== "none").pop();   // (fenêtre fixe : pas d'offsetParent)   // fenêtre au premier plan
    if (m) {
      if (m.querySelector(".settings-page")) return "reglages";
      if (m.id === "modal") return !$("#stepConfig").hidden ? "fiche" : "recherche";
      const h = m.querySelector("h2")?.textContent || "";
      if (/À faire/.test(h)) return "afaire";
      if (m.querySelector('[data-s="ok"]')) return "inventaire";
      return { modal: m, title: h.replace(/^\W+/, "") || "Cette fenêtre" };   // aide tirée des bulles de ses boutons
    }
    if (document.querySelector(".settings-page") && document.querySelector(".settings-page").offsetParent) return "reglages";
    if (state.current === STATS) return "stats";
    if (state.current === NOV) return "nov";
    if (typeof isPartsList === "function" && isPartsList(state.current)) return "commander";
    if (typeof isWish === "function" && isWish(state.current)) return "souhaits";
    return "liste";
  }

  function openHelp(btn) {
    document.querySelector(".help-ov")?.remove();
    const pg = pageOf(btn);
    let title, rows = [], text = "";
    if (typeof pg === "object") {   // fenêtre sans aide écrite : ses boutons et leur bulle
      title = pg.title;
      const seen = new Set();
      for (const b of pg.modal.querySelectorAll("button, select, a.btn, label.btn")) {
        const t = label(b); if (!t || t.length < 2 || seen.has(t) || b.classList.contains("help-btn")) continue;
        seen.add(t); rows.push({ el: b, name: (b.textContent || "").replace(/\s+/g, " ").trim().slice(0, 30) || t.slice(0, 30), text: b.getAttribute("title") || "" });
        if (rows.length >= 14) break;
      }
    } else if (TXT[pg]) { [title, text] = TXT[pg]; }
    else {
      const [t, list] = H[pg]; title = t;
      for (const [sel, name, expl] of list) {
        const el = [...document.querySelectorAll(sel)].find(e => vis(e)) || document.querySelector(sel);
        if (el && (el.offsetParent || getComputedStyle(el).position === "fixed") && !el.closest("[hidden]")) rows.push({ el, name, text: expl });
      }
    }
    rows.forEach((r, k) => { r.n = k + 1; });   // tout est numéroté ; le repère apparaît quand le bouton est à l'écran
    const ov = document.createElement("div");
    ov.className = "help-ov";
    ov.innerHTML = `<div class="help-marks"></div><div class="help-panel" role="dialog" aria-label="Aide">
      <div class="help-head"><b>? ${esc(title)}</b><span><button type="button" class="help-min" title="Replier / déplier les explications">▾</button><button type="button" class="help-x" aria-label="Fermer">✕</button></span></div>
      <div class="help-body">${text ? `<p>${esc(text)}</p>` : ""}${rows.length ? `<ol class="help-list">${rows.map(r => `<li data-n="${r.n}"><span class="help-k">${r.n}</span><span><b>${esc(r.name)}</b>${r.text ? ` — ${esc(r.text)}` : ""}</span></li>`).join("")}</ol>` : (!text ? "<p>Rien à expliquer ici.</p>" : "")}
      ${MEMO[typeof pg === "string" ? pg : ""] ? `<p class="help-foot"><a href="${esc((pg === "inventaire" ? [...document.querySelectorAll("body > .modal")].filter(x => !x.hidden).pop()?.dataset.memo : pg === "commander" ? document.querySelector("#stats")?.dataset.memo : "") || "/aide-memoire#/" + MEMO[pg])}" target="_blank" rel="noopener">📌 Aide-mémoire : ${pg === "inventaire" || pg === "commander" ? "étape en cours" : "la suite des étapes"}</a></p>` : ""}
      <p class="help-foot">Faites défiler la page : les numéros suivent. Toucher une explication pour voir son bouton ; ▾ replie ce panneau.</p></div></div>`;
    document.body.append(ov);
    const marks = ov.querySelector(".help-marks"), panel = ov.querySelector(".help-panel");
    const place = () => {   // repères des boutons visibles (recalculés au défilement)
      const pr = panel.getBoundingClientRect();
      marks.innerHTML = rows.map(r => { const rc = vis(r.el); if (!rc || rc.top > pr.top - 4) return "";
        return `<span class="help-ring" data-m="${r.n}" style="left:${rc.left - 3}px;top:${rc.top - 3}px;width:${rc.width + 6}px;height:${rc.height + 6}px"></span>
          <span class="help-num" data-m="${r.n}" style="left:${Math.min(innerWidth - 26, Math.max(2, rc.right - 12))}px;top:${Math.max(2, rc.top - 12)}px">${r.n}</span>`; }).join("");
    };
    const close = () => { ov.remove(); removeEventListener("scroll", onScroll, true); removeEventListener("resize", onScroll); document.removeEventListener("click", onDoc, true); };
    let raf = 0;
    const onScroll = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(place); };
    const onDoc = e => { if (!e.target.closest(".help-panel")) { e.preventDefault(); e.stopPropagation(); close(); } };   // un appui hors du panneau : ferme (sans déclencher le bouton dessous)
    addEventListener("scroll", onScroll, true); addEventListener("resize", onScroll);
    setTimeout(() => document.addEventListener("click", onDoc, true), 0);
    const minBtn = ov.querySelector(".help-min");
    const setMin = on => { panel.classList.toggle("min", on); minBtn.textContent = on ? "▴" : "▾"; setTimeout(place, 50); };
    minBtn.onclick = () => setMin(!panel.classList.contains("min"));
    ov.querySelector(".help-x").onclick = close;
    ov.querySelectorAll(".help-list li").forEach(li => li.onclick = () => {   // une explication : son bouton, mis en évidence
      const r = rows[+li.dataset.n - 1];
      setMin(true);
      r.el.scrollIntoView({ block: "center", behavior: "smooth" });
      setTimeout(() => { place(); marks.querySelectorAll(`[data-m="${r.n}"]`).forEach(m => m.classList.add("flash")); }, 450);
    });
    place();
  }

  const mkBtn = () => { const b = document.createElement("button"); b.type = "button"; b.className = "help-btn"; b.textContent = "?";
    b.title = "Aide : les boutons de cette page"; b.setAttribute("aria-label", "Aide de cette page"); b.onclick = e => { e.stopPropagation(); openHelp(b); }; return b; };
  const fab = mkBtn(); fab.classList.add("help-fab"); document.body.append(fab);   // un seul bouton, flottant, à côté de « ↑ »
  window.helpSync = () => { fab.hidden = state.helpOn === false; if (fab.hidden) document.querySelector(".help-ov")?.remove(); };   // Réglages › Aide
  const placeFab = () => {   // juste à gauche du bouton rond visible le plus à gauche (« ↑ », ou « ↻ » quand il est affiché), même hauteur
    const els = [...document.querySelectorAll(".to-top:not(.help-fab)")].filter(e => e.getClientRects().length && getComputedStyle(e).display !== "none");
    if (!els.length) {   // ↑ caché pour l'instant : au moins la même hauteur que lui
      const t = document.querySelector(".to-top:not(.help-fab):not(.to-reload)"); if (t) fab.style.bottom = getComputedStyle(t).bottom;
      return; }
    const rs = els.map(e => e.getBoundingClientRect()), left = Math.min(...rs.map(r => r.left));
    fab.style.right = Math.round(innerWidth - left + 8) + "px"; fab.style.bottom = Math.round(innerHeight - rs[0].bottom) + "px";
  };
  addEventListener("resize", placeFab); setTimeout(placeFab, 300);
  { const m = document.getElementById("modal"); if (m) new MutationObserver(() => requestAnimationFrame(placeFab)).observe(m, { attributes: true, attributeFilter: ["hidden"] }); }   // (fiche ouverte : ↑ plus bas, « ? » le suit)
  addEventListener("scroll", () => requestAnimationFrame(placeFab), { passive: true, capture: true });   // (↑ apparaît en défilant)
  window.helpSync();
})();

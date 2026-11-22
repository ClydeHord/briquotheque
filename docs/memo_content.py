# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · licence : LICENCE (mention à conserver)
"""Aide-mémoire (21/11) : pour chaque fonction, LA SUITE DES ÉVÈNEMENTS — ce qui se passe, dans l'ordre, du début à la fin —
sans le détail des boutons (le guide utilisateur s'en charge). Une fiche courte par fonction : des étapes, quelques « bon à savoir ».
Servi par l'application : /aide-memoire (construit par build_docs.py, moteur wiki.py) ; le « ? » de chaque écran renvoie à sa fiche.
Format : MEMO = [{"id", "title", "intro", "steps": [(qui / quand, ce qui se passe)], "know": [phrases]}] — HTML simple permis."""

MEMO = [
    {"id": "collection", "title": "Ajouter un set à la collection", "intro": "Du numéro du set à sa valeur estimée.",
     "steps": [
         ("Chercher le set", "par son numéro, son nom, une photo ou le code-barres, puis choisir sa liste."),
         ("Dire comment il est", "neuf ou occasion, avec ou sans ses figurines, complet ou partiel."),
         ("Briquothèque", "crée sa fiche, et une fiche pour chacune de ses figurines, rangées dans le set."),
         ("Briquothèque", "va chercher les infos du set (dates, prix magasin, pièces) et son prix du marché."),
         ("Briquothèque", "calcule sa valeur dans l'état du set, puis la tient à jour chaque jour."),
     ],
     "know": ["Rien n'est obligatoire : ce qui n'est pas précisé prend la valeur évidente (complet, avec ses figurines).",
              "Sans internet, les fiches de la collection s'ouvrent quand même (copie gardée sur l'appareil)."]},

    {"id": "figurines", "title": "Les figurines", "intro": "Une figurine = une fiche, qu'elle soit dans un set ou seule.",
     "steps": [
         ("En ajoutant un set", "ses figurines ont leur fiche, rattachées au set."),
         ("En ajoutant une figurine seule", "elle a sa fiche ; si elle est déjà là, le nombre d'exemplaires augmente."),
         ("Plusieurs exemplaires", "une seule fiche, avec le nombre total ; chaque set dit combien il en a."),
         ("Une modification", "les exemplaires identiques suivent ; un exemplaire modifié autrement n'est jamais touché."),
         ("Une variante", "« Dupliquer puis modifier » : une copie en plus, l'originale reste où elle est."),
     ],
     "know": ["Supprimer un set ne supprime jamais ses figurines : elles redeviennent seules.",
              "Une figurine n'est rattachée qu'à un seul set à la fois (par exemplaire)."]},

    {"id": "modifier", "title": "Modifier un set ou une figurine", "intro": "Pièces retirées, remplacées ou ajoutées : ce qui change ensuite.",
     "steps": [
         ("Modifier", "retirer, remplacer ou ajouter des pièces sur la fiche, puis enregistrer."),
         ("Briquothèque", "chiffre l'écart (prix des pièces retirées et des pièces ajoutées)."),
         ("Briquothèque", "pose l'étiquette : <b>Amélioré</b> (seulement des ajouts) ou <b>Modifié</b> (une pièce ou une figurine d'origine remplacée)."),
         ("Briquothèque", "met à jour la valeur du set ; une figurine d'origine modifiée fait baisser la cote du set."),
         ("Plus tard", "une pièce manquante reçue (« Commandes » → ✔ OK) peut y être remise : l'étiquette suit."),
     ],
     "know": []},

    {"id": "inventaire", "title": "Inventaire d'un set : vérifier, commander, recevoir", "intro": "Du set en vrac au set complet.",
     "steps": [
         ("Ouvrir", "l'inventaire du set : toutes ses pièces sont « non vérifiées »."),
         ("Pointer", "chaque pièce : ✔ OK (présente), 🛒 à commander (elle manque), ou exclue (elle ne compte pas)."),
         ("Exporter", "les pièces à commander en XML (copiées dans le presse-papier), puis passer la commande sur le site choisi. Les pièces <b>restent dans l'inventaire</b>."),
         ("Commande passée", "les pièces trouvées dans les commandes BrickLink ou BrickOwl passent <b>Commandée le …</b> toutes seules. Commandée ailleurs : la marquer à la main."),
         ("Réception", "vérifier et trier les pièces reçues, puis les passer <b>✔ OK</b> à la main (jamais automatique)."),
         ("Tout est OK", "Briquothèque propose de créer sa fiche : d'un « Oui », elle est créée tout de suite dans « À construire », avec la photo de l'inventaire."),
     ],
     "know": ["Ordre des lignes : non vérifiées, à commander, commandées, OK, exclues.",
              "Une erreur ? Une pièce commandée peut être remise à commander : cette commande ne la reprendra plus.",
              "Voir aussi : <a href=\"#/commandes\">Les commandes, lues automatiquement</a>."]},

    {"id": "commander", "title": "La liste « Commandes »", "intro": "Pièces et figurines à acheter, hors inventaire.",
     "steps": [
         ("Ajouter", "une pièce (photo, référence) ou une figurine ; pour un set, notez lequel."),
         ("Commander", "quand l'occasion se présente (l'export XML vers la liste d'achats aide, mais ne compte pas comme une commande)."),
         ("Commande passée", "elle passe <b>Commandée le …</b> (lue dans les commandes BrickLink ou BrickOwl, ou marquée à la main)."),
         ("Réception : figurine", "✔ OK → Briquothèque propose de créer sa fiche."),
         ("Réception : pièce", "✔ OK → si elle manquait dans un set ou une figurine de la collection, Briquothèque propose de l'y remettre ; si rien n'y manque mais qu'elle était pour un set, elle demande quoi en faire."),
         ("Nettoyer", "retire de la liste ce qui est reçu."),
     ],
     "know": ["Ordre : à commander, commandées, reçues."]},

    {"id": "commandes", "title": "Les commandes, lues automatiquement", "intro": "Comment une commande devient « Commandée ».",
     "steps": [
         ("Quand", "à l'ouverture de « Commandes » (au plus une fois par heure) et une fois par jour."),
         ("Quoi", "chaque pièce et chaque figurine des commandes BrickLink et BrickOwl (commandes annulées écartées)."),
         ("Où elle va", "aux lignes « à commander » qui lui correspondent (référence et couleur, règles de couleur comprises), du plus ancien au plus récent."),
         ("Combien", "la quantité commandée est partagée : une même pièce dans deux inventaires ne compte qu'une fois. Une ligne n'est « Commandée » que si toute sa quantité l'est."),
         ("Jamais", "une commande ne valide un inventaire créé après elle, et ne met jamais une pièce en ✔ OK."),
     ],
     "know": ["BrickLink : avec ses codes (Réglages) ; en panne, nouvel essai au passage suivant. BrickOwl : avec sa clé (Réglages).",
              "Ce qui reste d'une commande une fois tout réparti (surplus, ou sans équivalent) s'affiche tout en bas de « Commandes », en bleu : <b>➕ Commandées en plus</b>, attribuées à aucune fiche — chacune : ✔ OK (une figurine : l'ajouter à la collection ?), 🧩 Attribuer à une fiche, ou 📋 Vers un inventaire (« Commandée »)."]},

    {"id": "souhaits", "title": "Liste de souhaits", "intro": "Les envies, sans toucher à la collection.",
     "steps": [
         ("Ajouter", "un set ou une figurine souhaité (ou depuis les Nouveautés)."),
         ("Briquothèque", "suit son prix et sa disponibilité (bientôt retiré, retiré)."),
         ("Une fois acheté", "« ✔ Acquis » : il passe dans la collection, avec ses figurines."),
     ],
     "know": ["Tant qu'il n'est pas acquis, un souhait ne change jamais rien à la collection."]},

    {"id": "prix", "title": "D'où viennent les prix", "intro": "Ce qui alimente les valeurs et les courbes.",
     "steps": [
         ("Chaque jour", "les prix de la collection sont actualisés."),
         ("Sets", "le catalogue (dates, prix magasin) vient de Brickset ; le marché, de BrickLink (prix médian)."),
         ("Figurines et pièces", "BrickLink (prix médian)."),
         ("Si BrickLink ne répond plus depuis 24 h", "BrickOwl prend le relais, seulement pour les fiches consultées et l'actualisation du jour ; il s'arrête tout seul au retour de BrickLink."),
         ("Courbes", "seulement des valeurs réellement relevées : un trou quand il n'y a rien."),
     ],
     "know": []},

    {"id": "moc", "title": "MOC et set partiel", "intro": "Ce qui n'est pas un set complet.",
     "steps": [
         ("Créer", "le MOC, ou indiquer que le set est partiel."),
         ("Donner ses pièces", "en liste ou en fichier."),
         ("Briquothèque", "l'estime par ses pièces, et le tient à jour comme le reste."),
     ],
     "know": []},

    {"id": "public", "title": "Pages publiques", "intro": "Montrer sa collection sans rien risquer.",
     "steps": [
         ("Choisir", "dans les Réglages ce qui est public."),
         ("Les visiteurs", "voient les fiches telles quelles, en lecture seule : rien ne peut y être modifié."),
     ],
     "know": []},
]

# ---- ce que Briquothèque fait TOUTE SEULE (21/11 nuit) : quand, quoi, résultat, et ce qui reste à faire à la main
AUTO = [
    {"id": "auto", "title": "⚙️ Les tâches automatiques : le calendrier", "intro": "Ce que Briquothèque fait toute seule, et quand. Chaque tâche a sa fiche (pages suivantes).",
     "steps": [
         ("Tout de suite", "scan de la photo d'une figurine MOC ; infos et prix d'un set ajouté."),
         ("Toutes les heures", "sets ajoutés sans cote, nouveautés LEGO.com, images HD, secours BrickOwl (si besoin)."),
         ("Toutes les 3 heures", "scans de figurines MOC qui avaient échoué."),
         ("Toutes les 6 heures", "sauvegarde de la collection, images gardées en local, ménage des photos inutilisées, copie pour le hors ligne."),
         ("Chaque jour", "prix BrickLink (dès 3 h du matin), les commandes, catalogue Brickset, pages des thèmes LEGO.com, MOC à rechiffrer, pièces sans couleur."),
         ("Chaque semaine / mois", "prix des pièces de la collection (semaine) ; plans et boîtes vides (30 jours)."),
     ],
     "know": ["Aucune de ces tâches ne valide quoi que ce soit toute seule (jamais de ✔ OK automatique) : elles préparent, la décision reste manuelle."]},

    {"id": "auto-prix", "title": "⚙️ Prix du marché, chaque jour", "intro": "",
     "steps": [
         ("Quand", "chaque jour, dès 3 h du matin (ou au démarrage si la passe du jour n'est pas faite)."),
         ("Ce qu'elle fait", "relit les prix BrickLink (médiane) de toute la collection, dans la limite du quota du jour."),
         ("Résultat", "valeurs et courbes à jour ; les variations sont notées (Statistiques › Comprendre les variations)."),
         ("Prix douteux", "moins de 3 ventes : l'ancien prix est gardé."),
         ("À faire", "rien."),
     ],
     "know": ["Si BrickLink ne répond plus : voir <a href=\"#/auto-secours\">Secours BrickOwl</a>."]},

    {"id": "auto-secours", "title": "⚙️ Secours BrickOwl", "intro": "Quand BrickLink est en panne.",
     "steps": [
         ("Déclenchement", "BrickLink ne répond plus depuis 24 h (ou activé dans les Réglages)."),
         ("Ce qu'elle fait", "prend les prix chez BrickOwl, seulement pour les fiches ouvertes et la passe du jour."),
         ("Arrêt", "tout seul, dès que BrickLink répond de nouveau."),
         ("À faire", "rien."),
     ],
     "know": []},

    {"id": "auto-catalogue", "title": "⚙️ Catalogue des sets", "intro": "Dates, prix magasin, liens LEGO.com.",
     "steps": [
         ("Ajout d'un set", "ses infos sont cherchées tout de suite ; s'il n'a pas encore de cote, nouvel essai toutes les heures (estimation par ses pièces en attendant)."),
         ("Chaque jour", "Brickset : dates de sortie et de retrait, prix magasin, pièces, figurines (les nouveaux sets)."),
         ("Chaque jour", "pages des thèmes LEGO.com : prix public et lien des sets encore vendus."),
         ("Tous les 30 jours", "prix du plan seul et de la boîte vide de chaque set."),
         ("À faire", "rien (la clé Brickset doit être dans les Réglages)."),
     ],
     "know": []},

    {"id": "auto-moc", "title": "⚙️ MOC à valider et MOC rechiffrés", "intro": "Figurines MOC scannées, MOC et sets partiels estimés par leurs pièces.",
     "steps": [
         ("Photo ajoutée", "la photo d'une figurine MOC est scannée tout de suite : les pièces repérées sont proposées."),
         ("Scan impossible", "il est relancé toutes les 3 heures (quelques essais au plus)."),
         ("En attendant", "la figurine reste dans « MOC à valider »."),
         ("À faire", "cocher les bonnes pièces et valider (ou valider sans pièce) : elle quitte « MOC à valider »."),
         ("Ensuite, chaque jour", "les MOC et sets partiels chiffrés il y a plus d'une semaine sont rechiffrés."),
     ],
     "know": []},

    {"id": "auto-pieces", "title": "⚙️ Pièces : prix et couleurs", "intro": "",
     "steps": [
         ("Chaque semaine", "les prix des pièces de la collection sont mis à jour (un chiffrage coupé reprend au redémarrage)."),
         ("Chaque jour", "une pièce ajoutée sans couleur : si ses couleurs sont de nouveau connues, sa tâche devient « couleurs disponibles, choisissez-la »."),
         ("À faire", "choisir la couleur depuis la tâche (À faire)."),
     ],
     "know": []},

    {"id": "auto-commandes", "title": "⚙️ Les commandes", "intro": "Le détail : <a href=\"#/commandes\">Les commandes, lues automatiquement</a>.",
     "steps": [
         ("Quand", "à l'ouverture de « Commandes » (au plus une fois par heure) et chaque jour."),
         ("Ce qu'elle fait", "lit les commandes BrickLink et BrickOwl, et le prix payé de chaque pièce."),
         ("Résultat", "« Commandée le … » sur les lignes concernées ; dans l'inventaire, le montant réellement payé pour ses seules pièces."),
         ("À faire", "✔ OK à la réception."),
     ],
     "know": []},

    {"id": "auto-nouveautes", "title": "⚙️ Nouveautés", "intro": "",
     "steps": [
         ("Toutes les heures", "les sets à venir et les sorties récentes de LEGO.com, avec leurs figurines."),
         ("Résultat", "la page Nouveautés est prête ; un set à venir sans date est relu plus tard."),
         ("À faire", "rien, ou ⭐ pour l'ajouter à la liste de souhaits."),
     ],
     "know": []},

    {"id": "auto-images", "title": "⚙️ Images", "intro": "Des images toujours là, même sans internet.",
     "steps": [
         ("Toutes les heures", "images HD des nouveaux sets et figurines."),
         ("Toutes les 6 heures", "les images des fiches sont gardées sur le serveur ; figurine sans image : sa photo Rebrickable ; pièce sans photo : son image dans sa couleur."),
         ("Ménage", "toutes les 6 heures, les photos que plus rien n'utilise sont supprimées ; au-delà de la place prévue, les images inutilisées les plus anciennes d'abord."),
         ("À faire", "rien."),
     ],
     "know": ["Une image utilisée par une fiche n'est jamais supprimée."]},

    {"id": "auto-securite", "title": "⚙️ Sauvegardes et hors ligne", "intro": "",
     "steps": [
         ("Toutes les 6 heures", "copie de la collection (une par jour, les 30 derniers jours gardés), et avant chaque grosse opération."),
         ("Toutes les 6 heures", "les pièces de toutes les figurines et de tous les sets sont préparées pour le hors ligne."),
         ("Sur l'appareil", "une copie est gardée : les fiches s'ouvrent même sans internet."),
         ("À faire", "rien ; les sauvegardes se gèrent depuis le back office (outils du serveur)."),
     ],
     "know": []},
]
MEMO += AUTO

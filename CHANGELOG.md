# Historique des versions

Les nouveautés de Briquothèque, version par version (la plus récente en haut).

## 20 au 22 novembre 2026

- **Variations de prix : repartir d'aujourd'hui** — une date de départ (22/11) : aucun relevé d'avant ne sert de comparaison (ils venaient d'autres sources) ; les courbes gardent tout l'historique.
- **Inventaire : prix des pièces gardés sur l'appareil** (24 h) — la réouverture n'attend plus le chiffrage.
- **« 🔁 Commander à nouveau » : plusieurs couleurs d'un coup** (chacune sa quantité, une ligne par couleur) ; dans **☑ Sélection**, « 🔁 Commander à nouveau » pour toutes les lignes cochées. Sur ordinateur, « Commandée le … » seule sur sa ligne, les boutons dessous ; sur téléphone, ✔ OK plus étroit. Sur une ligne commandée, **un seul bouton « 🛒 À commander »** qui demande : changer le statut de cette ligne, ou préparer une nouvelle commande.
- **Fenêtres de choix plus lisibles** (« À commander », « Vers quel inventaire ? »…) : une ligne sans photo n'est plus écrasée ; sur ordinateur, deux grandes cartes par ligne, photo et texte plus gros.
- **Inventaire : 🗑️ Supprimer toujours possible** — corbeille en haut (à côté de ✏️) et bouton en bas, ses pièces commandées sont déplacées dans « Commandes » (pas celles à commander).
- **Fiche d'un MOC** : ses pièces ne s'affichent plus dans la fiche, seulement dans « 🔶 Pièces » (comme un set partiel).
- **Inventaire : tirer pour actualiser** (vers le bas, depuis le haut de la page) ; plus de bouton ↻ en haut.
- **Inventaire complet, jamais sans issue** : bouton « 🚧 Prêt à construire : créer sa fiche » dès que tout est OK, et la question à l'ouverture d'un inventaire déjà complet (pièces passées OK depuis « Commandes »…).
- **Inventaire : « 📷 Scanner des pièces »** ouvre la recherche de pièce (appareil photo, image collée ou référence) ; la liste se filtre sur la pièce trouvée. Plus de « 📋 Coller » à côté.
- **Recherche réparée** : elle ne trouvait plus rien depuis que BrickEconomy refuse l'accès ; elle cherche maintenant sets et figurines par Rebrickable (en français et en anglais) et une référence de figurine (sw0002…) par BrickLink.
- **Ajout d'un set** : la fiche est créée tout de suite, les prix arrivent en coulisse.
- **Inventaire** : « 🔎 Rechercher » (l'ancien scan de plusieurs pièces par photo est retiré) ; un nouvel inventaire apparaît tout de suite dans le menu ; 4 colonnes sur grand écran.
- **Commandes** : même barre sur ordinateur que sur téléphone ; « Exportée » seulement sur une ligne encore à commander, son ✕ au bout de la ligne.
- **Souhaits** : l'état souhaité se change sans passer en modification ; pas de ✔ Acquis sur « À surveiller » ; ⭐ dans le titre de la liste de souhaits (sans ✏️) ; plus de suggestion de liste.
- **Fiche** : liens tout en bas, sous les prix ; plus de case vide à côté de « Quantité » ; ✏️ au bout de chaque pièce d'un MOC.
- **Nouveautés** : un set en réassort ne passe plus pour une sortie du lendemain.
- **Pages publiques** : « À surveiller » affiche la note de chaque fiche.
- **Vitesse** : glisser une fiche plus léger (thème Verre sans flou sur les cartes) ; fenêtres opaques dans le thème Verre ; notes libres de « À faire » visibles aussitôt.
- **Lexique** : ⧉ copier, 🔁 remplacer, ✕ retirer, 🗑️ supprimer, ✔ valider — partout.
- **Mode démo retiré.**
- **Un seul menu « Liste »** partout (fiche, inventaire complet, souhait acquis) : même bouton avec logos, même fenêtre.
- **Encore plus rapide** : scripts et styles compressés (app.js 1 Mo → 312 Ko) et jamais retéléchargés s'ils n'ont pas changé ; collection recalculée en coulisse après chaque enregistrement.
- **« 🔶 Pièces » d'un MOC** toujours visibles, même sans clé Rebrickable ni internet ; l'inventaire en page se ferme aussi depuis les pastilles du haut ; 🗑️ et ✔ partout.
- **Priorité à l'écran** : tout ce qui tourne en fond (relevés de prix, images, inventaires, commandes…) passe après ce qui est en cours à l'écran — naviguer, ouvrir une fiche et chercher ses prix, rechercher ; les tâches de fond attendent que l'écran soit calme et tournent en priorité basse.
- **Tri par défaut** enfin gardé : le menu de gauche le respecte (plus de « Dernière modification » imposé), et il est enregistré sur le serveur — le même sur tous les appareils.
- **Inventaire complet** : une seule fenêtre — la liste où mettre la fiche (à choisir, rien d'office ; ★ marque la suggestion : celle qui a le plus de sets de son thème) et le type de fiche : 📦 Set complet, 🧩 Set partiel, 🛠️ MOC, ou « Pas encore ».
- **Plus rapide** : la collection (« /api/lists ») est gardée en mémoire tant que rien n'a changé — environ 20 fois plus rapide à chaque rafraîchissement.
- **Inventaire complet → « Oui »** : la fiche se crée en coulisse (le formulaire ne s'affiche plus), la liste reste utilisable, confirmation quand c'est enregistré.
- **Inventaire en vraie page** (comme « Commandes ») : il occupe la zone principale, menu et en-tête restent visibles ; un clic dans le menu le referme ; sur ordinateur, les pièces sur deux colonnes (trois sur grand écran).
- **« Commandes » : le menu ☰ propose les filtres** (Toutes, À commander, Commandées, OK, ☑ Sélection) à la place des tris ; plus de rangée de pastilles ; ☰ surligné quand un filtre est actif. Sur téléphone : liens à la ligne si besoin, « 📦 Commandée » sur une ligne.
- **Souhait acquis** : « ✔ Acquis » demande la liste (aucune d'office ; ★ = la liste qui a le plus de sets du même thème), puis enregistre le set dans la collection, coché « 🚧 À construire », sans autre question ; tout set passé de la liste de souhaits à la collection va dans « À construire ».
- **Liens** : plus de « Voir sur : » devant ; « LEGO » au lieu de « LEGO.com ».
- **« Commandes » : section 🧾 Exportées** à part ; « Exportée en XML » se retire d'un ✕.
- **Liens BrickOwl** de retour partout, à côté de BrickLink (application et pages publiques).
- **Lisibilité** : plus aucun texte sous 11 px (étiquettes des chiffres, « Modifiée », « sans figurines »), petits boutons agrandis ; un peu plus gros sur ordinateur.
- **Souhait : « État souhaité »** — boutons 📦 Neuf / ♻️ Occasion plus petits.
- **Un inventaire n'est rattaché à aucune fiche** : toujours rangé par numéro de set (plus de « Dans la collection »), quantités d'un set.
- **« Commandées en plus » : zoom en grand** — la grande photo Rebrickable de la pièce dans sa couleur ; une figurine BrickOwl : sa grande photo BrickOwl (700 px).

- **« À commander » devient « Commandes »** ; tout en bas, en bleu à part : <b>➕ Commandées en plus</b> — les pièces et figurines commandées qui ne sont attribuées à aucune fiche (surplus ou sans équivalent), avec photo, date et prix payé. Sur chacune : ✔ OK (une figurine : l'ajouter à la collection ?), 🧩 Attribuer à une fiche, 📋 Vers un inventaire (la ligne passe « Commandée »).
- **« 🔁 Commander à nouveau »** (ligne commandée ou reçue de « Commandes ») : une nouvelle ligne à commander, dans la même couleur ou une autre ; une ligne commandée n'est plus fondue avec une nouvelle.
- **« Commandes » en sections** (🛒 À commander · 📦 Commandées · ✔ Reçues) ; **sur ordinateur, jusqu'à quatre références par ligne** (trois dès 1 400 px, quatre dès 1 700 px ; photo, infos et ×N en haut, boutons dessous ; sans fond de couleur, seul le liseré dit l’état) ; la rangée Toutes / À commander / Commandées / OK / ☑ Sélection reste visible en haut pendant le défilement.
- **« Commandes » : ☑ Sélection** — cases à cocher et actions groupées (✔ OK, 📦 Commandée, ↩ À commander, 🗑 Supprimer ; commandées en plus : ✔ OK, 🧩 Attribuer à une fiche, 📋 Vers un inventaire).
- **« 📋 Vers un inventaire »** : tous les inventaires sont proposés ; un inventaire qui n'a pas la pièce la reçoit en ligne ajoutée (hors set), « Commandée ».
- **« Remplacer une couleur »** (inventaire) : couleurs dans l'ordre alphabétique, avec un carré de chaque couleur et une recherche.
- **Choix d'un inventaire** : chaque inventaire avec son nom et sa photo (celle de l'inventaire, sinon le set).
- **Pièce rangée dans un inventaire** : la couleur effective de chaque ligne compte (règle de couleur, couleur choisie).

- **Secours BrickOwl corrigé** : quand il se déclenche tout seul (BrickLink en panne), les prix BrickLink déjà connus restent prioritaires ; BrickOwl ne comble que les manques. Un prix BrickOwl de set ou de figurine n'est retenu que sur au moins 3 ventes ou annonces (une seule annonce à 14,54 € avait fait passer l'occasion d'une figurine au-dessus du neuf).

- **Statistiques « 📈 Valeur dans le temps » lissée** : un relevé quotidien qui s'écarte de plus de 3 % de ses voisins (9 jours) est remplacé par leur médiane ; l'historique reconstitué est raccordé au premier vrai relevé (plus de marche). Le dernier jour reste la vraie valeur.

- **Textes neutres partout** : ni « vous », ni « je », ni impératif — appli, aide « ? », aide-mémoire, installation, back office, guide utilisateur et notice du back office (« Dans la collection », « L'exemplaire », « ✔ Acquis », « 📍 Étape en cours », « Toucher une pièce… »).

- **Inventaire complet → fiche créée directement** dans « À construire », avec la photo de l'inventaire, dans la liste où vous avez le plus de sets du même thème (plus de formulaire à compléter).
- **Source des prix** : plus d'alerte « BrickLink ne répond pas » ; juste « Source : BrickLink » (ou BrickOwl pendant le secours), une fois par jour au plus.

**Commandes et pièces à commander**
- **Mes commandes lues automatiquement** (API officielles BrickLink et BrickOwl ; clé BrickOwl dans Réglages › 🦉 BrickOwl) : une pièce ou une figurine à commander trouvée dans une commande passe « 📦 Commandée le … » — jamais « ✔ OK » automatique (vous vérifiez à la réception). Relu à l'ouverture de « À commander » (une fois par heure au plus) et chaque jour ; commandes annulées écartées.
- **Rapprochement** : pièce = référence (aussi celles du nom) + couleur, règles de couleur de l'inventaire comprises ; figurine = sa référence BrickLink, ou son nom exact (BrickOwl). Une même pièce dans plusieurs inventaires : la quantité commandée est partagée, du plus ancien au plus récent ; une ligne n'est « Commandée » que si toute sa quantité l'est. **Surplus → vrac** : une commande ne sert qu'aux lignes déjà « à commander » quand elle a été passée, jamais à un inventaire créé après.
- **« 📦 Commandée » à la main** (commande passée ailleurs), avec « Annuler » ; **« ↩ À commander »** si erreur (cette commande ne la reprend plus).
- **Montant réellement payé** : « 📦 N commandées · X € payés » (prix payé dans la commande, seulement pour les pièces attribuées ; port non compté).
- **Inventaire** : les pièces à commander y restent ; ordre non vérifiées → à commander → commandées → OK → exclues ; pièces identiques rassemblées (ex. ×2 + ×2 → ×4) ; le nombre nécessaire (×N) en gros à droite ; boutons sous les infos sur tablette et ordinateur.
- **« À commander » a l'aspect de l'inventaire** : résumé ligne par ligne (à commander, commandées et payé, reçues), barre d'avancement, filtres Toutes / À commander / Commandées / OK ; lignes neutres tant qu'elles ne sont pas commandées (achats « si l'occasion se présente ») ; liens BrickLink / Rebrickable sur une ligne.
- **✔ OK à la réception** : figurine → « créer sa fiche ? » ; pièce → remise dans le set ou la figurine où elle manquait, sinon « qu'en faire ? » (la garder à part / l'ajouter au set).
- **« 🧾 Exporter en XML »** (inventaire et « À commander ») : copie dans le presse-papier les pièces encore à commander, au format BrickLink — aucun site ouvert, aucune question ; bouton discret.

**Prix et graphiques**
- **BrickLink, médiane partout** : prix = médiane des ventes des 6 derniers mois (France, puis Europe, puis monde) ; « À commander » : médiane des annonces, sinon des ventes. Liens et exports : toujours BrickLink.
- **Secours BrickOwl** : si BrickLink ne répond plus depuis 24 h, les prix viennent de BrickOwl (fiches ouvertes et actualisation du jour) — arrêt tout seul à son retour.
- **Brickset** (Réglages › 🗓️ Brickset) : dates de mise en vente et de retrait, prix magasin, pièces, figurines, code-barres. **Pages des thèmes LEGO.com** : prix public et lien des sets encore vendus.
- **Graphique « 📈 Évolution » : du vrai uniquement** (un trou s'il n'y a pas de donnée) — 🟩 Neuf (magasin), 🟨 Neuf (après retrait), 🟧 Occasion dans l'état de mon set, 🟥 Mon exemplaire s'il est modifié ; relevés farfelus écartés. Écarts de prix calculés sur mon exemplaire.
- **« Valeur de la liste »** quand une liste est ouverte (appli et pages publiques).
- **Pages publiques** : la flèche de variation et le tri « Écart de prix » calculés exactement comme dans l'appli (sur l'exemplaire, d'après l'historique réel du marché).
- **Images** : une fausse image « introuvable » n'est plus gardée ; l'image de la pièce dans sa couleur la remplace.

**Aide**
- **📌 Aide-mémoire** (`/aide-memoire`, Réglages › Aide et le « ? » de chaque écran) : pour chaque fonction et chaque tâche automatique (⚙️), la suite des étapes. Depuis un inventaire ou « À commander » : **« 📍 Vous en êtes là »** (étapes faites ✓, étape en cours encadrée).

## 17 au 19 novembre 2026

- **Pages publiques à jour avec l'appli** : mêmes tris (Écart de prix (%) et (€), tris retirés), plus de bouton 📈, écart en euros pour les tris en €, ligne du tri en cours avec la date de comparaison, et prix en bulles au-dessus des liens dans les fiches (si les prix sont publics).
- **Fiche : choix de la liste avec les logos** — le bouton et le menu montrent le logo de chaque liste en petit avant son nom. **Logo de la liste sur la fiche** : jamais plus haut que la ligne « Quantité » (un logo en hauteur était coupé).
- **Ajouter des figurines à un set** : la rubrique « Dans ma collection » précise « (figurines sans set) » — celles déjà rangées dans un set n'y sont pas proposées.
- **Réparé** : la fiche d'un set (hors collection) avait perdu l'historique de ses prix et les noms français de ses figurines depuis l'ajout des prix au-dessus des liens.
- **Ligne du tri en cours** : en tri Aléatoire, juste « Aléatoire » (plus de « ordre mélangé »).
- **Fiches : les prix au-dessus des liens BrickLink / Rebrickable**, en bulles de l’allure des liens BrickLink — « Prix magasin (retiré) », « Neuf · sans figurines », « Occasion · sans figurines », une par ligne pour un set, côte à côte pour une figurine (libellés normaux, prix en gras) ; le bouton « 💶 Tarifs » est retiré.
- **Bouton « Filtres »** : un entonnoir remplace la roue dentée (qui reste pour les Réglages). **Logo de la liste sur la fiche** : à surface égale — un logo allongé (Ninjago, Speed Champions…) s’élargit au lieu de rapetisser, sans repousser le texte.
- **Menu « ⇅ Tri »** : tris Nom, Année, Thème, Nombre d’exemplaires, Numéro et Ajout récent retirés (collection) ; « Augmentation / baisse » devient **Écart de prix (%)**, nouveau **Écart de prix (€)** ; avec un tri de variation ou d’écart, une ligne « 📅 Écarts par rapport au … » et « Changer la période » ; le bouton 📈 est retiré (les variations suivent les Réglages) ; icônes dessinées : barres en escalier pour le tri, deux flèches opposées pour inverser l’ordre (en Aléatoire : remélanger) ; une ligne toujours visible rappelle le tri et son sens en flèche (« Valeur ↘ » décroissant, « ↗ » croissant), avec la date de référence pour les variations ; un bouton calendrier, à droite de l’inversion, change la période de comparaison.
- **Tri « Variation de prix (€) »** : à côté de la flèche, l’écart en euros (« ↑ +12,40 € ») au lieu du pourcentage.
- **Réglages › 🧮 Estimations : « Comparer les variations à »** — un curseur : 1, 7, 15, 30, 90, 180 ou 365 jours, glissants (30 / 90 / 180 / 365 : le même jour il y a 1 / 3 / 6 / 12 mois — le 20/11 comparé au 20/10…) ; flèches, % et « par rapport au … » suivent ; une fiche plus récente se compare à son premier relevé. Un relevé qui ne reflète pas un vrai prix (prix pas encore connu à l’ajout) n’est jamais pris comme point de comparaison, et une fiche dont les pièces échangées sont en cours de chiffrage n’est pas relevée ce jour-là (plus de variations absurdes).
- **Remplacer une pièce d’une figurine : « ✔ Corriger l’originale »** (cette figurine n’est pas la bonne) : la pièce choisie devient celle d’origine — affichée comme telle, pas une modification (ni « Modifiée », ni « Modifié » sur le set), sans effet sur l’estimation.
- **Figurines d’origine : plus de question « laquelle ? »** : leur version Rebrickable se déduit de leur set (sa liste officielle comparée à l’inventaire Rebrickable du même set : élimination, quantités, noms, couleurs BrickLink / Rebrickable, et nom BrickOwl si besoin) ; leurs pièces sont prêtes d’avance. Quand les noms ne suffisent pas, les références tranchent : les pièces de la figurine chez BrickLink (API officielle) comparées à celles de chaque version Rebrickable — une seule correspond (ex. la tête). Ça vaut aussi pour les figurines ajoutées seules : la question « laquelle ? » ne reste que si rien ne permet de trancher.
- **Affichage tablette et téléphone** : les menus « ⚙️ Filtres » et « ⇅ Tri » restent entiers dans l’écran (plus de défilement de côté) ; dans la tuile « Valeur de la collection », le montant et son « ~ » restent sur une ligne.
- **Barres du haut sur PC** : plus de bande vide entre la barre du haut (réduite en défilant) et les barres collées dessous ; le bloc des sous-listes collé a un fond uni. **📅 Calendrier** : il s’ouvre bien sur « Aujourd’hui », visible juste sous l’en-tête (téléphone compris).
- **Ajouter une pièce en plusieurs couleurs d’un coup** : toucher d’autres couleurs les ajoute (une quantité pour chacune), toucher une couleur choisie la retire ; une ligne par couleur.
- **Bouton d’ajout** : juste « + » (plus « + Nouveau »), bien centré, sur PC comme sur téléphone.
- **Modifier l’image** : maintenir le doigt sur la photo pour recadrer n’ouvre plus le menu du téléphone (Copier / Télécharger l’image).
- **Jamais d’image manquante** : une figurine sans photo trouve la sienne dans l’ordre — photo Rebrickable sûre, version choisie sur sa fiche, version désignée par son nom BrickOwl, sinon la photo officielle de sa page BrickOwl ; une pièce dont la photo n’existe pas prend l’image de la pièce dans sa couleur. Tout est gardé sur le serveur ; rattrapage de toute la collection (repris toutes les 15 min tant qu’il reste du travail), puis toutes les 6 h et dès qu’une image manque à l’écran. La photo de secours est aussi servie aux figurines dont le n° BrickLink s’écrit autrement (sh086 / sh0086). Les images de secours et les photos des pièces des figurines ne sont jamais effacées par le ménage du disque (et sont retéléchargées si besoin) ; une pièce imprimée sans aucune image prend celle de sa forme sans impression. Nouveautés : la première photo vraiment disponible est affichée (une image disparue chez lego.com ne laisse plus la carte vide).
- **Photos des pièces et des figurines** : une photo de pièce absente chez Rebrickable est remplacée par l’image de la pièce dans sa couleur (gardée sur le serveur) ; quand plusieurs versions d’une figurine sont possibles, son nom BrickOwl départage (seulement s’il n’en désigne qu’une).
- **✨ Nouveautés : « ⚙️ Filtres »** : les cases (masqués, sans image, souhaits, surveillés, Sets, Figurines exclusives) regroupées dans un menu déroulant, à côté de « 🎯 Thèmes suivis » ; le nombre de filtres changés s’affiche sur le bouton.
- **Liens BrickLink et Rebrickable toujours côte à côte** : pièces à commander, fiche et détail d’une pièce, figurines des Nouveautés (appli et page publique), figurine de la page publique.
- **✨ Nouveautés** : l’en-tête (Dernières annonces / Calendrier, filtres) reste toujours visible, condensé quand on a défilé (onglets sur une ligne, filtres alignés sur la suivante) ; dans le Calendrier, « 📅 Calendrier des sorties » est en surbrillance dans le menu de gauche ; depuis le Calendrier, « ✨ Nouveautés » du menu de gauche revient bien aux Dernières annonces.
- **Photos des pièces** : « 🔍 Agrandir la photo » dans le menu d’une pièce, et un appui sur la vignette d’une pièce gardée ou retirée (Pièces d’une figurine) l’agrandit.
- **Figurines ajoutées dans un set** : « 🔢 Modifier la quantité » dans ⋯, et un appui sur leur « ×N ». Leur photo manquante est cherchée tout de suite ; si plusieurs versions Rebrickable sont possibles, celle choisie sur la fiche (Pièces › changer de version) donne la photo.
- **« 📚 Toute la collection » garde le tri par défaut** : le bouton du haut (et celui du nom de la liste ouverte) ne force plus le tri par valeur ; il remet le tri défini « par défaut » (⇅ Tri › Définir par défaut).
- **Thèmes Verre et Pastel sur PC** : plus de traits en haut quand on fait défiler — la barre du haut et la barre des filtres collée forment un seul bandeau, calé au pixel près ; dès le début du défilement, la barre du haut est en verre dense et le contenu s’efface en douceur dessous (plus de coupure nette) ; une fois défilé, les deux barres ont un fond uni : les images des cartes ne passent plus au travers.
- **Plus de faux « Hors ligne » au retour dans l’appli** : au réveil du téléphone, le réseau met un instant à revenir ; l’appli vérifie maintenant deux fois avant d’afficher le bandeau (la copie gardée sert en attendant).
- **Ajouter marche toujours, même si aucun site de prix ne répond** : un set ou une figurine s’ajoute sans prix (sous son nom, sinon son numéro) et son prix arrive tout seul dès qu’un site répond ; les relevés faits juste après l’ajout ne peuvent plus le faire échouer ; « changer en set » aussi ; un numéro de set tapé sans « -1 » est complété.
- **Prix** : les prix affichés ne nomment plus leur source (« Prix » au lieu de « Prix BrickOwl », plus de « (BrickOwl) » à côté des prix et des estimations). Les sources restent citées dans les Réglages et les mentions légales.
- **Ajouter une figurine** ne bloque plus quand BrickEconomy refuse l’accès et que BrickLink est en maintenance : comme sa fiche, l’ajout se contente du relevé BrickOwl (nom, prix d’occasion) ; la fiche complète est relue plus tard, toute seule.
- **Menu de gauche** : plus de traits autour de « Réglages » et « Se déconnecter », ni d’encadré autour de ces boutons : ils ont l’allure des autres lignes du menu. **Fiches** : le logo de la liste au bout de la ligne « Quantité ». **Correctifs** (relevés par une simulation de 240 manipulations de fiches) : une pièce déplacée vers une liste qui l’avait déjà ne fait plus de doublon ; une figurine « d’origine » d’un set qui ne la contient pas au catalogue redevient une figurine ajoutée (comptée pour son prix) ; la fiche d’ajout d’une figurine ne « sautille » plus.
- **Le nom d’une figurine vaut pour la figurine** : renommer une de ses fiches renomme aussi ses autres fiches (dans un set ou seules) qui n’ont pas de nom à elles ou portaient l’ancien nom ; un nom différent choisi exprès n’est jamais écrasé. Le nom de la fiche passe toujours avant celui gardé par un set.
- **Une fiche, c’est une fiche — jusqu’au bout** : tout ce qui appartient à une figurine d’origine est rangé dans sa propre fiche, plus dans son set — images, nom personnalisé, pièces échangées et leur chiffrage, accessoires, version Rebrickable (le set n’en garde qu’une copie) ; une modification faite depuis l’écran d’une figurine de set va directement sur sa fiche ; une figurine qui quitte un set emporte tout. Valeur de la collection inchangée.
- **Les images d’une figurine sont rangées dans sa propre fiche** : la photo et les apparences d’une figurine d’origine ne dépendent plus de son set (qui n’en garde qu’une copie) ; une photo ajoutée ou retirée depuis l’écran d’une figurine de set va directement sur sa fiche ; une figurine qui quitte un set emporte toujours ses images. 80 figurines d’origine ont reçu leur photo sur leur fiche.
- **Vos photos d’abord, partout** : une photo ajoutée ou retouchée sur une fiche passe toujours avant l’image du catalogue et avant la photo gardée par un set — cartes, fiches, sélections du jour, page publique, fiche partagée — sauf si vous la supprimez ou reprenez la photo officielle.
- **Supprimer un set qui a des figurines** : une fenêtre les liste, chacune avec une case (cochées d’office = gardées, seules et indépendantes) ; « Garder la sélection » ou « Supprimer tout ». Depuis la fiche et depuis une sélection de plusieurs cartes.
- **Images** : 2 839 images effacées par l’ancien ménage automatique remises sur le serveur (images de la collection manquantes : 917 → 27) ; une figurine sans photo à vous dont l’image ne vient pas affiche votre photo d’une autre fiche de la même figurine.
- **Nouveautés** : barre simplifiée — « Thèmes suivis » en tête des cases, « Sets / Figurines exclusives » à la fin, libellés raccourcis, liste « Tous les thèmes » retirée.
- **Une fiche, c’est une fiche** : supprimer un set ne touche plus jamais à ses figurines — celles d’origine deviennent des fiches indépendantes avec leur photo, leur nom et leurs pièces échangées, celles ajoutées restent seules ; des fiches de figurine identiques au même endroit (même set ou MOC, ou seules dans la même liste) ne font qu’une fiche, avec le nombre d’exemplaires ; les photos envoyées ne sont plus jamais supprimées automatiquement.
- **Dans mes sets** : « − » sort toujours un exemplaire que la ligne compte (avant : parfois un exemplaire d’une autre fiche, et le nombre ne bougeait pas).
- **MOC et set partiel** : leur carte ajoute la valeur des figurines rangées dedans (avant : « Sans estimation » sans liste de pièces).
- **Back office → Règles « si… alors »** : nouvelle action « 📝 Tâche à faire » — une vraie tâche ajoutée aux fiches qui remplissent la condition, retirée d’elle-même sinon ; les tâches écrites à la main ne sont jamais touchées.
- **Tâche automatique « Photo à faire »** : retirée (toutes les images sont gardées sur le serveur).
- **PC** : la barre du haut se réduit dès qu’on fait défiler. **Fiche** : 👀 à droite de « Voir sur », plus petit. **Verre et Pastel** : plus de fond sombre ni de trait en haut ; une image déjà vue ne montre plus la roue quand la liste se redessine.
- **Images : toujours par le serveur** : le téléphone et le PC ne vont jamais chercher une image directement chez Rebrickable, BrickLink, BrickEconomy ou LEGO — c’est le serveur qui la télécharge une fois et la garde ; l’appareil en garde une copie. Corrigé : photo agrandie d’un résultat de recherche, photo de secours d’une image en échec, photo d’un inventaire ; filet de sécurité dans l’appli et dans le service hors ligne pour toute image oubliée.
- **Moins de requêtes Rebrickable** : ce qui ne change pas n’est plus relu — fiche d’une pièce, pièces et correspondance d’une figurine, figurines et sous-ensembles d’un set, images (serveur et téléphone) : gardés pour toujours, une fois téléchargés ; « dans quels sets / quelles figurines » et couleurs d’une pièce : relus tous les 6 mois (chaque semaine avant) ; catégories et couleurs : tous les ans. Seuls les prix (BrickLink, catalogue des cotes) et les nouveautés LEGO restent vérifiés régulièrement.
- **Pièces des figurines instantanées, même sans internet** : la correspondance Rebrickable d’une figurine est gardée (avant : 2 à 4 requêtes Rebrickable à chaque ouverture, d’où « Chargement des pièces… ») ; une liste de pièces déjà connue est rendue tout de suite ; le serveur prépare d’avance les pièces de toutes les figurines de la collection (seules et dans les sets) et l’inventaire de tous les sets ; l’appli les reçoit en un seul envoi au démarrage, gardé sur l’appareil : une fiche de figurine montre ses pièces sans attendre, hors connexion comprise.
- **Images de figurines** : BrickEconomy refuse désormais les robots et BrickLink (la source de secours) est fermé : des centaines de photos de figurines n’avaient jamais pu être enregistrées (↻ à la place). Troisième source : la photo Rebrickable de la même figurine, repérée sans ambiguïté, cherchée en arrière-plan (au démarrage, puis toutes les 6 h) et enregistrée sur le serveur. Les images téléchargées restent sur le serveur : plus de ménage automatique, sauf disque presque plein (moins de 1 Go libre) — et jamais celles de la collection, des listes ou des nouveautés.
- **Back office → 🗂️ Tous les éléments** (Avancé) : l’inventaire de tout ce que l’appli affiche — boutons, liens, menus, titres, options, champs — même caché (menus fermés, fenêtres, éléments masqués), cherchable par zone ; « ✏️ Modifier » ouvre l’éditeur complet, « 🙈 Masquer » / « 👁 Afficher » d’un appui. Limites relevées partout (noms, icônes, colonnes, blocs, entrées du menu…) : seule reste la taille d’un envoi (16 Mo).
- **Revue du code** : Nouveautés ouverte depuis le menu puis quittée — son actualisation continuait et plantait (corrigé) ; icône d’onglet sur les pages publiques (collection, nouveautés, fiche partagée) ; le journal du serveur n’enregistre plus de fausses alertes quand un navigateur ferme une page en cours de chargement ; imports inutilisés retirés.
- **Thèmes** : l’aperçu des Réglages devient une mini fiche (photo d’un de vos sets, prix et 💶 Tarifs, type de fiche, Pièces / Plan, boutons de la photo — Appareil photo, Importer, Coller, Recadrer —, Enregistrer, liens) ; ✨ Moderne bien distinct de 🧱 Classique (pilules grises sans bord, cartes flottantes) ; 4 thèmes de plus : 💥 BD, 🍬 Pastel, 📐 Technique, 🌙 Nuit. 🫧 Verre : les boutons de la photo agrandie (Modifier image, Changer la photo…) en vrai verre dépoli. 🫧 Verre et 🍬 Pastel : plus de bande derrière la barre des filtres — transparente à sa place, fond de verre seulement quand elle reste collée en haut au défilement.
- **Bouton retour** : en revenant dans l’appli alors qu’une fiche était ouverte (Android l’avait fermée en arrière-plan), « retour » ferme la fiche au lieu de quitter l’appli.
- **Fiche** : 💶 Tarifs sur la ligne du prix, tout à droite ; 👀 (à surveiller) aussi petit que les liens « Voir sur » ; photo toujours carrée, son bas sur celui des boutons Pièces / Plan (plus grande sur tablette et ordinateur, sans faire passer à la ligne la description, le type de fiche ni les boutons). Pages publiques : plus de trait autour des étiquettes d'une fiche (thème Néon…).
- **Fiche** : un set partiel y montre les tarifs du set complet ; les vignettes de prix sous l’estimation sont retirées ; photo toujours carrée, aussi haute que la colonne de droite (au plus la moitié de la largeur) ; espaces resserrés (6 px) entre les infos, le type de fiche et les boutons Pièces / Plan ; le type de fiche toujours seul sur sa ligne, Pièces et Plan ensemble dessous.
- **Fiche** : le type de fiche (Set complet, Set partiel, Figurine, MOC…) à droite de l’image, sous la description ; description sur deux lignes (thème · pièces, puis année · état).
- **Thèmes de l’application** (Réglages → 🎨 Apparence) : ✨ Moderne (d’office : arrondi, dégradé léger, ombre douce, réagit au toucher), 🧱 Classique (l’aspect d’avant), 🫧 Verre, 🟥 Brique (relief façon LEGO), ◻️ Minimal, 🌃 Néon — tous les boutons et étiquettes, partout, pages publiques comprises ; changement immédiat ; un aperçu en direct du thème choisi dans les Réglages.
- **Back office → Menu** : chaque entrée du menu se renomme (émoji compris) et se masque une à une ; « + Ajouter un trait de séparation ».
- **Calendrier** : images plus grandes (vignettes carrées, fenêtre d’un set).
- **Fiches** : la photo du haut nettement plus grande (téléphone : environ la moitié de la largeur ; ordinateur : 260 px).
- **Calendrier** : toucher une vignette ouvre sa fenêtre (grande image, infos, date ; souhaits, à surveiller, lego.com, ne plus afficher) ; sur téléphone, 2 vignettes par ligne.
- **Page publique des nouveautés** : les thèmes se choisissent par cases à cocher (« 🎯 Thèmes »), comme sur la page privée ; le choix est gardé sur l’appareil du visiteur.
- **Calendrier des sorties** : dates plus visibles (mois en grand, jours en pastille « 📅 ») ; la date exacte d’un set vu « à venir » est retenue, il reste à son jour une fois sorti (lego.com ne donne ensuite plus que l’année) ; sorties dont seule l’année est connue : sous « 2026 ».
- **À commander** : une seule ligne « Prix », celui de BrickLink pour l’état voulu (neuf, occasion, ou le moins cher) ; BrickLink indisponible : le prix de secours. Une maintenance de BrickLink est reconnue (« BrickLink en maintenance ») au lieu d’une erreur obscure.
- **Page publique /calendrier** : les nouveautés ouvertes sur le calendrier des sorties (📤 depuis le calendrier partage ce lien). Sur la page publique, les choix du visiteur (onglet, cases, filtres, thème) sont gardés sur son appareil, et une mention le dit.
- **Menu latéral** : « 📅 Calendrier des sorties » sous « ✨ Nouveautés » ouvre directement l’onglet Calendrier.
- **Page publique des nouveautés** : mêmes onglets (Dernières annonces / Calendrier) et cases (Sets / Figurines exclusives), au choix de chaque visiteur.
- **Visuels manquants des nouveautés** : une boîte de set ou une silhouette de figurine grisée avec « ? » ; la toucher relance la recherche (Rebrickable) ; les visuels manquants sont aussi recherchés à l’ouverture de la page, et toutes les 6 h.
- **Nouveautés : deux onglets, « 📰 Dernières annonces » et « 📅 Calendrier »** ; cases « Sets » (cochée d’office) et « Figurines exclusives » pour les deux (ensemble possible). Le calendrier : une frise mois par mois (et jour par jour quand lego.com donne la date) ; on arrive sur « Aujourd’hui » : en dessous les prochaines sorties, au-dessus les sorties récentes. Appui sur l’image : en grand ; sur le set : souhaits, à surveiller, lego.com, ne plus afficher. Liseré doré : dans la liste de souhaits ; bleu : à surveiller.
- **Fenêtre d’une pièce** (ajouter, modifier, remplacer) : bouton 💾 en haut, à côté de ✕, en plus de celui du bas.
- **Pièce à commander, « Pour quel set ? »** : ce qu’on tape peut devenir une note (« 📝 En faire une note », ex. « pour Paul ») ; un texte qui n’est pas un numéro de set devient une note à l’enregistrement ; la note s’affiche aussitôt juste sous le champ (visible même avec le clavier du téléphone).
- **Téléphone, en défilant** : la barre du haut garde le montant de la liste (ou de toute la collection) et les boutons Tout / Sets / Figurines (un appui repart du début de la grille) ; la barre des filtres suit la barre du haut sans à-coup.
- **Ordre et noms des tris** (menu ⇅ Tri) : Dernière modification, Ajout récent, Aléatoire, Valeur (ex-« Valeur décroissante »), Variation de prix (%), Variation de prix (€), Augmentation / baisse (%), puis Nom (ex-« Nom (A → Z) ») et les autres ; « Ajout le plus ancien » retiré du menu (🔃 sur « Ajout récent »).
- **Cartes alignées** : la ligne des étiquettes (MOC, Modifié…) garde sa place même quand une carte n’en a pas.
- **Tri « Aléatoire »** partout (collection, listes, « À commander », page publique, back office) : un ordre au hasard, fixe le temps de la visite ; 🔃 (ou le rechoisir) remélange.
- **📋 Coller partout** : à côté de chaque « Importer une image » (dont « Remplacer une pièce », où il manquait) et dans les menus de photo (apparences alternatives, fiches personnalisées).
- **Appli plus légère** : les noms des tris réglés dans le back office (🧩 Éléments d’origine) étaient réécrits sans fin, des centaines de fois par seconde (batterie, lenteur) ; ils ne sont plus écrits que s’ils changent.
- **Nouveautés : figurines sans photo** : relues toutes les 6 h (avant : chaque jour) ; en attendant la photo de Rebrickable, l’image de leur torse imprimé sert de photo provisoire.
- **Nouveau tri « Augmentation / baisse (%) »** : de la plus forte hausse à la plus forte baisse (+, ~, −) ; avec 🔃 Renverser le tri, l’inverse.
- **Fiche d’un set ou d’une figurine** : sous l’estimation, des vignettes « Magasin » (prix public LEGO ; « Magasin (retiré) » pour un set qui n’est plus vendu), « Neuf » et « Occasion », chacune avec son prix sans figurines entre parenthèses (sur téléphone : une rangée par prix) ; la variation s’affiche aussi à côté du prix en haut quand 📈 est allumé. Comme les autres tris de variation, il affiche les pourcentages (📈).
- **Tris de variation renommés** : « Variation de prix (%) » (ex-« Évolution du prix ») met la plus grosse variation en % d’abord, hausse ou baisse (avant : les hausses d’abord) ; « Variation de prix (€) » (ex-« Écart de prix ») le plus gros écart en euros. La page publique trie de la même façon.
- **Téléphone** : en remontant au milieu de la page, la barre du haut ne se redéplie plus (listes, pastilles) ; elle reste réduite à la liste en cours jusqu'en haut de la page.
- **Couleur de la liste** : la pastille active des sous-listes (sur téléphone, sous le titre) et le pinceau actif suivent la couleur de la liste (avant : un fond rouge pâle fixe).
- **Logo individuel d’un set** : ses figurines rangées dedans l’affichent aussi (vignettes, page publique). Sur une figurine (y compris une figurine d’origine ouverte depuis son set), « Logo individuel » permet de retirer ce logo hérité (ou de le reprendre), ou de lui donner le sien.
- **Compteur de visites** des pages publiques : au plus une visite par personne et par jour (avant : chaque affichage comptait) ; les anciens chiffres ont été recalculés de la même façon.
- **Appli rouverte** ailleurs qu’à l’accueil (ex. Nouveautés, après qu’Android a fermé l’appli en arrière-plan) : « retour » ramène à l’accueil au lieu de quitter l’appli.
- **Sous-listes** : un bouton « ‹ » devant les pastilles ramène à la liste parente (aussi sur téléphone en faisant défiler).
- **Nombre de visites** des pages publiques : plus à côté du titre des listes (seul le 📤 y reste) ; il est dans la page 📊 Statistiques.
- **Nouveautés** (sets et figurines, appli et page publique) : à date de sortie égale (même mois, ou seulement l’année), l’ordre de lego.com départage — les plus récentes d’abord.
- **Nouveautés relevées toutes les heures** (avant : 12 h) ; ouvrir la page Nouveautés relit lego.com tout de suite.
- **Appli installée** : une page publique (collection, liste de souhaits, à surveiller, nouveautés, fiche partagée) ouverte dans la fenêtre de l’appli ne s’y garde jamais : en revenant dans l’appli, on retrouve l’appli privée. Dans un navigateur ordinaire, rien ne change.
- **Nouveautés** : les sets et figurines exclusives sans image ne s’affichent plus, sauf avec la case « Afficher celles sans image » (retenue sur l’appareil).
- **Page publique** : la fiche d’une figurine regroupée donne le même total que sa carte (ex. ×12) et la répartition « Dans mes sets : … ×3, … · seules : N », chaque set cliquable (avant : seulement le lot ouvert).
- **Back office → 🧩 Éléments d’origine** (groupe Avancé) : modifier l’existant — tris (« Trier par »), filtres (« ⚙️ Filtres ») et tuiles du haut : renommer, masquer, réordonner (brouillon puis Publier) ; calculs d’origine (boîte, livret, exemplaire modifié, seuils des flèches) : formule expliquée et pourcentage modifiable (effet immédiat).
- **Bas du menu latéral** : « © 2026 Clýde Hørd » n’est plus cliquable ; « ⚖️ Mentions légales · 🐙 GitHub » à côté.
- **Partager une page publique** : un petit **📤** à côté du compteur de visites (👁) sur « Toute la collection », la liste de souhaits, « À surveiller » et les Nouveautés partage le lien de leur page publique (ou le copie) ; ces liens quittent le bas du menu latéral (restent la démo, avec sa case « dans le menu latéral » dans les Réglages, et le code source).
- **Auteur** : mention « Clýde Hørd (ClydeHord sur GitHub), seul auteur et contributeur » dans le README et le fichier `AUTHORS.md`, à conserver dans toute copie.

- **Réglages réorganisés et uniformisés** : une seule règle — tout s’enregistre dès qu’on le change (✔), plus de bouton « Enregistrer » (estimations, zones BrickLink, nom des pages publiques, Instagram, couleur) ; seules les clés Rebrickable et BrickLink gardent « Vérifier et enregistrer ». Sections dans l’ordre : 🎨 Apparence (couleur, aide « ? ») · 💶 Prix · 🧮 Estimations · 🌐 Pages publiques (avec Instagram) · 🔑 Rebrickable · 🧱 BrickLink · 🔒 Sécurité · 📚 Aide et documentation · 🛠 Back office ; mêmes sous-titres partout.
- **Listes citées : « la liste « Ville » »** (fenêtres et questions sur une liste) au lieu du nom seul.
- **Téléphone : bouton « retour »** : il ramène à la page d’avant (liste, statistiques…) au lieu de quitter l’appli.
- **Téléphone, en descendant** : la liste en cours monte dans la barre du haut, entre ☰ et + (le + à droite) ; plus de bande en dessous.

### Nouveautés et améliorations
- **Nouveautés** (appli et page publique) : triées par date de sortie, de la plus récente à la plus ancienne (à venir d’abord ; même date : numéro de set le plus haut). **Page publique** : « ↩ Toute la collection » dans l’en-tête, à côté de la liste de souhaits.
- **Menu latéral** : espaces uniformes (12 px autour de chaque trait) ; liens publics : un appui ouvre la page ET copie son lien (la démo : copie seulement).
- **Chiffres des listes** (menu latéral, sous-listes, tuiles, barre du haut) : une liste compte aussi ses figurines rangées dans un set d’une autre liste (ex. 187e Légion : 2 fiches, 69 €) ; sans double compte quand le set est dans la même branche.
- **Plus de fiches qui se créent toutes seules** (tour complet du code) : une figurine sortie d’un set (« − », « Sortir du set ») rejoint sa jumelle seule identique au lieu de créer une fiche ; ranger dans un set où le même lot existe l’y ajoute ; une copie « Dupliquer puis modifier » / « ⧉ » jamais enregistrée (appli fermée en cours) est annulée au démarrage. Ajouter un set ne crée que le set et ses figurines d’origine (une figurine seule identique et non modifiée : une seule fiche, quantité augmentée).
- **Essais d’aberrations** (quantités absurdes, liens impossibles, boucles de listes, doubles clics, suppressions en cascade) : tout tient ; corrigé : une fiche ne peut plus être mise dans une liste qui n’existe pas.
- **Menus** : « Retirer du set » (doublon de « Sortir du set ») retiré de la fiche d’une figurine rangée ; type de fiche : plus d’option en double sur les téléphones qui montrent les options cachées.
- **Accessoires** : vignette avec ×N et ⋯ (comme les figurines) ; « 🔢 Modifier la quantité » multiplie ses pièces et sa valeur.
- **Figurines rangées dans un set d’une autre liste** (ex. clones de la 187e dans le tank rangé dans République) : leur liste les affiche (plus « Cette liste est vide ») et les compte ; changer la liste d’une figurine ouverte depuis son set ne déplace plus le set ; « ranger dans son set » garde la liste de la figurine.
- **Pièces** : toucher la photo d’une pièce (dans toutes les fiches) l’ouvre en grand ; le reste de la vignette garde son action.
- **Contrôle de cohérence (17/11 soir)** : totaux exacts (chaque fiche comptée une fois), 44 règles parent / enfant tenues, aucune fiche orpheline ; un doublon caché fusionné (sw1236 dans 75413). Ranger une figurine dans un set où un lot identique existe déjà l’y ajoute (plus de fiche en double).
- **Page publique = appli** : même nombre de figurines (les lots ajoutés dans un set comptaient pour 1), même regroupement « une figurine = une fiche », même ordre « Dernière modification ». Tuiles d’une liste à sous-listes : Sets / Figurines / Pièces comptent les sous-listes, comme la valeur (sauf « Non classées »).
- **Logos des vignettes** : 20 % plus grands, et cliquables — ils ouvrent la liste (appli et page publique).
- **Figurine seule + dans des sets** : la quantité descend jusqu’à ne plus avoir de figurine seule (💾 retire alors la fiche seule, celles des sets restent) ; plus bas, un message dit d’enlever la figurine d’un set.
- **Correctif** : une figurine d’un de mes sets (sans fiche à elle) s’ouvrait directement en modification ; elle s’ouvre en lecture comme toutes les fiches (🔧 pour modifier).
- **Affichage d’une liste** : cocher / décocher Émoji, Logo, Nom se voit tout de suite derrière la fenêtre ; Annuler remet l’affichage d’avant.
- **Émoji d’une liste** : « 😀 Choisir… » ouvre directement le choix ; « ✕ Retirer » apparaît dès qu’un émoji s’affiche (même celui « au hasard ») et la liste n’en a plus aucun.
- **🎯 Couleur prise dans une image** (couleur d’une liste, thème de l’application) : dans le logo ou une image importée, on touche un pixel ; pipette de l’écran sur ordinateur. Case « par défaut ».
- **Barre du haut** : plus de variation (flèche, %) à côté du prix de la collection et de la liste ouverte (elle reste sur la tuile « Valeur de la collection »).
- **Couleurs** : chaque liste peut avoir sa **couleur de thème** (✏️ Modifier la liste) — boutons, surlignages, barre du téléphone prennent sa couleur dans la liste (sous-listes comprises) et dans ses fiches ; Réglages → **🎨 Thème de l’application** (couleur générale) et **↺ Réinitialiser tous les thèmes**. Choisir un logo décoche l’émoji.
- **Nouvelle liste** : ＋ ouvre directement la fenêtre complète (nom, logo, émoji, « Afficher », rangement) ; Annuler n’en crée aucune. Choisir un logo coche « Logo » partout.
- **Pièces d’une figurine en plusieurs exemplaires** : 🔁 Remplacer et 🎨 Couleur demandent combien en changer (ex. 1 torse sur 9) ; la liste montre les gardées et les changées.
- **« Dans mes sets » : + remet une originale** : une figurine sortie de son set d’origine (−) y revient comme originale (avec ses modifications), et non plus comme « ajoutée ».
- **Figurines : une fiche** (suite) : une figurine ajoutée dans un set partiel ou un MOC (ex. le BARC) et la même originale d’un autre set (ex. l’AT-RT), identiques, n’ont plus qu’une carte ; « Dans mes sets » liste aussi les sets partiels et MOC.
- **Figurines : une fiche** (étape 2) : une figurine ajoutée dans un set, identique à une figurine seule, n’a plus qu’une carte et une fiche ; « Dans mes sets » compte aussi les exemplaires ajoutés (sets + seules = quantité) ; son − la remet dans les seules de la même fiche.
- **Figurines : modifications partagées** (étape 1) : les pièces échangées d’une figurine valent pour tous ses exemplaires (dans mes sets, originales et ajoutées, et seules), sauf les variantes « Dupliquer puis modifier » ; les exemplaires aux mêmes modifications n’ont plus qu’une carte.
- **Fiche d’une figurine rangée dans un set** : « Rangée dans le set » et « Dans mes sets » ne font plus qu’un bloc (« · rangée ici » en premier).
- **Set partiel** : sa fiche n’affiche plus ses pièces en vignettes (elles sont dans « 🔶 Pièces ») ; « Dans mes sets » montre ses nombres aussi en lecture.
- **« Dans mes sets » (fiche d’une figurine)** : **−** sort une figurine du set (elle redevient seule, prête pour un autre set) au lieu de la faire disparaître ; **+** range d’abord une figurine seule de même référence.
- **Logo des sous-listes** : aussi pour une sous-liste qui a ses propres sous-listes (ex. Grande Armée de la République) ; la liste la plus haute réglée sur « celle-ci » l’emporte.
- **Fiches : rien n’est enregistré sans 💾** (sauf les tâches) : le nom et les étiquettes (+ Étiquette, ✕) attendent la disquette ; fermer sans enregistrer les oublie. **Renommer** seulement en modification (après 🔧).
- **Faux « Cette fiche a été modifiée ailleurs »** : après avoir renommé une fiche (ou ajouté une tâche), changer sa photo puis enregistrer déclenchait l’alerte ; la fiche suit maintenant ses propres enregistrements.
- **Fiches** : le bouton pour passer en modification est maintenant **🔧** (la clé) au lieu de ✏️, pour ne plus le confondre avec 📝 (nouvelle tâche).
- **Tâches (📝 / ⚠️)** : enregistrées tout de suite ; fermer la fiche ensuite ne demande plus « Enregistrer les modifications ? ».
- **Guide utilisateur et notice du back office** : bouton **🤖 Condensé pour IA** — tout le guide en un texte à copier-coller dans une IA, avec la consigne de répondre « comment faire » d’après le guide (« 📋 Tout copier », ou .txt).
- **Doc technique (privée)** : bouton **🤖 Condensé pour IA** — une page avec tout ce qu’une IA doit savoir (règles du projet, carte des fichiers, l’essentiel de la doc technique), « 📋 Tout copier » ou téléchargement en .txt. Regénéré avec les guides ; jamais publié.
- **Réglages** : « 🛠 Back office » dans le sommaire ouvre directement le back office.
- **« Voir sur »** : le lien **Rebrickable** revient à côté de BrickLink (fiches, page publique, fiche partagée).
- **Téléphone** : en descendant, la barre du haut ne montre plus que la liste en cours ; dès qu’on remonte, tout revient (appli et pages publiques).
- **Correctif** : la page publique restait bloquée sur « Chargement… » (ligne du tri cassée par un commentaire).
- **Étiquettes** : plus que Complet, Amélioré, Modifié, Set partiel et MOC — « Pièces ajoutées », « N figurines remplacées / ajoutées », « Sans figurines » et « Prix par les pièces » ne s’affichent plus (le badge « Sans figurines » reste).
- **Étiquettes** : des pièces d’origine retirées et d’autres pièces ajoutées (ex. 3 têtes retirées, 3 têtes différentes ajoutées) donnent « Modifié », plus « Amélioré ».
- **Vignettes** : le prix en gros tout en bas, le prix à l’unité au-dessus (plusieurs exemplaires) ; plus de ligne « réel ».
- **Tris** : « Évolution du prix » (hausses d’abord ; ex-« Variation ») et « Écart de prix » (le plus gros écart en euros, hausse comme baisse) ; les choisir affiche les variations. Menu ⇅ Tri : « Définir par défaut » — toutes les listes de la collection (« Toute la collection » comprise) prennent ce tri, ↺ y revient.
- **Logo individuel d’une fiche** (mode modification, à côté de « Afficher dans la vue générale ») : sur sa vignette, il remplace le logo de sa liste et de la liste parente (ex. le Slayer avec le logo de DOOM, sans créer de liste DOOM). Tous les types de fiche ; page publique comprise.
- **Barre du haut d'une liste** : son logo devant son nom ; nom décoché (« Afficher le nom ») : le logo seul. Page publique : idem.
- **Guides en wiki** (plus de PDF) : `/guide-utilisateur` et `/backoffice/guide` — une page par chapitre, sommaire, « sur cette page », recherche dans tout le guide, captures qui s'agrandissent ; imprimer une page imprime le guide entier. Anciennes adresses redirigées. Écrits par `python3 docs/build_docs.py` (moteur : `docs/wiki.py`).
- **Back office — clic droit dans l'aperçu** : les outils de l'élément (modifier, masquer, copier / coller le style, copier le texte ou le sélecteur, couper puis coller avant / après, reculer / avancer d'un cran, élément parent, annuler ses modifications). Maj + clic droit : le menu du navigateur.
- **Back office — Comportements** : interrupteurs des nouveautés (flèches de variation, bouton « Comprendre les variations », fiches ouvertes directement en modification, pièce touchée = photo en grand, pages publiques sans la rangée de listes collée) ; **script libre** (JavaScript exécuté au chargement de l'appli privée, jamais sur les pages publiques).
- **« … devient une figurine »** : une vraie recherche (nom, numéro, photo, photo de la fiche) au lieu de taper le numéro.
- **Page publique** : en défilant, les listes principales restent dans la barre collée ; dans une liste, un bouton discret « ↩ Toute la collection ».
- **Sauvegardes** : 30 sauvegardes quotidiennes et 80 copies « avant-… » gardées séparément (les copies ne chassent plus les quotidiennes).
- **Tri « Variation »** : les fiches rangées selon leur flèche (plus fortes hausses d'abord ; sans relevé à la fin).
- **🔃 Renverser le tri** : un bouton, à droite de « Tri » (téléphone compris), donne l'ordre inverse du tri en cours (retenu liste par liste) ; pages publiques : idem.
- **Flèches de variation** : un peu plus grosses et plus visibles ; bouton **📈** dans la vue générale pour les montrer ou les cacher à la volée (allumé quand elles sont affichées) ; dans une fiche, la variation est toujours affichée — prix, estimation, cote et détail des prix (💶 Tarifs), à la taille du texte voisin. Leur apparence (seuils, « ~ », pourcentage, taille) se règle dans le back office (Comportements → Prix et variations) ; les options sont retirées des Réglages de l'appli, les valeurs choisies sont gardées.
- **Comprendre les variations** : sans le paragraphe d'explication.
- **Barre des filtres** : boutons en carrés de même taille, collée en haut de l'écran en défilant, recherche surlignée quand elle contient du texte ; 📈 éteint a la même allure que les autres boutons (sur téléphone, l'effet « survol » ne reste plus après le toucher).
- **Fiche d'un set** : plus de « · N dans le set » sur les figurines (le ×N le dit) ; la variation de leur prix est affichée.
- **Correction — estimation détaillée des fiches** : depuis l'ajout du curseur de taille des flèches (17/11 au matin), l'application ne lisait plus les réglages des estimations (décote d'une figurine d'origine modifiée, bonus de la boîte, livret) et prenait les valeurs par défaut (décote 5 % au lieu de 3 %…). Le détail de la fiche suit de nouveau les réglages ; les totaux et les cartes (calculés par le serveur) étaient justes.
- **Sous-listes** : « Afficher cette sous-liste dans le menu latéral » (sous sa liste parente ; une liste principale y est toujours ; décochée, la ligne « Menu latéral » du tableau se grise) .
- **Tableau « Afficher » d’une liste** : quatre lignes — « Menu latéral », « Barre supérieure », « Titre », « Vignettes » (le petit logo en bas à droite des cartes ; sans case « Nom »).
- **↳ en haut du menu latéral (à droite de ＋ et ⇅)** : montre ou cache toutes les sous-listes dans le menu (celles cochées « Afficher dans le menu latéral » restent) ; retenu sur l’appareil.
- **Affichage d’office d’une liste** : titre = le logo seul, barre supérieure = logo + nom, vignettes = le logo (sans logo : l’émoji) ; sur les vignettes, le logo de la sous-liste elle-même ; une liste principale peut choisir « Logo des sous-listes : celle-ci / listes enfant ».
- **« Menu latéral »** : ainsi nommé partout (plus « menu de gauche »).
- **Listes : logo ET émoji** ; « Modifier la liste » : un tableau « Afficher » — menu latéral / vue générale × émoji / logo / nom, à la carte (sans émoji ni logo coché, le nom s'affiche toujours). Pages publiques : la rangée des listes suit le menu latéral.
- **Revue complète du code (17/11)** : corrigés — une ligne cachée derrière un commentaire dans les données des pages publiques (un set partiel y passait pour un MOC), une fonction disparue appelée sur un code-barres inconnu, les variations calculées deux fois ; flèches un peu plus grandes dans les lignes de détail et les vignettes ; variation des figurines ajoutées depuis le dernier relevé ; jamais de flèche dans une fiche de la liste de souhaits.
- **Variations sur tous les types de fiche** : set, figurine, figurine vue depuis son set, MOC, set partiel, figurine MOC — sous l'estimation, sur la ligne de la cote (set et figurine) et sur les figurines rangées d'un MOC ou d'un set partiel. Une fiche sans relevé d'avant (ajoutée ou copiée depuis, par exemple une figurine dupliquée puis modifiée) a sa variation d'après ses composantes : la cote et le prix d'avant de ses pièces échangées.
- **Estimation d'un MOC, d'un set partiel ou d'une figurine MOC** : la ligne « Source : BrickLink, sinon BrickOwl » est retirée.
- **⚙️ Filtres** : plus de petit nombre sur le bouton (il se colore déjà en rouge quand un filtre est actif).
- **Estimation d'une fiche** : variation aussi sur « Figurines ajoutées » et « Figurines manquantes » (moyenne pondérée par leur prix).
- **Bouton ↑ (et « ? »)** : plus bas quand une fiche est ouverte, sur téléphone et tablette ; il ne masque plus l'estimation.
- **Estimation d'une fiche** : la variation passe à la ligne, sous le montant ; elle est suivie du relevé comparé — « (par rapport à 08:05) » s'il a moins de 24 h, sinon « (par rapport au 16/11/2026) ».
- **Variations dans la fiche** : plus sur le prix tout en haut ; sur l'estimation, la cote, les figurines et désormais les **pièces** (leur prix précédent est gardé à chaque relevé : les marques apparaissent au fil des relevés).
- **Variation faible (« ~ »)** : l'icône seule, sans pourcentage ; un bleu plus vif en clair, plus clair en sombre (il ressortait mal). Les seuils de hausse et de baisse se règlent de nouveau dans Réglages → Estimations.
- **Comprendre les variations** : le ← d'une fiche ouverte depuis la liste (ou le retour du téléphone) ramène à la liste, même période.
- **↑ ↓ ~ à côté des prix** : une marque très discrète de la variation depuis le dernier relevé (↑ vert en hausse, ↓ rouge en baisse, ~ stable), sur les cartes, la fiche et les totaux ; Réglages → Estimations : afficher ou non, seuils de hausse et de baisse (3 % par défaut), « ~ » quand c'est stable, afficher le pourcentage. Pages publiques : seulement si les prix y sont montrés.
- **🔍 Comprendre les variations** (Statistiques) : pour la liste affichée, ce qui a fait bouger la valeur, du plus gros au plus petit — ajout ou retrait d'une fiche, hausse ou baisse d'une cote (ancien → nouveau prix ; la figurine en cause est citée quand un set bouge à cause d'elle), quantité, fiche modifiée ; périodes Aujourd'hui / Depuis hier / 7 jours / 30 jours / Depuis le début.
- **Prix trop minces** : un prix BrickLink fondé sur moins de 3 ventes (dans toutes les zones) n'est plus retenu ; l'ancien prix est gardé et la fiche le dit (« prix gardé : seulement 1 vente »).
- **Toucher une pièce** (pièces d'une figurine, d'un MOC, d'une figurine MOC) ouvre sa fiche (où la trouver, prix) ; son ⋯ garde les fonctions.
- **Étiquette « Incomplet » supprimée** partout (cartes, fiches, filtres, page publique, partage, back office).
- **Barre du haut d'une liste à sous-listes** : la valeur seule, sans billet 💶.
- **Nouvelle fiche** : la 💾 en haut aussi (le bouton « Ajouter » du bas reste) ; « + Pièce », « + Set », « + Figurine » toujours proposés : sur une fiche pas encore ajoutée, ils l'ajoutent d'abord, la rouvrent, puis font l'action.
- **Figurine MOC créée avec ses pièces** (ajoutées ou validées à la création) : pas de scan de la photo ni de passage dans « MOC à valider ».
- **Correction — « Dupliquer puis modifier »** sur une figurine d'origine : c'est une copie EN PLUS (figurine ajoutée), l'originale reste dans le set ; une copie laissée sans modification est retirée. (Avant, l'originale disparaissait du set.)
- **Set partiel → Pièces** : « 🔎 Le set sur Rebrickable » à côté de « Le set sur BrickLink ».
- **Cartes : logo de la liste en bas à droite**, dans la ligne du prix (20 px de haut ; il rétrécit plutôt que de passer sur le prix). Dans « Toute la collection » : le logo de la liste principale ; dans une liste parente : celui de la sous-liste qui contient la fiche (rien pour ce qui est rangé directement dans la liste). Page publique : idem.
- **Corbeille 🗑️** : partout en émoji couleur (le menu d'une pièce montrait un petit glyphe noir pour « Je ne l'ai pas : la retirer »).
- **« 🖼️ À partir de la photo actuelle »** dans toutes les recherches de pièce lancées depuis une fiche (Remplacer, Échanger cette pièce, MOC…), plus seulement dans « Ajouter une pièce ».
- **Remplacer une pièce** : la recherche directement en haut (nom, référence, photo, photo actuelle), à la place des onglets et du champ « Filtrer » ; les pièces équivalentes dessous.

## 16 novembre 2026

### Nouveautés
- **🛠 Back office** (`/backoffice`, lien dans Réglages) : tout modifier **sans code ni console**, avec un brouillon, un aperçu en direct et « Publier ».
  - **Modifier à la souris** n'importe quel élément (texte, style, masquer, icône ou image d'un bouton, lien, action au clic, décalage) ; mode « ✋ Déplacer ».
  - Apparence, **boutons et tailles**, textes, **étiquettes et pastilles** (renommer, recolorer, masquer, condition d'affichage, en créer), fiches,
    champs personnalisés, liens automatiques, cartes, menu.
  - **Pages** à vous, par blocs (textes, images, boutons, listes de fiches, totaux, tableaux), éventuellement publiques (`/p/…`).
  - **Page « Réglages »** réorganisable ; **comportements** (page de départ, tri par défaut, raccourcis clavier, clics).
  - Avancé : formules et champs calculés, règles « si… alors », tuiles, vues, tris, filtres ; corrections du catalogue ; tableur CSV.
  - Serveur : sauvegardes, état et journal, fichiers de données, paramètres, images, **mots de passe**, code de l'application (avec filets de sécurité).
  - **Mot de passe à part**, créé à la première visite (avec avertissements) ; il permet aussi de changer celui de l'application s'il est oublié.
  - **Notice illustrée** : `docs/briquotheque-backoffice.pdf`, et en ligne (« ❓ Notice », lien « ❓ Aide » dans chaque rubrique).
  - Les fonctions de cette version s'y règlent aussi : **Comportements › Figurines identiques** (ne pas regrouper ; ne pas proposer « est-ce celle de
    ce set ? »), **Paramètres du serveur** (tâche « Photo à faire »), étiquettes posées à la main (mêmes réglages que celles de l'application, « Complet »
    comprise), nouvelles variables pour les formules, règles, vues et le tableur (`{statut}`, `{etiquettes}`, `{exemplaires}`, `{dans_un_set}`, `{accessoires}`).
- **Une figurine, plusieurs exemplaires** : la même figurine peut être seule et dans plusieurs de vos sets (ex. celle fournie avec un set et la même
  achetée à part) — **une seule carte** « ×N » et **une seule fiche**. « Quantité » donne le total ; « Dans mes sets » a un **− / +** par set (ex. 20
  figurines : 10 dans un set, 8 dans un autre, 2 seules) et une ligne « Seules (sans set) ». Le lien de partage donne le total et les sets. Pas de
  regroupement si la figurine du set a des pièces échangées, des accessoires ou un autre nom.
- **Lots de figurines** : les pièces d'une fiche sont comptées pour toutes ses figurines (fiche ×28 : tête ×28, casque ×28…). « 🔢 Modifier la quantité »
  sur une pièce d'origine (ex. 20 têtes d'origine, les 8 autres retirées), autres pièces ajoutées en nombre : une seule fiche pour un lot pas tout à
  fait identique, estimée au réel ; la décote « Modifiée » ne touche que les figurines modifiées. Les fiches existantes sont converties d'elles-mêmes
  au premier démarrage (même valeur ; sauvegarde avant).
- **Étiquettes à la main** : « + Étiquette » sous le nom d'une fiche (Complet, Amélioré, Modifié, Set partiel, MOC) ; **✕** pour retirer une étiquette,
  y compris celle que l'application calcule (« + Étiquette » → « ↩ Remettre »). Elles s'affichent sur les cartes, comptent dans ⚙️ Filtres et sur les
  pages publiques ; retirer une étiquette ne change pas la valeur.
- **Accessoires (mini-constructions) chiffrés** : liste de pièces facultative (XML BrickLink / Studio collé ou importé, CSV Rebrickable) → estimation
  réelle, ajoutée à la valeur de la fiche.
- **⧉ Copier cette fiche** sur les sets, sets partiels et MOC (copie dans la même liste) ; **⧉ Copier/Déplacer un exemplaire** sur les figurines
  (copier, ranger dans un set, déplacer vers un autre set, sortir du set).
- **Set ajouté dont vous aviez déjà une figurine seule** (ou souhait passé dans la collection) : « est-ce celle de ce set ? » — oui : elle devient sa
  figurine d'origine (une seule fiche ; photo, apparences, pièces, accessoires et tâches gardés).
- **« Photo à faire »** : tâche posée d'office sur une figurine sans aucune image disponible ni photo ; elle part d'elle-même dès qu'une image existe.
- Fiche d'un set, menu **⋯** d'une figurine : **🗑 Supprimer (je ne l'ai pas)**. Fenêtres qui demandent un nombre : boutons **− / +**.
- Vue générale : **« ⇅ Tri » est un menu identique à « ⚙️ Filtres »** (même bouton, même fenêtre, mêmes lignes), sur la page privée et les pages publiques ;
  la barre tient sur une seule ligne à toutes les largeurs (téléphone, tablette, ordinateur).
- Pages publiques : même affichage que la page privée (cartes, étiquettes, filtres, fiches), figurines de chaque exemplaire montrées une par une dans la fiche publique.
- Fiches publiques et partagées : lien **LEGO.com** (avec le prix public pour un set encore en vente) ; liens de partage : case **« Afficher les prix »** modifiable à tout moment.
- **Hors ligne** : toutes les fiches sont disponibles sans réseau, même jamais consultées ; un serveur éteint derrière un proxy est reconnu.
- Inventaire : résumé une information par ligne, estimation des pièces « à vérifier », total ; la couleur demandée est toujours vérifiée (pièce de remplacement comprise).

### Corrections et améliorations
- **Back office** : l'aperçu s'ouvre toujours sur l'accueil (et ne modifie plus l'endroit retenu par l'appli) ; zoom de l'aperçu − 100 % +.
- Barre de la liste ouverte (valeur, Tout, Sets, Figurines, Pièces) : plus grande.
- Fiche : le type (« 🧱 Set complet », ex-« Set ») sous l'image, à la hauteur des boutons Pièces / Plan / Tarifs. Liste : « ✏️ Modifier la liste » devient un simple ✏️, à droite sur la ligne du titre ; logo du titre agrandi de 50 %.
- Menu latéral : à côté de chaque liste, le **nombre de fiches** (au lieu du nombre de sets).
- **Ordre des sous-listes** : sur ordinateur, glisser une pastille de sous-liste devant / derrière une autre ; sur téléphone, « Ranger après… » dans « ✏️ Modifier la liste ».
- **Retour dans l'appli** : l'endroit (liste, fiche ouverte, fenêtres) est retenu en continu, plus seulement au passage en arrière-plan — l'appli fermée par Android rouvre là où vous étiez ; après plus d'une heure hors de l'appli, elle rouvre sur l'accueil.
- **Étiquettes revues** : **Modifié** = un élément en remplace un autre (même avec des ajouts) ; **Incomplet** (nouvelle, filtrable, calculée seulement : pas dans « + Étiquette ») = un élément retiré sans rien à sa place (pièce retirée, figurine manquante, sans figurines) ; **Amélioré** = tout est là, des choses ajoutées, rien de retiré ni remplacé. Set partiel : valeur = ses pièces, sans décote.
- **Décote « modifié » d'un set** : seulement si une figurine **d'origine** est modifiée (ligne « Figurine d'origine modifiée : décote ») ; des pièces du set échangées ou des figurines ajoutées modifiées comptent pour leur écart de prix, sans décote. L’étiquette « Modifié » ne change pas. Set complet : plus de ligne « Figurines : toutes présentes ».
- **Dupliquer puis modifier** le seul exemplaire d'une figurine d'un set : ses pièces échangées partent avec la copie (elles restaient sur l'original, qui paraissait ensuite modifié : ligne « Figurines modifiées » et décote à tort). Estimation : les ajoutées, modifiées ou non, restent dans « Figurines ajoutées » ; « Figurines modifiées (pièces) » ne concerne que les originales.
- « Ajouter des figurines à … » (on y cherche les originales à remettre) : le ✓ ne compte que les exemplaires non modifiés, une seule fois (il comptait deux fois les figurines rangées : 2 → « ✓4 ») ; une figurine dont il ne reste que des copies modifiées reste « manquante ».
- **Menu d'une pièce** remis en ordre : d'abord ce qui la modifie sur la fiche (🎨 Changer la couleur, 🔁 Échanger, 🔢 Quantité, 🗑 Retirer), puis le détail, puis À commander / inventaire / copier / déplacer ; en lecture, rien qui modifie. **Recherche de pièces** : traducteur intégré — une recherche en français qui ne trouve rien est traduite automatiquement en anglais et relancée.
- **Fiches en lecture d'abord** : une fiche s'ouvre sans les boutons qui modifient (étiquettes, infos, Tarifs, Pièces, Évolution, tâches et partage restent) ; ✏️ en haut passe en modification ; ↩️ (à gauche de 💾) annule les modifications non enregistrées ; en lecture, Boîte / Livret / À construire (« Plan » renommé « Livret ») n affichent que ce qui est coché (case cochée, non modifiable) ; 💾 enregistre sans fermer la fiche, qui revient en lecture.
- **Catégories de tâches** : l'emoji fait partie du texte — « ✏️ Renommer » s'ouvre avec « 📷 Photo », on change l'emoji et/ou le nom au même endroit (« Autres » : « ✏️ Modifier », emoji seulement) ; sans emoji, aucun.
- **Pièces** : « 🎨 Changer la couleur » (menu ✏️ d'une pièce) — même pièce, autre couleur, sans recherche. **Recherche en français** : mots courants traduits (jambes, tête, torse, casque, cheveux longs…, couleurs) ; « jambes » / « jambes unies » [couleur] donne directement les jambes unies (une pièce par couleur chez Rebrickable), « jambes courtes » les jambes courtes.
- **Cartes** : dans une vue de plusieurs listes (Toute la collection, À construire, une liste avec ses sous-listes), le logo de la liste en tout petit à gauche de la référence (MOC compris) ; « ⚙️ Filtres » → « Sur les cartes : Logo de la liste / Nom de la liste ». Page publique : idem.
- **✏️ Modifier la liste** (discret, sous le titre) : nom, logo, « Afficher le nom » (décoché : seul le logo s'affiche, partout), rangement et suppression dans une seule fenêtre ; les liens Renommer / Logo / Ranger / Supprimer ne s'affichent plus sous le titre.
- **Logo des listes** : bouton « 🖼️ Logo » sous le titre d'une liste — importer ou coller une image (PNG transparent gardé tel quel) ; affiché devant le nom dans le menu, le titre, les pastilles des sous-listes et les pages publiques. L'image passe par l'outil de recadrage habituel (cadre libre proposé au plus près, rotation, 🪄 Détourer qui SUPPRIME le fond : PNG transparent) ; affichée à la hauteur d'un emoji, largeur selon le recadrage ; « 😀 Choisir un emoji » à la place d'une image ; une liste sans icône reçoit un emoji d'office (toujours le même). En thème sombre, un léger contour clair garde lisibles les logos noirs.
- **Une action sur une figurine d'un set n'agit que sur elle** : sur l'originale (voir sa fiche, échanger des pièces, dupliquer), les exemplaires en
  plus ont d'abord leur propre fiche ; sur une fiche rangée en lot (×9…), Déplacer, Sortir du set et Supprimer portent sur un seul exemplaire.
- **Nombre de figurines** : une fiche rangée en lot dans un set (×2, ×9…) comptait pour une seule figurine ; elle compte maintenant chaque exemplaire.
- **Originales, ajoutées, modifiées : une seule règle.** Une figurine rangée dans un set avec sa propre fiche (copie « Dupliquer puis modifier »,
  ajoutées séparées, figurine rangée à la main) comble d'abord les originales qui manquent au set (les non modifiées en priorité) ; seul le reste est
  « ajouté ». Plus de « Modifié » à tort quand une originale a sa propre fiche. Une figurine rangée **modifiée** reste une ajoutée (« Amélioré ») :
  elle ne rend jamais le set « Modifié ». Tuiles des figurines rangées : marque « (modifiée) ».
- **Remplacer une pièce** : « Ajouter cette pièce » fonctionne pendant le chargement des couleurs (couleur de la pièce remplacée).
- Fiche d'un set, **tuile des ajoutées** (exemplaires en plus du nombre prévu) : « Voir la fiche », son nom et « Échanger des pièces » ouvrent une fiche
  à elles — changer une pièce ne modifie plus l'originale. Fermée sans changement, cette fiche rejoint les autres. Séparer un lot aux pièces échangées
  partage les échanges et leur prix au prorata.
- Toutes les fiches : coche **👁 Afficher dans la vue générale**. Décochée, la fiche n'a plus de carte dans la grille (page privée et page publique) ;
  elle reste comptée dans les totaux et le filtre texte la retrouve. Une copie « Dupliquer puis modifier » est décochée d'office.
- Fiche d'un set, menu **⋯** d'une figurine (originale ou ajoutée) : **✏️ Dupliquer puis modifier** — un exemplaire devient une figurine
  **ajoutée** avec sa propre fiche (pièces, photo, nom, accessoires), rangée dans le même set, **sans carte dans la vue générale**. Enregistrée sans
  rien de différent, elle rejoint les autres ; différente (pièces changées…), elle reste séparée. La valeur ne change pas.
- Fiches : bouton **←** à gauche du nom pour revenir à la fiche d'où vous venez (ex. figurine → son set → une autre figurine…) ; le geste ou bouton « retour » du téléphone fait de même.
- **Set que vous n'avez pas** : ses figurines s'affichent même quand le catalogue des cotes ne le connaît pas (liste BrickLink) ; touchez-en une pour
  ouvrir sa fiche et l'ajouter seule, puis ← pour revenir au set.
- **Ajouter une pièce** : lien **🔎 Où la trouver** — les sets et les figurines qui contiennent cette pièce, dans la couleur choisie.
  Un appui sur la photo d'un set ou d'une figurine l'agrandit (la photo en grand passe désormais devant toutes les fenêtres).
- **Accessoire** : « 📷 Changer la photo » (ou « Ajouter une photo ») dans son menu — appareil photo, fichier ou image copiée.
- **Qui se range où** — règles désormais garanties par le serveur : un set, un set partiel et un set MOC peuvent contenir des figurines ; seules les
  figurines et les figurines MOC se rangent dans un set (jamais un set dans un autre) ; un exemplaire n'est rangé que dans un seul set. Plus de fiche
  « orpheline » : un set supprimé laisse ses figurines ajoutées dans la collection, seules ; un set déplacé vers la liste de souhaits n'y emporte aucune
  fiche de figurine, et les retrouve dès son retour ; un set acquis depuis la liste de souhaits a tout de suite les fiches de ses figurines.
- **Changer le type d'une fiche** : un set changé en set MOC ou en set partiel garde **une** fiche par figurine (elles étaient en double) ; changé en
  figurine, il n'en laisse aucune ; changé en un autre set, il prend aussitôt les figurines du nouveau set ; une figurine rangée changée en set sort de son set.
- **Valeurs** : contrôle complet — chaque figurine est comptée une seule fois (dans son set si elle y est rangée, sinon dans le total général).
- Fiche d'un **set MOC** ou d'un **set partiel** : son estimation comprend les figurines rangées dedans (ligne « Figurines »), comme sa carte.
- **↩ Restaurer l'image** : la carte affiche bien l'image officielle actuelle. Les images du catalogue gardées sur l'appareil sont refaites une fois,
  puis relues d'elles-mêmes (au plus tard après 30 jours) : la carte et la fiche montrent la même image.
- **Recadrage** : sous le curseur de rotation, **−** et **+** font tourner l'image d'un degré par appui (à la place du bouton « ± »).
- Étiquette **« Modifié »** d'un set : seulement si une figurine d'**origine** est remplacée ou modifiée (ou des pièces du set retirées ou remplacées).
  Des exemplaires en plus, même modifiés, donnent « Amélioré » ; les exemplaires en plus d'une figurine d'origine comptent comme des figurines ajoutées.
- Fiche d'un set : **un seul nombre par figurine** — jusqu'au nombre prévu par le set, des « originales » ; au-delà, des « ajoutées ».
  « 🔢 Modifier la quantité » et « 🗑 Supprimer » agissent sur la tuile touchée (les ajoutées, ou celle d'origine), plus sur le tout.
- Fiche d'un set : « **Estimation de mon set** » comptait deux fois ses figurines d'origine (ligne « Figurines ajoutées » en double) ; les cartes, les
  listes et le total de la collection étaient justes. Une seule ligne « Figurines ajoutées » désormais (exemplaires en plus et fiches rangées).
- **Chaque fiche est unique** : toucher une figurine dans un set ouvre sa fiche (plus celle d'une autre figurine de même référence) ; renommer une
  figurine d'un set ne renomme plus celle des autres sets ; une figurine renommée rangée dans un set y garde sa fiche et son nom.
- Figurine ouverte alors que vous en avez une fiche : **sa fiche** s'ouvre (💾 en haut) ; une photo modifiée n'est plus perdue.
- **Figurines qui quittent un lot modifié** (sortir du set, déplacer, copier un exemplaire) : « combien sont modifiées ? » — leurs pièces les suivent ;
  **lot qui diminue** sous le nombre de figurines modifiées : ajustement proposé.
- Un set déplacé vers la **liste de souhaits** n'emporte pas les figurines ajoutées que vous possédez ; changer la liste d'un set depuis sa fiche emmène
  ses figurines de la même liste, comme le déplacement depuis la liste. La liste de souhaits ne modifie jamais la collection.
- **Figurines du BrickLink Designer Program** (« adp… » au catalogue des cotes, « bdp… » chez BrickLink) : image, prix, liens et export « wanted list »
  prennent la référence BrickLink.
- Fiche d'une figurine : « Set qui la contient » devient « **Aussi dans ce set — pas dans ma collection** ».
- **Lien de partage** collé dans une messagerie : l'aperçu affiche le **nom de la fiche** (plus « Fiche partagée »).
- Fiche d'une **figurine d'un de vos sets** : bouton **Supprimer** (elle est retirée de ce set, après confirmation) ; supprimer la fiche unique d'une
  figurine ne supprime que ses exemplaires sans set.
- Fiches des sets et des figurines du catalogue : bouton **↩ Restaurer l'image** (parmi les boutons de la photo) pour reprendre l'image officielle.
- **🪄 Détourer le fond** : un pourcentage avance pendant le calcul (estimation d'après la durée du dernier détourage). Recadrage : le **pinceau** garde
  la dernière taille utilisée ; cadre des figurines verrouillé au format des vignettes (déverrouillable).
- Fiche publique : figurines modifiées et ajoutées dans leurs propres groupes ; mêmes étiquettes que la fiche privée.
- Recherche sans résultat à cause des filtres cochés : section « Résultats sans filtres ».
- Mode hors ligne : une autre page visitée ne peut plus prendre la place de l'application dans la copie hors ligne.

## 15 novembre 2026

### Nouveautés
- **Liste des pièces de la fiche** : retirer, remettre, changer une quantité ne s'enregistre plus tout seul — seulement avec **💾** (fermer sans enregistrer annule). « ↩ Remettre la pièce d'origine » du menu demande aussi s'il faut garder ou retirer la remplaçante.
- Bouton **↺** à gauche du filtre : remet les filtres à zéro. Menu latéral : **✅ Aucune tâche** quand il n'y a plus rien à faire.
- **Ajouter une pièce** : option « 🖼️ À partir de la photo actuelle » (la photo de la fiche, cadrée sur la pièce), aussi dans « Pièces de … ».
- **Nouveautés** : cases « Afficher ceux déjà dans la liste de souhaits » et « Afficher les surveillés » (sets marqués clairement). Partout « liste de souhaits » au lieu de « wishlist ».
- **Téléphone et tablette** : tout tient dans la largeur de l'écran (menu Filtres, barre du haut, boutons photo, réglages des prix, tableaux des stats, pages publiques). Nouveautés déjà souhaitées ou surveillées : pas d'encadré.
- Un **MOC** n'a que l'étiquette « MOC ». Les cartes n'affichent plus « Dans le set … ». Plus de liseré violet autour des apparences alternatives.
- **Détourage ISNet** sur votre serveur (facultatif), **🖌️ pinceau** blanc, cadre au format des vignettes qui peut dépasser de la photo, cadrage proposé autour de l'objet.
- **Sous-listes en pastilles** en haut de la liste (la liste, ses sous-listes, « Non classées »).
- **Nouveautés** : photos officielles défilables, lien lego.com, figurines exclusives (photo, set, liste de souhaits, annonces BrickLink).
- **Apparences** : « Définir comme principale », défilables en grand ; coche « Afficher dans la vue générale ».
- **Sans internet** : images gardées en local (sources de secours essayées l'une après l'autre).
- **Réglages des prix** (curseurs) ; option « prix sur la collection publique » ; mentions légales éditables.
- **Figurines dans les sets** : une figurine rangée dans un set peut être dans une autre liste ; déplacer un set emmène ses figurines de la même liste ; on peut sortir une seule figurine (ou plusieurs) d'un set ; « Dans le set » suivi du nom du set.
- **Détourage** refait (fonds colorés et plissés, fonds enfermés) ; bouton « 🪄 Détourer le fond » dans le recadrage, le cadre est gardé.
- **MOC** : pièces repérées par le scan validées directement dans la fiche.
- **Réglages › Réseaux sociaux** : compte Instagram affiché sur les pages publiques. Les fonctions Instagram (relevé, analyse des photos) sont retirées.
- Bouton « Fermer » dans le menu des Réglages ; apparences alternatives en violet dans les listes.

- **Cadrage automatique** de toute image importée ; détourage qui retire aussi les ombres sur fond clair ; après détourage, « Détourer avec … » (outil en ligne).

### Corrections et améliorations
- Fiche : étiquette d'état sous le nom (Modifié, Amélioré, Set partiel, MOC) ; plus de ✏️ — toucher le nom renomme ; tâches : 📝 au lieu du ✅ vert.
- Remettre une pièce d'origine remplacée : l'application demande s'il faut garder la remplaçante (elle devient une pièce ajoutée) ou la retirer.
- Pièces retirées et pièces d'origine remplacées (« remplacée par … ») : toujours affichées, en rouge et barrées, avec « ↩ Remettre » (liste des pièces de la fiche, « Pièces de … », « Échanger des pièces »).
- Cartes : étiquette « Set partiel » (bleu-vert) ; un set ou une figurine qui n'a que des ajouts (pièces, figurines) porte « Amélioré » ; complet sans changement : aucune étiquette.
- Menu « ⚙️ Filtres » : sélection multiple par étiquette — Complet, Amélioré, Modifié, Set partiel, MOC (avec leur nombre) ; appliqué tout de suite ; « 📥 Non classées » avec son emoji.
- Collection publique : « MOC uniquement » n'affiche plus les sets partiels ; la fiche d'un MOC n'a plus de lien BrickLink ; le nom du compte Instagram n'est plus coupé en bas (y, g, p).
- Collection publique : listes comme dans l'appli — listes principales, puis sous-listes et « Non classées » encadrées de rouge ; une liste montre tout son contenu ; plus de cartes « sous-listes ».
- Statistiques : pastilles des listes regroupées comme la vue générale (listes principales, puis sous-listes et « Non classées » encadrées) ; une liste compte ses sous-listes.
- Fiches partagées : seulement le nom et la date (plus de numéro, de « MOC » ni de « depuis le »).
- La case « Valeur de la collection » ouvre les statistiques de la liste active (sa sous-liste, ou ses « Non classées »).
- README : prérequis de la machine Linux (processeur, mémoire, stockage selon le nombre de fiches) et l'outil de détourage intégré, ISNet.
- Photo en grand (fiche, apparence) : plus de bouton « 📋 Coller » (il reste dans « Modifier l'image »).
- Images : clic droit / appui long ouvrent de nouveau le menu du navigateur (enregistrer, copier…), y compris dans « Modifier l'image ».
- Réglages › 💶 Prix : **zones des prix BrickLink** réglables (pays, régions, monde, dans l'ordre, jusqu'à 8) et le nombre minimum de ventes / annonces avant de passer à la zone suivante ; drapeaux (pays, 🇪🇺, 🌎 🌏 🌍, 🇺🇳), noms et liens BrickLink suivent.
- Détourage : seulement local (ISNet sur le serveur, sinon sur l'appareil) — plus d'outil en ligne (réglages, bouton « Détourer avec … », envoi vers un site extérieur retirés).
- « Échanger des pièces » (set ou figurine) : pour chaque pièce (ou sa remplaçante), le prix **neuf** et le prix **d'occasion** BrickLink (zones réglées), × la quantité, avec le drapeau de la zone ; demandés pour les lignes visibles.
- Documentation : README réorganisé (une rubrique par fonction, avec sa description) et détail complet de chaque fonction dans docs/FONCTIONS.md.
- Fenêtres de confirmation : boutons aux libellés longs l'un sous l'autre (téléphone). Guide : captures d'écran refaites.
- Fiche pas encore enregistrée (ajout, copie ⧉) : encart vert léger « ✨ Créer une nouvelle fiche » en haut.
- Fiche d'une figurine : « ⧉ Une figurine à part » devient « ⧉ Copier cette fiche » : la nouvelle fiche s'ouvre tout de suite, identique ; enregistrée sans modification : confirmation demandée ; plus de retrait automatique : si l'original avait plusieurs exemplaires, l'application demande si ceux de la copie en viennent, avec les nombres (« Oui : 38 là-bas, 2 ici » / « Non : 40 là-bas + 2 en plus »).
- Réglages › 🌐 Pages publiques : option « Afficher les prix sur la collection publique » (désactivée par défaut) — valeur estimée de chaque fiche, prix du catalogue dans le détail.
- ⚖️ Mentions légales : page à part (lien en bas du menu) ; le paragraphe « Éditeur » se modifie avec le bouton « ✏️ Éditer » (pour qui gère le site pour quelqu'un d'autre ; texte générique par défaut).
- Pages publiques, en-tête : le lien vers l'autre page publique (« ⭐ Liste de souhaits de … ») à côté du compte Instagram ; « … · lecture seule » et « Le projet sur GitHub » à droite.
- Réglages sur ordinateur : sections sur 3 colonnes, plus aérées ; curseurs des prix bien alignés.
- Réglages › 💶 Prix : curseurs pour l'actualisation automatique (toutes les X heures, 24 par défaut), la limite d'appels BrickLink par jour (2 000 par défaut) et la relecture d'une fiche consultée (prix de plus de X heures, 24 par défaut).
- « MOC » dans les listes de figurines : même pastille que sur les cartes.
- MOC (et sets estimés par leurs pièces) : à l'ouverture, leurs pièces aux prix de plus de 24 h sont relues sur BrickLink, puis l'estimation est refaite.
- Sans internet : chaque image est cherchée chez ses sources l'une après l'autre et la première trouvée est gardée en local ; à l'affichage (et au zoom), la copie locale passe avant tout appel réseau ; les images des nouveautés sont gardées aussi.
- Han Solo en carbonite : sa photo (la brique imprimée 87561pr0001, Rebrickable).
- Fiche d'un souhait : le lien « BrickLink ↗ » suit l'état cherché (neuf, occasion, ou les deux) et la zone où ce prix a des annonces.
- Liste de souhaits, cartes : détail du prix sur plusieurs lignes — « Neuf : … », « Occasion : … », et « sans figurines : … » en dessous quand on les cherche sans figurines. Plus d'options boîte / plan pour un souhait d'occasion (ni dans la fiche, ni dans l'estimation).
- Drapeaux 🇪🇺 🇺🇳 visibles aussi sous Windows (police de drapeaux Twemoji, au lieu des lettres « EU »).
- Nouveautés › Figurines exclusives : « ⭐ La figurine » l'ajoute à la liste de souhaits (sur la carte et en grand) ; « ⭐ Le set » pour son set.
- Recherche : un set de la liste de souhaits apparaît sous « ⭐ Dans la liste de souhaits » (plus sous « Dans ma collection ») ; un appui ouvre la liste et sa fiche.
- Nouveautés › Figurines exclusives d'un set déjà sorti : « 🔎 La figurine sur BrickLink » (figurine retrouvée dans le set, annonces France, sinon Europe, sinon monde ; rien en vente : « Pas d'annonces » ; introuvable : recherche sur son nom ; réponse gardée 24 h). Page publique : recherche BrickLink.
- Nouveautés › Figurines exclusives : figurine sans photo signalée (« photo pas encore disponible », relue chaque jour) ; un appui montre la figurine en grand, les photos de son set à côté, et le lien lego.com du set (appli et page publique).
- Nouveautés, photo en grand : bouton « 🔗 Voir sur lego.com » (appli et page publique) ; plus de photo en double (la miniature) ; la page publique affiche bien la photo par-dessus la page.
- Barre de la liste : pastilles des sous-listes avec le nom seul ; les nombres dans Tout / Sets / Figurines / Pièces (aussi sur téléphone) ; bouton 💶 (valeur affichée) qui trie du plus cher au moins cher.
- Détourage ISNet depuis le téléphone : une copie réduite part au serveur, le masque revient et s'applique à la photo en pleine taille (les photos lourdes n'arrivaient pas au serveur) ; en cas d'échec, le message dit pourquoi.
- Sous-listes : plus dans le menu latéral ; en pastilles (PC : dans la barre du haut de la liste, en grand ; téléphone : sous le titre, puis dans la barre qui apparaît en faisant défiler) — la liste principale, chaque sous-liste, « Non classées » —, l'active surlignée, les sous-listes entourées d'un liseré rouge (la liste parente juste avant) ; une liste à sous-listes montre par défaut tout son contenu.
- Pinceau : curseur en cercle rouge, à la taille du pinceau. Détourage ISNet un peu plus rapide (1 fil par cœur).
- Pages publiques : le nom du compte Instagram s'affiche à côté de son logo.
- Vue principale : plus de drapeau de zone à côté des prix des cartes (ils restent dans les fiches et les tarifs).
- Menus de photo : « ✂️ Recadrer » devient « ✂️ Modifier image » (recadrer, pivoter, pinceau, détourer) ; plus de bouton Photoroom dans les menus ni à côté de « Importer une image » (il reste proposé après le détourage).
- Ouverture d'une photo (hors recherche) : cadre proposé au plus juste autour de l'objet, toujours modifiable (le fond est pris sur les bords de la photo, pas sur la marge blanche).
- Recadrage : le cadre peut dépasser de la photo (le surplus est blanc), assez pour contenir une photo très haute ou très large en entier ; boutons du bas alignés.
- Recadrage : 🖌️ Pinceau blanc pour effacer ce qui gêne sur la photo (taille réglable, « ↩ Annuler le trait »).
- Recadrages : partout le format des vignettes (4:3), figurines comprises ; seul le recadrage d'une recherche reste libre.
- 🪄 Détourer le fond : d'abord ISNet (modèle libre, sur votre serveur, ~8 s), puis l'outil en ligne réglé ; secours : détourage sur l'appareil.
- Pièce ajoutée à une figurine : « 🔢 Quantité » dans son menu ; le détail de l'estimation l'indique par figurine × la quantité.
- Bouton « 🪄 Détourer le fond » dans tous les recadrages de photo.
- Noms français des fiches revus (25 sets, 152 figurines) : noms officiels, sinon traduits à la main (ex. « Taun Nous » → « Taun We »).
- Zoom : l'image ne dépasse plus de l'écran ; titre = nom de la fiche suivi du nom de l'apparence entre parenthèses (plus de « Principale »).
- « ✂️ Recadrer » de la photo principale recadre bien la principale (catalogue ou importée), même quand une autre apparence est affichée.
- Apparences sans nom : plus de « Apparence 2 » (rien d'affiché) ; « Recadrer » une apparence garde le format de la fiche (figurine ou set).
- Apparences : « ⭐ Définir comme principale » ; en grand, les apparences à côté de l'image (dessous sur téléphone), l'actuelle encadrée — aussi sur la collection publique. La photo principale en grand propose ses outils (recadrer, changer, coller, détourer).
- Nouveautés : relues sur lego.com dès l'ouverture de la page (au plus toutes les 15 min) ; en grand, les photos officielles (set et boîte) défilables — aussi sur la page publique.
- Images de figurines qui ne chargeaient plus (ex. Deadshot) : la banque d'images BrickLink est essayée avec son n° officiel (sh0259).
- Apparences alternatives : coche « Afficher dans la vue générale » (oui par défaut) quand on ouvre une apparence.
- 💶 Tarifs : prix neuf et d'occasion cliquables vers les annonces BrickLink (état et zone du prix), même pour un prix relevé avant.
- Nouveautés : celles arrivées pendant que la page est ouverte s'affichent et sont encadrées ; compteur relu au retour dans l'appli.
- MOC : « + Figurine » sur un set MOC, « + Set » sur une figurine MOC.
- Le nom d'une apparence s'affiche entre parenthèses (« Slayer (The Dark Ages) »).
- « Changer la photo » ne propose plus les photos de galerie inaccessibles : leur vignette montrait le set, mais la photo enregistrée était une autre (ex. une figurine).
- **Estimations des MOC et figurines modifiées** : un prix BrickLink (ventes réelles) n'est plus remplacé par celui de « pièces semblables » (ex. torse à 0,03 € au lieu de 5,30 €) ; tout a été rechiffré.
- Le cadre des apparences d'un set a le format des sets (plus celui des figurines).
- La tâche d'une figurine reste sur la figurine (plus sur son set) ; plus de tâches automatiques pour les MOC (« MOC à valider » suffit).
- « 📋 Coller » n'ouvre plus la galerie ; flèche ↑ seulement quand on peut faire défiler.

## 14 novembre 2026

### Nouveautés
- **Aide « ? »** (Réglages › Aide pour l'afficher ou non) : un « ? » rond à côté de la flèche ↑ explique la page ou la fenêtre ouverte : chaque bouton visible est entouré et numéroté, avec son explication.
- **Prix = ventes réelles** : moyenne des ventes BrickLink des 6 derniers mois, neuf et occasion séparés (France, sinon Europe, sinon monde) ; sans vente, les annonces en cours, signalées.
- **Drapeau de zone** devant chaque prix relevé : 🇪🇺 Europe, 🇺🇳 monde (sans drapeau : France).
- **Figurines = fiches à part entière** : celles d'un set ont leur fiche, se déplacent (leur set suit), comptent dans la valeur du set (jamais deux fois) ; set d'origine retrouvé sur BrickLink ; gamme reprise du set si elle manque.
- **À commander** : figurines acceptées ; état voulu par ligne (n'importe, neuf, occasion), aussi dans l'export BrickLink ; quantité − / + ; prix neuf et occasion ; lien BrickLink dans la zone du prix ; « Pour … » ouvre la fiche du set ; recherche par photo des figurines.
- **Tâches** : gérer les catégories (renommer, supprimer : leurs tâches vont dans « Autres »).
- **Instagram (facultatif)** : relevé automatique (API officielle) et / ou ajout manuel d'un post ; analyse photo par photo (carrousels), jusqu'à 10 éléments par photo ; rattachement à partir de 70 % ; « Analyser les nouveaux posts » / « Tout réanalyser » avec date de fin estimée ; photos visibles sur la collection publique et les fiches partagées.
- **Apparences alternatives** : en ajouter une ne fait remonter que sa vignette.
- **Réglages** en page entière ; **compteur de visites** des pages publiques dans les statistiques.

- **Version GitHub** : les exemples livrés ont leurs images (visibles sans clé API), une tâche « À faire » d'exemple ; vue « Tout » par défaut ; aperçu en images dans le README.
- Libellés plus clairs : « Ajouter sans rechercher (MOC ou set partiel) », « Importer une image ».

- **⧉ Une figurine à part** : copier une figurine possédée (seule ou dans un set) en une nouvelle fiche à modifier ; l'original n'est déduit qu'à l'enregistrement.

- **MOC** : type de fiche demandé d'abord ; figurine MOC scannée dès l'ajout de sa photo ; « Rescanner la photo » ; tâches « à valider » / « à la main » ; pièces proposées dans la couleur reconnue.

- **Instagram** : un seul mode (désactivé / automatique / manuel) ; curseur 1-10 d'éléments cherchés ; scan automatique réglable (24 h par défaut) ; « Scan complet » et « Scanner les nouveaux posts » ; « Posts non identifiés » (rattacher ou exclure) ; bouton au logo Instagram « Vu dans N posts » + « + » sur toutes les fiches ; nom du compte en haut.

- **Détourage local** par défaut (sur l'appareil) ; outil en ligne facultatif, proposé après coup.

- **Pièces** : ajout possible sans couleur quand les couleurs sont indisponibles (tâche « couleur à valider », revérifiée chaque jour) ; photo de la fiche pour cadrer la pièce cherchée.
- Menus d'image explicites ; bouton ± de rotation ; flèche ↑ cachée en recherche ; logo Instagram seul en haut.

### Corrections et améliorations
- « Dernière modification » : seule la fiche modifiée remonte (une figurine ne fait plus remonter son set, et inversement).
- Fiches plus rapides à l'ouverture ; glisser-déposer plus réactif.
- Rebrickable : une requête à la fois et pause automatique en cas de refus (plus de blocage).
- Photo de tête de fiche plus petite ; lignes « À commander » plus compactes.
- Fenêtre ouverte : la page derrière ne défile plus ; appui long sur une image : plus de menu « enregistrer l'image » du navigateur.

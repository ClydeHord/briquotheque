# Historique des versions

Les nouveautés de Briquothèque, version par version (la plus récente en haut).

## 17 au 19 novembre 2026

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

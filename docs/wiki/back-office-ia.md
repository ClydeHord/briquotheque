# Briquothèque — Notice du back office (condensé pour IA)

Généré le 23/11/2026 09:46.

Consigne pour l'IA : ce texte est la notice complète du back office de Briquothèque (les coulisses : apparence, textes, fiches, étiquettes, pages, sauvegardes… sans code), une application web (sur téléphone et ordinateur) pour gérer une collection LEGO : sets, figurines, MOC, pièces, liste de souhaits, estimations de valeur. Quand l'utilisateur te demande comment faire quelque chose, réponds en français, simplement, en t'appuyant UNIQUEMENT sur cette notice : les étapes dans l'ordre, avec les noms exacts des boutons et des menus (et leur emoji). Si la notice ne couvre pas la demande, dis-le plutôt que d'inventer. Vocabulaire : « figurine » (jamais « minifig »).

## Avant de commencer

Le **back office** est l'atelier de la Briquothèque : on y change son apparence, ses textes, ses fiches, ses étiquettes, on y crée
des pages, on y fait les sauvegardes, on y corrige une donnée — **sans écrire de code et sans ligne de commande**.

**⚠️ Ce sont les entrailles de l'application.** Ce qui se règle ici change réellement le site. Rien de grave ne peut arriver
en suivant trois habitudes : regarder l'**aperçu** avant de publier, faire une **sauvegarde** avant un gros changement,
et se souvenir de `?bo=off` (voir En cas de problème).

#### Y entrer

- Dans la Briquothèque : **⚙️ Réglages → 🛠 Back office → Ouvrir le back office**. Ou taper directement l'adresse de le site suivie de
`/backoffice`.

- **La première fois**, le back office demande de créer **son mot de passe** (10 caractères au moins). Il faut être connecté à la
Briquothèque ce jour-là. Deux choix : un mot de passe **à part**, ou **le même** que celui de la Briquothèque (il est redemandé pour confirmer).

- Cocher « J'ai lu et compris », puis **Créer le mot de passe et entrer**.

**🔑 Ce mot de passe ne doit surtout pas se perdre.** Il ne peut pas être retrouvé depuis l'application. S'il est perdu, il faut supprimer
le fichier `data/backoffice_auth.json` sur le serveur (il faut donc un accès aux fichiers du serveur), puis rouvrir
`/backoffice` pour en créer un nouveau. À noter dans un endroit sûr.

Première visite : création du mot de passe du back office

#### Se connecter, se déconnecter

- Les fois suivantes, seul le mot de passe du back office est demandé. « **Rester connecté sur cet ordinateur** » garde la session 30 jours
(sinon 12 heures).

- Ce mot de passe **ouvre aussi la Briquothèque** : c'est la clé maîtresse. Il permet même de changer le mot de passe de la Briquothèque
s'il a été oublié (Mots de passe et sécurité).

- Après **10 essais ratés**, l'adresse est bloquée 15 minutes (et bannie 4 heures si elle vient d'Internet).

- Pour sortir : bouton **⎋ Quitter**, en haut à droite.

#### Ordinateur conseillé

Le back office est pensé pour un **ordinateur** : grand écran et souris. Sur tablette ou téléphone, il s'ouvre mais prévient :
« cliquer pour modifier » et « déplacer à la souris » y sont peu pratiques, et les panneaux sont à l'étroit.

Les fois suivantes : la porte du back office

## L'écran du back office

Trois colonnes : à gauche les **rubriques**, au milieu les **réglages** de la rubrique ouverte, à droite l'**aperçu** du site.

#### Brouillon, puis « Publier »

- **Modifier** dans une rubrique. L'aperçu à droite montre le résultat tout de suite.

- C'est un **brouillon**, visible ici seulement. Il est enregistré automatiquement (« brouillon enregistré », en haut).

- **✔ Publier sur le site** l'applique pour de bon. Un petit mot est proposé pour s'y retrouver plus tard dans l'historique.

**↶ Annuler / ↷ Rétablir** (ou Ctrl + Z / Ctrl + Y) reviennent en arrière pas à pas. **Abandonner le brouillon** jette tout ce qui n'est pas publié.

#### L'aperçu

- La liste déroulante choisit la page montrée : le site connecté, les pages publiques, la page de connexion.

- **👆 Utiliser le site** : l'aperçu se comporte comme le site (pour aller à l'endroit à modifier).
**🖱️ Cliquer pour modifier** : un clic sélectionne un élément. **✋ Déplacer** : on attrape un élément et on le pose ailleurs.

- 🖥️ ▭ 📱 : largeur d'ordinateur, de tablette, de téléphone. **− 100 % +** : zoom de l'aperçu (gardé sur l'appareil). « Montrer ce qui est masqué » laisse voir en transparence ce qui est caché.

- L'aperçu s'ouvre toujours sur l'**accueil** (pas sur la dernière fiche ouverte dans l'appli).

#### Fonctions avancées

L'interrupteur **Fonctions avancées** (en haut) montre les rubriques pour aller plus loin : calculs, règles « si… alors », tuiles, vues,
corrections du catalogue, tableur, fichiers de données, paramètres du serveur, code.

**Deux sortes de rubriques.** Celles qui **personnalisent** (apparence, textes, étiquettes, pages…) passent par le brouillon et
« Publier ». Les **outils du serveur** (sauvegardes, images, mots de passe, fichiers, paramètres, code) agissent **tout de suite**.

L'accueil : toutes les rubriques, classées

#### Publier

« ✔ Publier sur le site » demande un mot facultatif (« nouvelles couleurs », « page à vendre »…). Chaque publication est gardée dans
Historique et secours : n'importe laquelle peut être reprise.

Publier : un mot pour s'y retrouver

## Modifier à la souris

La façon la plus directe : **cliquer sur ce qu'on veut changer**. Tout élément du site — un bouton, un titre, une image, une ligne des
Réglages, une carte — se sélectionne et se règle. Ouvrir : Modifier à la souris ↗

#### Choisir un élément

- Ouvrir **Modifier à la souris** : l'aperçu passe en « 🖱️ Cliquer pour modifier ».

- **Cliquer l'élément** dans l'aperçu : il s'entoure d'orange. Le bouton « ⬆ Sélectionner ce qui l'entoure » remonte d'un cran (la zone qui le contient).

- Besoin d'aller ailleurs (ouvrir une fiche, le menu, la page Réglages) ? Repasser sur « 👆 Utiliser le site », y aller, puis revenir sur
« 🖱️ Cliquer pour modifier ».

#### Ce qu'on peut faire d'un élément

- **À quoi appliquer** : seulement cet élément, ou **tous ceux du même genre** (toutes les cartes, tous les boutons de ce type) ; sur cette page, ou sur toutes.

- **Texte** : le renommer (texte affiché, texte grisé d'un champ, info-bulle).

- **Masquer** l'élément.

- **Position** : le mettre en premier ou en dernier parmi ses voisins.

- **Style** : couleurs, taille du texte, gras, alignement, coins arrondis, bordure, espaces, largeur, hauteur, opacité.

- **Ajouter quelque chose à côté** : un texte, un titre, un bouton-lien, une image, un trait.

- **↺ Remettre cet élément comme à l'origine** annule tout pour lui.

Un élément choisi (ici le bouton « + Nouveau ») et ses réglages

#### Icône ou image

Pour **changer l'apparence d'un bouton** (ou de n'importe quel élément) :

- **Une icône** : un émoji ou un petit texte, placé avant le texte, après, ou **à la place** du texte (avec sa taille).

- **Une image** : « 🖼️ Choisir… » ouvre les images (ou en envoie une). Elle se place avant ou après le texte, **à la place** du texte
(un bouton-image), ou **en fond** de l'élément. Régler sa largeur et sa hauteur.

#### Lien et action au clic

- Pour un **lien** : changer son adresse, l'ouvrir dans un nouvel onglet.

- **Quand on clique dessus** : comme à l'origine · ne rien faire · demander une confirmation · ouvrir une adresse · une liste ·
« Toute la collection » · une vue · une page créée · une fiche · « + Nouveau » · la recherche · les Réglages · remonter · revenir en arrière.

**Exemple.** Pour que le logo ouvre le tableau de bord : cliquer le logo → « Quand on clique dessus » →
« Ouvrir une page créée » → « Tableau de bord ». Si un jour cette page est supprimée, le logo reprend simplement son comportement d'origine.

#### Décalage, échelle, rotation

Pour un réglage fin : décaler de quelques pixels, agrandir ou réduire (en %), incliner (en degrés).

Icône ou image d'un bouton, lien, action au clic, décalage

#### Tout replacer à la souris

- Au-dessus de l'aperçu, choisir **✋ Déplacer**.

- **Attraper** un élément (cliquer, garder appuyé), **glisser** : une barre verte montre où il se posera (avant ou après l'élément survolé).

- **Lâchez**. Échap annule. Chaque déplacement est listé dans la rubrique, avec un bouton pour le défaire.

Un bloc de fiche déplacé change l'ordre de la fiche ; une entrée du menu déplacée change l'ordre du menu : c'est la même chose que les rubriques
Fiches et Menu, à la souris.

Le mode « ✋ Déplacer »

#### Le clic droit : tous les outils d'un élément

Dans l'aperçu, **cliquer du bouton droit** sur n'importe quel élément, quel que soit le mode (« Utiliser le site », « Cliquer pour modifier », « Déplacer ») :
un menu s'ouvre, avec le nom de l'élément en titre.

- **✏️ Modifier** : ouvre ses réglages (texte, style, lien, action…), comme un clic en mode « Cliquer pour modifier ».

- **👁 Masquer** : il disparaît du site (la case « Montrer ce qui est masqué », au-dessus de l'aperçu, le fait réapparaître en transparence).

- **🎨 Copier le style**, puis sur un autre élément **🖌️ Coller le style** : couleurs, taille et graisse du texte, arrondi, bordure, transparence.

- **🔤 Copier le texte** et **🧷 Copier le sélecteur** (son adresse CSS, pour la feuille de style libre ou le script libre).

- **✂️ Couper**, puis sur un autre élément **📌 Coller avant** ou **📌 Coller après** : il change de place (c'est le mode « Déplacer », sans glisser).

- **⬅️ Reculer d'un cran** / **➡️ Avancer d'un cran** : il passe avant son voisin de gauche, ou après celui de droite.

- **⤴️ Élément parent** : le même menu pour ce qui le contient (le bouton → sa barre → le bloc…).

- **↩️ Annuler ses modifications** : retire tout ce qui a été changé sur cet élément (textes, style, ajouts, déplacement).

Tout passe par le brouillon : ↶ Annuler défait la dernière action, et rien n'est visible sur le site avant « Publier ».
**Maj + clic droit** ouvre le menu habituel du navigateur.

## Apparence, boutons et tailles

#### Apparence

Ouvrir : Apparence ↗

- **Nom du site** et **logo** (un émoji, ou une image).

- **Couleurs**, pour le thème clair et le thème sombre : couleur principale, fond, panneaux, texte… Des palettes toutes prêtes (Bleu, Vert, Violet…) font le gros du travail.

- **Coins arrondis**, **police**, **taille générale** du site.

**Exemple : passer le site en bleu.** Apparence → palette « Bleu » → regarder l'aperçu → Publier.

Apparence : nom, logo, couleurs, arrondis, police

#### Boutons et tailles

Ouvrir : Boutons et tailles ↗

- **Tous les boutons** d'un coup : coins arrondis, hauteur, largeur, taille et graisse du texte, bordure, MAJUSCULES, ombre.

- **Couleurs** des boutons ordinaires, des boutons principaux (« + Nouveau », « Enregistrer ») et des boutons de suppression.

- **Un bouton en particulier** (son icône, son image, son lien) : « 🖱️ Cliquer un bouton dans l'aperçu »
(voir Modifier à la souris).

- **Tailles générales** : largeur du menu, largeur de la fenêtre d'une fiche, largeur maximale du contenu, espace entre les cartes, taille du titre.

Une case vide = la valeur d'origine. « ↺ Boutons et tailles d'origine » remet tout.

Boutons et tailles

## Textes

#### Remplacer un texte

Ouvrir : Textes ↗

- « Choisir dans la page » liste les textes visibles dans l'aperçu ; ou taper soi-même le texte à remplacer.

- Indiquer par quoi le remplacer. Le remplacement vaut partout où ce texte apparaît (boutons, titres, messages).

**Exemple.** Remplacer « Liste de souhaits » par « Mes envies » : une ligne suffit, le menu, les titres et les boutons suivent.

Pour renommer un seul élément précis, préférer Modifier à la souris.

Remplacer un mot ou une phrase partout

## Étiquettes et pastilles

Les **étiquettes** sont les petits mots posés sous le nom d'une fiche (« Modifié », « MOC », « Set partiel »…) ; les **pastilles** sont
posées sur l'image (« Retiré », « Neuf », « ×2 »…). Celles de l'application se modifient, et d'autres se créent. Ouvrir : Étiquettes et pastilles ↗

#### Créer une étiquette

- **+ Nouvelle étiquette** (ou un exemple prêt à adapter : « 💰 Plus de 100 € », « 🕰️ Avant 2000 », « 📦 Avec sa boîte »…).

- Son **texte** (il peut reprendre une valeur de la fiche : `{annee}`, `{theme}`, un des champs…), son **icône**, son
**genre** (étiquette sous le nom, ou pastille sur l'image), ses **couleurs**.

- **Affichée si la fiche remplit…** : une ou plusieurs conditions (« Valeur estimée » « est plus grand que » « 100 »). Sans condition : toutes les fiches.
Le compteur indique combien de fiches la remplissent.

- **Sur quelles fiches** (sets, figurines, MOC…), **où** (cartes, haut de la fiche), et « **Proposer dans le menu ⚙️ Filtres** » pour
pouvoir ne montrer que ces fiches-là.

**Exemple : une étiquette « À vendre ».** 1) Rubrique « Champs personnalisés » : créer une case à cocher « À vendre ».
2) Ici : nouvelle étiquette « 🏷️ À vendre », condition « À vendre » « est oui », cocher « Proposer dans ⚙️ Filtres ».
3) Publier. Cocher la case sur les fiches concernées : l'étiquette apparaît, et le menu Filtres propose « À vendre ».

Les étiquettes : texte, icône, couleurs, condition

#### Modifier une étiquette de l'application

Chaque étiquette et chaque pastille d'origine a son bouton **Modifier** :

- **Nouveau texte** et icône (pour celles qui comptent, écrire `{n}` à la place du nombre : « {n} fig. en plus »).

- **Couleurs** : texte, fond, bordure.

- **Masquer complètement**.

- **L'afficher seulement si…** : une condition (par exemple ne montrer « Modifié » que sur les sets).

Les pastilles de l'application sont masquées sur les cartes de la collection ; une case permet de les y montrer.

Les étiquettes que l'on pose **à la main** sur une fiche de l'application (« + Étiquette » : Complet, Amélioré, Modifié, Set partiel, MOC) sont les
mêmes que celles-ci : elles suivent les mêmes réglages (texte, couleurs, masquage). « Complet » n'existe que posée à la main : elle a sa ligne,
« Complet (étiquette posée à la main) ».

Une étiquette de l'application, renommée

#### Résultat sur le site

Après publication, les étiquettes modifiées et les vôtres apparaissent sur les cartes et en haut des fiches. Le renommage, les couleurs et le
masquage valent aussi sur les pages publiques ; les conditions, elles, se lisent sur le site connecté.

Sur le site : « MOC » renommé en « 🎨 Création », étiquettes et calcul sur les cartes

## Fiches, champs, liens, cartes, menu

#### Fiches

Ouvrir : Fiches ↗ Pour chaque type de fiche (set, figurine, MOC, set partiel, figurine personnalisée, et leurs versions « liste de souhaits ») :

- **l'ordre des blocs** : glisser la poignée ⠿, ou ▲ ▼ ;
- **masquer** un bloc qui ne sert pas ;

- **renommer** le titre d'un bloc.

L'aperçu ouvre une fiche d'exemple du type choisi : chaque changement s'y voit aussitôt.

Le squelette d'une fiche : ordre et visibilité des blocs

#### Champs personnalisés

Ouvrir : Champs personnalisés ↗ Ajouter les informations aux fiches : texte court ou long, nombre, montant, date, case à cocher, liste de choix, étoiles, lien, fiche liée, liste liée.

- **+ Nouveau champ** : son nom, son type, sur quelles fiches.

- Le ranger dans un **bloc** (par défaut « Informations personnelles », à renommer ou multiplier au besoin).

- Cocher « sur les cartes » pour le montrer aussi dans les listes.

Un champ devient une **variable** : utilisable dans les étiquettes, les calculs, les règles, les filtres, les pages.

Les propres champs sur les fiches

#### Liens automatiques

Ouvrir : Liens automatiques ↗ Un bouton ajouté en bas des fiches, vers le site de le choix. Dans l'adresse, `{numero}`, `{nom}`,
`{annee}`, `{theme}` (ou un des champs) sont remplacés par ceux de la fiche.

**Exemple.** Nom : « BrickLink » — adresse : `https://www.bricklink.com/v2/search.page?q={numero}`. Des modèles tout prêts sont proposés.

Des boutons vers d'autres sites, sur chaque fiche

#### Cartes des listes

Ouvrir : Cartes des listes ↗ Taille minimale des cartes, format de l'image, nombre de lignes du nom, parties affichées (numéro, quantité, thème, valeur…).

Les cartes des listes

#### Menu

Ouvrir : Menu ↗ L'ordre des entrées (glisser ⠿), les entrées masquées, **chaque entrée renommée ou masquée une à une** (« Chaque entrée du menu » : Nouveautés, Calendrier des sorties, Réglages…), des **traits de séparation** en plus (« + Ajouter un trait de séparation »), et les **raccourcis** : vers une adresse, une liste, une fiche, une vue.
Les pages créées et les vues enregistrées y apparaissent aussi, et s'ordonnent ici.

Le menu latéral

## Pages

Une idée nouvelle ? **Créer une page.** Un tableau de bord, la liste des sets à vendre, les notes, une page publique à partager…
Une page se compose de **blocs** empilés. Ouvrir : Pages ↗

#### Créer une page

- **📄 Page vide**, **📊 Tableau de bord** (totaux, fiches les plus chères, derniers ajouts) ou **📝 Page de notes**.

- Lui donner un **titre** et une **icône**. Elle apparaît dans le **menu latéral** (décocher « Dans le menu latéral » pour une page
ouverte seulement par un bouton ou un raccourci clavier).

Les pages, et trois modèles pour démarrer

#### Les blocs

| Bloc | Ce qu'il montre

| 🔠 Titre | Un titre (grand, moyen, petit).

| 📝 Texte | Un texte : `**gras**`, `*italique*`, `[texte du lien](https://…)`, lignes commençant par `- ` pour une liste.

| 💡 Encadré coloré | Une information mise en avant, de la couleur de le choix.

| 🖼️ Image | Une des images, avec largeur, légende et lien facultatifs.

| 🔘 Bouton | Un bouton qui ouvre une adresse, une liste, une vue, une page, une fiche…

| 🧱 Liste de fiches | Des fiches choisies par une **condition**, triées, en nombre limité. Un clic ouvre la fiche.

| 🔢 Total (tuile) | Un nombre de fiches, une somme, une moyenne, un minimum, un maximum.

| 📋 Tableau | Un tableau de fiches, colonnes au choix (les champs et calculs compris).

| ➖ Trait · ↕️ Espace | Pour aérer.

| 🧩 HTML libre | Pour qui connaît le HTML (scripts, formulaires et cadres en sont retirés par sécurité).

| 🪟 Page d'un autre site | Un cadre qui montre une autre page web.

Chaque bloc prend **toute la largeur, la moitié ou un tiers** : trois tuiles « un tiers » se rangent côte à côte. « Copier » duplique un bloc,
⠿ et ▲ ▼ changent l'ordre.

**Exemple : une page « À vendre ».** Page vide → bloc « Encadré coloré » (« Sets que je vends, contactez-moi ») → bloc « Liste de fiches »,
condition « À vendre » « est oui », triées par « Valeur estimée ». Ajouter un bloc « Total » : somme de `{valeur}`, même condition.

L'éditeur d'une page : ses blocs, et le résultat en direct

#### Page publique

Cocher « **Publique** » : la page reçoit une adresse `/p/son-adresse`, visible **sans connexion**, à donner à qui on veut.
Les visiteurs n'y voient que les blocs **sans données** (titres, textes, encadrés, images, boutons vers une adresse, HTML, cadres) —
jamais les fiches, les totaux ni les prix.

La page, dans le site

## Page « Réglages » de l'appli

#### Réorganiser la page Réglages

Ouvrir : Page « Réglages » de l'appli ↗

- **⚙️ Ouvrir la page Réglages dans l'aperçu** pour voir le résultat en direct.

- Glisser les sections (⠿ ou ▲ ▼) pour changer leur **ordre** ; taper un nouveau **titre** ; décocher « visible » pour **masquer** une section.

- Pour une **option précise** (une ligne, un bouton, un texte de la page Réglages) : « 🖱️ Cliquer pour modifier », puis cliquer dessus dans l'aperçu.
On peut aussi y **ajouter** un texte, un lien ou une image (« Ajouter quelque chose à côté »).

Une section masquée garde ses réglages. Le back office reste toujours accessible par `/backoffice`, même si sa section est masquée.

Les sections de la page Réglages : ordre, titres, visibilité

#### Le lien vers le back office

La page Réglages de la Briquothèque a une section « 🛠 Back office » : « Ouvrir le back office » et cette notice en PDF.

Dans la Briquothèque : la section « 🛠 Back office » des Réglages

## Comportements

#### Régler les comportements

Ouvrir : Comportements ↗

- **À l'ouverture du site** : par quoi commencer (toute la collection, une liste, une vue, une des pages) ; ce qui est montré (tout, les sets, les figurines).

- **Tri par défaut** : pour « Toute la collection », pour une liste, pour une liste de souhaits. (Le choix du moment, liste par liste, reste prioritaire.)

- **Raccourcis clavier** : une touche (avec Ctrl ou Alt au choix) → une action : nouvelle fiche, ouvrir une page, une liste, la recherche…

- **Clics et liens modifiés** : la liste de tout ce qui a été changé avec « Lien et action au clic », avec un bouton pour le retirer.

- **Figurines identiques** : regrouper ou non, proposer ou non « est-ce celle de ce set ? » (voir ci-dessous).

- **Prix et variations** : ne pas afficher les flèches ↑ ↓ ~ à côté des prix ; masquer le bouton « 🔍 Comprendre les variations » des statistiques ;
**apparence des flèches** — affichées d'office ou non dans la vue générale (le bouton 📈 de l'appli les montre ou les cache à la volée), « ~ » quand le prix
est stable, pourcentage, taille (curseur). Les seuils de hausse et de baisse se règlent dans l'application (Réglages → 🧮 Estimations). L'aperçu suit en direct ; « Publier » les applique ; « ↺ Revenir aux valeurs
enregistrées » retire les changements.

- **Fiches et pièces** : ouvrir les fiches directement en modification (sans la clé 🔧) ; toucher une pièce l'agrandit au lieu d'ouvrir sa fiche.

- **Pages publiques** : ne pas garder les listes dans la barre collée en haut.

- **Divers** : le titre de l'onglet du navigateur ; réduire les animations.

- **Avancé : script libre** (facultatif) : un morceau de JavaScript exécuté une fois au chargement de l'application — jamais sur les pages publiques.
S'il casse l'affichage : ajouter `?bo=off` à l'adresse du site, puis vider la case.

**Exemple.** Touche `n` → « Ajouter une fiche » ; touche `t` → « Ouvrir une page créée : Tableau de bord ».
Un raccourci n'agit jamais pendant la frappe dans une case.

Ce que fait le site : départ, tri, raccourcis, clics

#### Figurines identiques

D'origine, une même figurine présente **à la fois seule et dans un set** (ou dans plusieurs sets) n'a qu'**une carte**, marquée « ×N », et
qu'une fiche ; et à l'ajout d'un set dont une figurine était déjà là, seule, l'application demande **« est-ce celle de ce set ? »**.
Deux cases règlent cela :

- **Ne pas regrouper…** : chaque exemplaire retrouve sa carte (celle du set, celle achetée à part). L'aperçu le montre tout de suite ; les pages
publiques suivent après publication.

- **Ne pas demander « est-ce celle de ce set ? »** : le set ajouté garde sa propre figurine, la vôtre reste seule.

La décote « modifié » se règle dans les Réglages de l'application (Estimations).

Figurines identiques : regrouper ou non, proposer ou non

## Images

#### Envoyer et réutiliser des images

Ouvrir : Images ↗ Les images des boutons, des pages et des éléments ajoutés sont gardées sur le serveur.

- **⬆ Envoyer des images…** : PNG, JPEG, WebP, GIF, SVG, ICO, AVIF — 4 Mo au plus (une photo plus lourde est réduite toute seule).

- Chaque image a une **adresse** (`/bo-img/…`) : « Copier l'adresse », ou plus simple, le bouton « 🖼️ Choisir… » présent partout où une image est demandée.

- La bibliothèque indique si une image est **utilisée** ; supprimer celles qui ne servent plus.

Effet immédiat : pas besoin de publier pour envoyer ou supprimer une image.

La bibliothèque d'images

## Avancé : calculs, règles, tuiles, vues

Ces rubriques apparaissent quand l'interrupteur **Fonctions avancées** est allumé. Elles partagent le même petit langage de **formules**.

#### Calculs et variables

Ouvrir : Calculs et variables ↗ Un **calcul** est un champ dont la valeur vient d'une formule ; il s'affiche sur la fiche, et sur les cartes si la case est cochée.
Une **variable** est une valeur perso (un taux, un seuil) réutilisable dans les formules.

| On écrit | Pour

| `{valeur}` | une variable de la fiche, entre accolades (bouton « variable » pour la choisir dans la liste)

| `"Neuf"` | un texte, entre guillemets

| `+ - * /` · `= <> > < >= <=` | calculer · comparer

| `et` `ou` `non` · `&` | la logique · coller deux textes

| `si(condition ; alors ; sinon)` | une fonction : ses valeurs se séparent par `;`

**Exemples.** Plus-value : `{valeur} - sivide({prix_achat} ; 0)` · Prix par pièce : `{valeur} / {pieces}` ·
Âge du set : `annee(aujourdhui()) - {annee}` · Mention : `si({valeur} > 100 ; "précieux" ; "courant")`.

Parmi les variables d'une fiche : `{statut}` (Complet, Amélioré, Modifié, Set partiel, MOC — comme l'étiquette calculée),
`{etiquettes}` (celles posées à la main), `{exemplaires}` (le total d'une figurine, seule et dans les sets), `{dans_un_set}`,
`{accessoires}` (valeur des accessoires chiffrés par leurs pièces). Exemple : une vue « Modifiés » = condition « État de la fiche » « = » « Modifié ».

Le résultat s'affiche en direct sous la formule, sur une fiche d'exemple ; une erreur est expliquée en français. L'aide-mémoire, en bas de la rubrique,
liste toutes les variables et toutes les fonctions.

Un champ calculé par une formule, avec son résultat en direct

#### Règles « si… alors »

Ouvrir : Règles « si… alors » ↗ Si une fiche remplit une **condition**, alors : une étiquette, une pastille, une couleur de carte, un message en haut de la fiche,
un bloc de la fiche masqué. Plusieurs effets par règle.

Une règle : si la fiche vaut plus de 100 €, alors…

#### Tuiles et totaux

Ouvrir : Tuiles et totaux ↗ Une tuile de plus au-dessus des listes : nombre de fiches, somme, moyenne, minimum ou maximum d'une formule, avec une condition facultative
(« valeur moyenne », « nombre de sets de plus de 100 € »…).

Les totaux, à côté de ceux de l'application

#### Vues, tris et filtres

Ouvrir : Vues, tris et filtres ↗

- Une **vue** est une liste filtrée prête à ouvrir depuis le menu (« Précieux », « À construire cet hiver »…).

- Un **tri** créé ici s'ajoute au menu « ⇅ Tri » du site (marqué ★).

- Un **filtre** créé ici s'ajoute au menu « ⚙️ Filtres » (section « Mes filtres »).

#### Tous les éléments : rien n'est verrouillé

Ouvrir : tout ↗ L'inventaire de **tout** ce que la page affichée dans l'aperçu contient : boutons, liens, entrées du menu, titres, étiquettes,
onglets, options des listes déroulantes, champs — y compris ce qu'on ne peut pas atteindre en cliquant (menus « Trier par » et « ⚙️ Filtres »
fermés, fenêtres, éléments déjà masqués). Une recherche et un tri par zone (barre du haut, menu latéral, fiche, fenêtres…) ; sur chaque ligne :

- **✏️ Modifier** : l'éditeur complet de l'élément, comme au clic (texte, style, lien, action, icône, position) ;

- **🙈 Masquer** / **👁 Afficher** d'un appui.

Ouvrir dans l'aperçu une fiche, les Réglages ou une autre page, puis « ⟳ Relire l'aperçu » pour en lister les éléments. Les noms, icônes,
colonnes, blocs et entrées n'ont plus de limite pratique (seule reste la taille d'un envoi : 16 Mo).

#### Éléments d'origine : modifier l'existant

Ouvrir : origine ↗ Ce que l'application propose déjà, à la main :

- **Tris** (menu « Trier par »), **Filtres** (menu « ⚙️ Filtres ») et **tuiles du haut** : un nouveau nom (vide : celui d'origine), « masquer »,
et ↑ ↓ pour l'ordre — brouillon, puis « Publier ». Les tuiles changent selon la page : ouvrir dans l'aperçu celle à régler, puis « ⟳ Relire les tuiles ».

- **Calculs d'origine** : la formule de chacun expliquée (boîte, livret de plans, exemplaire modifié, seuils des flèches) et son pourcentage,
modifiable — effet **immédiat**, sans « Publier » (ce sont les réglages du serveur, les mêmes que dans l'appli : Réglages → 🧮 Estimations).

Vues enregistrées, tris et filtres

## Données : fiches, catalogue, tableur

Ces rubriques touchent directement la collection, **sans passer par « Publier »**. Une sauvegarde automatique est faite avant chaque écriture.

#### Données

Ouvrir : Données ↗ Chercher une fiche et voir — ou corriger — chacune de ses valeurs brutes, ligne par ligne. Pour le cas où aucun écran de
l'application ne permet la correction.

Une fiche telle qu'elle est enregistrée

#### Corrections du catalogue

Ouvrir : Corrections du catalogue ↗ Un nom, un thème, une année, un nombre de pièces, une image ou un prix du catalogue est faux ? Chercher le set ou la figurine,
remplir seulement ce qui est faux : la correction passe par-dessus le catalogue, pour toutes les fiches concernées. Vider la case pour la retirer.

Corriger ce qui vient du catalogue

#### Tableur (CSV)

Ouvrir : Tableur (CSV) ↗ **Exporter** les fiches (colonnes au choix, champs et calculs compris) vers Excel ou LibreOffice. **Importer** un fichier pour
remplir les champs personnalisés en masse : garder la colonne « id », modifier les autres, réimporter.

Vers un tableur, et retour

## Suivi : mes modifications, historique

#### Mes modifications

Ouvrir : Mes modifications ↗ La liste de tous les réglages, rubrique par rubrique : « Montrer » fait clignoter l'élément dans l'aperçu, ✕ retire le réglage.
C'est ici qu'on retrouve un élément **masqué** pour le faire réapparaître.

Tout ce qui a été changé, au même endroit

#### Historique et secours

Ouvrir : Historique et secours ↗

- **Reprendre** une ancienne publication : elle devient le brouillon ; vérifier, puis publier.

- **↺ Tout remettre d'origine** : vide le brouillon de tous les réglages.

- **Exporter / Importer** les réglages dans un fichier (pour les garder ailleurs, ou les transférer). Un fichier importé est vérifié et remis d'aplomb par le serveur ;
il arrive dans le brouillon : regarder l'aperçu avant de publier, et n'importez que des fichiers de confiance.

- **Feuille de style libre** (pour qui connaît le CSS) : facultatif.

Chaque publication est gardée

## Serveur : sauvegardes, état, sécurité

Les outils du serveur agissent **tout de suite**. Chaque action est notée dans le journal du back office.

#### Sauvegardes

Ouvrir : Sauvegardes ↗

- **Sauvegarder la collection** maintenant ; la liste montre aussi les sauvegardes automatiques.

- **Télécharger** une sauvegarde pour la garder ailleurs ; en **déposer** une ; **restaurer** (l'état actuel est d'abord sauvegardé).

- **Tout emporter** : un export `.zip` de toutes les données (avec ou sans les photos). Les mots de passe n'y sont jamais ;
les **clés API** (Rebrickable, BrickLink…), elles, y sont : garder ce fichier pour soi.

**Avant un gros changement :** Sauvegardes → « Sauvegarder la collection ».

Sauvegarder, télécharger, restaurer

#### État et journal

Ouvrir : État et journal ↗ Depuis quand le serveur tourne, la place disponible sur le disque, la mémoire, la taille des données ; le **journal**
(avec recherche et « erreurs seulement ») ; le bouton **Redémarrer**.

La santé du serveur et le journal

#### Mots de passe et sécurité

Ouvrir : Mots de passe et sécurité ↗

- **Changer le mot de passe du back office** (l'actuel est demandé ; les autres appareils sont déconnectés).

- **Changer le mot de passe de la Briquothèque** : seul celui du back office est demandé — c'est le secours si celui de la Briquothèque est oublié.
Tous les appareils devront se reconnecter.

- **Sessions** : combien sont ouvertes, « Fermer les autres », se déconnecter.

- **Outils sensibles depuis Internet** : le code, les réglages de démarrage, la restauration d'un .zip et la page de secours ne répondent que
depuis le **réseau local** (à la maison). Une case permet de les ouvrir aussi depuis Internet ; elle ne se change que depuis le réseau local.

Mots de passe et sécurité

## Serveur : fichiers, paramètres, code

Pour les cas rares. Ces trois rubriques demandent l'interrupteur « Fonctions avancées ».

#### Fichiers de données

Ouvrir : Fichiers de données ↗ Tous les fichiers de données du serveur (collection, caches, réglages…), en lecture et en correction ligne par ligne, avec recherche.
Une copie de l'ancien fichier est gardée à chaque écriture. Les fichiers de mots de passe n'y figurent pas.

N'importe quelle donnée enregistrée, ligne par ligne

#### Paramètres du serveur

Ouvrir : Paramètres du serveur ↗ Les durées de garde des caches, les quotas d'appels, les tailles d'images, la durée des sessions… appliqués **à chaud**.
Les réglages de démarrage (port, proxy, démonstration publique) demandent un redémarrage, proposé sur place.

Durées, quotas, tailles ; port, proxy, démonstration

#### Code de l'application

Ouvrir : Code de l'application ↗ En dernier recours, les fichiers du programme se modifient depuis le navigateur :

- la **syntaxe est vérifiée** avant d'enregistrer (un fichier faux est refusé, avec la ligne de l'erreur) ;

- chaque **version précédente est gardée** et se remet d'un clic ;

- si le serveur ne redémarre pas avec un fichier modifié, l'**ancienne version revient toute seule**.

En tout dernier recours : la page de secours.

Le code de l'application, avec trois filets de sécurité

## En cas de problème

#### Les bons réflexes

| Ce qui se passe | Quoi faire

| Un réglage rend le site illisible ou inutilisable | Ajouter `?bo=off` à la fin de l'adresse du site : il s'affiche **sans aucune personnalisation**.
Puis ouvrir `/backoffice` (jamais personnalisé, toujours utilisable) → « Mes modifications » pour retirer le réglage fautif,
ou « Historique et secours » pour reprendre une version d'avant.

| Un élément a disparu | Aperçu → cocher « Montrer ce qui est masqué » ; ou « Mes modifications » → ✕ sur la ligne « masqué ».

| Un clic ne fait plus rien | « Comportements » → « Clics et liens modifiés » → ✕.

| Je veux tout remettre comme avant le back office | « Historique et secours » → « ↺ Tout remettre d'origine », puis Publier.

| Une donnée a été abîmée | « Sauvegardes » → Restaurer la sauvegarde d'avant.

| Le site ne répond plus après une modification du code | Attendre dix secondes (l'ancienne version revient seule). Sinon : `/backoffice/secours` →
mot de passe du back office → « Afficher les versions gardées » → remettre la version d'avant → Redémarrer.

| Mot de passe de la Briquothèque oublié | Back office → « Mots de passe et sécurité » → « Changer le mot de passe de la Briquothèque ».

| Mot de passe du back office oublié | Il ne se retrouve pas : supprimer `data/backoffice_auth.json` sur le serveur, puis rouvrir `/backoffice`.

| « Trop de tentatives » | Attendre 15 minutes. Une adresse bannie se débloque dans Réglages → Sécurité de la Briquothèque.

| Un outil répond « seulement depuis le réseau local » | Ouvrir le back office depuis la maison ; ou cocher « Outils sensibles depuis Internet » (depuis la maison).

#### Ce que le back office ne fait pas

Une fonction entièrement nouvelle de l'application (une nouvelle source de prix, par exemple) demande toujours du code — mais ce code se modifie
depuis la rubrique « Code de l'application », sans ligne de commande. Tout le reste se règle ici.

La page de secours : /backoffice/secours

## Dix recettes pas à pas

- **Changer la couleur du site.** Apparence → choisir une palette → Publier.

- **Mettre le logo.** Apparence → Logo → « Choisir un fichier… » → Publier.

- **Renommer « MOC » en « Création ».** Étiquettes et pastilles → ligne « MOC » → Modifier → Nouveau texte : « Création » → Publier.

- **Un bouton avec une image.** Images → envoyer l'image. Modifier à la souris → cliquer le bouton → « Icône ou image » → « Une image » →
« 🖼️ Choisir… » → place « à la place du texte » → régler largeur et hauteur → Publier.

- **Masquer une section des Réglages.** Page « Réglages » de l'appli → décocher « visible » sur la section → Publier.

- **Un champ « Emplacement » sur les sets.** Champs personnalisés → + Nouveau champ → « Emplacement », texte court, fiches « Sets » → Publier.
Le remplir ensuite sur chaque fiche.

- **Une étiquette pour les sets chers.** Étiquettes et pastilles → exemple « 💰 Plus de 100 € » → ajuster le montant → Publier.

- **Un tableau de bord en page de départ.** Pages → « 📊 Tableau de bord ». Puis Comportements → Page de départ → « Une page créée… » → Tableau de bord → Publier.

- **Une page publique de contact.** Pages → Page vide → blocs Texte et Bouton (« Ouvrir une adresse » : `mailto:contact@example.org`) →
cocher « Publique » → Publier → donner l'adresse `/p/…`.

- **Revenir à hier.** Historique et secours → « Reprendre » sur la publication d'hier → vérifier l'aperçu → Publier.


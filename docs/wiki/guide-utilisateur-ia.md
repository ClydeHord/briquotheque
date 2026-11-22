# Briquothèque — Guide utilisateur (condensé pour IA)

Généré le 22/11/2026 22:52.

Consigne pour l'IA : ce texte est le guide complet de Briquothèque, une application web (sur téléphone et ordinateur) pour gérer une collection LEGO : sets, figurines, MOC, pièces, liste de souhaits, estimations de valeur. Quand l'utilisateur te demande comment faire quelque chose, réponds en français, simplement, en t'appuyant UNIQUEMENT sur ce guide : les étapes dans l'ordre, avec les noms exacts des boutons et des menus (et leur emoji). Si le guide ne couvre pas la demande, dis-le plutôt que d'inventer. Vocabulaire : « figurine » (jamais « minifig »).

## Premiers pas

Briquothèque range la collection LEGO — **sets**, **figurines**, **MOC** (les créations), **pièces** — en estime la valeur,
et suit les envies (liste de souhaits, nouveautés, pièces à commander).

**La philosophie du projet** : des LEGO achetés, montés, utilisés, **modifiés**, inventoriés, et estimés **en l'état** —
rien n'est gardé scellé. Briquothèque n'est pas pensée pour stocker des boîtes neuves scellées. C'est la philosophie très personnelle
de son auteur : l'application répond d'abord à ses attentes, et s'ouvrira peut-être à d'autres selon son succès.

#### Première installation

- Au premier lancement, Briquothèque demande de **créer le mot de passe** (10 caractères au moins). Depuis Internet, elle demande
aussi le **code d'installation** affiché par le serveur.

- Puis, facultatif : la **clé API Rebrickable** (catalogue, images, inventaires) et les **codes API BrickLink** (prix des ventes réelles),
avec la marche à suivre pour les obtenir. Sans eux, un bandeau jaune le rappelle ; le toucher ouvre les Réglages.

- La liste **« Exemples »** contient une **fiche de démo** de chaque type et un inventaire de démo, marqués d'un bandeau jaune :
à explorer, modifier ou supprimer.

#### Se connecter

- Ouvrir l'adresse de la Briquothèque.
- Entrer le **mot de passe** ; cocher « Rester connecté » sur l'appareil personnel.

#### L'écran principal

- **☰** : ouvre le menu (listes, inventaires, pages…).

- Le **logo** ramène à l'accueil (toute la collection, en haut).

- **+** : ajouter un set, une figurine, un MOC (dans une liste de pièces : une pièce).

- **Valeur de la collection** : estimation d'occasion ; dessous, ce qu'elle vaudrait neuve.

- Tuiles **Sets** / **Figurines** / **Pièces** : les totaux. Toucher Sets ou Figurines pour afficher l'un, l'autre ou les deux.

L'écran principal

#### Lire une vignette

- Photo, numéro, nom, gamme, année, nombre de pièces, et la **valeur estimée** (en petit : la cote réelle du marché).

- Étiquettes : seulement **Complet**, **Amélioré**, **Modifié**, **Set partiel** et **MOC** ; à côté, les badges **Neuf**, **Sans figurines**, **×2** (quantité)…

- Toucher une vignette pour ouvrir sa **fiche**.

#### Rechercher, trier, filtrer

- **Filtrer par nom, numéro, thème…** : la liste se réduit pendant la saisie.

- Menu **Filtres (l'entonnoir)** : cocher une ou plusieurs étiquettes — **Complet**, **Amélioré**, **Modifié**, **Set partiel**, **MOC** — pour n'afficher que ces fiches (le bouton compte les étiquettes cochées).

- **↺** (à gauche du filtre) : remet les filtres à zéro.

- Étiquettes des cartes : **MOC** (seule étiquette d'un MOC), **Set partiel**, **Modifié** (pièces retirées ou remplacées, figurine d'origine
remplacée ou modifiée), **Amélioré** (seulement des ajouts : pièces, figurines en plus). L'application les calcule ; dans une fiche, il est possible d'en poser
d'autres à la main ou en retirer une (voir « Modifier une fiche »).

- Le **tri** : dernière modification, valeur, année, nom… En « dernière modification », seule la fiche modifiée remonte :
retoucher une figurine rangée dans un set ne fait pas remonter le set, et modifier un set ne fait pas remonter ses figurines.

Ajoutée à l'écran d'accueil du téléphone, Briquothèque s'ouvre comme une appli et marche même sans réseau : les changements partent dès le retour de la connexion.

**Mode hors ligne** : sans réseau, ou si le serveur est éteint, l'appli s'ouvre avec la dernière copie gardée sur l'appareil (bandeau « Hors ligne »).
Il faut l'avoir ouverte une fois **en ligne, en https** : en `http`, le navigateur n'autorise pas le mode hors ligne (l'appli passe d'elle-même
en https si l'adresse le permet ; une adresse locale en http reste sans mode hors ligne). **Toutes les fiches** s'ouvrent hors ligne, même jamais consultées : une fois par jour, en ligne, l'appli garde sur l'appareil un « paquet »
(environ 0,5 Mo) avec les fiches catalogue des sets et figurines et les pièces de les MOC. Ce qui demande Internet reste indisponible hors ligne :
la liste des pièces d'une figurine (Rebrickable), les recherches, les photos jamais affichées sur l'appareil.

Les vignettes

## Le menu et les listes

- **Toute la collection**, puis les **listes** avec leur nombre d'éléments et leur valeur. Une liste qui en contient d'autres est
**repliée** : toucher la flèche pour la déplier (le temps de la visite).

- **📝 À faire** : les tâches. **🚧 À construire** : les sets pas encore montés.

- **⭐ Liste de souhaits** (et **👀 À surveiller**), **✨ Nouveautés** (le nombre affiché suit les thèmes ; surligné s'il en est apparu de nouvelles),
**🔗 Fiches partagées**.

- **🔩 À commander** : les pièces — et les figurines — à acheter, avec leur coût estimé. Une figurine s'y ajoute par sa fiche (choix de la liste
« Commandes ») ou par « 🟡 Une figurine » dans l'ajout d'une pièce ; elle part aussi dans l'export vers la wanted list BrickLink.
La liste « Commandes » apparaît dans le choix de liste de toute fiche de figurine.

- Les **inventaires**, puis **+ Nouvel inventaire**.

Le menu

- **📊 Statistiques**, **🎲 Une fiche au hasard** (pour redécouvrir un set), **⚙️ Réglages**, **Se déconnecter**.

- Les **liens publics** (Collection, Nouveautés, À surveiller, Liste de souhaits, Mode Démo) : **un appui ouvre la page et copie son lien**, à envoyer aux proches ; « Mode Démo » copie seulement son lien (à ouvrir en navigation privée).
Dessous, **🐙 GitHub** ouvre la source officielle de Briquothèque, puis les **mentions légales**. Sur cette page, le bouton **✏️ Éditer** change le paragraphe « Éditeur » (quand le site est géré pour quelqu'un d'autre).

- **⇅** (en haut du menu) : changer l'ordre des listes.

Le bas du menu

#### Créer une liste

- Dans le menu, toucher **+** à côté des listes.
- Donner un **nom** ; choisir éventuellement **Ranger dans** une autre liste (elle devient une sous-liste).

- Toucher **Créer**.

**Sous-listes** : seules les listes principales sont dans le menu. Une liste qui a des sous-listes les montre en pastilles (sur ordinateur dans la barre du haut, sur téléphone sous le titre, puis dans la barre qui apparaît en faisant défiler ; l'active est surlignée) : la liste elle-même (tout son contenu, sous-listes comprises), chaque sous-liste, et **Non classées** (ce qui est rangé directement dans la liste). Dans une sous-liste, le bouton **‹** devant les pastilles ramène à la liste parente. On peut déposer des fiches sur une pastille. Les nombres sont dans les boutons Tout / Sets / Figurines / Pièces ; le bouton de la valeur (ce qui est affiché) trie du plus cher au moins cher. **Logo sur les cartes** : dans **Toute la collection**, chaque carte porte en bas à droite le logo de sa liste principale ; dans une liste qui a des sous-listes, celui de la sous-liste qui la contient (rien pour ce qui est rangé directement dans la liste). Réglable dans Filtres (l'entonnoir) → « Sur les cartes ». La barre du haut d'une liste montre aussi son logo, avec son nom seulement si « Afficher le nom » est coché.

Créer une liste

#### Gérer une liste

Sous le titre d'une liste ouverte :

Sous le titre d'une liste, **✏️ Modifier la liste** ouvre une fenêtre qui regroupe tout :

- **Logo** et **Émoji** : une liste peut avoir les deux ;
- **Afficher** : un petit tableau dit, pour le **menu latéral**, la **barre supérieure** (la liste et ses pastilles de sous-listes), le **titre** et les **vignettes** (le petit logo en bas à droite des cartes ; le nom de la liste sur les cartes se règle dans Filtres (l'entonnoir)), s'il faut montrer l'émoji, le logo et le nom — à la carte. Sans émoji ni logo coché, le nom s'affiche toujours ;
- **↳** (en haut du menu latéral, à droite de ＋ et ⇅) : montre ou cache toutes les sous-listes dans le menu ; cachées, celles cochées « Afficher cette sous-liste dans le menu latéral » restent ;
- **Sous-liste — Afficher cette sous-liste dans le menu latéral** : cochée, elle apparaît dans le menu, sous sa liste parente (une liste principale y est toujours) ; décochée, la ligne « Menu latéral » du tableau se grise ;
- **Couleur** : la couleur du thème de la liste — dans la liste (et ses sous-listes sans couleur à elles) et dans ses fiches, les boutons et surlignages la prennent. Réglages → **🎨 Thème de l'application** : la couleur générale ; **↺ Réinitialiser tous les thèmes** remet le rouge partout.
- **Liste qui a des sous-listes — Logo des sous-listes** : sur les vignettes, « listes enfant » (d’office : le logo de chaque sous-liste) ou « celle-ci » (son logo pour toutes ses sous-listes ; si plusieurs niveaux le demandent, le plus haut l’emporte) ;
- **D’office** (rien de réglé) : titre = le logo seul ; barre supérieure = logo + nom ; vignettes = le logo ; sans logo, l’émoji (et le nom) ;
- **Renommer** ;
- **Ranger après…** : sa place parmi les listes du même niveau (sur ordinateur : glisser sa pastille devant ou derrière une autre) ;
- **🖼️ Logo** : **😀 Choisir un emoji**, ou importer / coller une image (un PNG transparent, par exemple le logo d'une gamme), recadrée avec les outils habituels (cadre libre au plus près, 🪄 Détourer qui supprime le fond : transparent), affichée à la hauteur d'un emoji (largeur selon le recadrage) devant le nom de la liste partout. Sans rien choisi (et sans emoji dans le nom), la liste reçoit un emoji d'office ;
- **Ranger dans…** : la placer dans une autre liste ;

- **Supprimer la liste** (après confirmation ; ses éléments sont retirés avec elle).

Une liste ouverte

#### Déplacer ou copier plusieurs éléments

- Cocher la petite case en haut à gauche de chaque vignette.

- La barre du bas indique le nombre sélectionné : choisir la liste **Vers**…

- Toucher **Déplacer** ou **Copier** ; **Supprimer** les retire de leur liste (après confirmation) ; **Annuler** décoche tout.

Sur ordinateur : faites glisser une vignette sur une liste du menu pour l'y déplacer (Ctrl pour la copier) : elle part tout de suite.

**Les fiches reliées suivent** : déplacer un set emmène les figurines et MOC rangés dedans ; déplacer une figurine rangée
dans un set emmène son set (et tout son contenu) — sa vignette se glisse aussi sur une liste. Seule la fiche déplacée remonte dans « dernière modification ».

Plusieurs éléments à la fois

## Ajouter un set

#### 1. Chercher le set

- Toucher **+**.

- Taper le **numéro** (ex. 77256) ou le **nom** (en français ou en anglais), puis **Rechercher**.

- Ou bien : **📷 Appareil photo** — viser la boîte, le set monté, ou le **code-barres** de la boîte (lu tout seul) ; toucher l'image pour prendre la photo.
**📁 Importer une image** ou **📋 Coller** : une photo déjà prise ou copiée.

- Les résultats se trient par onglet : **Tout / Sets / Figurines / Pièces**. Ce qui est déjà dans la collection apparaît en premier, sous « Dans la collection ».

Pas trouvé ? « ✍️ Ajouter sans rechercher » crée l'élément à la main ; « 🛠️ Ajouter un MOC » crée une création personnelle.

+ : chercher

#### 2. Remplir la fiche

- Vérifier la photo, le nom, l'année, le nombre de pièces et le prix.

- **Choisir une liste…** (encadré rouge tant qu'aucune n'est choisie) ; **+** crée une nouvelle liste.

- **Quantité** : − / +.

- Cocher **📦 Boîte** (boîte présente), **📘 Livret** (livret de montage présent), **🚧 À construire** (pas encore monté).

- **🧱 Le set** ou **🟡 Uniquement les figurines** : si seules les figurines sont gardées, choisir combien de chacune.

- **🧩 Set partiel** : il manque une partie du set (il devient un « set partiel » estimé par ses pièces).

2. La fiche d'ajout

#### 3. Les figurines, puis Ajouter

- Sous **Figurines**, les figurines d'origine. Leur menu **…** : changer la quantité (0 = absente : la valeur baisse d'autant).

- **+ 🗡️ Accessoire**, **+ 🖼️ Apparence** : voir « Modifier une fiche ».

- **💶 Tarifs constatés** (set pas encore dans la collection) : prix magasin, prix neuf actuel, prix d'occasion, puis les prix BrickLink
en neuf et en occasion, **séparément** : la **moyenne des ventes réelles des 6 derniers mois** (ce que les acheteurs ont vraiment payé, pas
le prix demandé), minimum – maximum, nombre de ventes et zone : la France s'il y a au moins 3 ventes, sinon l'Europe, sinon le monde. Sans aucune
vente en 6 mois, ce sont les annonces en cours, signalées comme telles ; **📈 Évolution** : l'historique du prix. Une fois le set ajouté, sa fiche montre
l'**estimation** de l'exemplaire.

- **Voir sur** : la page du set sur LEGO.com (sa page produit quand elle est connue — sets relevés avec les Nouveautés —, sinon la recherche LEGO.com
tant que le set est vendu ou à venir ; rien pour un set retiré, une figurine ou un MOC), BrickLink et Rebrickable (rien pour un MOC). Pareil sur les pages publiques.

Toucher enfin **Ajouter à la liste**. Déjà possédé ? La fiche le signale ; « + Exemplaire séparé » ajoute un deuxième exemplaire avec ses propres réglages.

Figurines et estimation

## Ajouter une figurine

- **+**, puis taper son **nom** (« Dark Vador ») ou sa **référence** (sw0001). La photo marche aussi.

- Onglet **Figurines** : chaque résultat indique ses sets et sa cote d'occasion.

- Toucher la bonne : sa fiche s'ouvre. Choisir la **liste**, la **quantité**, puis **Ajouter à la liste**.

Figurine à collectionner (sachet ou boîte) : taper le **code à 7 chiffres** imprimé sous la boîte, ou le viser avec l'appareil photo.

Chercher une figurine

#### Voir ses figurines

Le bouton **Figurines** en haut (ou la tuile Figurines) montre toutes les figurines : celles rangées seules et celles des sets
(« Figurine de set »). En toucher une ouvre sa fiche.

Les figurines

**🛠️ Enregistrer comme MOC** : après une recherche par photo, si l'élément proposé n'est pas le bon, ce bouton garde
la photo et crée une fiche MOC à la place.

**✍️ Ajouter sans rechercher (MOC ou set partiel)** demande d'abord le type : 🛠️ MOC, 🟠 Figurine MOC ou 🧩 Set partiel.
Pour une **figurine MOC** (nouvelle ou déjà enregistrée), chaque nouvelle photo est scannée **dès qu'elle est ajoutée** (sans attendre l'enregistrement) : les **pièces repérées** s'affichent aussitôt dans la fiche (photo dans la couleur reconnue, %) — cocher les bonnes puis **✔ Ajouter les pièces cochées** ; « Plus tard » les laisse à valider après l'enregistrement ;
puis, à l'enregistrement, la validation des pièces s'ouvre. Au-delà de 5 secondes, un message indique que le scan continue ; s'il est
impossible, il est relancé automatiquement plus tard. Les figurines à valider restent dans « MOC à valider » (pas de tâche automatique). Dans la fiche, **🔄 Rescanner la photo** relance le scan ;
**+ 🔶 Pièce** ouvre la recherche habituelle (référence, nom, photo, coller). Les pièces proposées s'affichent dans la couleur reconnue.

**Détourage** : une photo importée est recadrée, et son fond peut être retiré **sur l'appareil** (détourage local, sans envoyer la photo).
Toute image importée est d'abord **cadrée automatiquement** autour de l'objet (ajustable). Dans la fenêtre de recadrage, le bouton **🪄 Détourer le fond** retire le fond tout de suite (fond uni ou coloré, plis et ombres compris) en gardant le cadre (« ✔ Fond retiré » ensuite). Dans le recadrage, **📋 Coller** colle une image copiée (il n'ouvre pas la galerie).
Le détourage se fait sur le serveur (ISNet) ou sur l'appareil : la photo n'est envoyée à aucun site extérieur.

**Ajouter une pièce** (figurine MOC, validation d'un scan) : la photo de la fiche s'affiche au-dessus des boutons — un appui permet
de **cadrer la pièce** cherchée dessus, sans chercher une autre image ; les boutons (appareil photo, image, coller, texte) restent là.
Couleurs indisponibles (service injoignable) ou inconnues : la pièce s'ajoute quand même, sans couleur, avec une tâche « Pièce … : couleur à
valider » (vérifiée une fois par jour). Les menus et fenêtres d'image disent à quoi ils servent (photo principale, apparence alternative…).
Recadrage : sous le curseur de rotation, **−** et **+** font tourner l'image d'**un degré** par appui (l'angle peut aussi se taper).
En recherche, la flèche ↑ n'est pas affichée.

Sur un **MOC**, la rangée d'ajout propose aussi « + Figurine » (set MOC) ou « + Set » (figurine MOC), une fois la fiche ajoutée. Le nom d'une apparence s'affiche entre parenthèses.

**Apparences alternatives** : en ouvrant une apparence, la coche « Afficher dans la vue générale » (cochée par défaut) décide si sa vignette apparaît dans la vue générale et la collection publique ; décochée, elle est marquée 🚫 dans la fiche.

En ouvrant une apparence : **⭐ Définir comme principale**. En grand, les apparences s'affichent à côté de l'image (dessous sur téléphone) ; un appui affiche l'une à la place de l'autre, l'actuelle est encadrée ; le titre est le nom de la fiche suivi du nom de l'apparence entre parenthèses. Pareil sur la collection publique.

**🪄 Détourer le fond** (recadrage d'une photo) : le fond est retiré sur le serveur (modèle ISNet, quelques secondes, la photo ne part pas ailleurs) ; sans ISNet, sur l'appareil.
Pendant le calcul, le bouton affiche un **pourcentage qui avance** et se remplit : c'est une **estimation**, calée sur la durée de le dernier détourage (le modèle n'annonce pas
son avancement) ; il ralentit vers la fin plutôt que d'afficher 100 % trop tôt.

**Recadrage** : cadre verrouillé (🔒 Format fixe) au format des vignettes (4:3) ; pour une **figurine ou une figurine MOC**, en **portrait 3:4**, centré sur la figurine entière. Un appui sur 🔒 le déverrouille (🔓 Format libre) ; seul le recadrage d'une photo pour une recherche est libre par défaut.

**🖌️ Pinceau** (recadrage) : peint en blanc ce qui gêne sur la photo (un autre objet, une tache) ; régler sa taille (elle est **retenue** : le pinceau reprend la dernière taille utilisée sur cet appareil), « ↩ Annuler le trait » revient en arrière. Le cadre ne bouge pas tant que le pinceau est actif.

Le cadre peut **dépasser de la photo** : ce qui dépasse sera blanc (pratique pour une photo très haute, sabre laser compris).

#### La fiche d'une figurine

**Chaque figurine est une fiche à part entière**, même celle d'un set : ajouter un set crée les fiches de ses figurines, rattachées
au set. Elles se sélectionnent, se glissent, se déplacent (sans leur set), ont leur date, leurs tâches. Une figurine a son prix
à elle, mais compté **dans la cote de son set** (jamais deux fois). **Sortie du set**, elle devient indépendante et sa valeur est déduite du set ;
retirée (« je ne l'ai pas »), elle est déduite du set.

- Sa photo (la toucher l'agrandit), ses sets d'origine, sa cote d'occasion et neuve (au-dessus des liens BrickLink et Rebrickable).

- Toucher le **nom** de la fiche : la **renommer**. Pour une figurine d'un des sets, le nom est gardé dans ce set — et lui seul — et affiché partout, pages publiques comprises.

- **🔁 Échanger des pièces** : remplacer une tête, un torse, une coiffe… (la figurine devient « modifiée »).

- **Pièces** : chaque pièce avec son prix d'occasion (BrickLink d'abord, BrickOwl sinon). Une pièce encore sans prix est cherchée
sur BrickLink pendant que la fiche est ouverte : « … » puis le prix apparaît ; « prix ? » = aucune annonce nulle part (💶 Mettre un prix).

- **Figurines rangées dans un set** : leur prix est compté dans celui du set (jamais deux fois) ; une figurine seule compte pour elle-même,
selon sa quantité. Une figurine d'un set peut être dans une autre liste que lui ; déplacer un set emmène ses figurines qui sont dans la même liste.

- La **liste** affichée sur la fiche d'une figurine ouverte depuis son set est celle du set : en choisir une autre puis 💾 déplace le set et tout
ce qu'il contient (ex. Biggs dans « Star Wars » : le X-Wing et ses figurines suivent).

- « **Aussi dans ce set — pas dans la collection** » : les autres sets du catalogue qui contiennent cette figurine et qui ne sont pas dans la collection
(ceux qui y sont : dans « Dans les sets »).

- **Supprimer** (en bas) : sur la fiche d'une figurine d'un des sets, la retire de ce set ; sur celle d'une figurine présente aussi dans des
sets, ne supprime que les exemplaires sans set (la confirmation le précise).

La fiche d'une figurine

#### Une même figurine, seule et dans les sets

Une même figurine peut être à la fois **seule** et **dans un ou plusieurs des sets** (ex. celle fournie avec un set, et la même achetée à part).
Briquothèque n'en fait **qu'une carte** (« ×N ») et **qu'une fiche** :

- **Quantité**, en haut : le **total** (ex. 12 = 1 dans un set + 11 seules). Elle ne descend pas sous le nombre rangé dans les sets.

- **Une figurine = une fiche** : tous ses exemplaires identiques (originales dans les sets, ajoutées dans un set, seules) ont une seule carte et une seule fiche ; une pièce changée vaut pour tous ceux qui étaient identiques. Seul **Dupliquer puis modifier** crée une variante à part.

- **Dans les sets**, en bas : chaque set qui la contient, avec un **− / +**. Sets + seules = la quantité. **−** sort une figurine du set : elle redevient **seule** (rien n'est perdu, le total ne change pas), prête à aller dans un autre set.
**+** range dans ce set une figurine seule de même référence s'il y en a une (sinon, une de plus). Enregistré tout de suite. Le total est rappelé à côté du titre.

- **Seules (sans set)** : celles qui n'appartiennent à aucun set ; l'augmenter augmente la quantité (enregistré avec 💾).

- Exemple : 20 figurines identiques — 10 dans un set, 8 dans un autre, 2 seules.

- Dans la fiche d'un set, toucher cette figurine ouvre la même fiche. Chaque set garde son exemplaire d'origine, compté dans sa valeur.

- Pas de regroupement quand la figurine du set a quelque chose à elle : des pièces échangées, des accessoires, un autre nom (une autre photo ne compte pas).
Elle garde alors sa carte et sa fiche : **chaque fiche est unique**, une action sur l'une ne touche jamais l'autre.

- Le lien de partage de la fiche donne le total et les sets. Pour ne rien regrouper du tout : back office, **Comportements › Figurines identiques**.

**Un set ajouté dont une figurine était déjà là, seule ?** Briquothèque demande si c'est celle de ce set. Oui : elle devient la
figurine d'origine du set (une seule fiche ; sa photo, ses apparences, ses pièces, ses accessoires et ses tâches la suivent). Pareil quand un souhait passe
dans la collection (« ✔ Acquis ») : la liste est demandée (★ = suggestion), puis le set va directement dans « 🚧 À construire ». La liste de souhaits, elle, ne modifie jamais la collection.

Une figurine, plusieurs exemplaires

#### ⧉ Copier, déplacer

- Fiche d'un **set**, d'un set partiel ou d'un MOC : **⧉ Copier cette fiche** crée une copie identique dans la même liste, ouverte aussitôt
(un set ne se range pas dans un autre set).

- Fiche d'une **figurine** : **⧉ Copier/Déplacer un exemplaire** ouvre un menu — **⧉ Copier un exemplaire**, **➡️ Ranger dans un set**
(ou **Déplacer vers un autre set**), **↩ Sortir du set**.

- **⧉ Copier un exemplaire** : une nouvelle fiche, copie de celle-ci, à modifier (tête changée, pièces échangées…). Elle s'ouvre tout de suite,
rangée là où est l'original ; enregistrée sans rien modifier, l'application demande confirmation ; fermée sans être enregistrée, elle est annulée.
À l'enregistrement, si l'original avait plusieurs exemplaires, l'application demande si ceux de la copie en viennent (« Oui : 38 là-bas, 2 ici » ou
« Non : 40 là-bas + 2 en plus »). La copie est cotée comme le modèle d'origine, puis estimée selon ses modifications.

- « Retirer du set » et « Sortir du set » demandent combien d'exemplaires sortent quand il y en a plusieurs.

⧉ Copier, déplacer un exemplaire

#### Échanger les pièces d'une figurine

- Dans sa fiche : **🔁 Échanger des pièces**.
- Toucher la pièce à changer : **🔁 Échanger cette pièce** (même pièce dans une autre couleur, ou une autre pièce),
**🗑 Je ne l'ai pas : la retirer**, ou **↩ Remettre la pièce d'origine** (une pièce remplacée : garder ou retirer la remplaçante).

- **Ajouter, remplacer ou échanger une pièce** : « 🖼️ À partir de la photo actuelle » cadre la pièce sur la photo de la fiche pour la chercher.

- Rien n'est enregistré avant **💾** : fermer la fiche sans enregistrer annule ces changements.

- La valeur suit : pièce retirée = sa valeur en moins, pièce ajoutée = sa valeur en plus.

Échanger les pièces d'une figurine

#### Un lot de figurines pas toutes identiques

Les pièces d'une fiche sont comptées pour **toutes ses figurines** : une fiche ×28 montre tête ×28, casque ×28, torse ×28, jambes ×28
(figurine d'un set : son nombre dans ce set). Inutile de faire une fiche par figurine :

- Menu **⋯** d'une pièce d'origine → **🔢 Modifier la quantité** : indiquer combien il y en a (ex. 20 têtes d'origine sur 28 ; les 8 autres
passent dans « retirées »). Boutons **− / +**, ou taper le nombre.

- **+ 🔶 Pièce** : ajouter les autres têtes, puis leur nombre (🔢 Modifier la quantité, dans leur menu).

- **💾** : l'estimation compte les vraies pièces du lot. La décote « Modifiée » ne touche que les figurines modifiées, pas les autres.

- Si la quantité de la fiche passe sous le nombre de figurines modifiées, l'application propose d'ajuster les pièces modifiées.

- Quand des figurines quittent un lot modifié (sortir du set, déplacer, copier un exemplaire), elle demande combien de celles qui partent sont
modifiées : leurs pièces les suivent.

- Rien n'oblige à détailler : sans toucher aux pièces, la fiche compte simplement N figurines d'origine.

Un lot de figurines

## Modifier une fiche

Toucher une vignette : sa fiche s'ouvre. Tout s'y modifie, puis **💾** (ou **Enregistrer**, en bas) enregistre.

#### Les boutons du haut

- le **nom** (le toucher) : renommer · **🔗** partager · **📝** ajouter une tâche · **💾** enregistrer · **✕** fermer.

#### Sous la photo

- Toucher la **photo** pour l'agrandir. Le menu **🧱 Set ▾** change le type de fiche (set, figurine, MOC, set partiel, figurine MOC).

- **🔶 Pièces (292 · 5 modifiées)** : la liste des pièces du set (voir plus bas). **📘 Plan** : la notice de montage sur LEGO.com
(ou dans l'appli LEGO Builder).

- Puis la **liste**, la **quantité**, **⧉ Copier cette fiche** (figurine : **⧉ Copier/Déplacer un exemplaire**), **📦 Boîte**, **📘 Livret**, **🚧 À construire**.

Le haut de la fiche

#### Les étiquettes

- Sous le nom : l'étiquette que l'application **calcule** (Modifié, Amélioré, Set partiel, MOC ; « complet » : aucune).

- **+ Étiquette** : en poser une à la main — Complet, Amélioré, Modifié, Set partiel ou MOC. Elle est enregistrée avec la fiche (💾), comme le reste.

- Le **✕** à côté d'une étiquette la retire de cette fiche, même celle que l'application calcule (elle revient par « + Étiquette » → « ↩ Remettre »).
Retirer une étiquette ne change pas la valeur.

- Les étiquettes s'affichent sur la carte, comptent dans le menu **Filtres (l'entonnoir)**, et apparaissent sur les pages publiques et les fiches partagées.

Les étiquettes d'une fiche

#### Ajouter à une fiche

- **+ 🟡 Figurine** : ranger une des figurines dans ce set (ou en ajouter une).

- **+ 🔶 Pièce** : une pièce en plus (elle compte dans la valeur).

- **+ 🗡️ Accessoire** : une mini-construction (photo ; la toucher → **📷 Changer la photo** pour la remplacer). Facultatif : la toucher → **🧾 Liste de pièces (XML)**, coller ou importer le XML BrickLink / Studio (ou le CSV Rebrickable) — ses pièces sont chiffrées et leur valeur s'ajoute à celle de la fiche (ligne « Accessoires (pièces) »).

- **+ 🖼️ Apparence** : les photos (📷 Appareil photo, 📁 Importer une image, 📋 Coller) — ou une **apparence alternative** (le set monté autrement).
Une apparence ajoutée a sa propre vignette dans la vue générale : en tri « dernière modification », **seule cette vignette remonte**, pas la fiche.
Chaque photo se **recadre** et son fond se retire (🪄 Détourer le fond), sans site extérieur.

- **La photo de la fiche** : la toucher pour la voir en grand, avec ses boutons — **✂️ Modifier image**, **📷 Changer la photo** et, sur un set ou une
figurine du catalogue dont la photo a été changée, **↩ Restaurer l'image** : la fiche reprend son **image officielle** (« Annuler », dans le message, remet
la photo ; enregistrer la fiche pour garder le changement). Les images du catalogue sont gardées sur l'appareil ; l'application les
relit d'elle-même de temps en temps (au plus tard après 30 jours), pour que la carte et la fiche montrent la même image.

Ajouter à la fiche

#### Chiffrer un accessoire (facultatif)

- Toucher l'accessoire (mini-construction) → **🧾 Liste de pièces (XML, facultatif)**.

- Coller le XML BrickLink / Studio, ou **📁 Importer un fichier** (XML, ou CSV Rebrickable) → **Valider**.

- La tuile de l'accessoire affiche son nombre de pièces et leur prix ; l'estimation de la fiche gagne la ligne « Accessoires (pièces) ». Son bouton **⋯** donne ses fonctions, dont **🔢 Modifier la quantité** : ×2 double ses pièces et sa valeur.
Enregistrer avec **💾**. Sans liste, un accessoire reste une simple photo, sans prix.

Les pièces d'un accessoire

#### Les figurines du set

- « 3 originales », « 7 ajoutées »… : **un seul nombre par figurine**. Jusqu'au nombre prévu par le set, ses exemplaires sont des **originales** ;
au-delà, ils passent dans **ajoutées** (ex. 8 pour 1 prévue : 1 originale + 7 ajoutées). Les figurines rangées dans le set avec leur propre fiche
(+ 🟡 Figurine) sont aussi des ajoutées.

- **Logo individuel** (en modification, à côté de la coche ci-dessous) : un logo propre à la fiche ; sur sa vignette, il remplace celui de sa liste et de la liste parente (ex. le logo de DOOM sur le Slayer, sans créer de liste DOOM). 🖼️ Choisir… : importer, coller, ou retirer ; puis 💾. Les figurines rangées dans un set qui a un logo individuel l'ont aussi ; sur une figurine, 🖼️ Choisir… → **Retirer le logo du set** l'enlève pour elle seule (**Reprendre le logo du set** le remet) ;
- **👁 Afficher dans la vue générale** (sur toutes les fiches, sous la quantité) : décochée, la fiche n'a plus de carte dans la grille ;
elle reste comptée dans la valeur et le filtre texte la retrouve.

- **Nouvelle fiche** : 💾 en haut ou « Ajouter » en bas ; « + Pièce », « + Set », « + Figurine » l'ajoutent d'abord puis font l'action. Une figurine MOC dont les pièces sont données à la création n'est pas scannée.

- **✏️ Dupliquer puis modifier** (menu **⋯** d'une figurine) : sur une originale, une **copie en plus** est créée (l'originale reste dans le set) ;
c'est une figurine **ajoutée** avec sa propre fiche. Changer ses pièces, sa photo ou son nom, puis 💾. Copie laissée sans modification : elle est retirée.
Sur un lot d'ajoutées : un exemplaire est mis à part ; s'il ne diffère en rien des autres, il les rejoint. Elle reste dans
le set et n'a pas de carte dans la vue générale.

- **Lecture d'abord** : une fiche s'ouvre en lecture (ses étiquettes et ses infos restent) ; **🔧** (la clé) en haut affiche les boutons de modification (et permet de renommer la fiche en touchant son nom) ; rien n'est enregistré avant **💾**, sauf les tâches 📝 ; **↩️** (à gauche de 💾) annule les modifications non enregistrées ; **💾** enregistre et la fiche reste ouverte, de nouveau en lecture.

- **← Retour** : à gauche du nom, il ramène à la fiche d'origine (une figurine ouverte depuis son set → le set). Le « retour » du téléphone fait de même.

- **Qui se range où** : un set, un set partiel et un set MOC peuvent contenir des figurines ; seules les **figurines** et les
**figurines MOC** se rangent dans un set — jamais un set dans un autre. Un exemplaire n'est rangé que dans **un seul** set ; un lot de plusieurs
exemplaires peut se répartir entre plusieurs sets (autant de sets que d'exemplaires, au plus).

- **Valeur** : une figurine rangée dans un set est comptée **dans la valeur de ce set**, jamais une seconde fois ; une figurine seule compte dans
le total général.

- **Set supprimé ou parti en liste de souhaits** : les figurines qui y avaient été ajoutées restent dans la collection, seules ; ses figurines
d'origine partent avec lui.

- Toucher une figurine pour ouvrir sa fiche. Une action sur une figurine n'agit que sur elle : l'originale sans les exemplaires en plus, et un seul exemplaire d'un lot.

- Le menu **…** d'une figurine : **🔢 Modifier la quantité** (celle de la tuile touchée : les originales, ou les ajoutées), **👁 Voir la fiche**,
**🔁 Échanger des pièces**, **⧉ Copier** ou **➡️ Déplacer vers un autre set…**, **🗑 Supprimer (je ne l'ai pas)** — sur la tuile des ajoutées,
seules les ajoutées partent ; sur celle d'origine, seule l'originale (« + 🟡 Figurine » la remet).

- **Étiquettes** : **Modifié** = un élément en remplace un autre (même s'il y a aussi des ajouts ; des pièces d'origine retirées et d'autres ajoutées à leur place comptent aussi comme un remplacement) ; **Amélioré** = tout est là et des choses sont ajoutées. La décote ne s'applique que si une figurine d'origine est modifiée.
Des exemplaires en plus, même modifiés, donnent « Amélioré ».

- Une figurine rangée dans le set avec sa propre fiche (même référence) **remplace d'abord une originale qui manque** si elle n'est pas modifiée ; modifiée, elle reste une ajoutée (marquée « modifiée », le set est « Amélioré », jamais « Modifié »).

Les figurines du set

Exemple : le menu **…** d'une figurine du set. Une figurine à 0 est comptée comme **manquante** : la valeur du set baisse d'autant.

Le menu … d'une figurine

#### Le bas de la fiche

- **Estimation de mon set** : le calcul détaillé (set complet d'occasion, figurines modifiées, pièces échangées, décote « modifié », boîte, plan…).

- **👀** : le mettre dans « À surveiller ». **Voir sur** : LEGO.com, BrickLink, Rebrickable.

- **Supprimer** : le retirer de sa liste, après confirmation (« Retirer … de la collection ? » ou « … de la liste de souhaits ? »).
Sur la fiche d'une **figurine d'un des sets**, « Supprimer » la retire de ce set (tous ses exemplaires) : le set reste, sans elle. Pour la remettre :
fiche du set, **+ 🟡 Figurine** (elle y est proposée en tête, marquée « manquante »).

- **Les figurines d'un set** : toucher le nom d'une figurine ouvre **sa** fiche — celle de la figurine de ce set pour une figurine d'origine (ou ses exemplaires en plus),
celle de la fiche rangée dans le set pour une figurine ajoutée (une copie renommée ou modifiée garde son nom). Une figurine **renommée** rangée dans un set
(+ 🟡 Figurine) y garde sa fiche et son nom.

Estimation et bas de fiche

#### 🔶 Pièces : échanger, retirer, ajouter

- Toucher **🔶 Pièces** (le nombre de pièces modifiées est indiqué) : la fenêtre « Échanger des pièces » s'ouvre, avec un **filtre** (nom, référence, couleur).

- Toucher une pièce : **sa fiche** (où la trouver, prix ; sa photo s'agrandit). Son **⋯** : **🔁 Échanger cette pièce** (autre couleur ou autre pièce), **🗑 Je ne l'ai pas : la retirer**, **🔎 Détail de la pièce**,
**🛒 À commander**, **📋 Cocher dans un inventaire…**

- **+ Ajouter une pièce** : une pièce en plus. **🛒 Commander des pièces** : envoyer des pièces dans « Commandes ».
**↩ Remettre le set d'origine** : annuler tous les échanges.

- **Ajustement de la valeur** : ce que les échanges retirent ou ajoutent. Toucher **Enregistrer**.
Les pièces retirées disparaissent de la liste ; les ajoutées s'affichent dessous ; le set devient « Modifié ».

Les pièces d'un set

#### Les prix d'une fiche

Au-dessus des liens BrickLink et Rebrickable, en bulles : **Prix magasin** (« retiré » s'il n'est plus vendu), **Neuf** (et sans figurines), **Occasion** (et sans figurines) — une bulle par ligne pour un set ; une figurine : neuf et occasion, côte à côte.
Pour un set pas encore dans la collection, le cadre « Tarifs constatés » donne en plus les prix **BrickLink** : **neuf** et **occasion**, moyenne des **ventes réelles des 6 derniers mois**,
minimum – maximum, nombre de ventes et zone (France, sinon 🇪🇺 Europe, sinon 🇺🇳 monde, s'il manque de ventes ; aucune vente : les annonces
en cours). **Partout** où un prix relevé s'affiche (cartes, fiches, estimation, figurines d'un set, pièces, « Commandes », pages publiques),
le drapeau de sa zone le précède : 🇪🇺 Europe, 🇺🇳 monde ; sans drapeau, le prix vient de France. (Sur les cartes de la vue principale, pas de drapeau : il apparaît dans la fiche.) Toucher un prix pour voir les annonces sur BrickLink.

Les prix sont relus chaque nuit, pour tout (sets, figurines, pièces), les plus anciens d'abord et dans une limite d'appels par jour ; et à l'ouverture d'une fiche dont le prix a plus de 24 h (pour un MOC : ses pièces) : la fiche se met à jour toute seule. Ces durées et la limite d'appels par jour se règlent dans ⚙️ Réglages › 💶 Prix (curseurs). Les **zones** où chercher les prix BrickLink (ex. Belgique, France, Europe, monde) et le nombre minimum de ventes pour en retenir une s'y règlent aussi.

Les prix d'une fiche

#### 📈 Évolution

La courbe du prix du set (ou de la figurine) dans le temps, en occasion et en neuf, sur 1 an, 3 ans ou tout.

Quand aucun historique n'est publié pour l'objet, la courbe vient des **relevés quotidiens de Briquothèque** (dès qu'il est dans les listes) :
une ligne plate veut dire que le prix n'a pas bougé depuis le premier relevé.

📈 Évolution

## Les MOC et sets partiels

Un **MOC** est une création personnelle ; un **set partiel**, un set incomplet. Les deux sont estimés par leurs pièces.

#### Créer un MOC

- **+ → 🛠️ Ajouter un MOC** (ou ✍️ Ajouter sans rechercher).

- Choisir le type : **MOC**, **set partiel** (indiquer le set d'origine) ou **figurine MOC**.

- Donner un **nom** et une **photo** (📷, 📁 ou 📋 Coller), recadrée au format des vignettes.

- Ses **pièces** : **📄 Import XML** (liste exportée de Rebrickable ou BrickLink), **🔎 Rechercher des pièces**, ou **+ Ajouter une pièce** une à une (photo possible).

- Choisir la liste, puis **Ajouter à la liste**. Chaque pièce est chiffrée en arrière-plan : la valeur apparaît peu à peu.

Créer un MOC

Les MOC portent l'étiquette **MOC** et leur nombre de pièces ; « ~ » devant la valeur signale une estimation approchée (pièces chiffrées par des pièces
semblables).

La liste des MOC

#### La fiche d'un MOC ou d'un set partiel

- Le menu de type (**🧩 Set partiel ▾**, MOC…) et **🔶 Pièces (268)** : sa liste de pièces, modifiable comme celle d'un set.

- Comme un set : liste, quantité, Boîte / Plan / À construire, + Figurine, + Pièce, + Accessoire, + Apparence.

La fiche d'un set partiel

- **Partie de** (set partiel) : le set d'origine ; **Changer** pour en choisir un autre.

- **Estimation** : le nombre de références chiffrées (BrickLink ou BrickOwl) et les références estimées par des pièces semblables.

- **Pièces** : celles du MOC ou du set partiel en vignettes dans la fiche (photo, quantité, nom, couleur, prix, ⋯), comme pour une figurine ;
**🔶 Pièces** garde les outils (commander, rechercher, importer).

- **Assemblage complet** (set partiel) : si les pièces forment un élément que BrickLink vend monté (le T-Rex du set 5886, par exemple),
il est compté au prix du monté (ligne « Monté : … » de l'estimation ; « 🧩 part de … » dans la liste des pièces).

Partie de, estimation

## Les inventaires de pièces

Un **inventaire** vérifie, pièce par pièce, qu'un set est complet — même un set pas encore dans la collection
(un lot d'occasion, un set à remonter). Les pièces manquantes partent ensuite dans **À commander**.

#### Créer un inventaire

- Menu **☰** → **+ Nouvel inventaire** (sous la liste des inventaires).

- Taper le **numéro** ou le **nom** du set (ex. 10316), puis **Rechercher** — ou **📷 Appareil photo** / **📁 Importer une image** pour le reconnaître en photo.

- Les sets apparaissent en premier ; toucher le bon set.

- L'inventaire s'ouvre avec toutes ses pièces (la liste vient de Rebrickable : la première ouverture peut prendre quelques secondes).
Il apparaît désormais dans le menu.

Créer un inventaire

#### Inventaire d'un lot qui n'est pas un set

- Dans **Nouvel inventaire**, toucher **📄 Import XML**.

- Donner un **nom** (ex. « Vrac du grenier »).

- Coller le **XML BrickLink** de la liste de pièces (sur Rebrickable : Inventory → Export → BrickLink XML).

- Toucher **Créer l'inventaire**.

Inventaire d'une liste XML

#### Le haut de l'inventaire

- **↻** recharge l'inventaire, **✏️** le renomme, **✕** le ferme (tout est enregistré au fur et à mesure, aussi sur les autres appareils).

- Photo du set (la toucher l'agrandit), puis le bilan : pièces, références, **✓ OK**, **🛒 à commander** (avec le coût estimé),
à vérifier, **✕ exclues**, et la barre d'avancement.

- **Filtrer** par nom, référence ou couleur ; filtres d'état : **Toutes, À vérifier, OK, À commander, Commandées, Exclues** ; **Tri** : type de pièce, couleur…

- **🎨 Remplacer une couleur** : remplace une couleur partout (ex. rose foncé → rouge) ; **↩ Réinitialiser les couleurs** annule.

- **📷 Scanner des pièces** : photographier des pièces étalées (à plat, espacées, sur fond clair), elles sont reconnues et comptées. **📋 Coller** : une photo copiée.

L'écran d'un inventaire

#### Pointer chaque pièce

- **✔ OK** : présente (en quantité). Ordre des lignes : non vérifiées, à commander, commandées, OK, exclues.

- **🛒 À commander** : elle manque ; régler la **quantité** avec − / +. Son prix estimé s'affiche.

- **🎨** : changer la couleur de cette pièce seulement. **🔁** : la remplacer par une autre pièce : la recherche (nom, référence, photo, « 🖼️ À partir de la photo actuelle ») est en haut, les pièces équivalentes dessous.

- **✕** : l'**exclure** (elle ne compte plus) ; **↩** la réintègre. **↺** : remet la pièce à zéro (état, couleur, remplacement).

- Toucher le **nom** d'une pièce pour sa fiche (sets où elle apparaît), sa **photo** pour l'agrandir. Toucher à nouveau un bouton actif l'annule.

Les pièces de l'inventaire

#### Passer commande depuis l'inventaire

- Dès qu'une pièce est à commander, le bouton **🧾 Exporter en XML (N pièces)** apparaît : il copie la liste dans le presse-papier, au format XML de BrickLink (aucun site ne s'ouvre). Les pièces **restent dans l'inventaire**.

- Une fois la commande passée, une pièce trouvée dans les commandes (BrickLink ou BrickOwl) passe toute seule en **📦 Commandée le …**. Commandée ailleurs ? Toucher **📦 Commandée** sur la pièce. Seule la date s'affiche (« Commandée le … »).

- Erreur : **↩ À commander** la remet à commander. À la réception, elles se passent à la main en **✔ OK** (jamais automatique). Quand tout est OK, Briquothèque propose de créer sa fiche : d'un « Oui », elle est créée tout de suite dans **À construire**, avec la photo de l'inventaire, dans la liste qui a le plus de sets du même thème.

Quand tout est OK : « Prêt à construire ? » — la liste (à choisir ; ★ marque la suggestion : celle qui a le plus de sets de son thème) et le type de fiche : 📦 Set complet, 🧩 Set partiel ou 🛠️ MOC ; la fiche est créée en coulisse dans « 🚧 À construire ». Le bouton **🚧 Prêt à construire : créer sa fiche** reste dans le résumé tant que tout est OK. **📷 Scanner des pièces** : trouver une pièce (appareil photo, image collée ou référence) ; la liste se filtre sur elle.

Tirer la page vers le bas (depuis le haut) l'actualise.

L'inventaire s'ouvre comme une **page** (le menu de gauche reste là ; un clic dans le menu le referme ; ✕ aussi).

**🗑️ Supprimer cet inventaire** (en haut, à côté de ✏️, ou tout en bas) le retire, après confirmation. Un inventaire n'est rattaché à aucune fiche : il est rangé par numéro de set, même ouvert depuis un set de la collection. Ses pièces **commandées** sont déplacées dans « Commandes » (avec leur commande) ; celles à commander ne le sont pas.

Remplacer une couleur

## Liste de souhaits et À surveiller

#### La liste de souhaits

- Ajouter un set comme pour la collection, en choisissant la liste **Liste de souhaits** — ou depuis **✨ Nouveautés** (⭐ Ajouter à la liste de souhaits).

- Tuiles : **coût estimé** de la liste, sets souhaités, **encore en vente** (prix public), **bientôt retirés**, **retirés**, pièces.

- Étiquettes des vignettes : **Bientôt disponible**, **Bientôt retiré**, **Retiré**, avec la date.

La liste de souhaits

#### Les souhaits

- **État souhaité** : 📦 Neuf ou Occasion (ou les deux) ; avec ou sans **Figurines** (l'estimation en tient compte ; boîte et plan ne comptent pas).

- **✔ Acquis** : le set passe dans la collection.

- **👀** (ou « Ne pas ajouter, c'est à surveiller ») : il va dans **À surveiller**, la liste de ce qui est guetté (neuf, occasion, boîte seule, plan, figurines…).
Elle a sa propre page publique, sans les notes.

La fiche d'un souhait

## Les pièces à commander

#### La liste

- Même présentation que l'inventaire. En haut, une information par ligne : les éléments (pièces et figurines), **🛒 à commander** (coût estimé), **📦 commandées** (montant réellement payé), **✔ reçues**, les sets concernés ; puis la barre d'avancement et les filtres **Toutes · À commander · Commandées · OK**.

- Chaque pièce (ou figurine) : photo, nom, couleur, référence, prix, le set pour lequel elle est commandée, le nombre en grand à droite ; dessous, les boutons comme dans l'inventaire (« Commandée le … », ✔ OK, 📦 Commandée / ↩ À commander, − / + tant qu'elle n'est pas commandée, 🗑).

- **État** voulu, sur chaque ligne : **N'importe**, **Neuf** (par défaut à l'ajout) ou **Occasion** — les choix « any / new / used »
de BrickLink. Le prix estimé suit : prix neuf, prix d'occasion, ou, pour « N'importe », le neuf s'il vient de France (prioritaire, même plus cher), sinon le moins cher des deux (prix voulu inconnu : l'autre,
signalé). Chaque ligne affiche toujours les **deux prix** : « Neuf : total » et « Occasion : total », avec le prix à l'unité entre parenthèses
s'il y a plus d'un exemplaire ; celui retenu pour le coût est en gras. Les noms trop longs sont coupés (nom complet au survol).
Les boutons sont sous les informations, comme dans l'inventaire ; « 🧱 Pour … » ouvre la fiche du set ; « 🛒 À commander » n'apparaît que pour une pièce
venue d'un inventaire. **BrickLink ↗** à côté de
l'état : les annonces de l'élément (pièce dans sa couleur, ou figurine), à l'état voulu, **dans la zone d'où vient le prix retenu**
(France : vendeurs en France ; Europe : vendeurs qui livrent en France ; monde : tous ; zone inconnue : la France). L'état part dans l'export BrickLink ; changé après l'export, penser à le changer aussi dans la wanted list.

- Toucher une pièce pour la modifier ; la **🗑** la retire.

#### Commander sur BrickLink

- Toucher **🧾 Exporter en XML** : toutes les pièces encore à commander (ni commandées ni reçues) sont copiées dans le presse-papier, au format XML de BrickLink. Aucun site ne s'ouvre ; elles se collent où il faut.

- Commande passée : une pièce trouvée dans les commandes (BrickLink ou BrickOwl) affiche **📦 Commandée le …** (seulement la date). Commandée ailleurs ? Toucher **📦 Commandée**. Les lignes exportées en XML ont leur section **🧾 Exportées** ; le ✕ retire « Exportée ». Ensuite, **🛒 À commander** demande : changer le statut de cette ligne (erreur : de nouveau à commander) ou préparer une nouvelle commande.

- La liste est en sections : **🛒 À commander**, **📦 Commandées**, **✔ Reçues** (chacune avec son nombre ; sur ordinateur, jusqu'à quatre par ligne). Tout en bas, en bleu : **➕ Commandées en plus** — ce qui reste des commandes une fois réparti entre les inventaires et la liste, attribué à aucune fiche (photo, quantité, date, prix payé). Sur chacune : **✔ OK** (reçue : elle disparaît ; une figurine propose de l'ajouter à la collection), **🧩 Attribuer à une fiche** (la pièce s'ajoute à la fiche choisie) ou **📋 Vers un inventaire** (la ligne de l'inventaire passe « Commandée », avec la date et le prix).

- Reçues ? Les passer en **✔ OK** (jamais automatique). Une **figurine** : Briquothèque propose de créer sa fiche. Une **pièce** qui manquait dans un des sets ou une des figurines : elle propose de l'y remettre (le set de la pièce d'abord) ; rien n'y manque mais elle était pour un des sets : elle demande quoi en faire (la garder à part, ou l'ajouter au set).

- **🛒 À commander** (ligne commandée) : changer le statut de cette ligne (de nouveau à commander) ou préparer une nouvelle commande ; **🔁 Commander à nouveau** (ligne reçue, ou ce second choix) : une nouvelle ligne à commander, dans la même couleur ou une autre — plusieurs couleurs possibles d'un coup (une ligne chacune) ; aussi pour toutes les lignes cochées avec ☑ Sélection.

- Le menu **☰** de « Commandes » propose les filtres (Toutes, À commander, Commandées, OK). **☑ Sélection** (dans ce même menu) : une case sur chaque ligne, puis une barre d'actions pour les lignes cochées — ✔ OK, 📦 Commandée, ↩ À commander, 🗑 Supprimer ; pour les commandées en plus : ✔ OK, 🧩 Attribuer à une fiche, 📋 Vers un inventaire.

- **🧹 Nettoyer** retire ensuite les pièces reçues de la liste.

La liste À commander

#### Ajouter une pièce à commander

- Dans **À commander**, toucher **+**.

- Chercher la pièce : **référence** (3001, 23443…), **nom** (brick 2 x 4), ou **photo** (📷, 📁, 📋 Coller). Par photo, les
**figurines** repérées s'affichent aussi, en tête (« 🟡 Figurines repérées ») : en toucher une ouvre sa fiche, liste « Commandes » déjà choisie.

Ajouter une pièce

- Toucher la bonne pièce.

- **🛒 À commander** (ou **➕ Dans un set / une figurine** pour l'ajouter à une fiche).

- **Pour quel set ?** (facultatif) : les couleurs présentes dans ce set s'affichent en premier, avec leur quantité. Ce n'est pas pour un set ? Taper plutôt une note (ex. « pour Paul ») et choisir **📝 En faire une note** : elle s'affiche sur la pièce.

- Choisir la **couleur**, éventuellement le **n° d'élément LEGO**, la **quantité**, l'**état** (neuf par défaut,
occasion ou n'importe), une **note**, puis enregistrer.

Choisir la pièce

La fiche d'une pièce reprend les mêmes champs. Depuis n'importe quelle pièce (fiche d'un set, inventaire, liste) :
**🔎 Détail de la pièce**, **🛒 À commander**, **📋 Cocher dans un inventaire…**, **⧉ Copier** ou **➡️ Déplacer vers une autre fiche…**,
et **💶 Mettre un prix** si aucun prix n'est connu.

**🔎 Détail de la pièce** : sa photo, sa couleur, son prix **BrickLink** en occasion et en neuf (ventes des 6 derniers mois ; toucher le prix pour voir les annonces),
le lien **BrickLink ↗** (la pièce dans cette couleur), les sets où elle apparaît et les figurines qui la portent.
Tous les liens externes (pièces, sets, figurines) ouvrent BrickLink, directement sur les **annonces en vente** (« Items For Sale ») :
vendeurs en France s'il y en a, sinon vendeurs qui livrent en France (Europe), sinon le monde entier — et, pour une pièce, dans sa couleur.

La fiche d'une pièce

## Nouveautés

- Les sets **à venir** et les **sorties récentes** de LEGO.com, du **dernier apparu** au plus ancien, sans ceux déjà dans la collection.

- Deux onglets : **📰 Dernières annonces** (la liste) et **📅 Calendrier**. Les cases **Sets** (cochée d'office) et **🟡 Figurines exclusives** choisissent ce qui s'affiche, dans les deux onglets (les deux ensemble possible ; dans le calendrier, une figurine est à la date de son set).
- Pages publiques : `/nouveautes` et `/calendrier` (la même, ouverte sur le calendrier). Les choix de chaque visiteur (onglet, cases, filtres, thème) sont gardés sur son appareil.
- Raccourci : **📅 Calendrier des sorties**, sous « ✨ Nouveautés » dans le menu, ouvre directement le calendrier.
- Visuel pas encore disponible : une boîte de set ou une silhouette de figurine grisée avec « ? ». La toucher relance la recherche ; les visuels manquants sont aussi recherchés à l'ouverture de la page et toutes les 6 h.
- **📅 Calendrier** : une frise des sorties, mois par mois et jour par jour (date de lego.com). On arrive sur « 📍 Aujourd'hui » : en dessous, les prochaines sorties ; en remontant, les sorties récentes. Toucher l'image l'agrandit ; toucher le set ouvre ses actions (liste de souhaits, à surveiller, lego.com, ne plus afficher). Liseré doré : déjà dans la liste de souhaits ; bleu : à surveiller.
- Celles apparues depuis la dernière visite sont **encadrées en jaune** ; le menu en affiche le nombre. Une fois vues, elles redeviennent normales.

- Filtres : **Tout / À venir / Sorties récentes** ; le thème. Les figurines exclusives sont celles qu'on ne trouve que dans ces sets.

- Sur chaque set : **⭐ Ajouter à la liste de souhaits**, **👀** (à surveiller), **🚫 Ne plus afficher** (« Afficher les masqués » les fait revenir). ; **Afficher celles sans image** : sans elle, les sets et figurines exclusives sans photo sont cachés

- Cases **Afficher ceux déjà dans la liste de souhaits** et **Afficher les surveillés** : ces sets reviennent, marqués « ⭐ Dans la liste de souhaits » (bandeau sur la photo) ou, plus discrètement, par le bouton « 👀 Surveillé » (toucher pour ouvrir la fiche).

Les nouveautés LEGO

#### 🎯 Thèmes suivis

Cocher les thèmes intéressants : les autres ne s'affichent plus (ni dans le compteur du menu).

🎯 Thèmes suivis

## Statistiques, tâches, à construire

#### 📊 Statistiques

- Choisir la liste en haut. Valeur, nombre de gammes et années, sets, figurines, pièces, pièces par set, valeur moyenne d'une pièce,
part de sets **déjà retirés** (toucher la tuile : lesquels sont encore en vente).

- Plus bas : **📈 Valeur dans le temps**, **Sets par année de sortie** (toucher une barre pour voir les sets de cette année),
**Gammes** (par sets, figurines, pièces ou valeur).

📊 Statistiques

#### 👁 Visites des pages publiques

En bas des Statistiques : pour chaque page publique (collection, liste de souhaits, À surveiller),
le nombre de visites, de visiteurs différents, d'aujourd'hui et des 7 derniers jours, et la dernière visite. Les propres visites (connecté) ne
comptent pas, une même personne compte au plus une visite par jour (recharger ou revenir ne compte pas), et les adresses des visiteurs ne sont jamais gardées en clair.

#### 📈 Valeur dans le temps

L'évolution de la valeur de la collection : **Occasion** ou **Neuf**, sur **1 an**, **3 ans** ou **Tout** ;
aujourd'hui, variation sur 1 an, minimum, maximum, moyenne.

#### 🔍 Comprendre les variations

Sous la courbe, le bouton **🔍 Comprendre les variations** explique ce qui a fait monter ou baisser la valeur de la liste
affichée, du plus gros au plus petit : **ajout** ou **retrait** d'une fiche, **hausse ou baisse d'une cote** (avec l'ancien et le nouveau prix),
quantité changée, fiche modifiée. Quand un set bouge à cause d'une figurine (manquante ou en plus), c'est la figurine qui est citée. Choisir la période :
Aujourd'hui, Depuis hier, 7 jours, 30 jours, Depuis le début. Toucher une ligne pour ouvrir la fiche ; le **←** de la fiche (ou le retour du téléphone) ramène à cette liste, sur la même période.

#### ↑ ↓ ~ La variation à côté des prix

À côté des prix, une marque dit comment ils ont bougé depuis le dernier relevé : **↑** vert en hausse,
**↓** rouge en baisse (avec le pourcentage), **~** stable (l'icône seule). Dans la vue générale (cartes, totaux), le bouton **📈** de la barre (à côté de 🔃) les montre
ou les cache à la volée ; il est allumé quand elles sont affichées, et l'appareil s'en souvient. Dans une fiche — de tout type : set, figurine (même vue depuis son set), MOC, set partiel, figurine MOC — la variation est **toujours** affichée
(mais pas sur le prix tout en haut) : sous le montant de l'estimation (à la ligne) — suivie de « (par rapport à 08:05) » si le relevé comparé a moins de 24 h, sinon
« (par rapport au 16/11/2026) » — de la cote (« Set complet d'occasion »), des lignes « Figurines ajoutées » et « Figurines manquantes », du prix de chaque figurine du set, du prix de chaque pièce,
et dans le détail des prix (prix de la fiche : neuf, occasion). Pour les pièces, elle compare au relevé précédent de la pièce : elle apparaît au fil des relevés.
Les **seuils** (à partir de quel écart la flèche monte ou descend) se règlent dans **Réglages → 🧮 Estimations** ; le « ~ », le pourcentage et la taille des
flèches, dans le **back office** (Comportements → Prix et variations). Sur les pages publiques, elles n'apparaissent
que si les prix y sont montrés.

**Prix trop minces** : un prix BrickLink fondé sur moins de 3 ventes (dans toutes les zones) n'est pas retenu : l'ancien prix est gardé, et la
fiche l'indique (« prix gardé : seulement 1 vente »). Le minimum se règle dans Réglages → 💶 Prix.

Valeur dans le temps

#### ✅ Les tâches

- Dans une fiche, toucher **✅** : écrire la tâche (photo à refaire, pièce à trouver…) et choisir sa catégorie.

- Menu → **📝 À faire** (ou **✅ Aucune tâche** s'il n'y en a plus) : toutes les tâches, rangées par catégorie. En toucher une ouvre sa fiche ; **✔ Fait** quand c'est fait.

- **📌 Note libre** : une tâche sans fiche. **+ Catégorie** : les propres catégories.

- **? Aide** : le petit « ? » à côté de la flèche ↑ explique la page ou la fenêtre ouverte — chaque bouton visible est entouré et
numéroté, la liste en bas l'explique (▾ la replie ; toucher une explication pour voir son bouton). Il a l'allure des boutons ↑ et ↻ ;
**Réglages › 🎨 Apparence** l'affiche ou le masque (affiché par défaut) ; ce **guide** est dans **Réglages › 📚 Aide et documentation**, qui s'ouvre dans le navigateur.

- **Une tâche d'une figurine** (même rangée dans un set) reste sur la fiche de la figurine : elle n'apparaît pas sur le set.

- Certaines tâches viennent de l'application : « couleur à valider » (pièce ajoutée sans couleur).

- **⚙️ Gérer les catégories** (en bas de « À faire ») : **✏️ Renommer** ou **🗑 Supprimer** une catégorie, même Photo, Pièces ou
Accessoires. Ses tâches suivent ; supprimée, elles vont dans **« Autres »**, qui ne peut être ni supprimée ni renommée. Le nombre de
tâches de chaque catégorie est indiqué.

- En enregistrant une fiche modifiée, Briquothèque demande si ses tâches sont faites — seulement celles qui existaient avant :
jamais celle qui vient d'être ajoutée.

Ajouter une tâche

📝 À faire

#### 🚧 À construire

Les sets cochés « À construire » dans leur fiche. Ils restent aussi dans leur liste ; décocher la case une fois montés.

🚧 À construire

## Partager

#### Partager une fiche

- Dans la fiche, toucher **🔗**, puis **🔗 Créer le lien**.
- Le lien est copié, prêt à envoyer. La personne voit cette fiche seule, en lecture
(photos, figurines, pièces, prix d'achat), sans mot de passe. Les notes et tâches ne sont jamais montrées.

- **Arrêter le partage** : depuis la fiche, ou le menu → **🔗 Fiches partagées**.

La fiche partagée montre les figurines comme la fiche : les **originales** du set (chacune une seule fois), les **modifiées** (figurines du set dont des pièces ont changé,
avec le nom et la photo qui leur ont été donnés), puis les **ajoutées**. Même classement sur la page publique de la collection. En bas : **LEGO.com** (page du produit si elle est connue, sinon la recherche
tant que le set est vendu) et BrickLink. Pour un set **encore en vente**, le bouton porte son prix public : « LEGO.com · 27,99 € »
(sur les fiches partagées et sur les pages publiques).

Les étiquettes d'état de la fiche partagée sont celles de la fiche (**Modifié**, Amélioré, Set partiel, MOC). Pas d'étiquette « Occasion ».

**Aperçu du lien** : collé dans une messagerie (WhatsApp, SMS, e-mail…), un lien de partage affiche le **nom de la fiche**
(« AT-AT — Briquothèque »). Une messagerie peut garder quelque temps l'ancien aperçu d'un lien déjà envoyé.

**Prix sur un lien de partage** : dans la fenêtre **🔗 Partager** (ou dans le menu → **🔗 Fiches partagées**), la case
**💶 Afficher les prix sur ce lien** montre ou masque la valeur, le prix d'achat et les cotes. C'est immédiat et le lien reste le même :
inutile d'en refaire un.

La barre au-dessus des vignettes : **↺**, la recherche, **Filtres (l'entonnoir)**, **Tri** (barres en escalier) et le bouton qui **inverse l'ordre** (deux flèches opposées ; en tri Aléatoire, il **remélange**), puis le **calendrier** : la période de comparaison des prix (sur téléphone et tablette, tout tient sur une ligne,
les boutons en carrés de même taille). Elle reste en haut de l'écran pendant le défilement, et la recherche est surlignée tant que quelque chose y est écrit.
« Filtres » et « Tri » sont deux menus **identiques** : un appui ouvre la même fenêtre, avec une ligne par choix. Dans « Filtres » on coche
autant d'étiquettes qu'on veut (la fenêtre reste ouverte) ; dans « Tri » on choisit un seul tri (la fenêtre se referme, et sur ordinateur le tri
en cours est rappelé sur le bouton). Un clic ailleurs ou la touche Échap referme le menu. C'est pareil sur les pages publiques.

Les tris de la collection : **Dernière modification**, **Aléatoire**, **Valeur**, **Variation de prix (%)** (les plus grosses variations en % d'abord, hausses comme baisses), **Variation de prix (€)** (le plus gros écart en euros d'abord), **Écart de prix (%)** (de la plus forte hausse à la plus forte baisse), **Écart de prix (€)** (idem, en euros), **Nombre de pièces** et **Nombre de figurines**. Avec un tri en euros, l'écart s'affiche en € à côté de la flèche. Sous la barre, une ligne rappelle toujours le tri en cours et son sens : ↘ décroissant, ↗ croissant (« Valeur ↘ ») ; avec un tri de variation ou d'écart, elle donne aussi la date de référence (« par rapport au … ») ; le bouton **calendrier** de la barre change la période (1, 7, 15, 30, 90, 180 ou 365 jours, glissants ; aussi dans Réglages › Estimations).
En tête du menu « Tri » : **Définir par défaut** fait du tri en cours le tri d'office (**↺** y revient), ; le bouton à côté du menu inverse l'ordre du tri en cours (les plus fortes baisses d'abord, du moins cher au plus cher…), retenu liste par liste — avec le tri Aléatoire, il remélange. Les « Pièces à commander » gardent leurs tris (ajout, nom, numéro, nombre).

**Inventaire** : son résumé donne une information par ligne (pièces, OK, à commander avec leur prix, commandées, à vérifier, exclues).
La ligne **❔ à vérifier** donne aussi ce que coûteraient les pièces pas encore triées s'il fallait toutes les commander, et
**Total 🛒 + ❔** additionne les pièces à commander et celles qui restent à vérifier (le chiffrage se complète en quelques instants,
référence par référence).

Dans un inventaire, un appui sur le nom d'une pièce ouvre sa fiche **dans la couleur affichée** : si une règle (ou le choix) remplace sa couleur,
c'est la couleur de remplacement qui est cherchée (prix, sets où elle apparaît) ; de même pour une pièce de remplacement.

**Couleurs demandées** : dans un inventaire, dès qu'une pièce change de couleur (règle « Remplacer une couleur », choix à la main, pièce de
remplacement), l'appli vérifie qu'elle **existe vraiment** dans cette couleur. Sinon la ligne porte **⚠ n'existe pas en …** (avec, si possible, une pièce
de même forme à mettre à la place), le résumé compte ces références, et la pièce **ne peut pas passer « à commander »** tant qu'elle n'est pas corrigée (🎨 ou 🔁).

**Recherche et filtres** : si une recherche ne trouve rien parce que des filtres sont cochés (Filtres (l'entonnoir)), ce qu'elle trouve sans eux
s'affiche juste en dessous, sous le titre **Résultats sans filtres** — comme « Ailleurs » pour les autres listes. Pareil sur les pages publiques.

Partager une fiche

🔗 Fiches partagées

#### Les pages publiques

- Chaque page publique ne montre **que son contenu**, avec des boutons vers les autres pages, toujours au même endroit : au bout de la rangée des listes, sous le titre.

- Elle s'affiche **comme l'application**, sans le menu latéral et sans rien de modifiable : mêmes boutons en haut (Tout, Sets, Figurines, Pièces), mêmes tuiles,
même barre (↺, recherche, **Filtres (l'entonnoir)** : Complet, Amélioré, Modifié, Set partiel, MOC ; même tri), mêmes cartes (étiquettes, figurines des sets en cartes « Dans un set »)
et même fiche (photo, figurines en vignettes, apparences, accessoires, pièces). Les listes remplacent le menu : une rangée sous le titre ; les sous-listes, dans la barre du haut. En défilant, les listes principales restent à portée dans la barre collée en haut, et dans une liste un bouton discret **↩ Toute la collection** y ramène. Sur téléphone, en descendant, cette barre ne montre que la liste en cours ; en remontant, tout revient (pareil dans l'application).
Aucun prix tant que l'option **Afficher les prix sur la collection publique** (Réglages › 🌐 Pages publiques) n'est pas cochée.

- **Page publique seulement** : dans une fiche, les figurines restent en vignettes regroupées (ex. « ×3 ») ; un appui sur une vignette les ouvre
**en grand, chaque figurine une par une** (les 3 Dark Troopers côte à côte), avec une apparition en cascade. Un appui n'importe où referme.

- **/collection** : les listes de collection seules (sans prix d'achat, ni notes, ni tâches), sets et figurines affichés ; lien « Liste de souhaits de … ».

- **/wishlist** : la liste de souhaits seule ; lien « Collection de … ». **/a-surveiller** : ce qui est surveillé.
**/nouveautes** : les nouveautés LEGO, avec des liens vers la collection et la liste de souhaits.

- Le menu (en bas) copie chaque lien d'un appui. Le nombre de visites de chaque page publique est dans la page **📊 Statistiques** (section « 👁 Visites ») ; les vôtres, connecté, ne comptent pas.

La page publique /collection

La page /wishlist

## Réglages

Menu → **⚙️ Réglages** : une page entière (application privée seulement). Sur ordinateur, le sommaire est à gauche et les sections sur deux colonnes ; sur téléphone, les raccourcis sont en haut, sur plusieurs lignes. La section choisie est surlignée. **Une seule règle** : chaque réglage s'enregistre dès qu'il est changé (un « ✔ » le confirme) ; seules les clés Rebrickable et BrickLink demandent **Vérifier et enregistrer** (elles sont testées). Les autres boutons lancent une action (actualiser, chiffrer, changer le mot de passe…). Ordre des sections : 🎨 Apparence · 💶 Prix · 🧮 Estimations · 🌐 Pages publiques · 🔑 Rebrickable · 🧱 BrickLink · 🔒 Sécurité · 📚 Aide et documentation · 🛠 Back office.

- **💶 Prix** : la passe BrickLink de la nuit (dès 3 h, les plus anciens d'abord, 2 000 appels au plus) ; **↻ Actualiser les prix** relit tout de suite
les sets, les figurines et les éléments estimés par leurs pièces (prix de plus de 24 h) ; **🧱 Chiffrer les pièces**.

- **🎨 Apparence** : le **style de l'application** — ✨ Moderne (d'office), 🧱 Classique, 🫧 Verre, 🟥 Brique, ◻️ Minimal, 🌃 Néon, 💥 BD, 🍬 Pastel, 📐 Technique ou 🌙 Nuit : l'aspect de tous les boutons et étiquettes, partout, pages publiques comprises (changement immédiat, aperçu en mini fiche) ; et la couleur de l'application.

- **🧮 Estimations** : la plus-value d'un set d'occasion **avec sa boîte** (%), la décote d'un exemplaire **modifié** (%), la plus-value du **livret de plans**.

- **🧱 BrickLink** : les 4 codes de l'API officielle de BrickLink (prix des ventes réelles), et le nombre d'appels du jour. Si BrickLink refuse (adresse IP changée), un message prévient.

- **🔑 Rebrickable** : la clé du catalogue (pièces, inventaires). Les clés restent sur le serveur et ne sont jamais réaffichées.

- **💬 Réseaux sociaux** (dans 🌐 Pages publiques) : le compte Instagram (champ libre) ; s'il est rempli, son logo, son nom et son lien s'affichent sur les pages publiques (pas dans l'application).

- **🌐 Public** : le nom affiché sur les pages publiques (« Collection de … »), ouvrir ou copier chaque page publique ; option **Afficher les prix sur la collection publique** (désactivée par défaut) ; pour partager une page publique : le petit **📤** à côté du compteur de visites (👁), en haut de sa page dans l'appli (Toute la collection, liste de souhaits, À surveiller, Nouveautés).

- **🔒 Sécurité** : **changer le mot de passe** ; les adresses bannies après trop d'échecs (débannir).

- **❓ Aide** : ce guide (adresse `/guide-utilisateur`), une page par chapitre, avec une recherche. Pour l'imprimer ou en faire un PDF : imprimer la page, tout le guide suit. Le bouton **🤖 Condensé pour IA** donne tout le guide en un texte : le coller dans une IA, puis lui demander « comment faire pour… ».

- **🛠 Back office** : « Ouvrir le back office » mène à l'atelier de la Briquothèque (adresse `/backoffice`), et sa notice (`/backoffice/guide`).

#### Le back office, en deux mots

Le back office sert à **tout modifier sans code** : apparence, textes, fiches, étiquettes, boutons (icônes et images), pages perso,
ordre des sections de cette page Réglages, comportements, sauvegardes, mots de passe… Il a **son propre mot de passe** (créé à la première visite),
se manie avec prudence et de préférence sur un ordinateur. Il a sa notice à lui, avec exemples et captures : **Réglages → 🛠 Back office → Notice**,
ou le bouton « ❓ Notice » en haut du back office.

## Fiches de démo et démonstration publique

**Fiches de démo** : la liste « Exemples » livrée avec Briquothèque montre une fiche de chaque type (set complet, set avec pièces ajoutées,
set avec figurine modifiée, set avec figurines ajoutées, set partiel, MOC, figurine MOC, figurine, figurine modifiée) et un inventaire.
Un bandeau jaune « Fiche de démo » les signale : ce sont de vraies fiches, à modifier ou supprimer librement.

**Démonstration publique** (facultative, désactivée par défaut) : l'administrateur du serveur peut ouvrir une démo en ligne, **/demo**
(variable `BQ_DEMO_SITE=1`), remise à zéro toutes les 12 h. Elle ne touche jamais la vraie collection et n'est pas accessible
quand on est connecté : pour la montrer, ouvrir le lien dans une fenêtre de navigation privée.


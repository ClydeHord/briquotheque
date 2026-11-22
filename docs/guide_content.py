# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Contenu du guide utilisateur de Briquothèque (lu par build_docs.py).

Chaque chapitre : titre, introduction, puis des blocs (capture d'écran, légende, texte HTML).
Les captures (docs/captures/<nom>.jpg) sont prises dans la DÉMO par captures.js.
À tenir à jour à chaque évolution de l'application : une fonction = des étapes précises.
"""

GUIDE = [
    # ------------------------------------------------------------------ 1
    {"title": "Premiers pas", "intro": """
<p>Briquothèque range la collection LEGO — <b>sets</b>, <b>figurines</b>, <b>MOC</b> (les créations), <b>pièces</b> — en estime la valeur,
et suit les envies (liste de souhaits, nouveautés, pièces à commander).</p>
<p class="tip"><b>La philosophie du projet</b> : des LEGO achetés, montés, utilisés, <b>modifiés</b>, inventoriés, et estimés <b>en l'état</b> —
rien n'est gardé scellé. Briquothèque n'est pas pensée pour stocker des boîtes neuves scellées. C'est la philosophie très personnelle
de son auteur : l'application répond d'abord à ses attentes, et s'ouvrira peut-être à d'autres selon son succès.</p>
<h3>Première installation</h3>
<ol><li>Au premier lancement, Briquothèque demande de <b>créer le mot de passe</b> (10 caractères au moins). Depuis Internet, elle demande
aussi le <b>code d'installation</b> affiché par le serveur.</li>
<li>Puis, facultatif : la <b>clé API Rebrickable</b> (catalogue, images, inventaires) et les <b>codes API BrickLink</b> (prix des ventes réelles),
avec la marche à suivre pour les obtenir. Sans eux, un bandeau jaune le rappelle ; le toucher ouvre les Réglages.</li>
<li>La liste <b>« Exemples »</b> contient une <b>fiche de démo</b> de chaque type et un inventaire de démo, marqués d'un bandeau jaune :
à explorer, modifier ou supprimer.</li></ol>""", "blocks": [
        ("accueil", "L'écran principal", """
<h3>Se connecter</h3>
<ol><li>Ouvrir l'adresse de la Briquothèque.</li><li>Entrer le <b>mot de passe</b> ; cocher « Rester connecté » sur l'appareil personnel.</li></ol>
<h3>L'écran principal</h3>
<ul><li><b>☰</b> : ouvre le menu (listes, inventaires, pages…).</li>
<li>Le <b>logo</b> ramène à l'accueil (toute la collection, en haut).</li>
<li><b>+</b> : ajouter un set, une figurine, un MOC (dans une liste de pièces : une pièce).</li>
<li><b>Valeur de la collection</b> : estimation d'occasion ; dessous, ce qu'elle vaudrait neuve.</li>
<li>Tuiles <b>Sets</b> / <b>Figurines</b> / <b>Pièces</b> : les totaux. Toucher Sets ou Figurines pour afficher l'un, l'autre ou les deux.</li></ul>"""),
        ("accueil-cartes", "Les vignettes", """
<h3>Lire une vignette</h3>
<ul><li>Photo, numéro, nom, gamme, année, nombre de pièces, et la <b>valeur estimée</b> (en petit : la cote réelle du marché).</li>
<li>Étiquettes : seulement <b>Complet</b>, <b>Amélioré</b>, <b>Modifié</b>, <b>Set partiel</b> et <b>MOC</b> ; à côté, les badges <b>Neuf</b>, <b>Sans figurines</b>, <b>×2</b> (quantité)…</li>
<li>Toucher une vignette pour ouvrir sa <b>fiche</b>.</li></ul>
<h3>Rechercher, trier, filtrer</h3>
<ul><li><b>Filtrer par nom, numéro, thème…</b> : la liste se réduit pendant la saisie.</li>
<li>Menu <b>Filtres (l'entonnoir)</b> : cocher une ou plusieurs étiquettes — <b>Complet</b>, <b>Amélioré</b>, <b>Modifié</b>, <b>Set partiel</b>, <b>MOC</b> — pour n'afficher que ces fiches (le bouton compte les étiquettes cochées).</li>
<li><b>↺</b> (à gauche du filtre) : remet les filtres à zéro.</li>
<li>Étiquettes des cartes : <b>MOC</b> (seule étiquette d'un MOC), <b>Set partiel</b>, <b>Modifié</b> (pièces retirées ou remplacées, figurine d'origine
remplacée ou modifiée), <b>Amélioré</b> (seulement des ajouts : pièces, figurines en plus). L'application les calcule ; dans une fiche, il est possible d'en poser
d'autres à la main ou en retirer une (voir « Modifier une fiche »).</li>
<li>Le <b>tri</b> : dernière modification, valeur, année, nom… En « dernière modification », seule la fiche modifiée remonte :
retoucher une figurine rangée dans un set ne fait pas remonter le set, et modifier un set ne fait pas remonter ses figurines.</li></ul>
<p class="tip">Ajoutée à l'écran d'accueil du téléphone, Briquothèque s'ouvre comme une appli et marche même sans réseau : les changements partent dès le retour de la connexion.</p>
<p><b>Mode hors ligne</b> : sans réseau, ou si le serveur est éteint, l'appli s'ouvre avec la dernière copie gardée sur l'appareil (bandeau « Hors ligne »).
Il faut l'avoir ouverte une fois <b>en ligne, en https</b> : en <code>http</code>, le navigateur n'autorise pas le mode hors ligne (l'appli passe d'elle-même
en https si l'adresse le permet ; une adresse locale en http reste sans mode hors ligne). <b>Toutes les fiches</b> s'ouvrent hors ligne, même jamais consultées : une fois par jour, en ligne, l'appli garde sur l'appareil un « paquet »
(environ 0,5 Mo) avec les fiches catalogue des sets et figurines et les pièces de les MOC. Ce qui demande Internet reste indisponible hors ligne :
la liste des pièces d'une figurine (Rebrickable), les recherches, les photos jamais affichées sur l'appareil.</p>"""),
    ]},
    # ------------------------------------------------------------------ 2
    {"title": "Le menu et les listes", "intro": "", "blocks": [
        ("menu", "Le menu", """
<ul><li><b>Toute la collection</b>, puis les <b>listes</b> avec leur nombre d'éléments et leur valeur. Une liste qui en contient d'autres est
<b>repliée</b> : toucher la flèche pour la déplier (le temps de la visite).</li>
<li><b>📝 À faire</b> : les tâches. <b>🚧 À construire</b> : les sets pas encore montés.</li>
<li><b>⭐ Liste de souhaits</b> (et <b>👀 À surveiller</b>), <b>✨ Nouveautés</b> (le nombre affiché suit les thèmes ; surligné s'il en est apparu de nouvelles),
<b>🔗 Fiches partagées</b>.</li>
<li><b>🔩 À commander</b> : les pièces — et les figurines — à acheter, avec leur coût estimé. Une figurine s'y ajoute par sa fiche (choix de la liste
« Commandes ») ou par « 🟡 Une figurine » dans l'ajout d'une pièce ; elle part aussi dans l'export vers la wanted list BrickLink.
La liste « Commandes » apparaît dans le choix de liste de toute fiche de figurine.</li>
<li>Les <b>inventaires</b>, puis <b>+ Nouvel inventaire</b>.</li></ul>"""),
        ("menu-bas", "Le bas du menu", """
<ul><li><b>📊 Statistiques</b>, <b>🎲 Une fiche au hasard</b> (pour redécouvrir un set), <b>⚙️ Réglages</b>, <b>Se déconnecter</b>.</li>
<li>Les <b>liens publics</b> (Collection, Nouveautés, À surveiller, Liste de souhaits, Mode Démo) : <b>un appui ouvre la page et copie son lien</b>, à envoyer aux proches ; « Mode Démo » copie seulement son lien (à ouvrir en navigation privée).
Dessous, <b>🐙 GitHub</b> ouvre la source officielle de Briquothèque, puis les <b>mentions légales</b>. Sur cette page, le bouton <b>✏️ Éditer</b> change le paragraphe « Éditeur » (quand le site est géré pour quelqu'un d'autre).</li>
<li><b>⇅</b> (en haut du menu) : changer l'ordre des listes.</li></ul>"""),
        ("liste-nouvelle", "Créer une liste", """
<h3>Créer une liste</h3>
<ol><li>Dans le menu, toucher <b>+</b> à côté des listes.</li><li>Donner un <b>nom</b> ; choisir éventuellement <b>Ranger dans</b> une autre liste (elle devient une sous-liste).</li>
<li>Toucher <b>Créer</b>.</li></ol>
<p><b>Sous-listes</b> : seules les listes principales sont dans le menu. Une liste qui a des sous-listes les montre en pastilles (sur ordinateur dans la barre du haut, sur téléphone sous le titre, puis dans la barre qui apparaît en faisant défiler ; l'active est surlignée) : la liste elle-même (tout son contenu, sous-listes comprises), chaque sous-liste, et <b>Non classées</b> (ce qui est rangé directement dans la liste). Dans une sous-liste, le bouton <b>‹</b> devant les pastilles ramène à la liste parente. On peut déposer des fiches sur une pastille. Les nombres sont dans les boutons Tout / Sets / Figurines / Pièces ; le bouton de la valeur (ce qui est affiché) trie du plus cher au moins cher. <b>Logo sur les cartes</b> : dans <b>Toute la collection</b>, chaque carte porte en bas à droite le logo de sa liste principale ; dans une liste qui a des sous-listes, celui de la sous-liste qui la contient (rien pour ce qui est rangé directement dans la liste). Réglable dans Filtres (l'entonnoir) → « Sur les cartes ». La barre du haut d'une liste montre aussi son logo, avec son nom seulement si « Afficher le nom » est coché.</p>"""),
        ("liste-actions", "Une liste ouverte", """
<h3>Gérer une liste</h3>
<p>Sous le titre d'une liste ouverte :</p>
<p>Sous le titre d'une liste, <b>✏️ Modifier la liste</b> ouvre une fenêtre qui regroupe tout :</p><ul><li><b>Logo</b> et <b>Émoji</b> : une liste peut avoir les deux ;</li><li><b>Afficher</b> : un petit tableau dit, pour le <b>menu latéral</b>, la <b>barre supérieure</b> (la liste et ses pastilles de sous-listes), le <b>titre</b> et les <b>vignettes</b> (le petit logo en bas à droite des cartes ; le nom de la liste sur les cartes se règle dans Filtres (l'entonnoir)), s'il faut montrer l'émoji, le logo et le nom — à la carte. Sans émoji ni logo coché, le nom s'affiche toujours ;</li><li><b>↳</b> (en haut du menu latéral, à droite de ＋ et ⇅) : montre ou cache toutes les sous-listes dans le menu ; cachées, celles cochées « Afficher cette sous-liste dans le menu latéral » restent ;</li><li><b>Sous-liste — Afficher cette sous-liste dans le menu latéral</b> : cochée, elle apparaît dans le menu, sous sa liste parente (une liste principale y est toujours) ; décochée, la ligne « Menu latéral » du tableau se grise ;</li><li><b>Couleur</b> : la couleur du thème de la liste — dans la liste (et ses sous-listes sans couleur à elles) et dans ses fiches, les boutons et surlignages la prennent. Réglages → <b>🎨 Thème de l'application</b> : la couleur générale ; <b>↺ Réinitialiser tous les thèmes</b> remet le rouge partout.</li><li><b>Liste qui a des sous-listes — Logo des sous-listes</b> : sur les vignettes, « listes enfant » (d’office : le logo de chaque sous-liste) ou « celle-ci » (son logo pour toutes ses sous-listes ; si plusieurs niveaux le demandent, le plus haut l’emporte) ;</li><li><b>D’office</b> (rien de réglé) : titre = le logo seul ; barre supérieure = logo + nom ; vignettes = le logo ; sans logo, l’émoji (et le nom) ;</li><li><b>Renommer</b> ;</li><li><b>Ranger après…</b> : sa place parmi les listes du même niveau (sur ordinateur : glisser sa pastille devant ou derrière une autre) ;</li><li><b>🖼️ Logo</b> : <b>😀 Choisir un emoji</b>, ou importer / coller une image (un PNG transparent, par exemple le logo d'une gamme), recadrée avec les outils habituels (cadre libre au plus près, 🪄 Détourer qui supprime le fond : transparent), affichée à la hauteur d'un emoji (largeur selon le recadrage) devant le nom de la liste partout. Sans rien choisi (et sans emoji dans le nom), la liste reçoit un emoji d'office ;</li><li><b>Ranger dans…</b> : la placer dans une autre liste ;</li>
<li><b>Supprimer la liste</b> (après confirmation ; ses éléments sont retirés avec elle).</li></ul>"""),
        ("selection", "Plusieurs éléments à la fois", """
<h3>Déplacer ou copier plusieurs éléments</h3>
<ol><li>Cocher la petite case en haut à gauche de chaque vignette.</li>
<li>La barre du bas indique le nombre sélectionné : choisir la liste <b>Vers</b>…</li>
<li>Toucher <b>Déplacer</b> ou <b>Copier</b> ; <b>Supprimer</b> les retire de leur liste (après confirmation) ; <b>Annuler</b> décoche tout.</li></ol>
<p class="tip">Sur ordinateur : faites glisser une vignette sur une liste du menu pour l'y déplacer (Ctrl pour la copier) : elle part tout de suite.</p>
<p class="tip"><b>Les fiches reliées suivent</b> : déplacer un set emmène les figurines et MOC rangés dedans ; déplacer une figurine rangée
dans un set emmène son set (et tout son contenu) — sa vignette se glisse aussi sur une liste. Seule la fiche déplacée remonte dans « dernière modification ».</p>"""),
    ]},
    # ------------------------------------------------------------------ 3
    {"title": "Ajouter un set", "intro": "", "blocks": [
        ("ajout-recherche", "+ : chercher", """
<h3>1. Chercher le set</h3>
<ol><li>Toucher <b>+</b>.</li>
<li>Taper le <b>numéro</b> (ex. 77256) ou le <b>nom</b> (en français ou en anglais), puis <b>Rechercher</b>.</li>
<li>Ou bien : <b>📷 Appareil photo</b> — viser la boîte, le set monté, ou le <b>code-barres</b> de la boîte (lu tout seul) ; toucher l'image pour prendre la photo.
<b>📁 Importer une image</b> ou <b>📋 Coller</b> : une photo déjà prise ou copiée.</li>
<li>Les résultats se trient par onglet : <b>Tout / Sets / Figurines / Pièces</b>. Ce qui est déjà dans la collection apparaît en premier, sous « Dans la collection ».</li></ol>
<p class="tip">Pas trouvé ? « ✍️ Ajouter sans rechercher » crée l'élément à la main ; « 🛠️ Ajouter un MOC » crée une création personnelle.</p>"""),
        ("ajout-fiche", "2. La fiche d'ajout", """
<h3>2. Remplir la fiche</h3>
<ol><li>Vérifier la photo, le nom, l'année, le nombre de pièces et le prix.</li>
<li><b>Choisir une liste…</b> (encadré rouge tant qu'aucune n'est choisie) ; <b>+</b> crée une nouvelle liste.</li>
<li><b>Quantité</b> : − / +.</li>
<li>Cocher <b>📦 Boîte</b> (boîte présente), <b>📘 Livret</b> (livret de montage présent), <b>🚧 À construire</b> (pas encore monté).</li>
<li><b>🧱 Le set</b> ou <b>🟡 Uniquement les figurines</b> : si seules les figurines sont gardées, choisir combien de chacune.</li>
<li><b>🧩 Set partiel</b> : il manque une partie du set (il devient un « set partiel » estimé par ses pièces).</li></ol>"""),
        ("ajout-fiche-bas", "Figurines et estimation", """
<h3>3. Les figurines, puis Ajouter</h3>
<ul><li>Sous <b>Figurines</b>, les figurines d'origine. Leur menu <b>…</b> : changer la quantité (0 = absente : la valeur baisse d'autant).</li>
<li><b>+ 🗡️ Accessoire</b>, <b>+ 🖼️ Apparence</b> : voir « Modifier une fiche ».</li>
<li><b>💶 Tarifs constatés</b> (set pas encore dans la collection) : prix magasin, prix neuf actuel, prix d'occasion, puis les prix BrickLink
en neuf et en occasion, <b>séparément</b> : la <b>moyenne des ventes réelles des 6 derniers mois</b> (ce que les acheteurs ont vraiment payé, pas
le prix demandé), minimum – maximum, nombre de ventes et zone : la France s'il y a au moins 3 ventes, sinon l'Europe, sinon le monde. Sans aucune
vente en 6 mois, ce sont les annonces en cours, signalées comme telles ; <b>📈 Évolution</b> : l'historique du prix. Une fois le set ajouté, sa fiche montre
l'<b>estimation</b> de l'exemplaire.</li>
<li><b>Voir sur</b> : la page du set sur LEGO.com (sa page produit quand elle est connue — sets relevés avec les Nouveautés —, sinon la recherche LEGO.com
tant que le set est vendu ou à venir ; rien pour un set retiré, une figurine ou un MOC), BrickLink et Rebrickable (rien pour un MOC). Pareil sur les pages publiques.</li></ul>
<p>Toucher enfin <b>Ajouter à la liste</b>. Déjà possédé ? La fiche le signale ; « + Exemplaire séparé » ajoute un deuxième exemplaire avec ses propres réglages.</p>"""),
    ]},
    # ------------------------------------------------------------------ 4
    {"title": "Ajouter une figurine", "intro": "", "blocks": [
        ("ajout-figurine", "Chercher une figurine", """
<ol><li><b>+</b>, puis taper son <b>nom</b> (« Dark Vador ») ou sa <b>référence</b> (sw0001). La photo marche aussi.</li>
<li>Onglet <b>Figurines</b> : chaque résultat indique ses sets et sa cote d'occasion.</li>
<li>Toucher la bonne : sa fiche s'ouvre. Choisir la <b>liste</b>, la <b>quantité</b>, puis <b>Ajouter à la liste</b>.</li></ol>
<p class="tip">Figurine à collectionner (sachet ou boîte) : taper le <b>code à 7 chiffres</b> imprimé sous la boîte, ou le viser avec l'appareil photo.</p>"""),
        ("figurines", "Les figurines", """
<h3>Voir ses figurines</h3>
<p>Le bouton <b>Figurines</b> en haut (ou la tuile Figurines) montre toutes les figurines : celles rangées seules et celles des sets
(« Figurine de set »). En toucher une ouvre sa fiche.</p>"""),
        ("figurine-fiche", "La fiche d'une figurine", """
<p class="tip"><b>🛠️ Enregistrer comme MOC</b> : après une recherche par photo, si l'élément proposé n'est pas le bon, ce bouton garde
la photo et crée une fiche MOC à la place.</p>
<p><b>✍️ Ajouter sans rechercher (MOC ou set partiel)</b> demande d'abord le type : 🛠️ MOC, 🟠 Figurine MOC ou 🧩 Set partiel.
Pour une <b>figurine MOC</b> (nouvelle ou déjà enregistrée), chaque nouvelle photo est scannée <b>dès qu'elle est ajoutée</b> (sans attendre l'enregistrement) : les <b>pièces repérées</b> s'affichent aussitôt dans la fiche (photo dans la couleur reconnue, %) — cocher les bonnes puis <b>✔ Ajouter les pièces cochées</b> ; « Plus tard » les laisse à valider après l'enregistrement ;
puis, à l'enregistrement, la validation des pièces s'ouvre. Au-delà de 5 secondes, un message indique que le scan continue ; s'il est
impossible, il est relancé automatiquement plus tard. Les figurines à valider restent dans « MOC à valider » (pas de tâche automatique). Dans la fiche, <b>🔄 Rescanner la photo</b> relance le scan ;
<b>+ 🔶 Pièce</b> ouvre la recherche habituelle (référence, nom, photo, coller). Les pièces proposées s'affichent dans la couleur reconnue.</p>
<p><b>Détourage</b> : une photo importée est recadrée, et son fond peut être retiré <b>sur l'appareil</b> (détourage local, sans envoyer la photo).
Toute image importée est d'abord <b>cadrée automatiquement</b> autour de l'objet (ajustable). Dans la fenêtre de recadrage, le bouton <b>🪄 Détourer le fond</b> retire le fond tout de suite (fond uni ou coloré, plis et ombres compris) en gardant le cadre (« ✔ Fond retiré » ensuite). Dans le recadrage, <b>📋 Coller</b> colle une image copiée (il n'ouvre pas la galerie).
Le détourage se fait sur le serveur (ISNet) ou sur l'appareil : la photo n'est envoyée à aucun site extérieur.</p>
<p><b>Ajouter une pièce</b> (figurine MOC, validation d'un scan) : la photo de la fiche s'affiche au-dessus des boutons — un appui permet
de <b>cadrer la pièce</b> cherchée dessus, sans chercher une autre image ; les boutons (appareil photo, image, coller, texte) restent là.
Couleurs indisponibles (service injoignable) ou inconnues : la pièce s'ajoute quand même, sans couleur, avec une tâche « Pièce … : couleur à
valider » (vérifiée une fois par jour). Les menus et fenêtres d'image disent à quoi ils servent (photo principale, apparence alternative…).
Recadrage : sous le curseur de rotation, <b>−</b> et <b>+</b> font tourner l'image d'<b>un degré</b> par appui (l'angle peut aussi se taper).
En recherche, la flèche ↑ n'est pas affichée.
</p>
<p>Sur un <b>MOC</b>, la rangée d'ajout propose aussi « + Figurine » (set MOC) ou « + Set » (figurine MOC), une fois la fiche ajoutée. Le nom d'une apparence s'affiche entre parenthèses.</p>
<p><b>Apparences alternatives</b> : en ouvrant une apparence, la coche « Afficher dans la vue générale » (cochée par défaut) décide si sa vignette apparaît dans la vue générale et la collection publique ; décochée, elle est marquée 🚫 dans la fiche.</p>
<p>En ouvrant une apparence : <b>⭐ Définir comme principale</b>. En grand, les apparences s'affichent à côté de l'image (dessous sur téléphone) ; un appui affiche l'une à la place de l'autre, l'actuelle est encadrée ; le titre est le nom de la fiche suivi du nom de l'apparence entre parenthèses. Pareil sur la collection publique.</p>
<p><b>🪄 Détourer le fond</b> (recadrage d'une photo) : le fond est retiré sur le serveur (modèle ISNet, quelques secondes, la photo ne part pas ailleurs) ; sans ISNet, sur l'appareil.
Pendant le calcul, le bouton affiche un <b>pourcentage qui avance</b> et se remplit : c'est une <b>estimation</b>, calée sur la durée de le dernier détourage (le modèle n'annonce pas
son avancement) ; il ralentit vers la fin plutôt que d'afficher 100 % trop tôt.</p>
<p><b>Recadrage</b> : cadre verrouillé (🔒 Format fixe) au format des vignettes (4:3) ; pour une <b>figurine ou une figurine MOC</b>, en <b>portrait 3:4</b>, centré sur la figurine entière. Un appui sur 🔒 le déverrouille (🔓 Format libre) ; seul le recadrage d'une photo pour une recherche est libre par défaut.</p>
<p><b>🖌️ Pinceau</b> (recadrage) : peint en blanc ce qui gêne sur la photo (un autre objet, une tache) ; régler sa taille (elle est <b>retenue</b> : le pinceau reprend la dernière taille utilisée sur cet appareil), « ↩ Annuler le trait » revient en arrière. Le cadre ne bouge pas tant que le pinceau est actif.</p>
<p>Le cadre peut <b>dépasser de la photo</b> : ce qui dépasse sera blanc (pratique pour une photo très haute, sabre laser compris).</p>
<h3>La fiche d'une figurine</h3>
<p class="tip"><b>Chaque figurine est une fiche à part entière</b>, même celle d'un set : ajouter un set crée les fiches de ses figurines, rattachées
au set. Elles se sélectionnent, se glissent, se déplacent (sans leur set), ont leur date, leurs tâches. Une figurine a son prix
à elle, mais compté <b>dans la cote de son set</b> (jamais deux fois). <b>Sortie du set</b>, elle devient indépendante et sa valeur est déduite du set ;
retirée (« je ne l'ai pas »), elle est déduite du set.</p>
<ul><li>Sa photo (la toucher l'agrandit), ses sets d'origine, sa cote d'occasion et neuve (au-dessus des liens BrickLink et Rebrickable).</li>
<li>Toucher le <b>nom</b> de la fiche : la <b>renommer</b>. Pour une figurine d'un des sets, le nom est gardé dans ce set — et lui seul — et affiché partout, pages publiques comprises.</li>
<li><b>🔁 Échanger des pièces</b> : remplacer une tête, un torse, une coiffe… (la figurine devient « modifiée »).</li>
<li><b>Pièces</b> : chaque pièce avec son prix d'occasion (BrickLink d'abord, BrickOwl sinon). Une pièce encore sans prix est cherchée
sur BrickLink pendant que la fiche est ouverte : « … » puis le prix apparaît ; « prix ? » = aucune annonce nulle part (💶 Mettre un prix).</li>
<li><b>Figurines rangées dans un set</b> : leur prix est compté dans celui du set (jamais deux fois) ; une figurine seule compte pour elle-même,
selon sa quantité. Une figurine d'un set peut être dans une autre liste que lui ; déplacer un set emmène ses figurines qui sont dans la même liste.</li>
<li>La <b>liste</b> affichée sur la fiche d'une figurine ouverte depuis son set est celle du set : en choisir une autre puis 💾 déplace le set et tout
ce qu'il contient (ex. Biggs dans « Star Wars » : le X-Wing et ses figurines suivent).</li>
<li>« <b>Aussi dans ce set — pas dans la collection</b> » : les autres sets du catalogue qui contiennent cette figurine et qui ne sont pas dans la collection
(ceux qui y sont : dans « Dans les sets »).</li>
<li><b>Supprimer</b> (en bas) : sur la fiche d'une figurine d'un des sets, la retire de ce set ; sur celle d'une figurine présente aussi dans des
sets, ne supprime que les exemplaires sans set (la confirmation le précise).</li></ul>"""),
        ("figurine-exemplaires", "Une figurine, plusieurs exemplaires", """
<h3>Une même figurine, seule et dans les sets</h3>
<p>Une même figurine peut être à la fois <b>seule</b> et <b>dans un ou plusieurs des sets</b> (ex. celle fournie avec un set, et la même achetée à part).
Briquothèque n'en fait <b>qu'une carte</b> (« ×N ») et <b>qu'une fiche</b> :</p>
<ul><li><b>Quantité</b>, en haut : le <b>total</b> (ex. 12 = 1 dans un set + 11 seules). Elle ne descend pas sous le nombre rangé dans les sets.</li>
<li><b>Une figurine = une fiche</b> : tous ses exemplaires identiques (originales dans les sets, ajoutées dans un set, seules) ont une seule carte et une seule fiche ; une pièce changée vaut pour tous ceux qui étaient identiques. Seul <b>Dupliquer puis modifier</b> crée une variante à part.</li>
<li><b>Dans les sets</b>, en bas : chaque set qui la contient, avec un <b>− / +</b>. Sets + seules = la quantité. <b>−</b> sort une figurine du set : elle redevient <b>seule</b> (rien n'est perdu, le total ne change pas), prête à aller dans un autre set.
<b>+</b> range dans ce set une figurine seule de même référence s'il y en a une (sinon, une de plus). Enregistré tout de suite. Le total est rappelé à côté du titre.</li>
<li><b>Seules (sans set)</b> : celles qui n'appartiennent à aucun set ; l'augmenter augmente la quantité (enregistré avec 💾).</li>
<li>Exemple : 20 figurines identiques — 10 dans un set, 8 dans un autre, 2 seules.</li>
<li>Dans la fiche d'un set, toucher cette figurine ouvre la même fiche. Chaque set garde son exemplaire d'origine, compté dans sa valeur.</li>
<li>Pas de regroupement quand la figurine du set a quelque chose à elle : des pièces échangées, des accessoires, un autre nom (une autre photo ne compte pas).
Elle garde alors sa carte et sa fiche : <b>chaque fiche est unique</b>, une action sur l'une ne touche jamais l'autre.</li>
<li>Le lien de partage de la fiche donne le total et les sets. Pour ne rien regrouper du tout : back office, <b>Comportements › Figurines identiques</b>.</li></ul>
<p class="tip"><b>Un set ajouté dont une figurine était déjà là, seule ?</b> Briquothèque demande si c'est celle de ce set. Oui : elle devient la
figurine d'origine du set (une seule fiche ; sa photo, ses apparences, ses pièces, ses accessoires et ses tâches la suivent). Pareil quand un souhait passe
dans la collection (« ✔ Acquis ») : la liste est demandée (★ = suggestion), puis le set va directement dans « 🚧 À construire ». La liste de souhaits, elle, ne modifie jamais la collection.</p>"""),
        ("figurine-copier", "⧉ Copier, déplacer un exemplaire", """
<h3>⧉ Copier, déplacer</h3>
<ul><li>Fiche d'un <b>set</b>, d'un set partiel ou d'un MOC : <b>⧉ Copier cette fiche</b> crée une copie identique dans la même liste, ouverte aussitôt
(un set ne se range pas dans un autre set).</li>
<li>Fiche d'une <b>figurine</b> : <b>⧉ Copier/Déplacer un exemplaire</b> ouvre un menu — <b>⧉ Copier un exemplaire</b>, <b>➡️ Ranger dans un set</b>
(ou <b>Déplacer vers un autre set</b>), <b>↩ Sortir du set</b>.</li>
<li><b>⧉ Copier un exemplaire</b> : une nouvelle fiche, copie de celle-ci, à modifier (tête changée, pièces échangées…). Elle s'ouvre tout de suite,
rangée là où est l'original ; enregistrée sans rien modifier, l'application demande confirmation ; fermée sans être enregistrée, elle est annulée.
À l'enregistrement, si l'original avait plusieurs exemplaires, l'application demande si ceux de la copie en viennent (« Oui : 38 là-bas, 2 ici » ou
« Non : 40 là-bas + 2 en plus »). La copie est cotée comme le modèle d'origine, puis estimée selon ses modifications.</li>
<li>« Retirer du set » et « Sortir du set » demandent combien d'exemplaires sortent quand il y en a plusieurs.</li></ul>"""),
        ("figurine-pieces", "Échanger les pièces d'une figurine", """
<h3>Échanger les pièces d'une figurine</h3>
<ol><li>Dans sa fiche : <b>🔁 Échanger des pièces</b>.</li><li>Toucher la pièce à changer : <b>🔁 Échanger cette pièce</b> (même pièce dans une autre couleur, ou une autre pièce),
<b>🗑 Je ne l'ai pas : la retirer</b>, ou <b>↩ Remettre la pièce d'origine</b> (une pièce remplacée : garder ou retirer la remplaçante).</li>
<li><b>Ajouter, remplacer ou échanger une pièce</b> : « 🖼️ À partir de la photo actuelle » cadre la pièce sur la photo de la fiche pour la chercher.</li>
<li>Rien n'est enregistré avant <b>💾</b> : fermer la fiche sans enregistrer annule ces changements.</li>
<li>La valeur suit : pièce retirée = sa valeur en moins, pièce ajoutée = sa valeur en plus.</li></ol>"""),
        ("figurine-lot", "Un lot de figurines", """
<h3>Un lot de figurines pas toutes identiques</h3>
<p>Les pièces d'une fiche sont comptées pour <b>toutes ses figurines</b> : une fiche ×28 montre tête ×28, casque ×28, torse ×28, jambes ×28
(figurine d'un set : son nombre dans ce set). Inutile de faire une fiche par figurine :</p>
<ol><li>Menu <b>⋯</b> d'une pièce d'origine → <b>🔢 Modifier la quantité</b> : indiquer combien il y en a (ex. 20 têtes d'origine sur 28 ; les 8 autres
passent dans « retirées »). Boutons <b>− / +</b>, ou taper le nombre.</li>
<li><b>+ 🔶 Pièce</b> : ajouter les autres têtes, puis leur nombre (🔢 Modifier la quantité, dans leur menu).</li>
<li><b>💾</b> : l'estimation compte les vraies pièces du lot. La décote « Modifiée » ne touche que les figurines modifiées, pas les autres.</li></ol>
<ul><li>Si la quantité de la fiche passe sous le nombre de figurines modifiées, l'application propose d'ajuster les pièces modifiées.</li>
<li>Quand des figurines quittent un lot modifié (sortir du set, déplacer, copier un exemplaire), elle demande combien de celles qui partent sont
modifiées : leurs pièces les suivent.</li>
<li>Rien n'oblige à détailler : sans toucher aux pièces, la fiche compte simplement N figurines d'origine.</li></ul>"""),
    ]},
    # ------------------------------------------------------------------ 5
    {"title": "Modifier une fiche", "intro": "<p>Toucher une vignette : sa fiche s'ouvre. Tout s'y modifie, puis <b>💾</b> (ou <b>Enregistrer</b>, en bas) enregistre.</p>", "blocks": [
        ("fiche", "Le haut de la fiche", """
<h3>Les boutons du haut</h3>
<ul><li>le <b>nom</b> (le toucher) : renommer · <b>🔗</b> partager · <b>📝</b> ajouter une tâche · <b>💾</b> enregistrer · <b>✕</b> fermer.</li></ul>
<h3>Sous la photo</h3>
<ul><li>Toucher la <b>photo</b> pour l'agrandir. Le menu <b>🧱 Set ▾</b> change le type de fiche (set, figurine, MOC, set partiel, figurine MOC).</li>
<li><b>🔶 Pièces (292 · 5 modifiées)</b> : la liste des pièces du set (voir plus bas). <b>📘 Plan</b> : la notice de montage sur LEGO.com
(ou dans l'appli LEGO Builder).</li>
<li>Puis la <b>liste</b>, la <b>quantité</b>, <b>⧉ Copier cette fiche</b> (figurine : <b>⧉ Copier/Déplacer un exemplaire</b>), <b>📦 Boîte</b>, <b>📘 Livret</b>, <b>🚧 À construire</b>.</li></ul>"""),
        ("fiche-etiquette", "Les étiquettes d'une fiche", """
<h3>Les étiquettes</h3>
<ul><li>Sous le nom : l'étiquette que l'application <b>calcule</b> (Modifié, Amélioré, Set partiel, MOC ; « complet » : aucune).</li>
<li><b>+ Étiquette</b> : en poser une à la main — Complet, Amélioré, Modifié, Set partiel ou MOC. Elle est enregistrée avec la fiche (💾), comme le reste.</li>
<li>Le <b>✕</b> à côté d'une étiquette la retire de cette fiche, même celle que l'application calcule (elle revient par « + Étiquette » → « ↩ Remettre »).
Retirer une étiquette ne change pas la valeur.</li>
<li>Les étiquettes s'affichent sur la carte, comptent dans le menu <b>Filtres (l'entonnoir)</b>, et apparaissent sur les pages publiques et les fiches partagées.</li></ul>"""),
        ("fiche-apparence", "Ajouter à la fiche", """
<h3>Ajouter à une fiche</h3>
<ul><li><b>+ 🟡 Figurine</b> : ranger une des figurines dans ce set (ou en ajouter une).</li>
<li><b>+ 🔶 Pièce</b> : une pièce en plus (elle compte dans la valeur).</li>
<li><b>+ 🗡️ Accessoire</b> : une mini-construction (photo ; la toucher → <b>📷 Changer la photo</b> pour la remplacer). Facultatif : la toucher → <b>🧾 Liste de pièces (XML)</b>, coller ou importer le XML BrickLink / Studio (ou le CSV Rebrickable) — ses pièces sont chiffrées et leur valeur s'ajoute à celle de la fiche (ligne « Accessoires (pièces) »).</li>
<li><b>+ 🖼️ Apparence</b> : les photos (📷 Appareil photo, 📁 Importer une image, 📋 Coller) — ou une <b>apparence alternative</b> (le set monté autrement).
Une apparence ajoutée a sa propre vignette dans la vue générale : en tri « dernière modification », <b>seule cette vignette remonte</b>, pas la fiche.
Chaque photo se <b>recadre</b> et son fond se retire (🪄 Détourer le fond), sans site extérieur.</li>
<li><b>La photo de la fiche</b> : la toucher pour la voir en grand, avec ses boutons — <b>✂️ Modifier image</b>, <b>📷 Changer la photo</b> et, sur un set ou une
figurine du catalogue dont la photo a été changée, <b>↩ Restaurer l'image</b> : la fiche reprend son <b>image officielle</b> (« Annuler », dans le message, remet
la photo ; enregistrer la fiche pour garder le changement). Les images du catalogue sont gardées sur l'appareil ; l'application les
relit d'elle-même de temps en temps (au plus tard après 30 jours), pour que la carte et la fiche montrent la même image.</li></ul>"""),
        ("accessoire-pieces", "Les pièces d'un accessoire", """
<h3>Chiffrer un accessoire (facultatif)</h3>
<ol><li>Toucher l'accessoire (mini-construction) → <b>🧾 Liste de pièces (XML, facultatif)</b>.</li>
<li>Coller le XML BrickLink / Studio, ou <b>📁 Importer un fichier</b> (XML, ou CSV Rebrickable) → <b>Valider</b>.</li>
<li>La tuile de l'accessoire affiche son nombre de pièces et leur prix ; l'estimation de la fiche gagne la ligne « Accessoires (pièces) ». Son bouton <b>⋯</b> donne ses fonctions, dont <b>🔢 Modifier la quantité</b> : ×2 double ses pièces et sa valeur.
Enregistrer avec <b>💾</b>. Sans liste, un accessoire reste une simple photo, sans prix.</li></ol>"""),
        ("fiche-milieu", "Les figurines du set", """
<h3>Les figurines du set</h3>
<ul><li>« 3 originales », « 7 ajoutées »… : <b>un seul nombre par figurine</b>. Jusqu'au nombre prévu par le set, ses exemplaires sont des <b>originales</b> ;
au-delà, ils passent dans <b>ajoutées</b> (ex. 8 pour 1 prévue : 1 originale + 7 ajoutées). Les figurines rangées dans le set avec leur propre fiche
(+ 🟡 Figurine) sont aussi des ajoutées.</li>
<li><b>Logo individuel</b> (en modification, à côté de la coche ci-dessous) : un logo propre à la fiche ; sur sa vignette, il remplace celui de sa liste et de la liste parente (ex. le logo de DOOM sur le Slayer, sans créer de liste DOOM). 🖼️ Choisir… : importer, coller, ou retirer ; puis 💾. Les figurines rangées dans un set qui a un logo individuel l'ont aussi ; sur une figurine, 🖼️ Choisir… → <b>Retirer le logo du set</b> l'enlève pour elle seule (<b>Reprendre le logo du set</b> le remet) ;</li><li><b>👁 Afficher dans la vue générale</b> (sur toutes les fiches, sous la quantité) : décochée, la fiche n'a plus de carte dans la grille ;
elle reste comptée dans la valeur et le filtre texte la retrouve.</li>
<li><b>Nouvelle fiche</b> : 💾 en haut ou « Ajouter » en bas ; « + Pièce », « + Set », « + Figurine » l'ajoutent d'abord puis font l'action. Une figurine MOC dont les pièces sont données à la création n'est pas scannée.</li>
<li><b>✏️ Dupliquer puis modifier</b> (menu <b>⋯</b> d'une figurine) : sur une originale, une <b>copie en plus</b> est créée (l'originale reste dans le set) ;
c'est une figurine <b>ajoutée</b> avec sa propre fiche. Changer ses pièces, sa photo ou son nom, puis 💾. Copie laissée sans modification : elle est retirée.
Sur un lot d'ajoutées : un exemplaire est mis à part ; s'il ne diffère en rien des autres, il les rejoint. Elle reste dans
le set et n'a pas de carte dans la vue générale.</li>
<li><b>Lecture d'abord</b> : une fiche s'ouvre en lecture (ses étiquettes et ses infos restent) ; <b>🔧</b> (la clé) en haut affiche les boutons de modification (et permet de renommer la fiche en touchant son nom) ; rien n'est enregistré avant <b>💾</b>, sauf les tâches 📝 ; <b>↩️</b> (à gauche de 💾) annule les modifications non enregistrées ; <b>💾</b> enregistre et la fiche reste ouverte, de nouveau en lecture.</li>
<li><b>← Retour</b> : à gauche du nom, il ramène à la fiche d'origine (une figurine ouverte depuis son set → le set). Le « retour » du téléphone fait de même.</li>
<li><b>Qui se range où</b> : un set, un set partiel et un set MOC peuvent contenir des figurines ; seules les <b>figurines</b> et les
<b>figurines MOC</b> se rangent dans un set — jamais un set dans un autre. Un exemplaire n'est rangé que dans <b>un seul</b> set ; un lot de plusieurs
exemplaires peut se répartir entre plusieurs sets (autant de sets que d'exemplaires, au plus).</li>
<li><b>Valeur</b> : une figurine rangée dans un set est comptée <b>dans la valeur de ce set</b>, jamais une seconde fois ; une figurine seule compte dans
le total général.</li>
<li><b>Set supprimé ou parti en liste de souhaits</b> : les figurines qui y avaient été ajoutées restent dans la collection, seules ; ses figurines
d'origine partent avec lui.</li>
<li>Toucher une figurine pour ouvrir sa fiche. Une action sur une figurine n'agit que sur elle : l'originale sans les exemplaires en plus, et un seul exemplaire d'un lot.</li>
<li>Le menu <b>…</b> d'une figurine : <b>🔢 Modifier la quantité</b> (celle de la tuile touchée : les originales, ou les ajoutées), <b>👁 Voir la fiche</b>,
<b>🔁 Échanger des pièces</b>, <b>⧉ Copier</b> ou <b>➡️ Déplacer vers un autre set…</b>, <b>🗑 Supprimer (je ne l'ai pas)</b> — sur la tuile des ajoutées,
seules les ajoutées partent ; sur celle d'origine, seule l'originale (« + 🟡 Figurine » la remet).</li>
<li><b>Étiquettes</b> : <b>Modifié</b> = un élément en remplace un autre (même s'il y a aussi des ajouts ; des pièces d'origine retirées et d'autres ajoutées à leur place comptent aussi comme un remplacement) ; <b>Amélioré</b> = tout est là et des choses sont ajoutées. La décote ne s'applique que si une figurine d'origine est modifiée.
Des exemplaires en plus, même modifiés, donnent « Amélioré ».</li>
<li>Une figurine rangée dans le set avec sa propre fiche (même référence) <b>remplace d'abord une originale qui manque</b> si elle n'est pas modifiée ; modifiée, elle reste une ajoutée (marquée « modifiée », le set est « Amélioré », jamais « Modifié »).</li></ul>"""),
        ("fiche-figurine-menu", "Le menu … d'une figurine", """
<p>Exemple : le menu <b>…</b> d'une figurine du set. Une figurine à 0 est comptée comme <b>manquante</b> : la valeur du set baisse d'autant.</p>"""),
        ("fiche-bas", "Estimation et bas de fiche", """
<h3>Le bas de la fiche</h3>
<ul><li><b>Estimation de mon set</b> : le calcul détaillé (set complet d'occasion, figurines modifiées, pièces échangées, décote « modifié », boîte, plan…).</li>
<li><b>👀</b> : le mettre dans « À surveiller ». <b>Voir sur</b> : LEGO.com, BrickLink, Rebrickable.</li>
<li><b>Supprimer</b> : le retirer de sa liste, après confirmation (« Retirer … de la collection ? » ou « … de la liste de souhaits ? »).
Sur la fiche d'une <b>figurine d'un des sets</b>, « Supprimer » la retire de ce set (tous ses exemplaires) : le set reste, sans elle. Pour la remettre :
fiche du set, <b>+ 🟡 Figurine</b> (elle y est proposée en tête, marquée « manquante »).</li>
<li><b>Les figurines d'un set</b> : toucher le nom d'une figurine ouvre <b>sa</b> fiche — celle de la figurine de ce set pour une figurine d'origine (ou ses exemplaires en plus),
celle de la fiche rangée dans le set pour une figurine ajoutée (une copie renommée ou modifiée garde son nom). Une figurine <b>renommée</b> rangée dans un set
(+ 🟡 Figurine) y garde sa fiche et son nom.</li></ul>"""),
        ("fiche-pieces", "Les pièces d'un set", """
<h3>🔶 Pièces : échanger, retirer, ajouter</h3>
<ol><li>Toucher <b>🔶 Pièces</b> (le nombre de pièces modifiées est indiqué) : la fenêtre « Échanger des pièces » s'ouvre, avec un <b>filtre</b> (nom, référence, couleur).</li>
<li>Toucher une pièce : <b>sa fiche</b> (où la trouver, prix ; sa photo s'agrandit). Son <b>⋯</b> : <b>🔁 Échanger cette pièce</b> (autre couleur ou autre pièce), <b>🗑 Je ne l'ai pas : la retirer</b>, <b>🔎 Détail de la pièce</b>,
<b>🛒 À commander</b>, <b>📋 Cocher dans un inventaire…</b></li>
<li><b>+ Ajouter une pièce</b> : une pièce en plus. <b>🛒 Commander des pièces</b> : envoyer des pièces dans « Commandes ».
<b>↩ Remettre le set d'origine</b> : annuler tous les échanges.</li>
<li><b>Ajustement de la valeur</b> : ce que les échanges retirent ou ajoutent. Toucher <b>Enregistrer</b>.
Les pièces retirées disparaissent de la liste ; les ajoutées s'affichent dessous ; le set devient « Modifié ».</li></ol>"""),
        ("tarifs", "Les prix d'une fiche", """
<h3>Les prix d'une fiche</h3>
<p>Au-dessus des liens BrickLink et Rebrickable, en bulles : <b>Prix magasin</b> (« retiré » s'il n'est plus vendu), <b>Neuf</b> (et sans figurines), <b>Occasion</b> (et sans figurines) — une bulle par ligne pour un set ; une figurine : neuf et occasion, côte à côte.
Pour un set pas encore dans la collection, le cadre « Tarifs constatés » donne en plus les prix <b>BrickLink</b> : <b>neuf</b> et <b>occasion</b>, moyenne des <b>ventes réelles des 6 derniers mois</b>,
minimum – maximum, nombre de ventes et zone (France, sinon 🇪🇺 Europe, sinon 🇺🇳 monde, s'il manque de ventes ; aucune vente : les annonces
en cours). <b>Partout</b> où un prix relevé s'affiche (cartes, fiches, estimation, figurines d'un set, pièces, « Commandes », pages publiques),
le drapeau de sa zone le précède : 🇪🇺 Europe, 🇺🇳 monde ; sans drapeau, le prix vient de France. (Sur les cartes de la vue principale, pas de drapeau : il apparaît dans la fiche.) Toucher un prix pour voir les annonces sur BrickLink.</p>
<p>Les prix sont relus chaque nuit, pour tout (sets, figurines, pièces), les plus anciens d'abord et dans une limite d'appels par jour ; et à l'ouverture d'une fiche dont le prix a plus de 24 h (pour un MOC : ses pièces) : la fiche se met à jour toute seule. Ces durées et la limite d'appels par jour se règlent dans ⚙️ Réglages › 💶 Prix (curseurs). Les <b>zones</b> où chercher les prix BrickLink (ex. Belgique, France, Europe, monde) et le nombre minimum de ventes pour en retenir une s'y règlent aussi.</p>"""),
        ("evolution", "📈 Évolution", """
<h3>📈 Évolution</h3><p>La courbe du prix du set (ou de la figurine) dans le temps, en occasion et en neuf, sur 1 an, 3 ans ou tout.</p>
<p>Quand aucun historique n'est publié pour l'objet, la courbe vient des <b>relevés quotidiens de Briquothèque</b> (dès qu'il est dans les listes) :
une ligne plate veut dire que le prix n'a pas bougé depuis le premier relevé.</p>"""),
    ]},
    # ------------------------------------------------------------------ 6
    {"title": "Les MOC et sets partiels", "intro": "<p>Un <b>MOC</b> est une création personnelle ; un <b>set partiel</b>, un set incomplet. Les deux sont estimés par leurs pièces.</p>", "blocks": [
        ("ajout-moc", "Créer un MOC", """
<h3>Créer un MOC</h3>
<ol><li><b>+ → 🛠️ Ajouter un MOC</b> (ou ✍️ Ajouter sans rechercher).</li>
<li>Choisir le type : <b>MOC</b>, <b>set partiel</b> (indiquer le set d'origine) ou <b>figurine MOC</b>.</li>
<li>Donner un <b>nom</b> et une <b>photo</b> (📷, 📁 ou 📋 Coller), recadrée au format des vignettes.</li>
<li>Ses <b>pièces</b> : <b>📄 Import XML</b> (liste exportée de Rebrickable ou BrickLink), <b>🔎 Rechercher des pièces</b>, ou <b>+ Ajouter une pièce</b> une à une (photo possible).</li>
<li>Choisir la liste, puis <b>Ajouter à la liste</b>. Chaque pièce est chiffrée en arrière-plan : la valeur apparaît peu à peu.</li></ol>"""),
        ("moc", "La liste des MOC", """
<p>Les MOC portent l'étiquette <b>MOC</b> et leur nombre de pièces ; « ~ » devant la valeur signale une estimation approchée (pièces chiffrées par des pièces
semblables).</p>"""),
        ("moc-fiche", "La fiche d'un set partiel", """
<h3>La fiche d'un MOC ou d'un set partiel</h3>
<ul><li>Le menu de type (<b>🧩 Set partiel ▾</b>, MOC…) et <b>🔶 Pièces (268)</b> : sa liste de pièces, modifiable comme celle d'un set.</li>
<li>Comme un set : liste, quantité, Boîte / Plan / À construire, + Figurine, + Pièce, + Accessoire, + Apparence.</li></ul>"""),
        ("moc-fiche-pieces", "Partie de, estimation", """
<ul><li><b>Partie de</b> (set partiel) : le set d'origine ; <b>Changer</b> pour en choisir un autre.</li>
<li><b>Estimation</b> : le nombre de références chiffrées (BrickLink ou BrickOwl) et les références estimées par des pièces semblables.</li>
<li><b>Pièces</b> : celles du MOC ou du set partiel en vignettes dans la fiche (photo, quantité, nom, couleur, prix, ⋯), comme pour une figurine ;
<b>🔶 Pièces</b> garde les outils (commander, rechercher, importer).</li>
<li><b>Assemblage complet</b> (set partiel) : si les pièces forment un élément que BrickLink vend monté (le T-Rex du set 5886, par exemple),
il est compté au prix du monté (ligne « Monté : … » de l'estimation ; « 🧩 part de … » dans la liste des pièces).</li></ul>"""),
    ]},
    # ------------------------------------------------------------------ 7
    {"title": "Les inventaires de pièces", "intro": """
<p>Un <b>inventaire</b> vérifie, pièce par pièce, qu'un set est complet — même un set pas encore dans la collection
(un lot d'occasion, un set à remonter). Les pièces manquantes partent ensuite dans <b>À commander</b>.</p>""", "blocks": [
        ("inventaire-nouveau", "Créer un inventaire", """
<h3>Créer un inventaire</h3>
<ol><li>Menu <b>☰</b> → <b>+ Nouvel inventaire</b> (sous la liste des inventaires).</li>
<li>Taper le <b>numéro</b> ou le <b>nom</b> du set (ex. 10316), puis <b>Rechercher</b> — ou <b>📷 Appareil photo</b> / <b>📁 Importer une image</b> pour le reconnaître en photo.</li>
<li>Les sets apparaissent en premier ; toucher le bon set.</li>
<li>L'inventaire s'ouvre avec toutes ses pièces (la liste vient de Rebrickable : la première ouverture peut prendre quelques secondes).
Il apparaît désormais dans le menu.</li></ol>"""),
        ("inventaire-xml", "Inventaire d'une liste XML", """
<h3>Inventaire d'un lot qui n'est pas un set</h3>
<ol><li>Dans <b>Nouvel inventaire</b>, toucher <b>📄 Import XML</b>.</li>
<li>Donner un <b>nom</b> (ex. « Vrac du grenier »).</li>
<li>Coller le <b>XML BrickLink</b> de la liste de pièces (sur Rebrickable : Inventory → Export → BrickLink XML).</li>
<li>Toucher <b>Créer l'inventaire</b>.</li></ol>"""),
        ("inventaire", "L'écran d'un inventaire", """
<h3>Le haut de l'inventaire</h3>
<ul><li><b>↻</b> recharge l'inventaire, <b>✏️</b> le renomme, <b>✕</b> le ferme (tout est enregistré au fur et à mesure, aussi sur les autres appareils).</li>
<li>Photo du set (la toucher l'agrandit), puis le bilan : pièces, références, <b>✓ OK</b>, <b>🛒 à commander</b> (avec le coût estimé),
à vérifier, <b>✕ exclues</b>, et la barre d'avancement.</li>
<li><b>Filtrer</b> par nom, référence ou couleur ; filtres d'état : <b>Toutes, À vérifier, OK, À commander, Commandées, Exclues</b> ; <b>Tri</b> : type de pièce, couleur…</li>
<li><b>🎨 Remplacer une couleur</b> : remplace une couleur partout (ex. rose foncé → rouge) ; <b>↩ Réinitialiser les couleurs</b> annule.</li>
<li><b>📷 Scanner des pièces</b> : photographier des pièces étalées (à plat, espacées, sur fond clair), elles sont reconnues et comptées. <b>📋 Coller</b> : une photo copiée.</li></ul>"""),
        ("inventaire-lignes", "Les pièces de l'inventaire", """
<h3>Pointer chaque pièce</h3>
<ul><li><b>✔ OK</b> : présente (en quantité). Ordre des lignes : non vérifiées, à commander, commandées, OK, exclues.</li>
<li><b>🛒 À commander</b> : elle manque ; régler la <b>quantité</b> avec − / +. Son prix estimé s'affiche.</li>
<li><b>🎨</b> : changer la couleur de cette pièce seulement. <b>🔁</b> : la remplacer par une autre pièce : la recherche (nom, référence, photo, « 🖼️ À partir de la photo actuelle ») est en haut, les pièces équivalentes dessous.</li>
<li><b>✕</b> : l'<b>exclure</b> (elle ne compte plus) ; <b>↩</b> la réintègre. <b>↺</b> : remet la pièce à zéro (état, couleur, remplacement).</li>
<li>Toucher le <b>nom</b> d'une pièce pour sa fiche (sets où elle apparaît), sa <b>photo</b> pour l'agrandir. Toucher à nouveau un bouton actif l'annule.</li></ul>"""),
        ("inventaire-couleur", "Remplacer une couleur", """
<h3>Passer commande depuis l'inventaire</h3>
<ol><li>Dès qu'une pièce est à commander, le bouton <b>🧾 Exporter en XML (N pièces)</b> apparaît : il copie la liste dans le presse-papier, au format XML de BrickLink (aucun site ne s'ouvre). Les pièces <b>restent dans l'inventaire</b>.</li>
<li>Une fois la commande passée, une pièce trouvée dans les commandes (BrickLink ou BrickOwl) passe toute seule en <b>📦 Commandée le …</b>. Commandée ailleurs ? Toucher <b>📦 Commandée</b> sur la pièce. Seule la date s'affiche (« Commandée le … »).</li>
<li>Erreur : <b>↩ À commander</b> la remet à commander. À la réception, elles se passent à la main en <b>✔ OK</b> (jamais automatique). Quand tout est OK, Briquothèque propose de créer sa fiche : d'un « Oui », elle est créée tout de suite dans <b>À construire</b>, avec la photo de l'inventaire, dans la liste qui a le plus de sets du même thème.</li></ol>
<p>Quand tout est OK : « Prêt à construire ? » — la liste (à choisir ; ★ marque la suggestion : celle qui a le plus de sets de son thème) et le type de fiche : 📦 Set complet, 🧩 Set partiel ou 🛠️ MOC ; la fiche est créée en coulisse dans « 🚧 À construire ». Le bouton <b>🚧 Prêt à construire : créer sa fiche</b> reste dans le résumé tant que tout est OK. <b>📷 Scanner des pièces</b> : trouver une pièce (appareil photo, image collée ou référence) ; la liste se filtre sur elle.</p>
<p>Tirer la page vers le bas (depuis le haut) l'actualise.</p>
<p>L'inventaire s'ouvre comme une <b>page</b> (le menu de gauche reste là ; un clic dans le menu le referme ; ✕ aussi).</p>
<p><b>🗑️ Supprimer cet inventaire</b> (en haut, à côté de ✏️, ou tout en bas) le retire, après confirmation. Un inventaire n'est rattaché à aucune fiche : il est rangé par numéro de set, même ouvert depuis un set de la collection. Ses pièces <b>commandées</b> sont déplacées dans « Commandes » (avec leur commande) ; celles à commander ne le sont pas.</p>"""),
    ]},
    # ------------------------------------------------------------------ 8
    {"title": "Liste de souhaits et À surveiller", "intro": "", "blocks": [
        ("souhaits", "La liste de souhaits", """
<h3>La liste de souhaits</h3>
<ul><li>Ajouter un set comme pour la collection, en choisissant la liste <b>Liste de souhaits</b> — ou depuis <b>✨ Nouveautés</b> (⭐ Ajouter à la liste de souhaits).</li>
<li>Tuiles : <b>coût estimé</b> de la liste, sets souhaités, <b>encore en vente</b> (prix public), <b>bientôt retirés</b>, <b>retirés</b>, pièces.</li>
<li>Étiquettes des vignettes : <b>Bientôt disponible</b>, <b>Bientôt retiré</b>, <b>Retiré</b>, avec la date.</li></ul>"""),
        ("souhait-fiche", "La fiche d'un souhait", """
<h3>Les souhaits</h3>
<ul><li><b>État souhaité</b> : 📦 Neuf ou Occasion (ou les deux) ; avec ou sans <b>Figurines</b> (l'estimation en tient compte ; boîte et plan ne comptent pas).</li>
<li><b>✔ Acquis</b> : le set passe dans la collection.</li>
<li><b>👀</b> (ou « Ne pas ajouter, c'est à surveiller ») : il va dans <b>À surveiller</b>, la liste de ce qui est guetté (neuf, occasion, boîte seule, plan, figurines…).
Elle a sa propre page publique, sans les notes.</li></ul>"""),
    ]},
    # ------------------------------------------------------------------ 9
    {"title": "Les pièces à commander", "intro": "", "blocks": [
        ("a-commander", "La liste À commander", """
<h3>La liste</h3>
<ul><li>Même présentation que l'inventaire. En haut, une information par ligne : les éléments (pièces et figurines), <b>🛒 à commander</b> (coût estimé), <b>📦 commandées</b> (montant réellement payé), <b>✔ reçues</b>, les sets concernés ; puis la barre d'avancement et les filtres <b>Toutes · À commander · Commandées · OK</b>.</li>
<li>Chaque pièce (ou figurine) : photo, nom, couleur, référence, prix, le set pour lequel elle est commandée, le nombre en grand à droite ; dessous, les boutons comme dans l'inventaire (« Commandée le … », ✔ OK, 📦 Commandée / ↩ À commander, − / + tant qu'elle n'est pas commandée, 🗑).</li>
<li><b>État</b> voulu, sur chaque ligne : <b>N'importe</b>, <b>Neuf</b> (par défaut à l'ajout) ou <b>Occasion</b> — les choix « any / new / used »
de BrickLink. Le prix estimé suit : prix neuf, prix d'occasion, ou, pour « N'importe », le neuf s'il vient de France (prioritaire, même plus cher), sinon le moins cher des deux (prix voulu inconnu : l'autre,
signalé). Chaque ligne affiche toujours les <b>deux prix</b> : « Neuf : total » et « Occasion : total », avec le prix à l'unité entre parenthèses
s'il y a plus d'un exemplaire ; celui retenu pour le coût est en gras. Les noms trop longs sont coupés (nom complet au survol).
Les boutons sont sous les informations, comme dans l'inventaire ; « 🧱 Pour … » ouvre la fiche du set ; « 🛒 À commander » n'apparaît que pour une pièce
venue d'un inventaire. <b>BrickLink ↗</b> à côté de
l'état : les annonces de l'élément (pièce dans sa couleur, ou figurine), à l'état voulu, <b>dans la zone d'où vient le prix retenu</b>
(France : vendeurs en France ; Europe : vendeurs qui livrent en France ; monde : tous ; zone inconnue : la France). L'état part dans l'export BrickLink ; changé après l'export, penser à le changer aussi dans la wanted list.</li>
<li>Toucher une pièce pour la modifier ; la <b>🗑</b> la retire.</li></ul>
<h3>Commander sur BrickLink</h3>
<ol><li>Toucher <b>🧾 Exporter en XML</b> : toutes les pièces encore à commander (ni commandées ni reçues) sont copiées dans le presse-papier, au format XML de BrickLink. Aucun site ne s'ouvre ; elles se collent où il faut.</li>
<li>Commande passée : une pièce trouvée dans les commandes (BrickLink ou BrickOwl) affiche <b>📦 Commandée le …</b> (seulement la date). Commandée ailleurs ? Toucher <b>📦 Commandée</b>. Les lignes exportées en XML ont leur section <b>🧾 Exportées</b> ; le ✕ retire « Exportée ». Ensuite, <b>🛒 À commander</b> demande : changer le statut de cette ligne (erreur : de nouveau à commander) ou préparer une nouvelle commande.</li>
<li>La liste est en sections : <b>🛒 À commander</b>, <b>📦 Commandées</b>, <b>✔ Reçues</b> (chacune avec son nombre ; sur ordinateur, jusqu'à quatre par ligne). Tout en bas, en bleu : <b>➕ Commandées en plus</b> — ce qui reste des commandes une fois réparti entre les inventaires et la liste, attribué à aucune fiche (photo, quantité, date, prix payé). Sur chacune : <b>✔ OK</b> (reçue : elle disparaît ; une figurine propose de l'ajouter à la collection), <b>🧩 Attribuer à une fiche</b> (la pièce s'ajoute à la fiche choisie) ou <b>📋 Vers un inventaire</b> (la ligne de l'inventaire passe « Commandée », avec la date et le prix).</li>
<li>Reçues ? Les passer en <b>✔ OK</b> (jamais automatique). Une <b>figurine</b> : Briquothèque propose de créer sa fiche. Une <b>pièce</b> qui manquait dans un des sets ou une des figurines : elle propose de l'y remettre (le set de la pièce d'abord) ; rien n'y manque mais elle était pour un des sets : elle demande quoi en faire (la garder à part, ou l'ajouter au set).</li>
<li><b>🛒 À commander</b> (ligne commandée) : changer le statut de cette ligne (de nouveau à commander) ou préparer une nouvelle commande ; <b>🔁 Commander à nouveau</b> (ligne reçue, ou ce second choix) : une nouvelle ligne à commander, dans la même couleur ou une autre — plusieurs couleurs possibles d'un coup (une ligne chacune) ; aussi pour toutes les lignes cochées avec ☑ Sélection.</li>
<li>Le menu <b>☰</b> de « Commandes » propose les filtres (Toutes, À commander, Commandées, OK). <b>☑ Sélection</b> (dans ce même menu) : une case sur chaque ligne, puis une barre d'actions pour les lignes cochées — ✔ OK, 📦 Commandée, ↩ À commander, 🗑 Supprimer ; pour les commandées en plus : ✔ OK, 🧩 Attribuer à une fiche, 📋 Vers un inventaire.</li>
<li><b>🧹 Nettoyer</b> retire ensuite les pièces reçues de la liste.</li></ol>"""),
        ("piece-ajout", "Ajouter une pièce", """
<h3>Ajouter une pièce à commander</h3>
<ol><li>Dans <b>À commander</b>, toucher <b>+</b>.</li>
<li>Chercher la pièce : <b>référence</b> (3001, 23443…), <b>nom</b> (brick 2 x 4), ou <b>photo</b> (📷, 📁, 📋 Coller). Par photo, les
<b>figurines</b> repérées s'affichent aussi, en tête (« 🟡 Figurines repérées ») : en toucher une ouvre sa fiche, liste « Commandes » déjà choisie.</li></ol>"""),
        ("piece-ajout-resultats", "Choisir la pièce", """
<ol start="3"><li>Toucher la bonne pièce.</li>
<li><b>🛒 À commander</b> (ou <b>➕ Dans un set / une figurine</b> pour l'ajouter à une fiche).</li>
<li><b>Pour quel set ?</b> (facultatif) : les couleurs présentes dans ce set s'affichent en premier, avec leur quantité. Ce n'est pas pour un set ? Taper plutôt une note (ex. « pour Paul ») et choisir <b>📝 En faire une note</b> : elle s'affiche sur la pièce.</li>
<li>Choisir la <b>couleur</b>, éventuellement le <b>n° d'élément LEGO</b>, la <b>quantité</b>, l'<b>état</b> (neuf par défaut,
occasion ou n'importe), une <b>note</b>, puis enregistrer.</li></ol>"""),
        ("piece-fiche", "La fiche d'une pièce", """
<p>La fiche d'une pièce reprend les mêmes champs. Depuis n'importe quelle pièce (fiche d'un set, inventaire, liste) :
<b>🔎 Détail de la pièce</b>, <b>🛒 À commander</b>, <b>📋 Cocher dans un inventaire…</b>, <b>⧉ Copier</b> ou <b>➡️ Déplacer vers une autre fiche…</b>,
et <b>💶 Mettre un prix</b> si aucun prix n'est connu.</p>
<p><b>🔎 Détail de la pièce</b> : sa photo, sa couleur, son prix <b>BrickLink</b> en occasion et en neuf (ventes des 6 derniers mois ; toucher le prix pour voir les annonces),
le lien <b>BrickLink ↗</b> (la pièce dans cette couleur), les sets où elle apparaît et les figurines qui la portent.
Tous les liens externes (pièces, sets, figurines) ouvrent BrickLink, directement sur les <b>annonces en vente</b> (« Items For Sale ») :
vendeurs en France s'il y en a, sinon vendeurs qui livrent en France (Europe), sinon le monde entier — et, pour une pièce, dans sa couleur.</p>"""),
    ]},
    # ------------------------------------------------------------------ 10
    {"title": "Nouveautés", "intro": "", "blocks": [
        ("nouveautes", "Les nouveautés LEGO", """
<ul><li>Les sets <b>à venir</b> et les <b>sorties récentes</b> de LEGO.com, du <b>dernier apparu</b> au plus ancien, sans ceux déjà dans la collection.</li>
<li>Deux onglets : <b>📰 Dernières annonces</b> (la liste) et <b>📅 Calendrier</b>. Les cases <b>Sets</b> (cochée d'office) et <b>🟡 Figurines exclusives</b> choisissent ce qui s'affiche, dans les deux onglets (les deux ensemble possible ; dans le calendrier, une figurine est à la date de son set).</li><li>Pages publiques : <code>/nouveautes</code> et <code>/calendrier</code> (la même, ouverte sur le calendrier). Les choix de chaque visiteur (onglet, cases, filtres, thème) sont gardés sur son appareil.</li><li>Raccourci : <b>📅 Calendrier des sorties</b>, sous « ✨ Nouveautés » dans le menu, ouvre directement le calendrier.</li><li>Visuel pas encore disponible : une boîte de set ou une silhouette de figurine grisée avec « ? ». La toucher relance la recherche ; les visuels manquants sont aussi recherchés à l'ouverture de la page et toutes les 6 h.</li><li><b>📅 Calendrier</b> : une frise des sorties, mois par mois et jour par jour (date de lego.com). On arrive sur « 📍 Aujourd'hui » : en dessous, les prochaines sorties ; en remontant, les sorties récentes. Toucher l'image l'agrandit ; toucher le set ouvre ses actions (liste de souhaits, à surveiller, lego.com, ne plus afficher). Liseré doré : déjà dans la liste de souhaits ; bleu : à surveiller.</li><li>Celles apparues depuis la dernière visite sont <b>encadrées en jaune</b> ; le menu en affiche le nombre. Une fois vues, elles redeviennent normales.</li>
<li>Filtres : <b>Tout / À venir / Sorties récentes</b> ; le thème. Les figurines exclusives sont celles qu'on ne trouve que dans ces sets.</li>
<li>Sur chaque set : <b>⭐ Ajouter à la liste de souhaits</b>, <b>👀</b> (à surveiller), <b>🚫 Ne plus afficher</b> (« Afficher les masqués » les fait revenir). ; <b>Afficher celles sans image</b> : sans elle, les sets et figurines exclusives sans photo sont cachés</li>
<li>Cases <b>Afficher ceux déjà dans la liste de souhaits</b> et <b>Afficher les surveillés</b> : ces sets reviennent, marqués « ⭐ Dans la liste de souhaits » (bandeau sur la photo) ou, plus discrètement, par le bouton « 👀 Surveillé » (toucher pour ouvrir la fiche).</li></ul>"""),
        ("nouveautes-themes", "🎯 Thèmes suivis", """
<h3>🎯 Thèmes suivis</h3><p>Cocher les thèmes intéressants : les autres ne s'affichent plus (ni dans le compteur du menu).</p>"""),
    ]},
    # ------------------------------------------------------------------ 11
    {"title": "Statistiques, tâches, à construire", "intro": "", "blocks": [
        ("statistiques", "📊 Statistiques", """
<h3>📊 Statistiques</h3>
<ul><li>Choisir la liste en haut. Valeur, nombre de gammes et années, sets, figurines, pièces, pièces par set, valeur moyenne d'une pièce,
part de sets <b>déjà retirés</b> (toucher la tuile : lesquels sont encore en vente).</li>
<li>Plus bas : <b>📈 Valeur dans le temps</b>, <b>Sets par année de sortie</b> (toucher une barre pour voir les sets de cette année),
<b>Gammes</b> (par sets, figurines, pièces ou valeur).</li></ul>"""),
        ("statistiques-courbe", "Valeur dans le temps", """
<h3>👁 Visites des pages publiques</h3><p>En bas des Statistiques : pour chaque page publique (collection, liste de souhaits, À surveiller),
le nombre de visites, de visiteurs différents, d'aujourd'hui et des 7 derniers jours, et la dernière visite. Les propres visites (connecté) ne
comptent pas, une même personne compte au plus une visite par jour (recharger ou revenir ne compte pas), et les adresses des visiteurs ne sont jamais gardées en clair.</p>
<h3>📈 Valeur dans le temps</h3><p>L'évolution de la valeur de la collection : <b>Occasion</b> ou <b>Neuf</b>, sur <b>1 an</b>, <b>3 ans</b> ou <b>Tout</b> ;
aujourd'hui, variation sur 1 an, minimum, maximum, moyenne.</p>
<h3>🔍 Comprendre les variations</h3><p>Sous la courbe, le bouton <b>🔍 Comprendre les variations</b> explique ce qui a fait monter ou baisser la valeur de la liste
affichée, du plus gros au plus petit : <b>ajout</b> ou <b>retrait</b> d'une fiche, <b>hausse ou baisse d'une cote</b> (avec l'ancien et le nouveau prix),
quantité changée, fiche modifiée. Quand un set bouge à cause d'une figurine (manquante ou en plus), c'est la figurine qui est citée. Choisir la période :
Aujourd'hui, Depuis hier, 7 jours, 30 jours, Depuis le début. Toucher une ligne pour ouvrir la fiche ; le <b>←</b> de la fiche (ou le retour du téléphone) ramène à cette liste, sur la même période.</p>
<h3>↑ ↓ ~ La variation à côté des prix</h3><p>À côté des prix, une marque dit comment ils ont bougé depuis le dernier relevé : <b>↑</b> vert en hausse,
<b>↓</b> rouge en baisse (avec le pourcentage), <b>~</b> stable (l'icône seule). Dans la vue générale (cartes, totaux), le bouton <b>📈</b> de la barre (à côté de 🔃) les montre
ou les cache à la volée ; il est allumé quand elles sont affichées, et l'appareil s'en souvient. Dans une fiche — de tout type : set, figurine (même vue depuis son set), MOC, set partiel, figurine MOC — la variation est <b>toujours</b> affichée
(mais pas sur le prix tout en haut) : sous le montant de l'estimation (à la ligne) — suivie de « (par rapport à 08:05) » si le relevé comparé a moins de 24 h, sinon
« (par rapport au 16/11/2026) » — de la cote (« Set complet d'occasion »), des lignes « Figurines ajoutées » et « Figurines manquantes », du prix de chaque figurine du set, du prix de chaque pièce,
et dans le détail des prix (prix de la fiche : neuf, occasion). Pour les pièces, elle compare au relevé précédent de la pièce : elle apparaît au fil des relevés.
Les <b>seuils</b> (à partir de quel écart la flèche monte ou descend) se règlent dans <b>Réglages → 🧮 Estimations</b> ; le « ~ », le pourcentage et la taille des
flèches, dans le <b>back office</b> (Comportements → Prix et variations). Sur les pages publiques, elles n'apparaissent
que si les prix y sont montrés.</p>
<p class="tip"><b>Prix trop minces</b> : un prix BrickLink fondé sur moins de 3 ventes (dans toutes les zones) n'est pas retenu : l'ancien prix est gardé, et la
fiche l'indique (« prix gardé : seulement 1 vente »). Le minimum se règle dans Réglages → 💶 Prix.</p>"""),
        ("tache-ajout", "Ajouter une tâche", """
<h3>✅ Les tâches</h3>
<ol><li>Dans une fiche, toucher <b>✅</b> : écrire la tâche (photo à refaire, pièce à trouver…) et choisir sa catégorie.</li>
<li>Menu → <b>📝 À faire</b> (ou <b>✅ Aucune tâche</b> s'il n'y en a plus) : toutes les tâches, rangées par catégorie. En toucher une ouvre sa fiche ; <b>✔ Fait</b> quand c'est fait.</li>
<li><b>📌 Note libre</b> : une tâche sans fiche. <b>+ Catégorie</b> : les propres catégories.</li>
<li><b>? Aide</b> : le petit « ? » à côté de la flèche ↑ explique la page ou la fenêtre ouverte — chaque bouton visible est entouré et
numéroté, la liste en bas l'explique (▾ la replie ; toucher une explication pour voir son bouton). Il a l'allure des boutons ↑ et ↻ ;
<b>Réglages › 🎨 Apparence</b> l'affiche ou le masque (affiché par défaut) ; ce <b>guide</b> est dans <b>Réglages › 📚 Aide et documentation</b>, qui s'ouvre dans le navigateur.</li>
<li><b>Une tâche d'une figurine</b> (même rangée dans un set) reste sur la fiche de la figurine : elle n'apparaît pas sur le set.</li>
<li>Certaines tâches viennent de l'application : « couleur à valider » (pièce ajoutée sans couleur).</li>
<li><b>⚙️ Gérer les catégories</b> (en bas de « À faire ») : <b>✏️ Renommer</b> ou <b>🗑 Supprimer</b> une catégorie, même Photo, Pièces ou
Accessoires. Ses tâches suivent ; supprimée, elles vont dans <b>« Autres »</b>, qui ne peut être ni supprimée ni renommée. Le nombre de
tâches de chaque catégorie est indiqué.</li>
<li>En enregistrant une fiche modifiée, Briquothèque demande si ses tâches sont faites — seulement celles qui existaient avant :
jamais celle qui vient d'être ajoutée.</li></ol>"""),
        ("taches", "📝 À faire", ""),
        ("a-construire", "🚧 À construire", """
<h3>🚧 À construire</h3><p>Les sets cochés « À construire » dans leur fiche. Ils restent aussi dans leur liste ; décocher la case une fois montés.</p>"""),
    ]},
    # ------------------------------------------------------------------ 12
    {"title": "Partager", "intro": "", "blocks": [
        ("partage", "Partager une fiche", """
<h3>Partager une fiche</h3>
<ol><li>Dans la fiche, toucher <b>🔗</b>, puis <b>🔗 Créer le lien</b>.</li><li>Le lien est copié, prêt à envoyer. La personne voit cette fiche seule, en lecture
(photos, figurines, pièces, prix d'achat), sans mot de passe. Les notes et tâches ne sont jamais montrées.</li>
<li><b>Arrêter le partage</b> : depuis la fiche, ou le menu → <b>🔗 Fiches partagées</b>.</li></ol>
<p>La fiche partagée montre les figurines comme la fiche : les <b>originales</b> du set (chacune une seule fois), les <b>modifiées</b> (figurines du set dont des pièces ont changé,
avec le nom et la photo qui leur ont été donnés), puis les <b>ajoutées</b>. Même classement sur la page publique de la collection. En bas : <b>LEGO.com</b> (page du produit si elle est connue, sinon la recherche
tant que le set est vendu) et BrickLink. Pour un set <b>encore en vente</b>, le bouton porte son prix public : « LEGO.com · 27,99 € »
(sur les fiches partagées et sur les pages publiques).</p>
<p>Les étiquettes d'état de la fiche partagée sont celles de la fiche (<b>Modifié</b>, Amélioré, Set partiel, MOC). Pas d'étiquette « Occasion ».</p>
<p><b>Aperçu du lien</b> : collé dans une messagerie (WhatsApp, SMS, e-mail…), un lien de partage affiche le <b>nom de la fiche</b>
(« AT-AT — Briquothèque »). Une messagerie peut garder quelque temps l'ancien aperçu d'un lien déjà envoyé.</p>
<p><b>Prix sur un lien de partage</b> : dans la fenêtre <b>🔗 Partager</b> (ou dans le menu → <b>🔗 Fiches partagées</b>), la case
<b>💶 Afficher les prix sur ce lien</b> montre ou masque la valeur, le prix d'achat et les cotes. C'est immédiat et le lien reste le même :
inutile d'en refaire un.</p>
<p>La barre au-dessus des vignettes : <b>↺</b>, la recherche, <b>Filtres (l'entonnoir)</b>, <b>Tri</b> (barres en escalier) et le bouton qui <b>inverse l'ordre</b> (deux flèches opposées ; en tri Aléatoire, il <b>remélange</b>), puis le <b>calendrier</b> : la période de comparaison des prix (sur téléphone et tablette, tout tient sur une ligne,
les boutons en carrés de même taille). Elle reste en haut de l'écran pendant le défilement, et la recherche est surlignée tant que quelque chose y est écrit.
« Filtres » et « Tri » sont deux menus <b>identiques</b> : un appui ouvre la même fenêtre, avec une ligne par choix. Dans « Filtres » on coche
autant d'étiquettes qu'on veut (la fenêtre reste ouverte) ; dans « Tri » on choisit un seul tri (la fenêtre se referme, et sur ordinateur le tri
en cours est rappelé sur le bouton). Un clic ailleurs ou la touche Échap referme le menu. C'est pareil sur les pages publiques.</p>
<p>Les tris de la collection : <b>Dernière modification</b>, <b>Aléatoire</b>, <b>Valeur</b>, <b>Variation de prix (%)</b> (les plus grosses variations en % d'abord, hausses comme baisses), <b>Variation de prix (€)</b> (le plus gros écart en euros d'abord), <b>Écart de prix (%)</b> (de la plus forte hausse à la plus forte baisse), <b>Écart de prix (€)</b> (idem, en euros), <b>Nombre de pièces</b> et <b>Nombre de figurines</b>. Avec un tri en euros, l'écart s'affiche en € à côté de la flèche. Sous la barre, une ligne rappelle toujours le tri en cours et son sens : ↘ décroissant, ↗ croissant (« Valeur ↘ ») ; avec un tri de variation ou d'écart, elle donne aussi la date de référence (« par rapport au … ») ; le bouton <b>calendrier</b> de la barre change la période (1, 7, 15, 30, 90, 180 ou 365 jours, glissants ; aussi dans Réglages › Estimations).
En tête du menu « Tri » : <b>Définir par défaut</b> fait du tri en cours le tri d'office (<b>↺</b> y revient), ; le bouton à côté du menu inverse l'ordre du tri en cours (les plus fortes baisses d'abord, du moins cher au plus cher…), retenu liste par liste — avec le tri Aléatoire, il remélange. Les « Pièces à commander » gardent leurs tris (ajout, nom, numéro, nombre).</p>
<p><b>Inventaire</b> : son résumé donne une information par ligne (pièces, OK, à commander avec leur prix, commandées, à vérifier, exclues).
La ligne <b>❔ à vérifier</b> donne aussi ce que coûteraient les pièces pas encore triées s'il fallait toutes les commander, et
<b>Total 🛒 + ❔</b> additionne les pièces à commander et celles qui restent à vérifier (le chiffrage se complète en quelques instants,
référence par référence).</p>
<p>Dans un inventaire, un appui sur le nom d'une pièce ouvre sa fiche <b>dans la couleur affichée</b> : si une règle (ou le choix) remplace sa couleur,
c'est la couleur de remplacement qui est cherchée (prix, sets où elle apparaît) ; de même pour une pièce de remplacement.</p>
<p><b>Couleurs demandées</b> : dans un inventaire, dès qu'une pièce change de couleur (règle « Remplacer une couleur », choix à la main, pièce de
remplacement), l'appli vérifie qu'elle <b>existe vraiment</b> dans cette couleur. Sinon la ligne porte <b>⚠ n'existe pas en …</b> (avec, si possible, une pièce
de même forme à mettre à la place), le résumé compte ces références, et la pièce <b>ne peut pas passer « à commander »</b> tant qu'elle n'est pas corrigée (🎨 ou 🔁).</p>
<p><b>Recherche et filtres</b> : si une recherche ne trouve rien parce que des filtres sont cochés (Filtres (l'entonnoir)), ce qu'elle trouve sans eux
s'affiche juste en dessous, sous le titre <b>Résultats sans filtres</b> — comme « Ailleurs » pour les autres listes. Pareil sur les pages publiques.</p>"""),
        ("partagees", "🔗 Fiches partagées", ""),
        ("page-publique", "La page publique /collection", """
<h3>Les pages publiques</h3>
<ul><li>Chaque page publique ne montre <b>que son contenu</b>, avec des boutons vers les autres pages, toujours au même endroit : au bout de la rangée des listes, sous le titre.</li>
<li>Elle s'affiche <b>comme l'application</b>, sans le menu latéral et sans rien de modifiable : mêmes boutons en haut (Tout, Sets, Figurines, Pièces), mêmes tuiles,
même barre (↺, recherche, <b>Filtres (l'entonnoir)</b> : Complet, Amélioré, Modifié, Set partiel, MOC ; même tri), mêmes cartes (étiquettes, figurines des sets en cartes « Dans un set »)
et même fiche (photo, figurines en vignettes, apparences, accessoires, pièces). Les listes remplacent le menu : une rangée sous le titre ; les sous-listes, dans la barre du haut. En défilant, les listes principales restent à portée dans la barre collée en haut, et dans une liste un bouton discret <b>↩ Toute la collection</b> y ramène. Sur téléphone, en descendant, cette barre ne montre que la liste en cours ; en remontant, tout revient (pareil dans l'application).
Aucun prix tant que l'option <b>Afficher les prix sur la collection publique</b> (Réglages › 🌐 Pages publiques) n'est pas cochée.</li>
<li><b>Page publique seulement</b> : dans une fiche, les figurines restent en vignettes regroupées (ex. « ×3 ») ; un appui sur une vignette les ouvre
<b>en grand, chaque figurine une par une</b> (les 3 Dark Troopers côte à côte), avec une apparition en cascade. Un appui n'importe où referme.</li>
<li><b>/collection</b> : les listes de collection seules (sans prix d'achat, ni notes, ni tâches), sets et figurines affichés ; lien « Liste de souhaits de … ».</li>
<li><b>/wishlist</b> : la liste de souhaits seule ; lien « Collection de … ». <b>/a-surveiller</b> : ce qui est surveillé.
<b>/nouveautes</b> : les nouveautés LEGO, avec des liens vers la collection et la liste de souhaits.</li>
<li>Le menu (en bas) copie chaque lien d'un appui. Le nombre de visites de chaque page publique est dans la page <b>📊 Statistiques</b> (section « 👁 Visites ») ; les vôtres, connecté, ne comptent pas.</li></ul>"""),
        ("page-publique-souhaits", "La page /wishlist", ""),
    ]},
    # ------------------------------------------------------------------ 13
    {"title": "Réglages", "intro": "<p>Menu → <b>⚙️ Réglages</b> : une page entière (application privée seulement). Sur ordinateur, le sommaire est à gauche et les sections sur deux colonnes ; sur téléphone, les raccourcis sont en haut, sur plusieurs lignes. La section choisie est surlignée. <b>Une seule règle</b> : chaque réglage s'enregistre dès qu'il est changé (un « ✔ » le confirme) ; seules les clés Rebrickable et BrickLink demandent <b>Vérifier et enregistrer</b> (elles sont testées). Les autres boutons lancent une action (actualiser, chiffrer, changer le mot de passe…). Ordre des sections : 🎨 Apparence · 💶 Prix · 🧮 Estimations · 🌐 Pages publiques · 🔑 Rebrickable · 🧱 BrickLink · 🔒 Sécurité · 📚 Aide et documentation · 🛠 Back office.</p>", "blocks": [
        (None, "", """
<ul><li><b>💶 Prix</b> : la passe BrickLink de la nuit (dès 3 h, les plus anciens d'abord, 2 000 appels au plus) ; <b>↻ Actualiser les prix</b> relit tout de suite
les sets, les figurines et les éléments estimés par leurs pièces (prix de plus de 24 h) ; <b>🧱 Chiffrer les pièces</b>.</li>
<li><b>🎨 Apparence</b> : le <b>style de l'application</b> — ✨ Moderne (d'office), 🧱 Classique, 🫧 Verre, 🟥 Brique, ◻️ Minimal, 🌃 Néon, 💥 BD, 🍬 Pastel, 📐 Technique ou 🌙 Nuit : l'aspect de tous les boutons et étiquettes, partout, pages publiques comprises (changement immédiat, aperçu en mini fiche) ; et la couleur de l'application.</li>
<li><b>🧮 Estimations</b> : la plus-value d'un set d'occasion <b>avec sa boîte</b> (%), la décote d'un exemplaire <b>modifié</b> (%), la plus-value du <b>livret de plans</b>.</li>
<li><b>🧱 BrickLink</b> : les 4 codes de l'API officielle de BrickLink (prix des ventes réelles), et le nombre d'appels du jour. Si BrickLink refuse (adresse IP changée), un message prévient.</li>
<li><b>🔑 Rebrickable</b> : la clé du catalogue (pièces, inventaires). Les clés restent sur le serveur et ne sont jamais réaffichées.</li>
<li><b>💬 Réseaux sociaux</b> (dans 🌐 Pages publiques) : le compte Instagram (champ libre) ; s'il est rempli, son logo, son nom et son lien s'affichent sur les pages publiques (pas dans l'application).</li>
<li><b>🌐 Public</b> : le nom affiché sur les pages publiques (« Collection de … »), ouvrir ou copier chaque page publique ; option <b>Afficher les prix sur la collection publique</b> (désactivée par défaut) ; pour partager une page publique : le petit <b>📤</b> à côté du compteur de visites (👁), en haut de sa page dans l'appli (Toute la collection, liste de souhaits, À surveiller, Nouveautés).</li>
<li><b>🔒 Sécurité</b> : <b>changer le mot de passe</b> ; les adresses bannies après trop d'échecs (débannir).</li>
<li><b>❓ Aide</b> : ce guide (adresse <code>/guide-utilisateur</code>), une page par chapitre, avec une recherche. Pour l'imprimer ou en faire un PDF : imprimer la page, tout le guide suit. Le bouton <b>🤖 Condensé pour IA</b> donne tout le guide en un texte : le coller dans une IA, puis lui demander « comment faire pour… ».</li>
<li><b>🛠 Back office</b> : « Ouvrir le back office » mène à l'atelier de la Briquothèque (adresse <code>/backoffice</code>), et sa notice (<code>/backoffice/guide</code>).</li></ul>
<h3>Le back office, en deux mots</h3>
<p>Le back office sert à <b>tout modifier sans code</b> : apparence, textes, fiches, étiquettes, boutons (icônes et images), pages perso,
ordre des sections de cette page Réglages, comportements, sauvegardes, mots de passe… Il a <b>son propre mot de passe</b> (créé à la première visite),
se manie avec prudence et de préférence sur un ordinateur. Il a sa notice à lui, avec exemples et captures : <b>Réglages → 🛠 Back office → Notice</b>,
ou le bouton « ❓ Notice » en haut du back office.</p>"""),
    ]},
    # ------------------------------------------------------------------ 14
    {"title": "Fiches de démo et démonstration publique", "intro": "", "blocks": [
        (None, "", """
<p><b>Fiches de démo</b> : la liste « Exemples » livrée avec Briquothèque montre une fiche de chaque type (set complet, set avec pièces ajoutées,
set avec figurine modifiée, set avec figurines ajoutées, set partiel, MOC, figurine MOC, figurine, figurine modifiée) et un inventaire.
Un bandeau jaune « Fiche de démo » les signale : ce sont de vraies fiches, à modifier ou supprimer librement.</p>
<p><b>Démonstration publique</b> (facultative, désactivée par défaut) : l'administrateur du serveur peut ouvrir une démo en ligne, <b>/demo</b>
(variable <code>BQ_DEMO_SITE=1</code>), remise à zéro toutes les 12 h. Elle ne touche jamais la vraie collection et n'est pas accessible
quand on est connecté : pour la montrer, ouvrir le lien dans une fenêtre de navigation privée.</p>"""),
    ]},
]

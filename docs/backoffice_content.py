# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Contenu de la NOTICE DU BACK OFFICE de Briquothèque (lu par build_docs.py).

Chaque chapitre : identifiant (ancre), titre, introduction, puis des blocs (capture d'écran, légende, texte HTML).
Les captures (docs/captures/bo-*.jpg) sont prises par captures_bo.js sur une instance temporaire, avec les données d'exemple.
Dans les textes : [[go:rubrique]] devient un lien « Ouvrir cette rubrique » (version en ligne) ou son chemin (PDF).
À tenir à jour à chaque évolution du back office.
"""

NOTICE = [
    # ------------------------------------------------------------------ 1
    {"id": "debut", "title": "Avant de commencer", "intro": """
<p>Le <b>back office</b> est l'atelier de la Briquothèque : on y change son apparence, ses textes, ses fiches, ses étiquettes, on y crée
des pages, on y fait les sauvegardes, on y corrige une donnée — <b>sans écrire de code et sans ligne de commande</b>.</p>
<p class="tip"><b>⚠️ Ce sont les entrailles de l'application.</b> Ce qui se règle ici change réellement le site. Rien de grave ne peut arriver
si vous suivez trois habitudes : regarder l'<b>aperçu</b> avant de publier, faire une <b>sauvegarde</b> avant un gros changement,
et vous souvenir de <code>?bo=off</code> (voir <a href="#secours">En cas de problème</a>).</p>""", "blocks": [
        ("bo-premiere-visite", "Première visite : création du mot de passe du back office", """
<h3>Y entrer</h3>
<ol><li>Dans la Briquothèque : <b>⚙️ Réglages → 🛠 Back office → Ouvrir le back office</b>. Ou tapez directement l'adresse de votre site suivie de
<code>/backoffice</code>.</li>
<li><b>La première fois</b>, le back office vous demande de créer <b>son mot de passe</b> (10 caractères au moins). Il faut être connecté à la
Briquothèque ce jour-là. Deux choix : un mot de passe <b>à part</b>, ou <b>le même</b> que celui de la Briquothèque (on vous le redemande pour confirmer).</li>
<li>Cochez « J'ai lu et compris », puis <b>Créer le mot de passe et entrer</b>.</li></ol>
<p class="tip"><b>🔑 Ne perdez surtout pas ce mot de passe.</b> Il ne peut pas être retrouvé depuis l'application. S'il est perdu, il faut supprimer
le fichier <code>data/backoffice_auth.json</code> sur le serveur (il faut donc un accès aux fichiers du serveur), puis rouvrir
<code>/backoffice</code> pour en créer un nouveau. Notez-le dans un endroit sûr.</p>"""),
        ("bo-connexion", "Les fois suivantes : la porte du back office", """
<h3>Se connecter, se déconnecter</h3>
<ul><li>Les fois suivantes, seul le mot de passe du back office est demandé. « <b>Rester connecté sur cet ordinateur</b> » garde la session 30 jours
(sinon 12 heures).</li>
<li>Ce mot de passe <b>ouvre aussi la Briquothèque</b> : c'est la clé maîtresse. Il permet même de changer le mot de passe de la Briquothèque
s'il a été oublié (<a href="#securite">Mots de passe et sécurité</a>).</li>
<li>Après <b>10 essais ratés</b>, l'adresse est bloquée 15 minutes (et bannie 4 heures si elle vient d'Internet).</li>
<li>Pour sortir : bouton <b>⎋ Quitter</b>, en haut à droite.</li></ul>
<h3>Ordinateur conseillé</h3>
<p>Le back office est pensé pour un <b>ordinateur</b> : grand écran et souris. Sur tablette ou téléphone, il s'ouvre mais vous prévient :
« cliquer pour modifier » et « déplacer à la souris » y sont peu pratiques, et les panneaux sont à l'étroit.</p>"""),
    ]},
    # ------------------------------------------------------------------ 2
    {"id": "accueil", "title": "L'écran du back office", "intro": """
<p>Trois colonnes : à gauche les <b>rubriques</b>, au milieu les <b>réglages</b> de la rubrique ouverte, à droite l'<b>aperçu</b> du site.</p>""", "blocks": [
        ("bo-accueil", "L'accueil : toutes les rubriques, classées", """
<h3>Brouillon, puis « Publier »</h3>
<ol><li><b>Vous modifiez</b> dans une rubrique. L'aperçu à droite montre le résultat tout de suite.</li>
<li>C'est un <b>brouillon</b> : vous seul le voyez. Il est enregistré automatiquement (« brouillon enregistré », en haut).</li>
<li><b>✔ Publier sur le site</b> l'applique pour de bon. Un petit mot vous est proposé pour vous y retrouver plus tard dans l'historique.</li></ol>
<p><b>↶ Annuler / ↷ Rétablir</b> (ou Ctrl + Z / Ctrl + Y) reviennent en arrière pas à pas. <b>Abandonner le brouillon</b> jette tout ce qui n'est pas publié.</p>
<h3>L'aperçu</h3>
<ul><li>La liste déroulante choisit la page montrée : le site connecté, les pages publiques, la page de connexion.</li>
<li><b>👆 Utiliser le site</b> : l'aperçu se comporte comme le site (pour aller à l'endroit à modifier).
<b>🖱️ Cliquer pour modifier</b> : un clic sélectionne un élément. <b>✋ Déplacer</b> : on attrape un élément et on le pose ailleurs.</li>
<li>🖥️ ▭ 📱 : largeur d'ordinateur, de tablette, de téléphone. <b>− 100 % +</b> : zoom de l'aperçu (gardé sur l'appareil). « Montrer ce qui est masqué » laisse voir en transparence ce que vous avez caché.</li>
<li>L'aperçu s'ouvre toujours sur l'<b>accueil</b> (pas sur la dernière fiche ouverte dans l'appli).</li></ul>
<h3>Fonctions avancées</h3>
<p>L'interrupteur <b>Fonctions avancées</b> (en haut) montre les rubriques pour aller plus loin : calculs, règles « si… alors », tuiles, vues,
corrections du catalogue, tableur, fichiers de données, paramètres du serveur, code.</p>
<p class="tip"><b>Deux sortes de rubriques.</b> Celles qui <b>personnalisent</b> (apparence, textes, étiquettes, pages…) passent par le brouillon et
« Publier ». Les <b>outils du serveur</b> (sauvegardes, images, mots de passe, fichiers, paramètres, code) agissent <b>tout de suite</b>.</p>"""),
        ("bo-publier", "Publier : un mot pour s'y retrouver", """
<h3>Publier</h3>
<p>« ✔ Publier sur le site » demande un mot facultatif (« nouvelles couleurs », « page à vendre »…). Chaque publication est gardée dans
<a href="#historique">Historique et secours</a> : vous pouvez reprendre n'importe laquelle.</p>"""),
    ]},
    # ------------------------------------------------------------------ 3
    {"id": "souris", "title": "Modifier à la souris", "intro": """
<p>La façon la plus directe : <b>cliquer sur ce qu'on veut changer</b>. Tout élément du site — un bouton, un titre, une image, une ligne des
Réglages, une carte — se sélectionne et se règle. [[go:souris]]</p>""", "blocks": [
        ("bo-souris", "Un élément choisi (ici le bouton « + Nouveau ») et ses réglages", """
<h3>Choisir un élément</h3>
<ol><li>Ouvrez <b>Modifier à la souris</b> : l'aperçu passe en « 🖱️ Cliquer pour modifier ».</li>
<li><b>Cliquez l'élément</b> dans l'aperçu : il s'entoure d'orange. Le bouton « ⬆ Sélectionner ce qui l'entoure » remonte d'un cran (la zone qui le contient).</li>
<li>Besoin d'aller ailleurs (ouvrir une fiche, le menu, la page Réglages) ? Repassez sur « 👆 Utiliser le site », allez-y, puis revenez sur
« 🖱️ Cliquer pour modifier ».</li></ol>
<h3>Ce qu'on peut faire d'un élément</h3>
<ul><li><b>À quoi appliquer</b> : seulement cet élément, ou <b>tous ceux du même genre</b> (toutes les cartes, tous les boutons de ce type) ; sur cette page, ou sur toutes.</li>
<li><b>Texte</b> : le renommer (texte affiché, texte grisé d'un champ, info-bulle).</li>
<li><b>Masquer</b> l'élément.</li>
<li><b>Position</b> : le mettre en premier ou en dernier parmi ses voisins.</li>
<li><b>Style</b> : couleurs, taille du texte, gras, alignement, coins arrondis, bordure, espaces, largeur, hauteur, opacité.</li>
<li><b>Ajouter quelque chose à côté</b> : un texte, un titre, un bouton-lien, une image, un trait.</li>
<li><b>↺ Remettre cet élément comme à l'origine</b> annule tout pour lui.</li></ul>"""),
        ("bo-souris-icone", "Icône ou image d'un bouton, lien, action au clic, décalage", """
<h3>Icône ou image</h3>
<p>Pour <b>changer l'apparence d'un bouton</b> (ou de n'importe quel élément) :</p>
<ul><li><b>Une icône</b> : un émoji ou un petit texte, placé avant le texte, après, ou <b>à la place</b> du texte (avec sa taille).</li>
<li><b>Une image</b> : « 🖼️ Choisir… » ouvre vos images (ou en envoie une). Elle se place avant ou après le texte, <b>à la place</b> du texte
(un bouton-image), ou <b>en fond</b> de l'élément. Réglez sa largeur et sa hauteur.</li></ul>
<h3>Lien et action au clic</h3>
<ul><li>Pour un <b>lien</b> : changer son adresse, l'ouvrir dans un nouvel onglet.</li>
<li><b>Quand on clique dessus</b> : comme à l'origine · ne rien faire · demander une confirmation · ouvrir une adresse · une liste ·
« Toute la collection » · une vue · une page créée · une fiche · « + Nouveau » · la recherche · les Réglages · remonter · revenir en arrière.</li></ul>
<p class="tip"><b>Exemple.</b> Vous voulez que le logo ouvre votre tableau de bord : cliquez le logo → « Quand on clique dessus » →
« Ouvrir une page créée » → « Tableau de bord ». Si un jour vous supprimez cette page, le logo reprend simplement son comportement d'origine.</p>
<h3>Décalage, échelle, rotation</h3>
<p>Pour un réglage fin : décaler de quelques pixels, agrandir ou réduire (en %), incliner (en degrés).</p>"""),
        ("bo-deplacer", "Le mode « ✋ Déplacer »", """
<h3>Tout replacer à la souris</h3>
<ol><li>Au-dessus de l'aperçu, choisissez <b>✋ Déplacer</b>.</li>
<li><b>Attrapez</b> un élément (cliquez, gardez appuyé), <b>glissez</b> : une barre verte montre où il se posera (avant ou après l'élément survolé).</li>
<li><b>Lâchez</b>. Échap annule. Chaque déplacement est listé dans la rubrique, avec un bouton pour le défaire.</li></ol>
<p>Un bloc de fiche déplacé change l'ordre de la fiche ; une entrée du menu déplacée change l'ordre du menu : c'est la même chose que les rubriques
<a href="#fiches">Fiches</a> et <a href="#menu">Menu</a>, à la souris.</p>"""),
        ("", "", """
<h3>Le clic droit : tous les outils d'un élément</h3>
<p>Dans l'aperçu, <b>cliquez du bouton droit</b> sur n'importe quel élément, quel que soit le mode (« Utiliser le site », « Cliquer pour modifier », « Déplacer ») :
un menu s'ouvre, avec le nom de l'élément en titre.</p>
<ul><li><b>✏️ Modifier</b> : ouvre ses réglages (texte, style, lien, action…), comme si vous l'aviez cliqué en mode « Cliquer pour modifier ».</li>
<li><b>👁 Masquer</b> : il disparaît du site (la case « Montrer ce qui est masqué », au-dessus de l'aperçu, le fait réapparaître en transparence).</li>
<li><b>🎨 Copier le style</b>, puis sur un autre élément <b>🖌️ Coller le style</b> : couleurs, taille et graisse du texte, arrondi, bordure, transparence.</li>
<li><b>🔤 Copier le texte</b> et <b>🧷 Copier le sélecteur</b> (son adresse CSS, pour la feuille de style libre ou le script libre).</li>
<li><b>✂️ Couper</b>, puis sur un autre élément <b>📌 Coller avant</b> ou <b>📌 Coller après</b> : il change de place (c'est le mode « Déplacer », sans glisser).</li>
<li><b>⬅️ Reculer d'un cran</b> / <b>➡️ Avancer d'un cran</b> : il passe avant son voisin de gauche, ou après celui de droite.</li>
<li><b>⤴️ Élément parent</b> : le même menu pour ce qui le contient (le bouton → sa barre → le bloc…).</li>
<li><b>↩️ Annuler ses modifications</b> : retire tout ce que vous avez changé sur cet élément (textes, style, ajouts, déplacement).</li></ul>
<p class="tip">Tout passe par le brouillon : ↶ Annuler défait la dernière action, et rien n'est visible sur le site avant « Publier ».
<b>Maj + clic droit</b> ouvre le menu habituel du navigateur.</p>"""),
    ]},
    # ------------------------------------------------------------------ 4
    {"id": "apparence", "title": "Apparence, boutons et tailles", "intro": "", "blocks": [
        ("bo-apparence", "Apparence : nom, logo, couleurs, arrondis, police", """
<h3>Apparence</h3>
<p>[[go:apparence]]</p>
<ul><li><b>Nom du site</b> et <b>logo</b> (un émoji, ou une image).</li>
<li><b>Couleurs</b>, pour le thème clair et le thème sombre : couleur principale, fond, panneaux, texte… Des palettes toutes prêtes (Bleu, Vert, Violet…) font le gros du travail.</li>
<li><b>Coins arrondis</b>, <b>police</b>, <b>taille générale</b> du site.</li></ul>
<p class="tip"><b>Exemple : passer le site en bleu.</b> Apparence → palette « Bleu » → regardez l'aperçu → Publier.</p>"""),
        ("bo-boutons", "Boutons et tailles", """
<h3 id="boutons">Boutons et tailles</h3>
<p>[[go:boutons]]</p>
<ul><li><b>Tous les boutons</b> d'un coup : coins arrondis, hauteur, largeur, taille et graisse du texte, bordure, MAJUSCULES, ombre.</li>
<li><b>Couleurs</b> des boutons ordinaires, des boutons principaux (« + Nouveau », « Enregistrer ») et des boutons de suppression.</li>
<li><b>Un bouton en particulier</b> (son icône, son image, son lien) : « 🖱️ Cliquer un bouton dans l'aperçu »
(voir <a href="#souris">Modifier à la souris</a>).</li>
<li><b>Tailles générales</b> : largeur du menu, largeur de la fenêtre d'une fiche, largeur maximale du contenu, espace entre les cartes, taille du titre.</li></ul>
<p>Une case vide = la valeur d'origine. « ↺ Boutons et tailles d'origine » remet tout.</p>"""),
    ]},
    # ------------------------------------------------------------------ 5
    {"id": "textes", "title": "Textes", "intro": "", "blocks": [
        ("bo-textes", "Remplacer un mot ou une phrase partout", """
<h3>Remplacer un texte</h3>
<p>[[go:textes]]</p>
<ol><li>« Choisir dans la page » liste les textes visibles dans l'aperçu ; ou tapez vous-même le texte à remplacer.</li>
<li>Indiquez par quoi le remplacer. Le remplacement vaut partout où ce texte apparaît (boutons, titres, messages).</li></ol>
<p class="tip"><b>Exemple.</b> Remplacer « Liste de souhaits » par « Mes envies » : une ligne suffit, le menu, les titres et les boutons suivent.</p>
<p>Pour renommer un seul élément précis, préférez <a href="#souris">Modifier à la souris</a>.</p>"""),
    ]},
    # ------------------------------------------------------------------ 6
    {"id": "etiquettes", "title": "Étiquettes et pastilles", "intro": """
<p>Les <b>étiquettes</b> sont les petits mots posés sous le nom d'une fiche (« Modifié », « MOC », « Set partiel »…) ; les <b>pastilles</b> sont
posées sur l'image (« Retiré », « Neuf », « ×2 »…). Vous pouvez modifier celles de l'application et créer les vôtres. [[go:etiquettes]]</p>""", "blocks": [
        ("bo-etiquettes", "Vos étiquettes : texte, icône, couleurs, condition", """
<h3>Créer une étiquette</h3>
<ol><li><b>+ Nouvelle étiquette</b> (ou un exemple prêt à adapter : « 💰 Plus de 100 € », « 🕰️ Avant 2000 », « 📦 Avec sa boîte »…).</li>
<li>Son <b>texte</b> (il peut reprendre une valeur de la fiche : <code>{annee}</code>, <code>{theme}</code>, un de vos champs…), son <b>icône</b>, son
<b>genre</b> (étiquette sous le nom, ou pastille sur l'image), ses <b>couleurs</b>.</li>
<li><b>Affichée si la fiche remplit…</b> : une ou plusieurs conditions (« Valeur estimée » « est plus grand que » « 100 »). Sans condition : toutes les fiches.
Le compteur indique combien de fiches la remplissent.</li>
<li><b>Sur quelles fiches</b> (sets, figurines, MOC…), <b>où</b> (cartes, haut de la fiche), et « <b>Proposer dans le menu ⚙️ Filtres</b> » pour
pouvoir ne montrer que ces fiches-là.</li></ol>
<p class="tip"><b>Exemple : une étiquette « À vendre ».</b> 1) Rubrique « Champs personnalisés » : créez une case à cocher « À vendre ».
2) Ici : nouvelle étiquette « 🏷️ À vendre », condition « À vendre » « est oui », cochez « Proposer dans ⚙️ Filtres ».
3) Publiez. Cochez la case sur les fiches concernées : l'étiquette apparaît, et le menu Filtres propose « À vendre ».</p>"""),
        ("bo-etiquettes-origine", "Une étiquette de l'application, renommée", """
<h3>Modifier une étiquette de l'application</h3>
<p>Chaque étiquette et chaque pastille d'origine a son bouton <b>Modifier</b> :</p>
<ul><li><b>Nouveau texte</b> et icône (pour celles qui comptent, écrivez <code>{n}</code> à la place du nombre : « {n} fig. en plus »).</li>
<li><b>Couleurs</b> : texte, fond, bordure.</li>
<li><b>Masquer complètement</b>.</li>
<li><b>L'afficher seulement si…</b> : une condition (par exemple ne montrer « Modifié » que sur les sets).</li></ul>
<p>Les pastilles de l'application sont masquées sur les cartes de la collection ; une case permet de les y montrer.</p>
<p>Les étiquettes que l'on pose <b>à la main</b> sur une fiche de l'application (« + Étiquette » : Complet, Amélioré, Modifié, Set partiel, MOC) sont les
mêmes que celles-ci : elles suivent les mêmes réglages (texte, couleurs, masquage). « Complet » n'existe que posée à la main : elle a sa ligne,
« Complet (étiquette posée à la main) ».</p>"""),
        ("bo-site-etiquettes", "Sur le site : « MOC » renommé en « 🎨 Création », étiquettes et calcul sur les cartes", """
<h3>Résultat sur le site</h3>
<p>Après publication, les étiquettes modifiées et les vôtres apparaissent sur les cartes et en haut des fiches. Le renommage, les couleurs et le
masquage valent aussi sur les pages publiques ; les conditions, elles, se lisent sur le site connecté.</p>"""),
    ]},
    # ------------------------------------------------------------------ 7
    {"id": "fiches", "title": "Fiches, champs, liens, cartes, menu", "intro": "", "blocks": [
        ("bo-fiches", "Le squelette d'une fiche : ordre et visibilité des blocs", """
<h3>Fiches</h3>
<p>[[go:fiches]] Pour chaque type de fiche (set, figurine, MOC, set partiel, figurine personnalisée, et leurs versions « liste de souhaits ») :</p>
<ul><li><b>l'ordre des blocs</b> : glissez la poignée ⠿, ou ▲ ▼ ;</li><li><b>masquer</b> un bloc dont vous ne vous servez pas ;</li>
<li><b>renommer</b> le titre d'un bloc.</li></ul>
<p>L'aperçu ouvre une fiche d'exemple du type choisi : chaque changement s'y voit aussitôt.</p>"""),
        ("bo-champs", "Vos propres champs sur les fiches", """
<h3 id="champs">Champs personnalisés</h3>
<p>[[go:champs]] Ajoutez vos informations aux fiches : texte court ou long, nombre, montant, date, case à cocher, liste de choix, étoiles, lien, fiche liée, liste liée.</p>
<ol><li><b>+ Nouveau champ</b> : son nom, son type, sur quelles fiches.</li>
<li>Rangez-le dans un <b>bloc</b> (par défaut « Informations personnelles », que vous pouvez renommer ou multiplier).</li>
<li>Cochez « sur les cartes » pour le montrer aussi dans les listes.</li></ol>
<p>Un champ devient une <b>variable</b> : utilisable dans les étiquettes, les calculs, les règles, les filtres, les pages.</p>"""),
        ("bo-liens", "Des boutons vers d'autres sites, sur chaque fiche", """
<h3 id="liens">Liens automatiques</h3>
<p>[[go:liens]] Un bouton ajouté en bas des fiches, vers le site de votre choix. Dans l'adresse, <code>{numero}</code>, <code>{nom}</code>,
<code>{annee}</code>, <code>{theme}</code> (ou un de vos champs) sont remplacés par ceux de la fiche.</p>
<p class="tip"><b>Exemple.</b> Nom : « BrickLink » — adresse : <code>https://www.bricklink.com/v2/search.page?q={numero}</code>. Des modèles tout prêts sont proposés.</p>"""),
        ("bo-cartes", "Les cartes des listes", """
<h3 id="cartes">Cartes des listes</h3>
<p>[[go:cartes]] Taille minimale des cartes, format de l'image, nombre de lignes du nom, parties affichées (numéro, quantité, thème, valeur…).</p>"""),
        ("bo-menu", "Le menu latéral", """
<h3 id="menu">Menu</h3>
<p>[[go:menu]] L'ordre des entrées (glisser ⠿), les entrées masquées, <b>chaque entrée renommée ou masquée une à une</b> (« Chaque entrée du menu » : Nouveautés, Calendrier des sorties, Réglages…), des <b>traits de séparation</b> en plus (« + Ajouter un trait de séparation »), et vos <b>raccourcis</b> : vers une adresse, une liste, une fiche, une vue.
Les pages que vous créez et vos vues enregistrées y apparaissent aussi, et s'ordonnent ici.</p>"""),
    ]},
    # ------------------------------------------------------------------ 8
    {"id": "pages", "title": "Pages", "intro": """
<p>Une idée nouvelle ? <b>Créez une page.</b> Un tableau de bord, la liste des sets à vendre, vos notes, une page publique à partager…
Une page se compose de <b>blocs</b> empilés. [[go:pages]]</p>""", "blocks": [
        ("bo-pages", "Vos pages, et trois modèles pour démarrer", """
<h3>Créer une page</h3>
<ol><li><b>📄 Page vide</b>, <b>📊 Tableau de bord</b> (totaux, fiches les plus chères, derniers ajouts) ou <b>📝 Page de notes</b>.</li>
<li>Donnez-lui un <b>titre</b> et une <b>icône</b>. Elle apparaît dans le <b>menu latéral</b> (décochez « Dans le menu latéral » pour une page
ouverte seulement par un bouton ou un raccourci clavier).</li></ol>"""),
        ("bo-page-edition", "L'éditeur d'une page : ses blocs, et le résultat en direct", """
<h3>Les blocs</h3>
<table><tr><th>Bloc</th><th>Ce qu'il montre</th></tr>
<tr><td>🔠 Titre</td><td>Un titre (grand, moyen, petit).</td></tr>
<tr><td>📝 Texte</td><td>Un texte : <code>**gras**</code>, <code>*italique*</code>, <code>[texte du lien](https://…)</code>, lignes commençant par <code>- </code> pour une liste.</td></tr>
<tr><td>💡 Encadré coloré</td><td>Une information mise en avant, de la couleur de votre choix.</td></tr>
<tr><td>🖼️ Image</td><td>Une de vos images, avec largeur, légende et lien facultatifs.</td></tr>
<tr><td>🔘 Bouton</td><td>Un bouton qui ouvre une adresse, une liste, une vue, une page, une fiche…</td></tr>
<tr><td>🧱 Liste de fiches</td><td>Des fiches choisies par une <b>condition</b>, triées, en nombre limité. Un clic ouvre la fiche.</td></tr>
<tr><td>🔢 Total (tuile)</td><td>Un nombre de fiches, une somme, une moyenne, un minimum, un maximum.</td></tr>
<tr><td>📋 Tableau</td><td>Un tableau de fiches, colonnes au choix (vos champs et calculs compris).</td></tr>
<tr><td>➖ Trait · ↕️ Espace</td><td>Pour aérer.</td></tr>
<tr><td>🧩 HTML libre</td><td>Pour qui connaît le HTML (scripts, formulaires et cadres en sont retirés par sécurité).</td></tr>
<tr><td>🪟 Page d'un autre site</td><td>Un cadre qui montre une autre page web.</td></tr></table>
<p>Chaque bloc prend <b>toute la largeur, la moitié ou un tiers</b> : trois tuiles « un tiers » se rangent côte à côte. « Copier » duplique un bloc,
⠿ et ▲ ▼ changent l'ordre.</p>
<p class="tip"><b>Exemple : une page « À vendre ».</b> Page vide → bloc « Encadré coloré » (« Sets que je vends, contactez-moi ») → bloc « Liste de fiches »,
condition « À vendre » « est oui », triées par « Valeur estimée ». Ajoutez un bloc « Total » : somme de <code>{valeur}</code>, même condition.</p>"""),
        ("bo-site-page", "La page, dans le site", """
<h3>Page publique</h3>
<p>Cochez « <b>Publique</b> » : la page reçoit une adresse <code>/p/son-adresse</code>, visible <b>sans connexion</b>, à donner à qui vous voulez.
Les visiteurs n'y voient que les blocs <b>sans données</b> (titres, textes, encadrés, images, boutons vers une adresse, HTML, cadres) —
jamais vos fiches, vos totaux ni vos prix.</p>"""),
    ]},
    # ------------------------------------------------------------------ 9
    {"id": "reglages", "title": "Page « Réglages » de l'appli", "intro": "", "blocks": [
        ("bo-reglages", "Les sections de la page Réglages : ordre, titres, visibilité", """
<h3>Réorganiser la page Réglages</h3>
<p>[[go:reglages]]</p>
<ol><li><b>⚙️ Ouvrir la page Réglages dans l'aperçu</b> pour voir le résultat en direct.</li>
<li>Glissez les sections (⠿ ou ▲ ▼) pour changer leur <b>ordre</b> ; tapez un nouveau <b>titre</b> ; décochez « visible » pour <b>masquer</b> une section.</li>
<li>Pour une <b>option précise</b> (une ligne, un bouton, un texte de la page Réglages) : « 🖱️ Cliquer pour modifier », puis cliquez-la dans l'aperçu.
Vous pouvez aussi y <b>ajouter</b> un texte, un lien ou une image (« Ajouter quelque chose à côté »).</li></ol>
<p>Une section masquée garde ses réglages. Le back office reste toujours accessible par <code>/backoffice</code>, même si vous masquez sa section.</p>"""),
        ("bo-site-reglages", "Dans la Briquothèque : la section « 🛠 Back office » des Réglages", """
<h3>Le lien vers le back office</h3>
<p>La page Réglages de la Briquothèque a une section « 🛠 Back office » : « Ouvrir le back office » et cette notice en PDF.</p>"""),
    ]},
    # ------------------------------------------------------------------ 10
    {"id": "comportements", "title": "Comportements", "intro": "", "blocks": [
        ("bo-comportements", "Ce que fait le site : départ, tri, raccourcis, clics", """
<h3>Régler les comportements</h3>
<p>[[go:comportements]]</p>
<ul><li><b>À l'ouverture du site</b> : par quoi commencer (toute la collection, une liste, une vue, une de vos pages) ; ce qui est montré (tout, les sets, les figurines).</li>
<li><b>Tri par défaut</b> : pour « Toute la collection », pour une liste, pour une liste de souhaits. (Votre choix du moment, liste par liste, reste prioritaire.)</li>
<li><b>Raccourcis clavier</b> : une touche (avec Ctrl ou Alt si vous voulez) → une action : nouvelle fiche, ouvrir une page, une liste, la recherche…</li>
<li><b>Clics et liens modifiés</b> : la liste de tout ce que vous avez changé avec « Lien et action au clic », avec un bouton pour le retirer.</li>
<li><b>Figurines identiques</b> : regrouper ou non, proposer ou non « est-ce celle de ce set ? » (voir ci-dessous).</li>
<li><b>Prix et variations</b> : ne pas afficher les flèches ↑ ↓ ~ à côté des prix ; masquer le bouton « 🔍 Comprendre les variations » des statistiques ;
<b>apparence des flèches</b> — affichées d'office ou non dans la vue générale (le bouton 📈 de l'appli les montre ou les cache à la volée), « ~ » quand le prix
est stable, pourcentage, taille (curseur). Les seuils de hausse et de baisse se règlent dans l'application (Réglages → 🧮 Estimations). L'aperçu suit en direct ; « Publier » les applique ; « ↺ Revenir aux valeurs
enregistrées » retire vos changements.</li>
<li><b>Fiches et pièces</b> : ouvrir les fiches directement en modification (sans la clé 🔧) ; toucher une pièce l'agrandit au lieu d'ouvrir sa fiche.</li>
<li><b>Pages publiques</b> : ne pas garder les listes dans la barre collée en haut.</li>
<li><b>Divers</b> : le titre de l'onglet du navigateur ; réduire les animations.</li>
<li><b>Avancé : script libre</b> (facultatif) : un morceau de JavaScript exécuté une fois au chargement de l'application — jamais sur les pages publiques.
S'il casse l'affichage : ajoutez <code>?bo=off</code> à l'adresse du site, puis videz la case.</li></ul>
<p class="tip"><b>Exemple.</b> Touche <code>n</code> → « Ajouter une fiche » ; touche <code>t</code> → « Ouvrir une page créée : Tableau de bord ».
Un raccourci n'agit jamais pendant que vous tapez dans une case.</p>"""),
        ("bo-comportements-figurines", "Figurines identiques : regrouper ou non, proposer ou non", """
<h3>Figurines identiques</h3>
<p>D'origine, une même figurine que vous avez <b>à la fois seule et dans un set</b> (ou dans plusieurs sets) n'a qu'<b>une carte</b>, marquée « ×N », et
qu'une fiche ; et quand vous ajoutez un set dont vous aviez déjà une figurine seule, l'application demande <b>« est-ce celle de ce set ? »</b>.
Deux cases règlent cela :</p>
<ul><li><b>Ne pas regrouper…</b> : chaque exemplaire retrouve sa carte (celle du set, celle achetée à part). L'aperçu le montre tout de suite ; les pages
publiques suivent après publication.</li>
<li><b>Ne pas demander « est-ce celle de ce set ? »</b> : le set ajouté garde sa propre figurine, la vôtre reste seule.</li></ul>
<p>La décote « modifié » se règle dans les Réglages de l'application (Estimations).</p>"""),
    ]},
    # ------------------------------------------------------------------ 11
    {"id": "images", "title": "Images", "intro": "", "blocks": [
        ("bo-images", "Votre bibliothèque d'images", """
<h3>Envoyer et réutiliser des images</h3>
<p>[[go:images]] Les images des boutons, des pages et des éléments ajoutés sont gardées sur le serveur.</p>
<ul><li><b>⬆ Envoyer des images…</b> : PNG, JPEG, WebP, GIF, SVG, ICO, AVIF — 4 Mo au plus (une photo plus lourde est réduite toute seule).</li>
<li>Chaque image a une <b>adresse</b> (<code>/bo-img/…</code>) : « Copier l'adresse », ou plus simple, le bouton « 🖼️ Choisir… » présent partout où une image est demandée.</li>
<li>La bibliothèque indique si une image est <b>utilisée</b> ; supprimez celles qui ne servent plus.</li></ul>
<p>Effet immédiat : pas besoin de publier pour envoyer ou supprimer une image.</p>"""),
    ]},
    # ------------------------------------------------------------------ 12
    {"id": "calculs", "title": "Avancé : calculs, règles, tuiles, vues", "intro": """
<p>Ces rubriques apparaissent quand l'interrupteur <b>Fonctions avancées</b> est allumé. Elles partagent le même petit langage de <b>formules</b>.</p>""", "blocks": [
        ("bo-calculs", "Un champ calculé par une formule, avec son résultat en direct", """
<h3>Calculs et variables</h3>
<p>[[go:calculs]] Un <b>calcul</b> est un champ dont la valeur vient d'une formule ; il s'affiche sur la fiche, et sur les cartes si vous le cochez.
Une <b>variable</b> est une valeur à vous (un taux, un seuil) réutilisable dans les formules.</p>
<table><tr><th>On écrit</th><th>Pour</th></tr>
<tr><td><code>{valeur}</code></td><td>une variable de la fiche, entre accolades (bouton « variable » pour la choisir dans la liste)</td></tr>
<tr><td><code>"Neuf"</code></td><td>un texte, entre guillemets</td></tr>
<tr><td><code>+ - * /</code> · <code>= &lt;&gt; &gt; &lt; &gt;= &lt;=</code></td><td>calculer · comparer</td></tr>
<tr><td><code>et</code> <code>ou</code> <code>non</code> · <code>&amp;</code></td><td>la logique · coller deux textes</td></tr>
<tr><td><code>si(condition ; alors ; sinon)</code></td><td>une fonction : ses valeurs se séparent par <code>;</code></td></tr></table>
<p class="tip"><b>Exemples.</b> Plus-value : <code>{valeur} - sivide({prix_achat} ; 0)</code> · Prix par pièce : <code>{valeur} / {pieces}</code> ·
Âge du set : <code>annee(aujourdhui()) - {annee}</code> · Mention : <code>si({valeur} &gt; 100 ; "précieux" ; "courant")</code>.</p>
<p>Parmi les variables d'une fiche : <code>{statut}</code> (Complet, Amélioré, Modifié, Set partiel, MOC — comme l'étiquette calculée),
<code>{etiquettes}</code> (celles posées à la main), <code>{exemplaires}</code> (le total d'une figurine, seule et dans vos sets), <code>{dans_un_set}</code>,
<code>{accessoires}</code> (valeur des accessoires chiffrés par leurs pièces). Exemple : une vue « Modifiés » = condition « État de la fiche » « = » « Modifié ».</p>
<p>Le résultat s'affiche en direct sous la formule, sur une fiche d'exemple ; une erreur est expliquée en français. L'aide-mémoire, en bas de la rubrique,
liste toutes les variables et toutes les fonctions.</p>"""),
        ("bo-regles", "Une règle : si la fiche vaut plus de 100 €, alors…", """
<h3 id="regles">Règles « si… alors »</h3>
<p>[[go:regles]] Si une fiche remplit une <b>condition</b>, alors : une étiquette, une pastille, une couleur de carte, un message en haut de la fiche,
un bloc de la fiche masqué. Plusieurs effets par règle.</p>"""),
        ("bo-tuiles", "Vos totaux, à côté de ceux de l'application", """
<h3 id="tuiles">Tuiles et totaux</h3>
<p>[[go:tuiles]] Une tuile de plus au-dessus des listes : nombre de fiches, somme, moyenne, minimum ou maximum d'une formule, avec une condition facultative
(« valeur moyenne », « nombre de sets de plus de 100 € »…).</p>"""),
        ("bo-vues", "Vues enregistrées, tris et filtres", """
<h3 id="vues">Vues, tris et filtres</h3>
<p>[[go:vues]]</p>
<ul><li>Une <b>vue</b> est une liste filtrée prête à ouvrir depuis le menu (« Précieux », « À construire cet hiver »…).</li>
<li>Un <b>tri</b> à vous s'ajoute au menu « ⇅ Tri » du site (marqué ★).</li>
<li>Un <b>filtre</b> à vous s'ajoute au menu « ⚙️ Filtres » (section « Mes filtres »).</li></ul>
<h3 id="tout">Tous les éléments : rien n'est verrouillé</h3>
<p>[[go:tout]] L'inventaire de <b>tout</b> ce que la page affichée dans l'aperçu contient : boutons, liens, entrées du menu, titres, étiquettes,
onglets, options des listes déroulantes, champs — y compris ce qu'on ne peut pas atteindre en cliquant (menus « Trier par » et « ⚙️ Filtres »
fermés, fenêtres, éléments déjà masqués). Une recherche et un tri par zone (barre du haut, menu latéral, fiche, fenêtres…) ; sur chaque ligne :</p>
<ul><li><b>✏️ Modifier</b> : l'éditeur complet de l'élément, comme au clic (texte, style, lien, action, icône, position) ;</li>
<li><b>🙈 Masquer</b> / <b>👁 Afficher</b> d'un appui.</li></ul>
<p>Ouvrez dans l'aperçu une fiche, les Réglages ou une autre page, puis « ⟳ Relire l'aperçu » pour en lister les éléments. Les noms, icônes,
colonnes, blocs et entrées n'ont plus de limite pratique (seule reste la taille d'un envoi : 16 Mo).</p>
<h3 id="origine">Éléments d'origine : modifier l'existant</h3>
<p>[[go:origine]] Ce que l'application propose déjà, à votre main :</p>
<ul><li><b>Tris</b> (menu « Trier par »), <b>Filtres</b> (menu « ⚙️ Filtres ») et <b>tuiles du haut</b> : un nouveau nom (vide : celui d'origine), « masquer »,
et ↑ ↓ pour l'ordre — brouillon, puis « Publier ». Les tuiles changent selon la page : ouvrez dans l'aperçu celle à régler, puis « ⟳ Relire les tuiles ».</li>
<li><b>Calculs d'origine</b> : la formule de chacun expliquée (boîte, livret de plans, exemplaire modifié, seuils des flèches) et son pourcentage,
modifiable — effet <b>immédiat</b>, sans « Publier » (ce sont les réglages du serveur, les mêmes que dans l'appli : Réglages → 🧮 Estimations).</li></ul>"""),
    ]},
    # ------------------------------------------------------------------ 13
    {"id": "donnees", "title": "Données : fiches, catalogue, tableur", "intro": """
<p class="tip">Ces rubriques touchent directement la collection, <b>sans passer par « Publier »</b>. Une sauvegarde automatique est faite avant chaque écriture.</p>""", "blocks": [
        ("bo-donnees", "Une fiche telle qu'elle est enregistrée", """
<h3>Données</h3>
<p>[[go:donnees]] Chercher une fiche et voir — ou corriger — chacune de ses valeurs brutes, ligne par ligne. Pour le cas où aucun écran de
l'application ne permet la correction.</p>"""),
        ("bo-catalogue", "Corriger ce qui vient du catalogue", """
<h3 id="catalogue">Corrections du catalogue</h3>
<p>[[go:catalogue]] Un nom, un thème, une année, un nombre de pièces, une image ou un prix du catalogue est faux ? Cherchez le set ou la figurine,
remplissez seulement ce qui est faux : votre correction passe par-dessus le catalogue, pour toutes les fiches concernées. Videz la case pour la retirer.</p>"""),
        ("bo-tableur", "Vers un tableur, et retour", """
<h3 id="tableur">Tableur (CSV)</h3>
<p>[[go:tableur]] <b>Exporter</b> vos fiches (colonnes au choix, champs et calculs compris) vers Excel ou LibreOffice. <b>Importer</b> un fichier pour
remplir vos champs personnalisés en masse : gardez la colonne « id », modifiez les autres, réimportez.</p>"""),
    ]},
    # ------------------------------------------------------------------ 14
    {"id": "modifs", "title": "Suivi : mes modifications, historique", "intro": "", "blocks": [
        ("bo-modifs", "Tout ce que vous avez changé, au même endroit", """
<h3>Mes modifications</h3>
<p>[[go:modifs]] La liste de tous vos réglages, rubrique par rubrique : « Montrer » fait clignoter l'élément dans l'aperçu, ✕ retire le réglage.
C'est ici qu'on retrouve un élément <b>masqué</b> pour le faire réapparaître.</p>"""),
        ("bo-historique", "Chaque publication est gardée", """
<h3 id="historique">Historique et secours</h3>
<p>[[go:historique]]</p>
<ul><li><b>Reprendre</b> une ancienne publication : elle devient votre brouillon ; vérifiez, puis publiez.</li>
<li><b>↺ Tout remettre d'origine</b> : vide le brouillon de tous vos réglages.</li>
<li><b>Exporter / Importer</b> vos réglages dans un fichier (pour les garder ailleurs, ou les transférer). Un fichier importé est vérifié et remis d'aplomb par le serveur ;
il arrive dans le brouillon : regardez l'aperçu avant de publier, et n'importez que des fichiers de confiance.</li>
<li><b>Feuille de style libre</b> (pour qui connaît le CSS) : facultatif.</li></ul>"""),
    ]},
    # ------------------------------------------------------------------ 15
    {"id": "sauvegardes", "title": "Serveur : sauvegardes, état, sécurité", "intro": """
<p class="tip">Les outils du serveur agissent <b>tout de suite</b>. Chaque action est notée dans le journal du back office.</p>""", "blocks": [
        ("bo-sauvegardes", "Sauvegarder, télécharger, restaurer", """
<h3>Sauvegardes</h3>
<p>[[go:sauvegardes]]</p>
<ul><li><b>Sauvegarder la collection</b> maintenant ; la liste montre aussi les sauvegardes automatiques.</li>
<li><b>Télécharger</b> une sauvegarde pour la garder ailleurs ; en <b>déposer</b> une ; <b>restaurer</b> (l'état actuel est d'abord sauvegardé).</li>
<li><b>Tout emporter</b> : un export <code>.zip</code> de toutes les données (avec ou sans les photos). Les mots de passe n'y sont jamais ;
vos <b>clés API</b> (Rebrickable, BrickLink…), elles, y sont : gardez ce fichier pour vous.</li></ul>
<p class="tip"><b>Avant un gros changement :</b> Sauvegardes → « Sauvegarder la collection ».</p>"""),
        ("bo-serveur", "La santé du serveur et le journal", """
<h3 id="serveur">État et journal</h3>
<p>[[go:serveur]] Depuis quand le serveur tourne, la place disponible sur le disque, la mémoire, la taille des données ; le <b>journal</b>
(avec recherche et « erreurs seulement ») ; le bouton <b>Redémarrer</b>.</p>"""),
        ("bo-securite", "Mots de passe et sécurité", """
<h3 id="securite">Mots de passe et sécurité</h3>
<p>[[go:securite]]</p>
<ul><li><b>Changer le mot de passe du back office</b> (l'actuel est demandé ; les autres appareils sont déconnectés).</li>
<li><b>Changer le mot de passe de la Briquothèque</b> : seul celui du back office est demandé — c'est le secours si celui de la Briquothèque est oublié.
Tous les appareils devront se reconnecter.</li>
<li><b>Sessions</b> : combien sont ouvertes, « Fermer les autres », se déconnecter.</li>
<li><b>Outils sensibles depuis Internet</b> : le code, les réglages de démarrage, la restauration d'un .zip et la page de secours ne répondent que
depuis le <b>réseau local</b> (chez vous). Une case permet de les ouvrir aussi depuis Internet ; elle ne se change que depuis le réseau local.</li></ul>"""),
    ]},
    # ------------------------------------------------------------------ 16
    {"id": "fichiers", "title": "Serveur : fichiers, paramètres, code", "intro": """
<p>Pour les cas rares. Ces trois rubriques demandent l'interrupteur « Fonctions avancées ».</p>""", "blocks": [
        ("bo-fichiers", "N'importe quelle donnée enregistrée, ligne par ligne", """
<h3>Fichiers de données</h3>
<p>[[go:fichiers]] Tous les fichiers de données du serveur (collection, caches, réglages…), en lecture et en correction ligne par ligne, avec recherche.
Une copie de l'ancien fichier est gardée à chaque écriture. Les fichiers de mots de passe n'y figurent pas.</p>"""),
        ("bo-parametres", "Durées, quotas, tailles ; port, proxy, démonstration", """
<h3 id="parametres">Paramètres du serveur</h3>
<p>[[go:parametres]] Les durées de garde des caches, les quotas d'appels, les tailles d'images, la durée des sessions… appliqués <b>à chaud</b>.
Les réglages de démarrage (port, proxy, démonstration publique) demandent un redémarrage, proposé sur place.</p>"""),
        ("bo-code", "Le code de l'application, avec trois filets de sécurité", """
<h3 id="code">Code de l'application</h3>
<p>[[go:code]] En dernier recours, les fichiers du programme se modifient depuis le navigateur :</p>
<ol><li>la <b>syntaxe est vérifiée</b> avant d'enregistrer (un fichier faux est refusé, avec la ligne de l'erreur) ;</li>
<li>chaque <b>version précédente est gardée</b> et se remet d'un clic ;</li>
<li>si le serveur ne redémarre pas avec un fichier modifié, l'<b>ancienne version revient toute seule</b>.</li></ol>
<p>En tout dernier recours : la <a href="#secours">page de secours</a>.</p>"""),
    ]},
    # ------------------------------------------------------------------ 17
    {"id": "secours", "title": "En cas de problème", "intro": "", "blocks": [
        ("bo-secours", "La page de secours : /backoffice/secours", """
<h3>Les bons réflexes</h3>
<table><tr><th>Ce qui se passe</th><th>Quoi faire</th></tr>
<tr><td>Un réglage rend le site illisible ou inutilisable</td><td>Ajoutez <code>?bo=off</code> à la fin de l'adresse du site : il s'affiche <b>sans aucune personnalisation</b>.
Puis ouvrez <code>/backoffice</code> (jamais personnalisé, toujours utilisable) → « Mes modifications » pour retirer le réglage fautif,
ou « Historique et secours » pour reprendre une version d'avant.</td></tr>
<tr><td>Un élément a disparu</td><td>Aperçu → cochez « Montrer ce qui est masqué » ; ou « Mes modifications » → ✕ sur la ligne « masqué ».</td></tr>
<tr><td>Un clic ne fait plus rien</td><td>« Comportements » → « Clics et liens modifiés » → ✕.</td></tr>
<tr><td>Je veux tout remettre comme avant le back office</td><td>« Historique et secours » → « ↺ Tout remettre d'origine », puis Publier.</td></tr>
<tr><td>Une donnée a été abîmée</td><td>« Sauvegardes » → Restaurer la sauvegarde d'avant.</td></tr>
<tr><td>Le site ne répond plus après une modification du code</td><td>Attendez dix secondes (l'ancienne version revient seule). Sinon : <code>/backoffice/secours</code> →
mot de passe du back office → « Afficher les versions gardées » → remettre la version d'avant → Redémarrer.</td></tr>
<tr><td>Mot de passe de la Briquothèque oublié</td><td>Back office → « Mots de passe et sécurité » → « Changer le mot de passe de la Briquothèque ».</td></tr>
<tr><td>Mot de passe du back office oublié</td><td>Il ne se retrouve pas : supprimez <code>data/backoffice_auth.json</code> sur le serveur, puis rouvrez <code>/backoffice</code>.</td></tr>
<tr><td>« Trop de tentatives »</td><td>Attendez 15 minutes. Une adresse bannie se débloque dans Réglages → Sécurité de la Briquothèque.</td></tr>
<tr><td>Un outil répond « seulement depuis le réseau local »</td><td>Ouvrez le back office depuis chez vous ; ou cochez « Outils sensibles depuis Internet » (depuis chez vous).</td></tr></table>
<h3>Ce que le back office ne fait pas</h3>
<p>Une fonction entièrement nouvelle de l'application (une nouvelle source de prix, par exemple) demande toujours du code — mais ce code se modifie
depuis la rubrique « Code de l'application », sans ligne de commande. Tout le reste se règle ici.</p>"""),
    ]},
    # ------------------------------------------------------------------ 18
    {"id": "recettes", "title": "Dix recettes pas à pas", "intro": "", "blocks": [
        ("", "", """
<ol class="rec">
<li><b>Changer la couleur du site.</b> Apparence → choisissez une palette → Publier.</li>
<li><b>Mettre votre logo.</b> Apparence → Logo → « Choisir un fichier… » → Publier.</li>
<li><b>Renommer « MOC » en « Création ».</b> Étiquettes et pastilles → ligne « MOC » → Modifier → Nouveau texte : « Création » → Publier.</li>
<li><b>Un bouton avec une image.</b> Images → envoyez l'image. Modifier à la souris → cliquez le bouton → « Icône ou image » → « Une image » →
« 🖼️ Choisir… » → place « à la place du texte » → réglez largeur et hauteur → Publier.</li>
<li><b>Masquer une section des Réglages.</b> Page « Réglages » de l'appli → décochez « visible » sur la section → Publier.</li>
<li><b>Un champ « Emplacement » sur les sets.</b> Champs personnalisés → + Nouveau champ → « Emplacement », texte court, fiches « Sets » → Publier.
Remplissez-le ensuite sur chaque fiche.</li>
<li><b>Une étiquette pour les sets chers.</b> Étiquettes et pastilles → exemple « 💰 Plus de 100 € » → ajustez le montant → Publier.</li>
<li><b>Un tableau de bord en page de départ.</b> Pages → « 📊 Tableau de bord ». Puis Comportements → Page de départ → « Une page créée… » → Tableau de bord → Publier.</li>
<li><b>Une page publique de contact.</b> Pages → Page vide → blocs Texte et Bouton (« Ouvrir une adresse » : <code>mailto:vous@exemple.fr</code>) →
cochez « Publique » → Publier → donnez l'adresse <code>/p/…</code>.</li>
<li><b>Revenir à hier.</b> Historique et secours → « Reprendre » sur la publication d'hier → vérifiez l'aperçu → Publier.</li>
</ol>"""),
    ]},
]

# nom lisible de chaque rubrique (pour « [[go:…]] » dans la version PDF)
PANELS = {"accueil": "Accueil", "souris": "Modifier à la souris", "apparence": "Apparence", "boutons": "Boutons et tailles", "textes": "Textes", "etiquettes": "Étiquettes et pastilles",
          "fiches": "Fiches", "champs": "Champs personnalisés", "liens": "Liens automatiques", "cartes": "Cartes des listes", "menu": "Menu", "pages": "Pages",
          "reglages": "Page « Réglages » de l'appli", "comportements": "Comportements", "images": "Images", "calculs": "Calculs et variables", "regles": "Règles « si… alors »",
          "tuiles": "Tuiles et totaux", "vues": "Vues, tris et filtres", "donnees": "Données", "catalogue": "Corrections du catalogue", "tableur": "Tableur (CSV)",
          "modifs": "Mes modifications", "historique": "Historique et secours", "sauvegardes": "Sauvegardes", "serveur": "État et journal", "securite": "Mots de passe et sécurité",
          "fichiers": "Fichiers de données", "parametres": "Paramètres du serveur", "code": "Code de l'application"}

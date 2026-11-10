#### Sprint 3 : Préparation de la démonstration et amélioration de l'ergonomie

Objectif du sprint : rendre le parcours de collecte des photos plus
compréhensible dans Gradio et préparer une démonstration reproductible de la
comparaison avant/après.

Périmètre du bilan : changements intégrés après le commit `2baa760` du
28 septembre 2026, jusqu'au commit `fcb0cdb` du 7 octobre 2026. Le sprint est
centré sur l'aide à la saisie et la préparation du parcours de démonstration ;
la validation humaine des anomalies n'a pas encore été intégrée.

User Stories réalisées pendant le sprint :

- **US-9.8 : Ajouter des captures ou une démonstration** *(Partiellement
  réalisé)* — ajout de photos d'exemple représentant les six angles attendus
  par l'application afin de guider la saisie et de faciliter une démonstration.
- **US-4.5 : Afficher les six angles avant/après** *(Amélioré)* — les champs de
  téléversement de photos d'analyse affichent désormais un exemple visuel
  correspondant à chaque angle.

Fonctionnalités et travaux techniques réalisés :

- Ajout des six images d'exemple dans `img/` :
  `capot.jpg`, `dessous.jpg`, `ecran.jpg`, `clavier.jpg`, `gauche.jpg` et
  `droite.jpg`.
- Association centralisée entre le nom métier d'une zone et son image
  d'exemple dans `EXEMPLES_PHOTOS`.
- Création d'un composant Gradio commun pour afficher un exemple à côté de
  chaque champ de téléversement.
- Conservation de l'ordre des six zones utilisé par l'analyse :
  dessus, dessous, écran, clavier, connectique gauche et connectique droite.
- Conservation du comportement existant : les images d'exemple sont
  uniquement informatives et ne sont pas enregistrées en base à la place des
  photos fournies par le gestionnaire.
- Les tests unitaires existants restent indépendants des images de démonstration
  et ne nécessitent ni PostgreSQL actif ni serveur Ollama.

Travail restant :

- **US-5.1 : Accepter une dégradation.**
- **US-5.2 : Modifier le type ou la gravité d'une anomalie.**
- **US-5.3 : Ignorer un faux positif.**
- **US-5.4 : Ajouter une remarque.**
- **US-5.5 : Enregistrer la décision du gestionnaire.**
- **US-6.4 : Distinguer explicitement le résultat de l'IA de la validation
  humaine.**
- **US-8.7 : Valider les anomalies depuis l'interface.**
- **US-8.9 : Vérifier le scénario complet avec un test d'intégration.**
- **US-9.8 : Finaliser la démonstration avec un parcours documenté, des
  photos de référence et des photos de restitution.**
- **US-9.9 : Mettre à jour la documentation après l'intégration finale.**
- Préserver séparément les photos originales et les photos annotées au lieu de
  remplacer la photo de restitution en base.
- Rafraîchir automatiquement les images affichées après la fin d'une analyse.
- Vérifier le parcours complet avec une base PostgreSQL réelle et le modèle
  Ollama cible.

Limites constatées :

- Les photos d'exemple servent de repères visuels ; elles ne constituent pas
  des photos avant/après enregistrées pour un matériel.
- Aucune décision humaine n'est encore persistée avec le rapport IA.
- La qualité de détection reste dépendante du modèle VLM, de sa configuration
  et de la qualité des photos fournies.
- Le parcours complet n'est pas couvert par un test automatisé de type
  intégration ou navigateur.

Livrables / DoR & DoD :

- DoR (Definition of Ready) retenue pour le prochain incrément :
  - Les six zones et leur ordre sont définis.
  - Le format des anomalies et les gravités acceptées sont connus.
  - Les photos d'exemple sont disponibles dans le dépôt et chargées par
    l'interface.
  - Un serveur Ollama et une base PostgreSQL de test sont disponibles pour la
    recette.
  - Les règles de validation humaine sont définies : accepter, modifier,
    ignorer et commenter une anomalie.
- Livrables réalisés :
  - Six photos d'exemple versionnées dans le dépôt.
  - Affichage des exemples à côté des champs de téléversement dans Gradio.
  - Parcours de saisie plus explicite pour préparer la démonstration.
- DoD restant à vérifier :
  - Un gestionnaire peut confirmer ou corriger chaque anomalie détectée.
  - La décision humaine est distinguée du résultat brut de l'IA et enregistrée.
  - Le rapport final peut être retrouvé après redémarrage.
  - Le scénario création, restitution, analyse, validation, sauvegarde et
    consultation est testé de bout en bout.
  - Une démonstration reproductible avec les photos d'exemple est documentée.

Tests et critères d'acceptation :

- Les images d'exemple correspondent bien aux six libellés affichés dans le
  formulaire.
- La sélection d'une photo par le gestionnaire reste nécessaire : une image
  d'exemple ne déclenche ni enregistrement ni analyse.
- L'analyse continue d'utiliser uniquement les paires avant/après présentes en
  base.
- Les tests unitaires du sprint précédent restent la référence pour la
  validation JSON, les bounding boxes, le transport Ollama et les accès au
  stockage.
- La validation du scénario réel avec Docker Compose, PostgreSQL, Ollama et
  les photos d'exemple reste à effectuer.

Traçabilité des changements :

| Commit | Apport au sprint |
| --- | --- |
| `fcb0cdb` | Ajout des six photos d'exemple et affichage d'un exemple à côté de chaque zone dans Gradio. |

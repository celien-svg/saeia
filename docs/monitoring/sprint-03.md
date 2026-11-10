#### Sprint 3 : Préparation de la démonstration et amélioration de l'ergonomie

Objectif du sprint : rendre le parcours de collecte des photos plus
compréhensible dans Gradio et préparer une démonstration reproductible de la
comparaison avant/après.

Périmètre du bilan : changements intégrés après le commit `2baa760` du
28 septembre 2026, jusqu'au commit `fcb0cdb` du 7 octobre 2026. Le sprint est
centré sur l'aide à la saisie et la préparation du parcours de démonstration ;
la validation humaine des anomalies est maintenant intégrée.

User Stories réalisées pendant le sprint :

- **US-9.8 : Ajouter des captures ou une démonstration** *(Partiellement
  réalisé)* — ajout de photos d'exemple représentant les six angles attendus
  par l'application afin de guider la saisie et de faciliter une démonstration.
- **US-4.5 : Afficher les six angles avant/après** *(Amélioré)* — les champs de
  téléversement de photos d'analyse affichent désormais un exemple visuel
  correspondant à chaque angle.

Fonctionnalités et travaux techniques réalisés :

- Association centralisée entre le nom métier d'une zone et son image
  d'exemple dans `EXEMPLES_PHOTOS` lorsque le dossier `img/` est fourni.
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

- Ajouter un test d'intégration reproductible avec PostgreSQL, Ollama et des
  photos réelles.
- Finaliser une démonstration avec un jeu de photos versionné.
- Ajouter des tests navigateur pour couvrir le parcours complet.

Limites constatées :

- Les photos d'exemple servent de repères visuels ; elles ne constituent pas
  des photos avant/après enregistrées pour un matériel.
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
  - Le parcours de validation humaine est disponible et séparé du rapport IA.
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

#### Sprint 1 : Restitution, comparaison IA & rapport d'analyse

Objectif du sprint : permettre au gestionnaire d'enregistrer la restitution d'un
ordinateur, de comparer les photos avant/apres avec le VLM et de consulter un
premier rapport lisible dans l'interface.

User Stories :
- **US-01** *(Terminé)* : En tant que gestionnaire, je veux enregistrer les photos prises au retour afin de les associer à l'ordinateur contrôlé.
- **US-02** *(En cours)* : En tant que gestionnaire, je veux lancer l'analyse depuis l'interface afin de comparer les photos de référence et de restitution.
- **US-03** *(Terminé)* : En tant que gestionnaire, je veux valider strictement la réponse JSON du modèle afin de détecter les réponses invalides ou incomplètes.
- **US-04** *(En cours)* : En tant que gestionnaire, je veux afficher les images avant et apres côte à côte afin de faciliter la comparaison visuelle.
- **US-06** *(En cours)* : En tant que gestionnaire, je veux générer un rapport final regroupant les résultats de l'analyse afin de conserver une trace du contrôle.
- **US-09** *(En cours)* : En tant que développeur, je veux documenter l'installation, la configuration et le parcours complet afin de rendre le prototype utilisable par l'équipe.
- **US-10** *(Terminé)* : En tant que gestionnaire, je veux modifier un matériel existant afin de corriger ses informations et de conserver ou remplacer ses photos.

Fonctionnalités réalisées :
- Enregistrement des photos de restitution avec distinction entre photos de référence et photos d'analyse.
- Association des photos par zone et construction des paires avant/apres.
- Envoi des deux images au VLM dans le bon ordre.
- Validation du JSON retourné : racine, liste des zones, champs obligatoires, gravité autorisée et coordonnées de bounding box.
- Gestion contrôlée des erreurs de connexion Ollama et des réponses JSON invalides.
- Annotation des anomalies détectées sur l'image de restitution.
- Conversion du résultat JSON en texte lisible pour préparer l'affichage dans Gradio.
- Création et modification d'un matériel avec normalisation des champs et traitement des photos.

Travail restant :
- Connecter le parcours complet de comparaison aux composants Gradio.
- Afficher les six angles avant/apres et les résultats associés dans une vue unique.
- Afficher les anomalies, leur gravité et leurs bounding boxes dans l'interface.
- Regrouper les résultats de toutes les zones dans un rapport final structuré.
- Distinguer clairement le résultat de l'IA de la validation humaine.
- Enregistrer le rapport et permettre sa consultation ultérieure.
- Ajouter des tests d'intégration avec des réponses VLM simulées et documenter une démonstration complète.

Livrables / DoR & DoD :
- DoR (Definition of Ready) :
  - Les six types de photos attendus sont définis et nommés de manière constante.
  - Le modèle de données distingue les photos avant et apres.
  - Le format JSON attendu par le VLM et les valeurs de gravité autorisées sont validés.
  - Le serveur Ollama et le modèle VLM sont accessibles pour les tests d'intégration.
  - Les critères d'acceptation de l'affichage et du rapport sont définis.
- DoD (Definition of Done) :
  - Une restitution complète peut être enregistrée avec son matériel associé.
  - Une comparaison ne peut être lancée que si une paire avant/apres correspondante existe.
  - Une réponse JSON invalide est refusée et présentée comme une erreur contrôlée.
  - Les anomalies sont affichées avec leur élément, leur description, leur gravité et leur position lorsqu'elle est disponible.
  - Les images avant et apres sont consultables depuis l'interface.
  - Un rapport regroupant les résultats des différentes zones est généré et testable.
  - Les parcours principaux sont couverts par des tests automatisés et la documentation est mise à jour.

Tests et critères d'acceptation :
- Une photo de restitution est enregistrée avec `est_avant = FALSE` et reste associée au bon matériel.
- Une analyse utilise uniquement les zones possédant une photo avant et une photo apres.
- Le modèle reçoit toujours la photo de référence avant la photo de restitution.
- Les JSON invalides, les gravités inconnues et les bounding boxes incohérentes sont rejetés.
- Une zone sans anomalie produit un résultat lisible indiquant qu'aucune dégradation n'a été détectée.
- Une erreur Ollama n'empêche pas la génération des résultats des autres zones.
- La modification d'un matériel conserve les photos existantes lorsqu'aucune nouvelle photo n'est fournie.
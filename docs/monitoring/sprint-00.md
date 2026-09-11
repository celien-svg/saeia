#### Sprint 0 : Socle Technique & Suivi Visuel des Prêts

User Stories :
- **US 0.1** *(Terminé)* : En tant que développeur, j'initialise le dépôt Git avec sa configuration (.gitignore, convention de nommage) afin de permettre la collaboration et le versioning du code.
- **US 0.2** *(Terminé)* : En tant que développeur, je mets en place l'architecture et la structure Python du projet (packages `src/suivi_pret`, modules de configuration, services et stockage) pour assurer une organisation claire et modulaire.
- **US 0.3** *(Terminé)* : En tant que développeur, je configure l'environnement et les dépendances (`requirements.txt`, variables `.env`, base PostgreSQL sous Docker) afin de garantir un environnement d'exécution reproductible.
- **US 0.4** *(Terminé)* : En tant que concepteur / développeur, je réalise les maquettes de l'interface utilisateur pour cadrer l'expérience utilisateur et les écrans de gestion des prêts de matériel.
- **US 0.5** *(En cours)* : En tant que gestionnaire, je dispose d'une interface graphique interactive (Gradio) me permettant d'administrer et visualiser le parc de matériels informatiques.
- **US 0.6** *(En cours)* : En tant qu'utilisateur / gestionnaire, je peux enregistrer et téléverser des photos de l'état de l'ordinateur avant utilisation pour attester de son état initial lors de la remise.
- **US 0.7** *(En cours)* : En tant qu'utilisateur / gestionnaire, je peux enregistrer et téléverser des photos de l'ordinateur après utilisation pour attester de son état lors de la restitution.
- **US 0.8** *(En cours)* : En tant que gestionnaire, je dispose d'un module d'analyse par intelligence artificielle (VLM) comparant les photos avant et après utilisation afin d'identifier automatiquement les éventuelles dégradations ou anomalies.

Livrables / DoR & DoD :
- Dépôt Git configuré et accessible à l'équipe.
- Arborescence du projet Python structurée et prête pour l'ajout des modules métiers.
- Fichier `requirements.txt` et conteneur PostgreSQL fonctionnels via Docker Compose.
- Maquettes d'écrans validées pour le flux de prêt et restitution.
- Interface Gradio opérationnelle connectée à la base de données PostgreSQL.
- DoR (Definition of Ready) : Spécifications des états du matériel définies, serveur VLM / Ollama accessible, modèle de données PostgreSQL validé.
- DoD (Definition of Done) : Code source documenté et testé, photos avant/après associées au matériel en base, rapport d'analyse généré par le VLM sur la comparaison des deux photos.


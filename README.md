# Suivi de pret d'ordinateurs avec IA

Projet de suivi de l'état physique d'ordinateurs portables prêtés a des étudiants.
L'application compare une photo prise avant le prêt avec une photo prise au retour,
puis utilise un modèle de vision (VLM) via Ollama pour détecter les dégradations
nouvelles : rayure, tâche, déformation, casse, etc.

## Suivi du projet

Le suivi des tâches et des user stories est disponible sur le [tableau Trello](https://trello.com/b/3we9QZwI/sae-ia).

## Objectif

Pour chaque zone de l'ordinateur (par exemple l'écran ou le clavier), le système :

1. reçoit la photo de réference prise avant le prêt ;
2. reçoit la photo prise apres la réstitution ;
3. envoie les deux photos au modèle de vision dans cet ordre ;
4. demande une réponse structurée en JSON ;
5. retourne les anomalies détectées, leur gravité et leur position lorsqu'elle est fournie.

Le client Ollama est disponible dans `src/suivi_pret/ollama_client/vlm.py`.
L'interface Gradio, dans `src/suivi_pret/ui_gradio.py`, permet de gérer les matériels, lancer l'analyse et sauvegarder les rapports dans PostgreSQL.

## Prérequis

- Docker avec Compose ;
- une connexion réseau pour construire l'image et télécharger le modèle Ollama.

Docker Compose est le seul mode de lancement fourni. Python, PostgreSQL et
Ollama sont exécutés dans les conteneurs ; aucune installation locale de ces
outils n'est nécessaire.

## Installation

Depuis la racine du projet, préparer la configuration ci-dessous puis suivre
la section **Lancement avec Docker Compose**.

## Configuration

Copier le fichier d'exemple puis adapter les valeurs :

```bash
cp .env.example .env
```

Sous Windows PowerShell :

```powershell
Copy-Item .env.example .env
```

Le fichier `.env` doit contenir au minimum :

```dotenv
OLLAMA_HOST=http://ollama:11434
OLLAMA_VLM_MODEL=qwen3-vl:8b-instruct
POSTGRES_HOST=pg
POSTGRES_PORT=5432
POSTGRES_USER=suivi_pret
POSTGRES_PASSWORD=mot_de_passe_a_remplacer
POSTGRES_DB=suivi_pret
```

Les noms `pg` et `ollama` désignent les services du réseau Compose.
Sur un volume PostgreSQL neuf, le conteneur crée le rôle et la base configurés,
puis exécute [database/01-tables.sql](database/01-tables.sql).
Ne pas versionner `.env`, qui contient les identifiants de connexion.

Après une modification de `.env`, relancer `docker compose up -d --build`
pour que Compose applique la configuration aux conteneurs concernés.
`OLLAMA_VLM_MODEL` doit être le nom exact d'un modèle installé sur le serveur ciblé. La valeur d'exemple ne confirme pas le modèle disponible à l'IUT.

Pour utiliser le serveur Ollama de l'IUT, adapter `OLLAMA_HOST` avec une
adresse accessible depuis le conteneur et renseigner le modèle disponible.

## Interface Gradio

Après le lancement avec Compose, ouvrir `http://localhost:7860`, puis suivre ce parcours :

1. Créer un ordinateur avec ses informations et ses photos de référence.
   L'identifiant d'entité doit correspondre à une entité existant en base.
2. Ouvrir **Analyse** depuis la liste des ordinateurs.
3. Fournir les photos après et cliquer sur **Ajouter les photos** pour les
   enregistrer avant de lancer la comparaison.
4. Cliquer sur **Lancer l'analyse**, puis consulter le résultat texte.
5. Cliquer sur **Sauvegarder le rapport** pour conserver le résultat.
6. Utiliser **Liste des rapports** pour consulter l'historique du matériel.

Les six angles avant/après sont présentés côte à côte. L'analyse utilise les
photos en base : une photo simplement sélectionnée dans l'interface n'est
pas encore prise en compte. La sauvegarde du rapport est une action distincte.

Actuellement, les annotations remplacent les photos après dans la base.
Les images affichées ne sont pas rafraîchies automatiquement à la fin de
l'analyse : rouvrir la page d'analyse pour charger les images annotées.

## Prompt et validation

La consigne est dans [prompt.md](src/suivi_pret/ollama_client/prompt.md).
Elle est lue à l'import du module : exécuter `docker compose restart app`
après modification.
`{zone}` est remplacé par la zone analysée. Les accolades littérales de
l'exemple JSON doivent rester doublées (`{{` et `}}`), car le code utilise
`str.format()`. Les images sont envoyées dans l'ordre avant, puis après.

La réponse doit être un objet contenant uniquement une liste `zones`.
Chaque anomalie contient `element`, `anomalie`, `gravite` et `bbox`.
Les gravités acceptées sont `aucune`, `legere`, `marquee` et `importante`.
Une réponse invalide produit un message d'erreur pour la zone.

Le contrôle des boîtes englobantes vérifie quatre coordonnées numériques,
finies, non négatives et ordonnées. Leur appartenance aux dimensions réelles
de l'image n'est pas encore vérifiée.

## Lancement avec Docker Compose

Compose fournit l'application, PostgreSQL et Ollama. Pour joindre les services
depuis le conteneur applicatif, adapter ces valeurs dans `.env`, tout en
conservant les autres variables requises :

```dotenv
POSTGRES_HOST=pg
OLLAMA_HOST=http://ollama:11434
```

Le service applicatif expose le port `7860` :

```bash
docker compose up -d --build
```

Télécharger le modèle dans le service Ollama avant de lancer une analyse :

```bash
docker compose exec ollama ollama pull qwen3-vl:8b-instruct
```

Adapter le nom au modèle configuré dans `OLLAMA_VLM_MODEL`. Un serveur Ollama
externe peut aussi être utilisé via une adresse accessible depuis le conteneur.

Le schéma SQL est appliqué automatiquement lors de l'initialisation d'un volume
PostgreSQL neuf. Les changements ultérieurs du script ne sont pas rejoués sur
une base existante : leurs évolutions de schéma doivent y être appliquées
explicitement.

Pour consulter les journaux ou arrêter les services :

```bash
docker compose logs -f app
docker compose down
```

Les volumes de données sont conservés par `docker compose down`.

## Architecture simplifiee

```text
Photos avant/apres
	|
	v
Interface Gradio (Docker)
	|
	v
OllamaVLM.compare_images()
	|
	v
Serveur Ollama + modele VLM
	|
	v
Validation JSON → rapport texte et annotations
```

La répartition du code est la suivante :

- `service/` : logique métier de gestion des matériels et des rapports.
- `storage/base.py` : contrat de persistance ; `storage/postgres.py` :
  connexions et requêtes PostgreSQL.
- `ollama_client/base.py` : transport HTTP asynchrone partagé, erreurs et
  fermeture des connexions avec `async with`.
- `ollama_client/vlm.py` : `OllamaVLM`, qui hérite de cette base et expose
  `compare_images()`. Les clients LLM et embedding restent des squelettes.
- `ollama_client/ia_comparaison.py` : association des photos par zone, appels
  au VLM, validation JSON, annotations et conversion en texte.

Les appels Ollama sont asynchrones. Les opérations PostgreSQL de l'analyse
restent synchrones dans le stockage, mais s'exécutent dans des threads via
`asyncio.to_thread()` pour libérer la boucle asynchrone pendant les accès à
la base. Les zones sont analysées successivement, sans générations parallèles.

## Qualité et CI

Exécuter les tests dans un conteneur, depuis la racine du dépôt :

```bash
docker compose run --rm --no-deps app python -m unittest discover -s tests -v
```

Le workflow GitHub Actions `.github/workflows/ci.yml` s'execute sur les push et les
pull requests. Il installe les dépendances, vérifie la compilation Python et teste
l'import d'`OllamaVLM`, puis exécute les tests unitaires.

Les tests simulent les échanges réseau et le stockage. Ils ne nécessitent ni
serveur PostgreSQL actif, ni serveur Ollama, ni modèle téléchargé. Ils couvrent
notamment la validation JSON, le transport HTTP, l'association des photos et
l'exécution des accès au stockage hors de la boucle asynchrone.

Le parcours complet et la qualité de détection restent à vérifier avec des
photos réelles, une base PostgreSQL initialisée et un serveur Ollama disponible.

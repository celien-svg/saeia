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
L'interface Gradio est prevue dans `src/suivi_pret/ui_gradio.py` et reste a complèter.

## Prérequis

- Python 3.12 ou une version compatible ;
- un modele Ollama multimodal, par exemple `qwen3-vl:8b-instruct` ;
- un serveur Ollama accessible depuis l'application.

## Installation

Depuis la racine du projet :

```bash
python -m venv venv
source venv/bin/activate  # Windows : venv\\Scripts\\activate
pip install -r requirements.txt
```

Sous Windows PowerShell, l'activation s'écrit :

```powershell
venv\\Scripts\\Activate.ps1
```

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
OLLAMA_HOST=http://localhost:11434
OLLAMA_VLM_MODEL=qwen3-vl:8b-instruct
```

Ne pas versionner `.env` : il peut contenir des parametres propres à votre machine.

Verifier qu'Ollama fonctionne et que le modèle est disponible :

```bash
ollama serve
ollama pull qwen3-vl:8b-instruct
```

Si Ollama est installé sur une autre machine, remplacer `localhost` par son nom
ou son adresse IP. Le port par defaut est `11434`.

## Lancer une comparaison

Le script d'essai compare les images présentes dans
`src/suivi_pret/ollama_client/testimage/`. Il attend notamment les paires suivantes :

- `ecranbefore.jpg` et `ecranafter.jpg` ;
- `clavierbefore.jpg` et `clavierafter.jpg`.

Avec l'environnement virtuel active :

```bash
python src/suivi_pret/ollama_client/test_compare_image.py
```

Le rapport est affiché dans le terminal sous forme de JSON. Une anomalie contient
notamment la zone analysée, sa description, sa gravité (`aucune`, `legere`,
`marquee` ou `importante`) et une boite englobante lorsque le modèle en fournit une.

## Interface Gradio

Le point d'entrée prévu pour l'interface est :

```bash
python -m src.suivi_pret.ui_gradio
```

L'interface est actuellement un squelette. La comparaison fonctionnelle peut etre
testée avec le script indique dans la section précèdente.

## Docker

Le service applicatif expose le port `7860` :

```bash
docker compose up --build
```

Le serveur Ollama doit être accessible depuis le conteneur. Dans ce cas, utilisez
le nom du service ou l'adresse réseau approprié dans `OLLAMA_HOST`.

## Architecture simplifiee

```text
Photos avant/apres
	|
	v
Script ou future interface Gradio
	|
	v
OllamaWrapper.compare_images()
	|
	v
Serveur Ollama + modele VLM
	|
	v
Rapport JSON des anomalies
```

## Qualité et CI

Le workflow GitHub Actions `.github/workflows/ci.yml` s'execute sur les push et les
pull requests. Il installe les dépendances, vérifie la compilation Python et teste
l'import du client Ollama. Il ne nécessite ni serveur Ollama ni modèle téléchargé,
ce qui permet de l'executer dans un environnement CI standard.

L'analyse visuelle complète reste un test d'intégration local, car elle dépend du
modèle VLM et des images de test.

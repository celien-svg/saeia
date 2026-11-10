# Documentation du projet SAEIA

Cette documentation décrit l'application de suivi de prêt d'ordinateurs avec
comparaison d'images par un modèle de vision Ollama.

## Documents

| Document | Contenu |
| --- | --- |
| [Documentation technique](./documentation_technique.md) | Architecture, base de données, installation, exploitation et API interne |
| [Documentation utilisateur](./documentation_utilisateur.md) | Utilisation de l'interface Gradio et procédure avant/après |
| [Qualité de développement](./qualite_developpement.md) | Qualité logicielle, tests unitaires, validation JSON et scénarios BDD |
| [Suivi sprint 0](./monitoring/sprint-00.md) | Mise en place du socle du projet |
| [Suivi sprint 1](./monitoring/sprint-01.md) | Photos de restitution et comparaison IA |
| [Suivi sprint 2](./monitoring/sprint-02.md) | Rapports, validations humaines et fiabilisation |
| [Suivi sprint 3](./monitoring/sprint-03.md) | Ergonomie et démonstration |

## Parcours fonctionnel actuel

1. Créer un ordinateur et ses photos de référence.
2. Consulter, modifier ou supprimer sa fiche.
3. Ajouter les photos prises lors de la restitution.
4. Comparer les paires avant/après disponibles avec Ollama.
5. Consulter les anomalies, les photos annotées et l'historique des rapports.
6. Modifier le rapport avant de l'enregistrer comme rapport humain.
7. Ajouter une décision humaine à un rapport enregistré.

## Démarrage rapide

La procédure complète et les variables obligatoires sont détaillées dans la
[documentation technique](./documentation_technique.md). En résumé :

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

L'interface est ensuite accessible à l'adresse
`http://localhost:7860`. Les tests unitaires peuvent être lancés sans
PostgreSQL ni Ollama :

```powershell
python -m unittest discover -s tests -v
```

## Principes importants

- Ollama est une aide à la décision : le gestionnaire conserve la décision
  finale.
- Une photo d'analyse n'est comparée que si une photo avant correspondante
  existe pour la même zone.
- Les photos originales sont conservées ; les annotations sont stockées dans
  `image_annotee`.
- Les fichiers `.env` et les mots de passe ne doivent jamais être commités.

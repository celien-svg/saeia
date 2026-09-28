#### Sprint 2 : Sauvegarde des rapports & fiabilisation de l'analyse IA

Objectif du sprint : permettre au gestionnaire de sauvegarder et consulter les
rapports d'analyse d'un ordinateur, tout en fiabilisant les échanges avec Ollama,
les accès aux données et le lancement de l'application.

Périmètre du bilan : changements intégrés à `main` après le commit `48af442`
(ajout du bilan du sprint 1, le 23 septembre 2026), jusqu'au commit `2baa760`
du 28 septembre 2026. Cette borne sert de référence en l'absence d'une date de
clôture distincte du sprint 1.

Les identifiants ci-dessous suivent les nouvelles checklists Trello : chaque case
devient une sous-US `US-N.x`, selon son ordre dans la checklist. Le bilan distingue
les réalisations nouvelles des améliorations de fonctionnalités déjà présentes.

User Stories réalisées pendant le sprint :

- **US-6.5 : Enregistrer le rapport en base** *(Réalisé)* — ajout de la sauvegarde explicite depuis Gradio et de la table PostgreSQL `rapports_ia`.
- **US-6.6 : Permettre sa consultation ultérieure** *(Réalisé)* — consultation de l'historique des rapports d'un matériel, datés et présentés du plus récent au plus ancien.
- **US-8.8 : Enregistrer le rapport final** *(Réalisé)* — intégration de la sauvegarde dans le parcours d'analyse. Cette sous-US et US-6.5 reposent sur la même fonctionnalité ; la sauvegarde ne constitue pas une validation humaine des anomalies.
- **US-9.7 : Documenter le parcours complet** *(Réalisé)* — description des étapes de création du matériel, d'ajout des photos de restitution, d'analyse, de sauvegarde et de consultation des rapports.

User Stories consolidées pendant le sprint :

- **US-2.4 : Appeler le VLM depuis Gradio** — passage du déclenchement de l'analyse et des appels Ollama en asynchrone.
- **US-3.1 : Demander une réponse JSON au modèle** — déplacement du prompt dans `prompt.md` et précision du format des coordonnées attendu.
- **US-3.7 : Vérifier les quatre coordonnées d'une bbox** — rejet des coordonnées hors de l'intervalle `0–1024`.
- **US-3.8 : Ajouter des tests automatisés** — adaptation des tests au pipeline asynchrone et ajout d'un cas de coordonnées hors limites.
- **US-4.5 : Dessiner les bounding boxes** — limitation des coordonnées utilisées pour le dessin aux dimensions de l'image.
- **US-7.5 : Bbox incorrecte** — ajout d'un test avec une coordonnée supérieure à 1024.
- **US-7.6 : Timeout** — test de la conversion d'un timeout HTTP en erreur de connexion Ollama contrôlée.
- **US-9.2 : Configuration d'Ollama** — documentation de la configuration dans Docker et de l'utilisation d'un serveur distant.
- **US-9.4 : Lancement avec Docker** — attente de PostgreSQL avant le démarrage de l'application et centralisation du lancement avec Docker Compose.
- **US-9.5 : Explication du prototype de comparaison** — mise à jour de la documentation du pipeline, du prompt, de la validation et de l'organisation du code.

Fonctionnalités et travaux techniques réalisés :

- Ajout des boutons « Sauvegarder le rapport » et « Liste des rapports » dans Gradio.
- Conservation de plusieurs rapports textuels par matériel, avec leur date de création.
- Rechargement des photos de restitution, éventuellement annotées, à l'ouverture de la page d'analyse.
- Réalisation de la carte technique Trello « Rendre asynchrone le client Ollama », sans identifiant US dans l'export.
- Mutualisation du transport HTTP asynchrone, de la fermeture des connexions et de la gestion des erreurs dans `BaseModelEndpoint`.
- Simplification du client VLM et renommage d'`OllamaWrapper` en `OllamaVLM`.
- Déplacement de la lecture des photos et de l'enregistrement des annotations dans la couche `Storage` / `PostgresStorage`.
- Exécution des accès PostgreSQL de l'analyse dans des threads via `asyncio.to_thread()` pour libérer la boucle asynchrone. Les zones restent analysées successivement.
- Mise à jour de `.env.example`, du point d'entrée Docker, du README et du contrôle d'import dans la CI.

Travail restant :

- **US-5.1 : Accepter une dégradation.**
- **US-5.2 : Modifier son type ou sa gravité.**
- **US-5.3 : Ignorer un faux positif.**
- **US-5.4 : Ajouter une remarque.**
- **US-5.5 : Enregistrer la décision du gestionnaire.**
- **US-6.4 : Distinguer résultat IA et validation humaine.**
- **US-8.7 : Valider les anomalies.**
- **US-8.9 : Vérifier tout le scénario avec un test.**
- **US-9.8 : Ajouter des captures ou une démonstration.**
- **US-9.9 : Mettre à jour la documentation après l'intégration** — des mises à jour sont présentes dans les commits, mais la case reste décochée dans l'export Trello. La revue finale reste à confirmer.

Les US parentes 6, 8 et 9 restent donc en cours. US-11 « Voir un matériel » reste
à faire dans l'export et ne contient pas de checklist à numéroter.

Limites constatées :

- Les images annotées remplacent actuellement les photos de restitution en base ; les originaux ne sont pas conservés séparément.
- L'affichage des images n'est pas rafraîchi automatiquement après l'analyse : il faut rouvrir la page pour charger les annotations.
- Le contrôle JSON utilise une borne fixe de 1024 ; le dessin borne ensuite les coordonnées aux dimensions réelles de l'image.
- La qualité de détection et le parcours complet avec PostgreSQL, Ollama et des photos réelles restent à valider.

Livrables / DoR & DoD :

- DoR (Definition of Ready) retenue pour ce périmètre :
  - Le parcours de comparaison avant/après existe dans Gradio.
  - Les photos sont associées au matériel et distinguées entre référence et restitution.
  - Le format JSON attendu et les valeurs de gravité sont définis.
- Livrables réalisés :
  - Sauvegarde et historique des rapports intégrés à l'interface, au service métier et au stockage.
  - Pipeline IA asynchrone avec accès PostgreSQL déportés dans des threads.
  - Tests automatisés du transport HTTP, du client VLM et des interactions avec le stockage.
  - Documentation du lancement Docker et du parcours utilisateur.
- DoD (Definition of Done) restant à vérifier pour le parcours complet :
  - Un rapport sauvegardé peut être retrouvé après un redémarrage, lors d'un test avec une base réelle.
  - Le scénario complet de restitution, analyse, sauvegarde et consultation est vérifié dans l'application.
  - Une démonstration avec des photos réelles et le modèle Ollama cible est documentée.

Tests et critères d'acceptation :

- Vérification locale effectuée : `venv/bin/python -m unittest discover -s tests` — **28 tests réussis**.
- Les tests utilisent des échanges HTTP et des accès au stockage simulés ; ils ne valident pas le déploiement complet ni la qualité du modèle.
- Les tests couvrent notamment le refus des JSON invalides et des bbox hors limites, l'ordre avant/après des images, les erreurs HTTP et les timeouts, la fermeture du client, l'association des photos par zone et l'enregistrement des annotations.
- Les accès au stockage de l'analyse sont vérifiés hors de la boucle asynchrone.
- La sauvegarde et la consultation des rapports sont implémentées ; leur validation de bout en bout relève d'US-8.9.

Traçabilité des changements :

| Commit | Apport au sprint |
| --- | --- |
| `59ae0a2` | Attente de PostgreSQL avant le démarrage de l'application. |
| `1a03b04` | Sauvegarde des rapports, historique et rechargement des photos de restitution ; intégré par la PR #9 (`5e92c3f`). |
| `3f9c767` | Externalisation du prompt dans un fichier Markdown. |
| `35423af` | Renforcement des coordonnées, du dessin des annotations et des tests ; intégré par la PR #10 (`a9181a8`). |
| `2baa760` | Intégration de la PR #11 : pipeline asynchrone, séparation du stockage, transport HTTP partagé, tests et lancement Docker documenté. |

L'intégration initiale de l'IA dans Gradio, l'affichage des six angles et la
modification des matériels étaient déjà présents avant la borne retenue pour le
sprint 2. Ils ne sont pas comptabilisés comme de nouvelles réalisations ici.

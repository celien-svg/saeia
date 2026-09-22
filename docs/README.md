# Dossier Documentaire – SAE Suivi de Prêt d'Ordinateurs
## Référentiel Qualité de Développement R5-08A (L. Conoir – IUTLCO Informatique)

Ce dossier regroupe l'intégralité de la documentation du projet **SAE Suivi de Prêt d'Ordinateurs avec IA Multimodale**, rédigée conformément aux exigences méthodologiques et pédagogiques du cours **R5-08A – Qualité de Développement**.

---

## 📚 Cartographie des Documents

La documentation est articulée en trois volets complémentaires, répondant chacun aux normes et formats définis dans le cours :

```
docs/
├── README.md                      <-- Sommaire et guide d'accès (ce document)
│
├── qualite_developpement.md       <-- PARTIE 1 & 2 DU COURS :
│                                      - Caractéristiques de qualité ISO/IEC 25010
│                                      - Évaluation détaillée de la qualité d'usage & grille notée
│                                      - Techniques d'inspection : Test Driven Development (TDD)
│                                      - Spécifications BDD complètes en métalangage Gherkin
│
├── documentation_technique.md     <-- PARTIE 3 DU COURS (Volet Informaticien) :
│                                      - Modélisation du domaine (Entité-Association & BDD PostgreSQL)
│                                      - Diagramme de classes UML & Patrons de conception (Repository, DI, Adapter)
│                                      - Architecture logique multicouche & tiers physiques Docker
│                                      - Normes de codage PEP 8, typage statique, gestion des exceptions
│                                      - Processus de génération (Build Docker, compilation, CI GitHub Actions)
│                                      - Déploiement et commandes d'exploitation
│
├── documentation_utilisateur.md   <-- PARTIE 3 DU COURS (Volet Utilisateur) :
│                                      - Manuel et guide d'utilisation pas à pas sans jargon
│                                      - Déroulé chronologique du prêt à la restitution
│                                      - Tutoriel pédagogique de prise en main en 5 minutes
│                                      - Foire Aux Questions (FAQ) et gestion des cas limites
│                                      - Guide des bonnes pratiques de prise de vue photographique
│
└── monitoring/
    └── sprint-00.md               <-- Suivi agile des User Stories, DoR et DoD
```

---

## 🔍 Correspondance avec le Programme R5-08A

| Partie du cours R5-08A | Concepts théoriques abordés | Document de mise en œuvre |
| :--- | :--- | :--- |
| **Partie 1 : Caractéristiques de qualité** | • Crise du logiciel et causes d'erreurs<br>• Norme ISO/IEC 25010 (Interne, Externe, Usage)<br>• 6 caractéristiques (Fonctionnelle, Facilité, Fiabilité, Performance, Maintenabilité, Portabilité)<br>• Grilles d'évaluation de la qualité d'usage | [`qualite_developpement.md`](file:///c:/cours/BUT3/saeia/docs/qualite_developpement.md) |
| **Partie 2 : Techniques d'inspection** | • Philosophie TDD (logique Einstein)<br>• Cycle RED - GREEN - REFACTOR<br>• Pair-Programming (Driver / Navigator)<br>• BDD & métalangage Gherkin (`Feature`, `Scenario`, `Given`, `When`, `Then`) | [`qualite_developpement.md`](file:///c:/cours/BUT3/saeia/docs/qualite_developpement.md) |
| **Partie 3 : Documentation Technique** | • Pour informaticiens et mainteneurs<br>• Modélisation conceptuelle, relationnelle et objet (UML)<br>• Architecture multicouche & multi-tiers (Docker)<br>• Normes de code (PEP 8, docstrings, typing)<br>• Processus de build et déploiement continu (CI/CD) | [`documentation_technique.md`](file:///c:/cours/BUT3/saeia/docs/documentation_technique.md) |
| **Partie 3 : Documentation Utilisateur** | • Pour utilisateurs finaux sans jargon<br>• Manuel utilisateur pas à pas par fonctionnalité<br>• Tutoriel pédagogique de démarrage rapide<br>• FAQ (Foire Aux Questions)<br>• Aide en ligne, prévention d'erreurs & ergonomie | [`documentation_utilisateur.md`](file:///c:/cours/BUT3/saeia/docs/documentation_utilisateur.md) |

---

## 🚀 Accès Rapide aux Guides

- 👨‍💻 **Vous êtes développeur ou évaluateur technique ?**
  $\rightarrow$ Consultez la [Documentation Technique](file:///c:/cours/BUT3/saeia/docs/documentation_technique.md) et l'analyse [Qualité & Inspections TDD/BDD](file:///c:/cours/BUT3/saeia/docs/qualite_developpement.md).
- 🧑‍💼 **Vous êtes gestionnaire de prêt ou utilisateur ?**
  $\rightarrow$ Suivez le [Manuel Utilisateur & Tutoriel Pas à Pas](file:///c:/cours/BUT3/saeia/docs/documentation_utilisateur.md).
- 📋 **Vous souhaitez consulter le suivi agile ?**
  $\rightarrow$ Consultez le journal du [Sprint 0](file:///c:/cours/BUT3/saeia/docs/monitoring/sprint-00.md).


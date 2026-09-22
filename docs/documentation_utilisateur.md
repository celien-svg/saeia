# Guide d'Utilisation & Manuel Utilisateur
## Application de Suivi de Prêt d'Ordinateurs avec Analyse Visuelle par IA

---

## Table des matières

1. [Bienvenue](#1-bienvenue)
   - 1.1 [À quoi sert cette application ?](#11--quoi-sert-cette-application-)
   - 1.2 [Les grands principes : l'état Avant et l'état Après](#12-les-grands-principes--ltat-avant-et-ltat-aprs)
2. [Guide d'Utilisation Pas à Pas](#2-guide-dutilisation-pas--pas)
   - 2.1 [Étape 1 : Accéder à l'application et page d'accueil](#21-tape-1--accder--lapplication-et-page-daccueil)
   - 2.2 [Étape 2 : Consulter la liste du parc d'ordinateurs](#22-tape-2--consulter-la-liste-du-parc-dordinateurs)
   - 2.3 [Étape 3 : Enregistrer un nouvel ordinateur (Prêt initial)](#23-tape-3--enregistrer-un-nouvel-ordinateur-prt-initial)
   - 2.4 [Étape 4 : Restitution du matériel et versement des nouvelles photos](#24-tape-4--restitution-du-matriel-et-versement-des-nouvelles-photos)
   - 2.5 [Étape 5 : Consulter le diagnostic comparatif de l'IA](#25-tape-5--consulter-le-diagnostic-comparatif-de-lia)
   - 2.6 [Étape 6 : Modifier les informations d'un ordinateur](#26-tape-6--modifier-les-informations-dun-ordinateur)
   - 2.7 [Étape 7 : Supprimer un ordinateur en toute sécurité](#27-tape-7--supprimer-un-ordinateur-en-toute-scurit)
3. [Tutoriel Prise en Main Rapide (5 minutes)](#3-tutoriel-prise-en-main-rapide-5-minutes)
4. [Foire Aux Questions (FAQ)](#4-foire-aux-questions-faq)
5. [Conseils pour des Prises de Vue Optimales](#5-conseils-pour-des-prises-de-vue-optimales)

---

## 1. Bienvenue

### 1.1 À quoi sert cette application ?

Bienvenue sur l'application de **Suivi de Prêt d'Ordinateurs**. 

Cette solution a été spécialement conçue pour les gestionnaires et personnels administratifs chargés du prêt d'ordinateurs portables aux étudiants. Elle vous permet :
- De tenir un **inventaire à jour** et clair de toutes vos machines disponibles.
- D'enregistrer des **photos de référence** lors de la remise de l'ordinateur à l'étudiant.
- De photographier la machine à son **retour de prêt**.
- De confier à une **Intelligence Artificielle d'analyse visuelle** la comparaison minutieuse des deux états afin de mettre automatiquement en évidence les rayures, fissures, touches de clavier manquantes ou chocs récents.

> [!NOTE]
> L'Intelligence Artificielle est un **outil d'aide à la décision**. Elle surligne les zones suspectes pour vous faire gagner du temps, mais c'est toujours vous, gestionnaire, qui conservez le contrôle et la décision finale.

---

### 1.2 Les grands principes : l'état Avant et l'état Après

Pour chaque ordinateur portable, l'application suit deux étapes photographiques :

```
┌─────────────────────────────────┐        ┌──────────────────────────────────┐
│        1. PHOTO AVANT           │        │         2. PHOTO APRÈS           │
│   (État initial de référence)   │        │     (État lors du retour)        │
│ Prise le jour où l'ordinateur   │  ────► │ Prise le jour où l'étudiant      │
│ est remis à l'étudiant.         │        │ rend l'ordinateur.               │
└─────────────────────────────────┘        └──────────────────────────────────┘
                                                            │
                                                            ▼
                                           ┌──────────────────────────────────┐
                                           │       3. COMPARAISON IA          │
                                           │ L'ordinateur compare chaque face │
                                           │ et signale toute dégradation     │
                                           │ nouvelle (rayure, casse, tâche). │
                                           └──────────────────────────────────┘
```

Pour une efficacité maximale, 6 angles de vue sont documentés :
1. **Dessus** (capot supérieur)
2. **Dessous** (coque inférieure et patins)
3. **Écran** (dalle allumée ou éteinte)
4. **Clavier** (touches et pavé tactile)
5. **Connectique gauche** (ports USB, HDMI, alimentation)
6. **Connectique droite** (ports audio, lecteur de carte, USB)

---

## 2. Guide d'Utilisation Pas à Pas

### 2.1 Étape 1 : Accéder à l'application et page d'accueil

1. Ouvrez votre navigateur internet habituel (Google Chrome, Mozilla Firefox, Microsoft Edge).
2. Saisissez l'adresse de l'application : `http://localhost:7860` (ou l'adresse transmise par votre administrateur).
3. La page d'accueil s'affiche avec un bouton central : **« Voir la liste des ordinateurs »**. Cliquez dessus pour démarrer.

---

### 2.2 Étape 2 : Consulter la liste du parc d'ordinateurs

L'écran principal présente l'ensemble des machines sous forme de tableau clair et synthétique :

| Colonne | Signification |
| :--- | :--- |
| **Nom** | Désignation usuelle de la machine (ex. *Dell Latitude 5420 n°12*). |
| **État** | Situation physique : `OK`, `Réservé`, `En réparation`, `Endommagé`, ou `Disparu`. |
| **Localisation** | Salle ou bureau où se trouve actuellement la machine (ex. *Bureau B102*). |
| **Modifier** | Bouton ouvrant la fiche de l'ordinateur pour corriger ou actualiser ses informations. |
| **Supprimer** | Bouton permettant de retirer définitivement une machine de l'inventaire. |
| **Analyse** | Bouton ouvrant le comparateur photographique pour vérifier l'état au retour de prêt. |

En haut du tableau, vous disposez de deux boutons d'action rapide :
- **« Ajouter un ordinateur »** : pour enregistrer un nouvel appareil.
- **« Accueil »** : pour revenir à la page d'ouverture.

---

### 2.3 Étape 3 : Enregistrer un nouvel ordinateur (Prêt initial)

Pour ajouter une machine dans l'inventaire :
1. Depuis la liste, cliquez sur le bouton **« Ajouter un ordinateur »**.
2. Remplissez les informations demandées :
   - **Nom \*** *(obligatoire)* : Nom reconnaissable de l'ordinateur.
   - **Modèle** : Marque et modèle précis (ex. *Lenovo ThinkPad E14*).
   - **Année** : Année d'acquisition.
   - **Étiquette ULCO** : Numéro d'inventaire unique figurant sur le code-barres de la machine.
   - **État \*** *(obligatoire)* : Sélectionnez `OK` par défaut.
   - **Localisation \*** *(obligatoire)* : Lieu de stockage initial.
   - **Descriptif & Remarque** : Remarques éventuelles (ex. *Chargeur d'origine inclus*).
   - **Identifiant de l'entité \*** *(obligatoire)* : Entrez `1` (pour l'ULCO).
3. **Déposez les 6 photos d'état initial** dans les cadres prévus :
   - Vous pouvez glisser-déposer vos fichiers images ou cliquer sur chaque zone pour sélectionner les photos depuis votre ordinateur ou smartphone.
4. Cliquez sur **« Enregistrer »**.
   - *Si tout est valide :* un message vert de confirmation s'affiche en haut de l'écran et vous retournez à la liste.
   - *Si un champ obligatoire a été oublié :* un message d'avertissement jaune apparaît pour vous indiquer précisément quel champ manque, sans effacer le reste de vos saisies !

---

### 2.4 Étape 4 : Restitution du matériel et versement des nouvelles photos

Lorsqu'un étudiant rapporte son ordinateur à l'issue de sa période de prêt :
1. Repérez la ligne correspondant à l'ordinateur dans la liste.
2. Cliquez sur le bouton **« Analyse »** situé à droite de la ligne.
3. La page d'analyse s'ouvre :
   - Dans la colonne de gauche, vous retrouvez la **Photo avant** prise le jour du prêt.
   - Dans la colonne de droite, déposez la **Photo après** correspondante que vous venez de prendre.
4. Une fois les photos de retour déposées, cliquez sur le bouton bleu **« Ajouter les photos »**.
5. Une notification confirme : *« Photos d'analyse enregistrées. »*

---

### 2.5 Étape 5 : Consulter le diagnostic comparatif de l'IA

Directement sous les photos de la page d'analyse se trouve le bloc **🤖 Réponse de l'IA** :
- L'analyse comparative se charge d'examiner chaque angle de l'ordinateur.
- Si l'ordinateur est restitué en parfait état, l'IA indique qu'aucune dégradation n'a été constatée.
- En cas d'anomalie, un compte-rendu clair vous indique :
  - La zone touchée (écran, capot, connectique, etc.).
  - Le type de dégât (rayure, fissure, choc, tâche).
  - Le degré de gravité : **légère**, **marquée** ou **importante**.

---

### 2.6 Étape 6 : Modifier les informations d'un ordinateur

Si un ordinateur change de localisation, passe en maintenance ou si vous souhaitez corriger une étiquette :
1. Dans la liste, cliquez sur le bouton **« Modifier »** de la machine concernée.
2. Le formulaire s'ouvre **automatiquement pré-rempli** avec toutes les données actuelles de l'ordinateur.
3. Modifiez uniquement les informations souhaitées (par exemple, passez l'état à `En réparation` ou changez la localisation).
4. *Gestion des photos :* Vous n'avez pas besoin de recharger les photos ! Laissez les cadres de photos vides pour **conserver automatiquement les photos existantes**. Déposez une photo uniquement si vous souhaitez remplacer une photo de référence.
5. Cliquez sur **« Enregistrer les modifications »**. Un message vert confirme la mise à jour.

---

### 2.7 Étape 7 : Supprimer un ordinateur en toute sécurité

Pour éviter toute perte accidentelle de données suite à une maladresse de souris, le logiciel intègre une **sécurité à double confirmation** :
1. Cliquez sur le bouton **« Supprimer »** en face de l'ordinateur concerné.
2. Le bouton devient rouge et son texte se transforme en **« Confirmer ? »**.
3. **Si vous avez cliqué par erreur :** cliquez simplement ailleurs ou rechargez la page, l'ordinateur ne sera pas supprimé.
4. **Si vous souhaitez réellement supprimer la fiche :** cliquez une deuxième fois sur **« Confirmer ? »**. L'ordinateur et toutes ses photos associées sont alors supprimés définitivement.

---

## 3. Tutoriel Prise en Main Rapide (5 minutes)

### Scénario : « Mon premier prêt et retour d'ordinateur »

Suivez cet exemple guidé pour maîtriser l'application en quelques minutes :

1. **Création du matériel (Départ)** :
   - Cliquez sur **« Voir la liste des ordinateurs »**, puis sur **« Ajouter un ordinateur »**.
   - Nom : `PC Test 01` | État : `OK` | Localisation : `Accueil IUT` | Entité : `1`.
   - Chargez une photo nette du capot et de l'écran dans les cadres correspondants.
   - Cliquez sur **« Enregistrer »**. Votre ordinateur apparaît aussitôt dans le tableau !
2. **Simulation du retour (Restitution)** :
   - Sur la ligne de `PC Test 01`, cliquez sur **« Analyse »**.
   - Observez à gauche la photo de départ.
   - Déposez dans le cadre de droite la photo prise au retour.
   - Cliquez sur **« Ajouter les photos »**.
3. **Mise à jour de l'inventaire** :
   - Cliquez sur **« Retour à la liste »**.
   - Cliquez sur **« Modifier »** pour passer l'état à `Réservé` pour le prochain prêt.
   - Cliquez sur **« Enregistrer les modifications »**.

Félicitations, vous maîtrisez l'intégralité du cycle de gestion !

---

## 4. Foire Aux Questions (FAQ)

### Q1 : Quels sont les formats de photos acceptés ?
**R :** L'application accepte tous les formats d'images courants : **JPEG (.jpg, .jpeg)**, **PNG (.png)** et **WebP**. Les images sont automatiquement compressées et optimisées par le logiciel pour ne pas saturer l'espace disque.

### Q2 : Que se passe-t-il si j'oublie de remplir un champ obligatoire ?
**R :** Aucun risque de blocage ! Un bandeau d'avertissement jaune apparaît en haut de l'écran en vous indiquant les champs manquants (par exemple : *« Champs obligatoires manquants : le nom, la localisation »*). Tout ce que vous aviez déjà écrit ou téléversé reste en place.

### Q3 : Pourquoi l'application refuse-t-elle mon étiquette ULCO ?
**R :** Chaque étiquette ULCO est un identifiant unique. Si vous recevez le message *« Cette étiquette ULCO existe déjà »*, c'est qu'un autre ordinateur porte déjà ce numéro dans la base. Vérifiez l'inventaire pour éviter les doublons.

### Q4 : Que faire si l'IA signale une rayure qui n'en est pas une (faux positif) ?
**R :** Un reflet de lumière ou un cheveu sur la coque peut parfois être interprété comme une rayure par le modèle de vision. L'avis de l'IA n'étant qu'indicatif, vous pouvez inspecter visuellement la zone et ignorer le signalement si la machine est intacte.

### Q5 : Puis-je modifier un ordinateur sans devoir reprendre toutes les photos ?
**R :** Oui, absolument ! Dans le formulaire de modification, laissez simplement les champs photos vides : l'application conservera fidèlement les photos de référence déjà enregistrées.

---

## 5. Conseils pour des Prises de Vue Optimales

Pour que la comparaison visuelle par l'Intelligence Artificielle soit la plus précise et fiable possible, suivez ces quelques recommandations lors de vos prises de clichés :

```
    ✅ À FAIRE                                   ❌ À ÉVITER
 ────────────────────────────────────────────────────────────────────────────
 • Poser l'ordinateur à plat sur une table   • Tenir l'ordinateur à bout de bras
 • Privilégier une lumière blanche et diffuse• Utiliser un flash direct (reflets)
 • Cadrer la face entière de façon centrée   • Prendre la photo de biais / trop près
 • Nettoyer l'écran avec un chiffon microfibre• Laisser des traces de doigts ou poussière
```

En respectant ces consignes simples, la détection des dégradations sera quasi-instantanée et sans ambiguïté.


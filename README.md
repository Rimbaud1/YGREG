# YGREG - Éditeur de Texte en Console

YGREG est un éditeur de texte léger et rapide qui s'exécute entièrement dans votre terminal. Il est conçu pour être simple à utiliser tout en offrant des fonctionnalités puissantes pour les développeurs et les écrivains.

## Fonctionnalités

*   **Coloration syntaxique** pour plusieurs langages (Python, JavaScript, HTML, CSS, JSON).
*   **Explorateur de fichiers intégré** pour naviguer facilement dans vos projets.
*   **Recherche et remplacement** de texte.
*   **Support de la souris** pour la navigation et la sélection.
*   **Auto-complétion** pour les dates, heures et UUIDs.
*   **Calculatrice intégrée** pour les opérations mathématiques simples.
*   **Gestion des thèmes** pour personnaliser l'apparence de l'éditeur.
*   **Sauvegarde automatique** pour ne jamais perdre votre travail.
*   **Support des caractères Unicode**.

## Installation et Lancement

Pour utiliser YGREG, vous devez avoir Python 3.6 ou une version ultérieure installée sur votre système.

1.  Clonez ce dépôt sur votre machine locale.
2.  Accédez au répertoire du projet.
3.  Lancez l'éditeur :
    ```bash
    python3 ygreg_cli.py
    ```
Vous pouvez également ouvrir un fichier directement :
    ```bash
    python3 ygreg_cli.py chemin/vers/votre/fichier.txt
    ```

## Commandes et Raccourcis

### Explorateur de fichiers

*   **Flèches haut/bas** : Naviguer dans la liste des fichiers.
*   **Entrée** : Ouvrir un fichier ou un dossier.
*   **Suppr** : Supprimer un fichier ou un dossier.
*   **Tab** : Ouvrir le menu des commandes.
*   **p** : Ouvrir les paramètres.
*   **h** : Ouvrir la page d'aide.
*   **q** : Quitter l'application.

### Éditeur de texte

*   **Tab** : Ouvrir le menu des commandes.
    *   **s** : Sauvegarder le fichier.
    *   **q** : Quitter l'éditeur.
    *   **h** : Ouvrir la page d'aide.
    *   **p** : Ouvrir les paramètres.
    *   **f** : Rechercher du texte.
    *   **r** : Remplacer du texte.
    *   **g** : Aller à une ligne spécifique.
    *   **d** : Dupliquer la ligne ou la sélection.
    *   **j** : Joindre la ligne actuelle avec la suivante.
    *   **o** : Ordonner les lignes.
    *   **t** : Insérer un tableau.
    *   **x** : Couper la sélection.
    *   **c** : Copier la sélection.
    *   **v** : Coller la sélection.
*   **Ctrl + s** : Sauvegarder le fichier.
*   **Ctrl + q** : Quitter l'éditeur.
*   **Ctrl + f** : Rechercher du texte.
*   **Ctrl + c** : Copier la sélection.
*   **Ctrl + x** : Couper la sélection.
*   **Ctrl + v** : Coller la sélection.
*   **Ctrl + d** : Dupliquer la ligne ou la sélection.
*   **Flèches** : Déplacer le curseur.
*   **Page précédente/suivante** : Naviguer dans le fichier.
*   **Début/Fin** : Aller au début/fin de la ligne.
*   **Retour arrière** : Supprimer le caractère précédent.
*   **Suppr** : Supprimer le caractère suivant.
*   **Entrée** : Insérer une nouvelle ligne.

## Contribuer

Les contributions sont les bienvenues ! Si vous souhaitez améliorer YGREG, n'hésitez pas à forker le projet, à apporter vos modifications et à créer une pull request.
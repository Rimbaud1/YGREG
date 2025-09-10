ygreg_editor/
├── ygreg_cli.py          # Script principal, point d'entrée de l'application
└── ygreg/
    ├── __init__.py         # Rend 'ygreg' un package Python
    ├── constants.py      # Toutes les constantes (mots-clés, icônes, etc.)
    ├── editor.py         # Classe principale de l'éditeur de texte
    ├── file_selector.py  # Classe de l'explorateur de fichiers
    ├── screens.py        # Classes pour les écrans secondaires (Aide, Paramètres)
    ├── settings.py       # Classe pour la gestion des paramètres (config.json)
    ├── syntax.py         # Fonctions dédiées à la coloration syntaxique
    ├── themes.py         # Fonction pour la gestion des thèmes de couleur
    └── utils.py          # Fonctions utilitaires partagées
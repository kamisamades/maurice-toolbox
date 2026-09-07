# Maurice Toolbox 🛠️

Boite à outils Python avec interface graphique Tkinter - Collection d'utilitaires développés par Maurice.

## 📋 Description

**Maurice Toolbox** est une application Python modulaire qui regroupe différents outils utilitaires dans une interface graphique unique. Chaque outil est développé dans un module séparé et peut être lancé indépendamment depuis l'interface principale.

## ✨ Fonctionnalités

### Interface Principale
- Menu **Fichier** : Quitter l'application
- Menu **Outils** : Réservé pour les futurs outils
- Menu **Aide** : Informations sur l'application (version, auteur)
- Grille d'icônes carrées pour accéder aux outils
- Fenêtres séparées pour chaque outil

### Outils Disponibles

#### 🗑️ Clean Useless Files
Permet de nettoyer un dossier en supprimant les fichiers temporaires et inutiles :
- Fichiers système macOS (`.DS_Store`, `._*`, `__MACOSX`)
- Fichiers Windows (`Thumbs.db`, `desktop.ini`)
- Fichiers temporaires (`.tmp`, `.bak`, `.swp`, `*~`)
- Fichiers de verrouillage Office (`~$*.doc*`, `.~lock.*`)

**Fonctionnement :**
1. Sélectionnez un dossier à nettoyer
2. Cliquez sur "Analyser le dossier"
3. Visualisez la liste des fichiers détectés
4. Confirmez la suppression

#### 📦 Zip Dir
Permet de compresser un dossier dans un fichier zip
- Possibilité d'analyser au préalable le dossier choisi
- Possibilité d'inclure et/ou exclure des extensions de fichier en particuliers

**Fonctionnement :**
1. Sélectionner un dossier à compresser
2. Sélectionner le fichier zip de sortie (par défaut, <dir>-archive.zip dans le dossier parent de <dir>)
3. Saisir (ou laisser vide) les extensions de fichier à inclure et/ou exclure dans le fichier zip
4. Cliquer sur "Créer un zip"

## 🏗️ Architecture du Projet

```
maurice-toolbox/
├── main.py                 # Point d'entrée et interface principale
├── modules/                # Dossier des modules/outils
│   ├── __init__.py        # Fichier d'initialisation du package
│   └── clean_useless_files.py  # Premier outil : Clean Useless Files
├── README.md              # Ce fichier
└── .gitignore             # Fichiers à ignorer (optionnel)
```

## 🚀 Installation

### Prérequis
- Python 3.6 ou supérieur
- Tkinter (généralement inclus avec Python)

### Cloner le dépôt
```bash
git clone https://github.com/kamisamades/maurice-toolbox.git
cd maurice-toolbox
```

### Lancer l'application
```bash
python main.py
```

## 📦 Ajouter un Nouvel Outil

Pour ajouter un nouvel outil :

1. Créez un nouveau fichier dans `modules/` : `modules/mon_outil.py`
2. Développez votre classe d'outil avec une interface Tkinter
3. Importez le module dans `main.py`
4. Ajoutez une icône dans `_create_tools_area()`
5. Créez la méthode de lancement correspondante

### Exemple de structure de module
```python
import tkinter as tk

class MonOutil:
    def __init__(self, root):
        self.root = root
        self.root.title("Mon Outil")
        # Votre code ici
```

## 📝 Informations

- **Version** : 1.1.0
- **Auteur** : Maurice
- **Web** : [lebrun.dev](https://lebrun.dev)
- **Licence** : MIT

## 🤝 Contributions

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📞 Contact

Pour toute question ou suggestion, vous pouvez contacter l'auteur via son site web.

## 🗒️ Changelog

Version 1.1.0 (07/09/2026) :
- Ajout du Changelog
- Ajout du module "zip_dir.py" permettant de créer un fichier zip à partir d'un répertoire
- Possibilité d'inclure et/ou exclure des extensions de fichier en particuliers
- Possibilité d'analyse du dossier (taille du répertoire + nombre de fichier)
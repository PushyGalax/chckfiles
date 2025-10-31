
# 🗂️ Comparateur d'Archives - APST2607

**Développé par Michel Bermond - Association Prévention Santé au Travail 2607**

## 📦 Description

Ce projet est une application graphique professionnelle permettant de comparer le contenu d'une archive extraite avec un répertoire de référence. Il identifie les fichiers et dossiers **manquants**, **supplémentaires**, ou **modifiés**, et propose une interface moderne pour visualiser les résultats.

L'application est optimisée pour traiter de **gros volumes de données** (jusqu'à 144K fichiers et 96GB), avec une console étendue, une barre de progression, et des exports détaillés.

## ✨ Fonctionnalités

- 🔍 Comparaison complète d'archives avec détection :
  - Fichiers/Dossiers manquants
  - Fichiers/Dossiers supplémentaires
  - Fichiers modifiés (via hash SHA-256)
- 📊 Interface graphique moderne (Tkinter + ttk)
- 📁 Export/Import des résultats au format JSON
- 🧠 Détection intelligente des doublons
- 🖥️ Console étendue pour gros volumes
- 📈 Statistiques et affichage en arbre
- 🧪 Gestion robuste des erreurs et des fichiers système
## 🛠️ Installation
```bash
git clone https://github.com/<ton-utilisateur>/comparateur-archives.git
cd comparateur-archives
pip install -r requirements.txt  # Si tu ajoutes un requirements.txt
python main.py
